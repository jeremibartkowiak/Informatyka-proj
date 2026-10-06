using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SmartTravelApp.Models;
using SmartTravelApp.Services;

namespace SmartTravelApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;

        public AuthController(IAuthService authService)
        {
            _authService = authService;
        }

        /// <summary>
        /// Rejestracja nowego użytkownika i wysłanie linku aktywacyjnego
        /// </summary>
        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterRequest request)
        {
            string baseUrl = $"{Request.Scheme}://{Request.Host}";
            var result = await _authService.RegisterAsync(request, baseUrl);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }

        /// <summary>
        /// Potwierdzenie adresu e-mail na podstawie tokena
        /// </summary>
        [HttpGet("confirm-email")]
        public async Task<IActionResult> ConfirmEmail([FromQuery] string token)
        {
            var result = await _authService.ConfirmEmailAsync(token);

            if (!result.Success)
            {
                return BadRequest(result);
            }

            // Opcjonalnie można przekierować na stronę logowania frontendu z komunikatem
            return Ok(result);
        }

        /// <summary>
        /// Logowanie użytkownika (wymaga aktywnego e-maila) i zwrot JWT Token
        /// </summary>
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            var result = await _authService.LoginAsync(request);

            if (!result.Success)
            {
                return Unauthorized(result);
            }

            return Ok(result);
        }

        /// <summary>
        /// Pobieranie profilu zalogowanego użytkownika
        /// </summary>
        [Authorize]
        [HttpGet("me")]
        public async Task<IActionResult> GetProfile()
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
            if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out int userId))
            {
                return Unauthorized(new { Message = "Brak autoryzacji." });
            }

            var profile = await _authService.GetUserProfileAsync(userId);
            if (profile == null)
            {
                return NotFound(new { Message = "Nie znaleziono profilu." });
            }

            return Ok(profile);
        }
    }
}
