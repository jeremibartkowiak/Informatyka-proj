using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SmartTravelApp.Services;

namespace SmartTravelApp.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class DashboardController : ControllerBase
    {
        private readonly ITravelDashboardService _dashboardService;

        public DashboardController(ITravelDashboardService dashboardService)
        {
            _dashboardService = dashboardService;
        }

        /// <summary>
        /// Pobieranie połączonych danych z 3 API (Geo, NBP Kursy, Open-Meteo Pogoda)
        /// </summary>
        [HttpGet("destination")]
        public async Task<IActionResult> GetDestinationData([FromQuery] string country = "Poland")
        {
            int userId = GetCurrentUserId();
            var data = await _dashboardService.GetDashboardDataAsync(country, userId);
            return Ok(data);
        }

        /// <summary>
        /// Pobieranie historii zapytań zalogowanego użytkownika
        /// </summary>
        [HttpGet("history")]
        public async Task<IActionResult> GetSearchHistory()
        {
            int userId = GetCurrentUserId();
            var history = await _dashboardService.GetSearchHistoryAsync(userId);
            return Ok(history);
        }

        private int GetCurrentUserId()
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
            if (!string.IsNullOrEmpty(userIdClaim) && int.TryParse(userIdClaim, out int userId))
            {
                return userId;
            }
            return 0;
        }
    }
}
