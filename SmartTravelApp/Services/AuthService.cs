using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using BCrypt.Net;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using SmartTravelApp.Data;
using SmartTravelApp.Models;

namespace SmartTravelApp.Services
{
    public interface IAuthService
    {
        Task<AuthResponse> RegisterAsync(RegisterRequest request, string baseUrl);
        Task<AuthResponse> ConfirmEmailAsync(string token);
        Task<AuthResponse> LoginAsync(LoginRequest request);
        Task<UserProfileDto?> GetUserProfileAsync(int userId);
    }

    public class AuthService : IAuthService
    {
        private readonly ApplicationDbContext _db;
        private readonly IEmailService _emailService;
        private readonly IConfiguration _configuration;

        public AuthService(ApplicationDbContext db, IEmailService emailService, IConfiguration configuration)
        {
            _db = db;
            _emailService = emailService;
            _configuration = configuration;
        }

        public async Task<AuthResponse> RegisterAsync(RegisterRequest request, string baseUrl)
        {
            if (string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Password))
            {
                return new AuthResponse { Success = false, Message = "Email i hasło są wymagane." };
            }

            string emailLower = request.Email.Trim().ToLowerInvariant();

            if (await _db.Users.AnyAsync(u => u.Email == emailLower))
            {
                return new AuthResponse { Success = false, Message = "Użytkownik o podanym adresie e-mail już istnieje." };
            }

            // Haszowanie hasła za pomocą BCrypt
            string passwordHash = BCrypt.Net.BCrypt.HashPassword(request.Password);

            var user = new User
            {
                Email = emailLower,
                PasswordHash = passwordHash,
                IsEmailConfirmed = false,
                CreatedAt = DateTime.UtcNow
            };

            _db.Users.Add(user);
            await _db.SaveChangesAsync();

            // Generowanie tokena aktywacyjnego
            string activationTokenString = Guid.NewGuid().ToString("N") + Guid.NewGuid().ToString("N");
            var activationToken = new EmailConfirmationToken
            {
                UserId = user.Id,
                Token = activationTokenString,
                ExpiresAt = DateTime.UtcNow.AddHours(24),
                IsUsed = false,
                CreatedAt = DateTime.UtcNow
            };

            _db.EmailConfirmationTokens.Add(activationToken);
            await _db.SaveChangesAsync();

            // Wysyłka symulowana e-maila
            await _emailService.SendActivationEmailAsync(user.Email, activationTokenString, baseUrl);

            string activationLink = $"{baseUrl.TrimEnd('/')}/api/auth/confirm-email?token={activationTokenString}";

            return new AuthResponse
            {
                Success = true,
                Message = "Rejestracja powiodła się! Na podany adres e-mail został wysłany link aktywacyjny.",
                Email = user.Email,
                ActivationLink = activationLink
            };
        }

        public async Task<AuthResponse> ConfirmEmailAsync(string token)
        {
            if (string.IsNullOrWhiteSpace(token))
            {
                return new AuthResponse { Success = false, Message = "Nieprawidłowy token aktywacyjny." };
            }

            var confirmationToken = await _db.EmailConfirmationTokens
                .Include(t => t.User)
                .FirstOrDefaultAsync(t => t.Token == token);

            if (confirmationToken == null)
            {
                return new AuthResponse { Success = false, Message = "Token aktywacyjny nie istnieje w systemie." };
            }

            if (confirmationToken.IsUsed)
            {
                return new AuthResponse { Success = false, Message = "Ten token aktywacyjny został już wcześniej wykorzystany." };
            }

            if (confirmationToken.ExpiresAt < DateTime.UtcNow)
            {
                return new AuthResponse { Success = false, Message = "Token aktywacyjny wygasł. Proszę zarejestrować się ponownie." };
            }

            // Potwierdzenie e-maila
            confirmationToken.IsUsed = true;
            if (confirmationToken.User != null)
            {
                confirmationToken.User.IsEmailConfirmed = true;
            }

            await _db.SaveChangesAsync();

            return new AuthResponse
            {
                Success = true,
                Message = "Konto zostało pomyślnie aktywowane! Możesz się teraz zalogować.",
                Email = confirmationToken.User?.Email
            };
        }

        public async Task<AuthResponse> LoginAsync(LoginRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Password))
            {
                return new AuthResponse { Success = false, Message = "Proszę podać e-mail oraz hasło." };
            }

            string emailLower = request.Email.Trim().ToLowerInvariant();
            var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == emailLower);

            if (user == null)
            {
                return new AuthResponse { Success = false, Message = "Nieprawidłowy e-mail lub hasło." };
            }

            // Weryfikacja hasła BCrypt
            if (!BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            {
                return new AuthResponse { Success = false, Message = "Nieprawidłowy e-mail lub hasło." };
            }

            // Weryfikacja czy e-mail został potwierdzony
            if (!user.IsEmailConfirmed)
            {
                return new AuthResponse
                {
                    Success = false,
                    Message = "Konto nie zostało jeszcze aktywowane. Proszę kliknąć w link aktywacyjny przesłany na adres e-mail."
                };
            }

            // Generowanie tokena JWT
            string jwtToken = GenerateJwtToken(user);

            return new AuthResponse
            {
                Success = true,
                Message = "Logowanie udane!",
                Token = jwtToken,
                Email = user.Email
            };
        }

        public async Task<UserProfileDto?> GetUserProfileAsync(int userId)
        {
            var user = await _db.Users.FindAsync(userId);
            if (user == null) return null;

            return new UserProfileDto
            {
                Id = user.Id,
                Email = user.Email,
                IsEmailConfirmed = user.IsEmailConfirmed,
                CreatedAt = user.CreatedAt
            };
        }

        private string GenerateJwtToken(User user)
        {
            var jwtKey = _configuration["Jwt:Key"] ?? "SuperSecretDefaultSecurityKeyForInformatykaProj2026WithEnoughLength!!";
            var issuer = _configuration["Jwt:Issuer"] ?? "SmartTravelApp";
            var audience = _configuration["Jwt:Audience"] ?? "SmartTravelAppUsers";

            var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey));
            var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);

            var claims = new[]
            {
                new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
                new Claim(JwtRegisteredClaimNames.Email, user.Email),
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
                new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
            };

            var token = new JwtSecurityToken(
                issuer: issuer,
                audience: audience,
                claims: claims,
                expires: DateTime.UtcNow.AddHours(8),
                signingCredentials: credentials);

            return new JwtSecurityTokenHandler().WriteToken(token);
        }
    }
}
