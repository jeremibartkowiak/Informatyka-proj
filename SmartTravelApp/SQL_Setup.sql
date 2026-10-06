-- ============================================================================
-- Skrypt T-SQL dla SQL Server / SSMS: Tworzenie bazy danych i tabel SmartTravelDb
-- ============================================================================

-- 1. Tworzenie bazy danych (jeśli nie istnieje)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SmartTravelDb')
BEGIN
    CREATE DATABASE [SmartTravelDb];
    PRINT 'Baza danych SmartTravelDb została utworzona pomyślnie.';
END
GO

USE [SmartTravelDb];
GO

-- 2. Tabela: Users
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
BEGIN
    CREATE TABLE [Users] (
        [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Email] NVARCHAR(256) NOT NULL,
        [PasswordHash] NVARCHAR(MAX) NOT NULL,
        [IsEmailConfirmed] BIT NOT NULL CONSTRAINT DF_Users_IsEmailConfirmed DEFAULT 0,
        [CreatedAt] DATETIME2 NOT NULL CONSTRAINT DF_Users_CreatedAt DEFAULT GETUTCDATE()
    );

    CREATE UNIQUE INDEX [IX_Users_Email] ON [Users]([Email]);
    PRINT 'Tabela Users została utworzona.';
END
GO

-- 3. Tabela: EmailConfirmationTokens
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'EmailConfirmationTokens')
BEGIN
    CREATE TABLE [EmailConfirmationTokens] (
        [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [UserId] INT NOT NULL,
        [Token] NVARCHAR(128) NOT NULL,
        [ExpiresAt] DATETIME2 NOT NULL,
        [IsUsed] BIT NOT NULL CONSTRAINT DF_Tokens_IsUsed DEFAULT 0,
        [CreatedAt] DATETIME2 NOT NULL CONSTRAINT DF_Tokens_CreatedAt DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_EmailConfirmationTokens_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [Users]([Id]) ON DELETE CASCADE
    );

    CREATE UNIQUE INDEX [IX_EmailConfirmationTokens_Token] ON [EmailConfirmationTokens]([Token]);
    PRINT 'Tabela EmailConfirmationTokens została utworzona.';
END
GO

-- 4. Tabela: UserSearchLogs
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserSearchLogs')
BEGIN
    CREATE TABLE [UserSearchLogs] (
        [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [UserId] INT NOT NULL,
        [Query] NVARCHAR(100) NOT NULL,
        [SearchedAt] DATETIME2 NOT NULL CONSTRAINT DF_UserSearchLogs_SearchedAt DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_UserSearchLogs_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [Users]([Id]) ON DELETE CASCADE
    );

    PRINT 'Tabela UserSearchLogs została utworzona.';
END
GO

PRINT '============================================================================';
PRINT 'Struktura bazy SmartTravelDb została przygotowana dla SSMS / SQL Server!';
PRINT '============================================================================';
