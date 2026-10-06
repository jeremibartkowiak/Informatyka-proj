# Plan Architektoniczny i Wzorcowa Implementacja Aplikacji .NET + SQL Server + PaaS

Niniejszy dokument przedstawia kompletny plan architektoniczny, schemat bazy danych SQL Server, wzorcową kodową implementację backendową i frontendową oraz przewodnik wdrożeniowy PaaS (Azure / Cloud) dla aplikacji webowej z systemem aktywacji konta e-mail i integracją z 3 publicznymi API.

---

## 1. Architektura i Przepływ Danych

### Scenariusz Aplikacji: "Smart Travel & Weather Dashboard"
Aplikacja agreguje dane geograficzne, walutowe oraz pogodowe dla wybranego kraju/miasta na podstawie 3 darmowych, publicznych API niewymagających kluczy API (No-Key Required):
1. **REST Countries API** (`https://restcountries.com/v3.1/`) – pobieranie danych geograficznych (stolica, populacja, region, flaga, kod waluty, współrzędne geograficzne).
2. **NBP Web API** (`https://api.nbp.pl/api/`) / **Open Exchange Rates** – pobieranie aktualnych kursów walut przeliczonych na PLN/USD.
3. **Open-Meteo Weather API** (`https://api.open-meteo.com/v1/forecast`) – pobieranie aktualnej pogody oraz prognozy dla współrzędnych geograficznych stolicy.

### Architektura Systemu
```
+-----------------------------------------------------------------------+
|                           CLIENT (Browser)                            |
|             Vanilla HTML5 + Modern CSS3 + Vanilla JavaScript          |
+-----------------------------------+-----------------------------------+
                                    | REST API (JSON) + JWT Bearer Token
                                    v
+-----------------------------------------------------------------------+
|                    BACKEND (ASP.NET Core Web API)                     |
|                                                                       |
|  +--------------------+  +---------------------+  +-----------------+ |
|  | AuthController     |  | DashboardController |  | EmailService    | |
|  +---------+----------+  +----------+----------+  +-----------------+ |
|            |                        |                                 |
|            v                        v                                 |
|  +--------------------+  +------------------------------------------+ |
|  | AuthService        |  | ExternalApiService (IHttpClientFactory)  | |
|  | (BCrypt, JWT)      |  +----+---------------+---------------------+ |
|  +---------+----------+       |               |               |       |
+------------|------------------|---------------+---------------|-------+
             |                  |               |               |
             v                  v               v               v
   +------------------+  +-------------+ +-------------+ +-------------+
   |   SQL Server     |  |  REST       | |  NBP API    | | Open-Meteo  |
   | (EF Core DB)     |  |  Countries  | | (Kursy)     | | (Pogoda)    |
   +------------------+  +-------------+ +-------------+ +-------------+
```

### Przepływ Danych (Data Flow)
1. **Rejestracja:** Użytkownik przesyła e-mail i hasło. Backend generuje unikalny token aktywacyjny (`Guid`), zapisuje go w bazie z czasem wygaśnięcia, a użytkownikowi wysyła link aktywacyjny (np. `/api/auth/confirm-email?token=...`).
2. **Aktywacja:** Kliknięcie w link weryfikuje token w bazie, ustawia `IsEmailConfirmed = true` i unieważnia token.
3. **Logowanie:** Użytkownik podaje dane. Po zweryfikowaniu aktywacji konta oraz poprawności hasła (BCrypt), backend generuje token JWT.
4. **Dashboard:** Po zalogowaniu frontend pobiera dane z 3 serwisów zewnętrznych poprzez bezpieczne endpointy backendowe (chroniące CORS i zapobiegające blokowaniu zapytań klienckich).

---

## 2. Model Bazy Danych (SQL Server & EF Core)

### Diagram Tabel SQL Server
- **`Users`**: Przechowuje id, email, hashed password (BCrypt), stan weryfikacji e-mail, datę utworzenia.
- **`EmailConfirmationTokens`**: Przechowuje id, reference do użytkownika, token GUID, datę utworzenia i wygaśnięcia oraz czy został użyty.
- **`UserSearchLogs`** *(opcjonalnie)*: Historię zapytań użytkowników do 3 API.

