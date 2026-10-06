using Microsoft.EntityFrameworkCore;
using SmartTravelApp.Models;

namespace SmartTravelApp.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users => Set<User>();
        public DbSet<EmailConfirmationToken> EmailConfirmationTokens => Set<EmailConfirmationToken>();
        public DbSet<UserSearchLog> UserSearchLogs => Set<UserSearchLog>();

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Tabela Users
            modelBuilder.Entity<User>(entity =>
            {
                entity.ToTable("Users");
                entity.HasKey(e => e.Id);
                entity.HasIndex(e => e.Email).IsUnique();
                entity.Property(e => e.Email).IsRequired().HasMaxLength(256);
                entity.Property(e => e.PasswordHash).IsRequired();
                entity.Property(e => e.IsEmailConfirmed).HasDefaultValue(false);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
            });

            // Tabela EmailConfirmationTokens
            modelBuilder.Entity<EmailConfirmationToken>(entity =>
            {
                entity.ToTable("EmailConfirmationTokens");
                entity.HasKey(e => e.Id);
                entity.HasIndex(e => e.Token).IsUnique();
                entity.Property(e => e.Token).IsRequired().HasMaxLength(128);
                entity.Property(e => e.ExpiresAt).IsRequired();
                entity.Property(e => e.IsUsed).HasDefaultValue(false);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");

                entity.HasOne(e => e.User)
                      .WithMany(u => u.ConfirmationTokens)
                      .HasForeignKey(e => e.UserId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // Tabela UserSearchLogs
            modelBuilder.Entity<UserSearchLog>(entity =>
            {
                entity.ToTable("UserSearchLogs");
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Query).IsRequired().HasMaxLength(100);
                entity.Property(e => e.SearchedAt).HasDefaultValueSql("GETUTCDATE()");

                entity.HasOne(e => e.User)
                      .WithMany(u => u.SearchLogs)
                      .HasForeignKey(e => e.UserId)
                      .OnDelete(DeleteBehavior.Cascade);
            });
        }
    }
}
