using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace SmartTravelApp.Services
{
    public interface IEmailService
    {
        Task SendActivationEmailAsync(string recipientEmail, string activationToken, string baseUrl);
    }

    public class EmailService : IEmailService
    {
        private readonly ILogger<EmailService> _logger;

        public EmailService(ILogger<EmailService> logger)
        {
            _logger = logger;
        }

        public Task SendActivationEmailAsync(string recipientEmail, string activationToken, string baseUrl)
        {
            string activationUrl = $"{baseUrl.TrimEnd('/')}/api/auth/confirm-email?token={activationToken}";

            // W rzeczywistej aplikacji tutaj znajdowałby się kod SMTP (np. Mailkit / SendGrid / Azure Communication Services)
            _logger.LogInformation("==================================================================");
            _logger.LogInformation($"[EMAIL ACTIVATION SIMULATION] Do: {recipientEmail}");
            _logger.LogInformation($"Link Aktywacyjny: {activationUrl}");
            _logger.LogInformation("==================================================================");

            return Task.CompletedTask;
        }
    }
}
