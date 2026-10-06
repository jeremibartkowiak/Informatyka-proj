using System;
using System.Collections.Generic;

namespace SmartTravelApp.Models
{
    // Auth DTOs
    public class RegisterRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }

    public class LoginRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }

    public class AuthResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public string? Token { get; set; }
        public string? Email { get; set; }
        public string? ActivationLink { get; set; } // Zwracany przy rejestracji dla celów prezentacji/testów
    }

    public class UserProfileDto
    {
        public int Id { get; set; }
        public string Email { get; set; } = string.Empty;
        public bool IsEmailConfirmed { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    // Dashboard & Zewnętrzne API DTOs
    public class DashboardRequest
    {
        public string CountryName { get; set; } = string.Empty;
    }

    public class TravelDashboardResponse
    {
        public string Country { get; set; } = string.Empty;
        public CountryInfoDto? GeoData { get; set; }
        public CurrencyRateDto? CurrencyData { get; set; }
        public WeatherDto? WeatherData { get; set; }
        public DateTime FetchedAt { get; set; } = DateTime.UtcNow;
    }

    public class CountryInfoDto
    {
        public string Name { get; set; } = string.Empty;
        public string OfficialName { get; set; } = string.Empty;
        public string Capital { get; set; } = string.Empty;
        public long Population { get; set; }
        public string Region { get; set; } = string.Empty;
        public string FlagUrl { get; set; } = string.Empty;
        public string FlagEmoji { get; set; } = string.Empty;
        public string CurrencyCode { get; set; } = string.Empty;
        public string CurrencyName { get; set; } = string.Empty;
        public string CurrencySymbol { get; set; } = string.Empty;
        public double CapitalLatitude { get; set; }
        public double CapitalLongitude { get; set; }
    }

    public class CurrencyRateDto
    {
        public string CurrencyCode { get; set; } = string.Empty;
        public string BaseCurrency { get; set; } = "PLN";
        public decimal RateToPln { get; set; }
        public string RateDate { get; set; } = string.Empty;
        public string Note { get; set; } = string.Empty;
    }

    public class WeatherDto
    {
        public string LocationName { get; set; } = string.Empty;
        public double TemperatureC { get; set; }
        public double WindSpeedKmh { get; set; }
        public int WeatherCode { get; set; }
        public string WeatherDescription { get; set; } = string.Empty;
    }

    public class SearchLogDto
    {
        public int Id { get; set; }
        public string Query { get; set; } = string.Empty;
        public DateTime SearchedAt { get; set; }
    }
}
