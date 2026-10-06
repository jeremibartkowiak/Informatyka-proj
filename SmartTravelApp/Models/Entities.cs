using System;
using System.Collections.Generic;

namespace SmartTravelApp.Models
{
    public class User
    {
        public int Id { get; set; }
        public string Email { get; set; } = string.Empty;
        public string PasswordHash { get; set; } = string.Empty;
        public bool IsEmailConfirmed { get; set; } = false;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        // Navigation properties
        public ICollection<EmailConfirmationToken> ConfirmationTokens { get; set; } = new List<EmailConfirmationToken>();
        public ICollection<UserSearchLog> SearchLogs { get; set; } = new List<UserSearchLog>();
    }

    public class EmailConfirmationToken
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public string Token { get; set; } = string.Empty;
        public DateTime ExpiresAt { get; set; }
        public bool IsUsed { get; set; } = false;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        // Navigation property
        public User? User { get; set; }
    }

    public class UserSearchLog
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public string Query { get; set; } = string.Empty;
        public DateTime SearchedAt { get; set; } = DateTime.UtcNow;

        // Navigation property
        public User? User { get; set; }
    }
}