```sql
CREATE TABLE [Users] (
    [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [Email] NVARCHAR(256) NOT NULL UNIQUE,
    [PasswordHash] NVARCHAR(MAX) NOT NULL,
    [IsEmailConfirmed] BIT NOT NULL DEFAULT 0,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

CREATE TABLE [EmailConfirmationTokens] (
    [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [UserId] INT NOT NULL FOREIGN KEY REFERENCES [Users]([Id]) ON DELETE CASCADE,
    [Token] NVARCHAR(128) NOT NULL UNIQUE,
    [ExpiresAt] DATETIME2 NOT NULL,
    [IsUsed] BIT NOT NULL DEFAULT 0,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

CREATE TABLE [UserSearchLogs] (
    [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [UserId] INT NOT NULL FOREIGN KEY REFERENCES [Users]([Id]) ON DELETE CASCADE,
    [Query] NVARCHAR(100) NOT NULL,
    [SearchedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
```

---

## 3. Struktura Projektu Backendowego (C# ASP.NET Core)

Proponujemy czystą strukturę w pojedynczym projekcie ASP.NET Core Web API:
- `Data/ApplicationDbContext.cs` – Konfiguracja EF Core i Fluent API.
- `Models/User.cs`, `Models/EmailConfirmationToken.cs`, `Models/UserSearchLog.cs` – DTO i encje.
- `Services/IAuthService.cs`, `Services/AuthService.cs` – Obsługa rejestracji, BCrypt, generowania JWT, tokenów aktywacyjnych.
- `Services/IEmailService.cs`, `Services/EmailService.cs` – Serwis symulacji/wysyłki e-mail.
- `Services/ITravelDashboardService.cs`, `Services/TravelDashboardService.cs` – `HttpClientFactory` do 3 zewnętrznych API.
- `Controllers/AuthController.cs`, `Controllers/DashboardController.cs` – Endpointy REST.
- `wwwroot/` – Statyczny frontend SPA (HTML, CSS, JS).

---

## User Review Required

> [!IMPORTANT]
> Prosimy o zatwierdzenie powyższego planu architektonicznego, zaproponowanych 3 publicznych API (REST Countries, NBP, Open-Meteo) oraz struktury aplikacji. Po zatwierdzeniu wygenerujemy pełny, gotowy do uruchomienia kod w środowisku projekowym oraz przygotujemy przewodnik PaaS Azure.

## Open Questions

> [!NOTE]
> 1. Czy preferujesz autentykację opartą o **JWT Bearer Token** w nagłówku `Authorization: Bearer <token>`, czy opartą o **Cookie Session**? (W planie przyjęto domyślnie JWT).
> 2. Czy backend ma serwować frontend bezpośrednio jako pliki statyczne (`wwwroot` w ASP.NET Core), czy jako osobną strukturę katalogów frontendowych?

---

## Proposed Changes

### [Backend (.NET 8 Web API + EF Core)]
#### [NEW] `InformatykaProj.csproj`
#### [NEW] `Program.cs`
#### [NEW] `Data/ApplicationDbContext.cs`
#### [NEW] `Models/Entities.cs`
#### [NEW] `Models/DTOs.cs`
#### [NEW] `Services/AuthService.cs`
#### [NEW] `Services/EmailService.cs`
#### [NEW] `Services/TravelDashboardService.cs`
#### [NEW] `Controllers/AuthController.cs`
#### [NEW] `Controllers/DashboardController.cs`

### [Frontend (HTML5 / Vanilla JS / CSS3)]
#### [NEW] `wwwroot/index.html`
#### [NEW] `wwwroot/css/styles.css`
#### [NEW] `wwwroot/js/app.js`

### [Dokumentacja & PaaS]
#### [NEW] `README.md` / `PaaS_Deployment_Guide.md`

---

## Verification Plan

### Automated Tests / Builds
- Kompilacja projektu .NET (`dotnet build`)
- Uruchomienie backendu (`dotnet run` / server test)
- Weryfikacja endpointów rejestracji, potwierdzania tokenu i dashboardu API.

### Manual Verification
- Przetestowanie formularza rejestracji, odebrania linku aktywacyjnego.
- Weryfikacja logowania i zapisu danych w bazie EF Core (SQLite / LocalDB / SQL Server).
- Testowanie płynności i wyglądu interfejsu UI Dashboardu (3 API).
