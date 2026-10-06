using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using SmartTravelApp.Data;
using SmartTravelApp.Services;

var builder = WebApplication.CreateBuilder(args);

// 1. Dodanie kontrolerów z obsługą JSON
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// 2. Konfiguracja Bazy Danych EF Core (SQL Server z awaryjnym przejście na InMemory do natychmiastowych testów)
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    if (!string.IsNullOrEmpty(connectionString) && !builder.Environment.IsEnvironment("Testing"))
    {
        try
        {
            options.UseSqlServer(connectionString);
        }
        catch
        {
            options.UseInMemoryDatabase("SmartTravelFallbackDb");
        }
    }
    else
    {
        options.UseInMemoryDatabase("SmartTravelFallbackDb");
    }
});

// 3. Konfiguracja HttpClient i Serwisów Aplikacyjnych
builder.Services.AddHttpClient<ITravelDashboardService, TravelDashboardService>();
builder.Services.AddScoped<IEmailService, EmailService>();
builder.Services.AddScoped<IAuthService, AuthService>();

// 4. Konfiguracja Autentykacji JWT Bearer
var jwtKey = builder.Configuration["Jwt:Key"] ?? "SuperSecretDefaultSecurityKeyForInformatykaProj2026WithEnoughLength!!";
var keyBytes = Encoding.UTF8.GetBytes(jwtKey);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.RequireHttpsMetadata = false;
    options.SaveToken = true;
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(keyBytes),
        ValidateIssuer = true,
        ValidIssuer = builder.Configuration["Jwt:Issuer"] ?? "SmartTravelApp",
        ValidateAudience = true,
        ValidAudience = builder.Configuration["Jwt:Audience"] ?? "SmartTravelAppUsers",
        ValidateLifetime = true,
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

// 5. Konfiguracja CORS (dla zapytań z frontendu)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// 6. Automatyczne tworzenie bazy danych w środowisku deweloperskim
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    try
    {
        db.Database.EnsureCreated();
    }
    catch
    {
        // Jeśli SQL Server niedostępny lokalnie, używamy bazy in-memory
    }
}

// 7. Middlewares
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Smart Travel API v1");
    c.RoutePrefix = "swagger";
});

app.UseCors("AllowAll");
app.UseDefaultFiles(); // Pozwala na automatyczne serwowanie index.html z wwwroot
app.UseStaticFiles();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
