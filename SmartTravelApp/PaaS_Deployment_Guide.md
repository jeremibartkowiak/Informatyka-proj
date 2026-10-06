# Przewodnik Wdrożenia na Platformie PaaS (Azure App Service + Azure SQL Database)

Niniejszy przewodnik opisuje proces krok po kroku wdrożenia aplikacji **SmartTravel** (ASP.NET Core Web API / MVC + SQL Server EF Core + Vanilla Frontend) na platformie chmurowej PaaS **Microsoft Azure**.

---

## Architecture Cloud Component Summary

| Komponent | Usługa PaaS Azure | Opis |
| :--- | :--- | :--- |
| **Backend & Frontend SPA** | **Azure App Service** (Linux/Windows, .NET 8/9 runtime) | Skalowalne środowisko uruchomieniowe bez zarządzania serwerami. |
| **Baza Danych** | **Azure SQL Database** (Serverless / Standard tier) | Zarządzalna relacyjna baza danych SQL Server. |
| **Bezpieczeństwo / Secrets** | **Azure App Service Application Settings** | Przechowywanie Connection String oraz Kluczy JWT w zmiennych środowiskowych. |

---

## Krok 1: Utworzenie Bazy Danych Azure SQL Database

1. Zaloguj się do portalu Azure (`https://portal.azure.com`).
2. Kliknij **Create a resource** -> **SQL Database**.
3. Wypełnij podstawowe parametry:
   - **Resource Group**: Utwórz nową, np. `rg-smarttravel-prod`.
   - **Database Name**: `sqldb-smarttravel`.
   - **Server**: Utwórz nowy serwer SQL (np. `sqlserver-smarttravel.database.windows.net`), wybierz metodę uwierzytelniania *Use SQL authentication* i zdefiniuj login oraz hasło administratora.
   - **Compute + storage**: Wybierz opcję *Serverless* (dla optymalizacji kosztów z funkcją Auto-pause) lub *Standard DTU (S0/S1)*.
4. W zakładce **Networking**:
   - Włącz opcję **Allow Azure services and resources to access this server** (Zezwól usługom Azure na dostęp do serwera SQL).
   - Dodaj swój obecny adres IP do reguł zapory ogniowej (Firewall rules) w celu przetestowania połączenia lokalnego.

---

## Krok 2: Konfiguracja EF Core Migrations w Projekcie

Przed wdrożeniem wygeneruj migrację bazy danych dla SQL Server:

```bash
# Zainstaluj narzędzia dotnet-ef (jeśli nie są zainstalowane)
dotnet tool install --global dotnet-ef

# Utwórz pierwszą migrację dla SQL Server
dotnet ef migrations add InitialCreate

# (Opcjonalnie) Zaktualizuj bazę chmurową bezpośrednio z wiersza poleceń:
dotnet ef database update --connection "Server=tcp:sqlserver-smarttravel.database.windows.net,1433;Initial Catalog=sqldb-smarttravel;Persist Security Info=False;User ID=sqladmin;Password=TwojeHaslo123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
```

---

## Krok 3: Utworzenie i Konfiguracja Azure App Service

1. W portalu Azure wybierz **Create a resource** -> **Web App**.
2. Wypełnij parametry:
   - **Name**: np. `app-smarttravel-demo` (adres URL: `https://app-smarttravel-demo.azurewebsites.net`).
   - **Publish**: Code.
   - **Runtime stack**: `.NET 8 (LTS)` lub nowszy.
   - **Operating System**: Linux lub Windows.
   - **Pricing Plan**: Free (F1) / Basic (B1).
3. Po utworzeniu zasobu przejdź do sekcji **Settings** -> **Environment variables** (lub **Configuration**):
   - Dodaj zmienną połączeniową bazy danych (**Connection Strings**):
     - Name: `DefaultConnection`
     - Value: `Server=tcp:sqlserver-smarttravel.database.windows.net,1433;Initial Catalog=sqldb-smarttravel;Persist Security Info=False;User ID=sqladmin;Password=TwojeHaslo123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;`
     - Type: `SQLServer`
   - Dodaj zmienne konfiguracyjne aplikacji (**App settings**):
     - Name: `Jwt__Key` -> Value: `TwojSuperTajnyKluczDlaProdukcjiMinimum32Znakow!`
     - Name: `Jwt__Issuer` -> Value: `https://app-smarttravel-demo.azurewebsites.net`
     - Name: `Jwt__Audience` -> Value: `SmartTravelAppUsers`

---

## Krok 4: Publikacja Aplikacji na Azure App Service

Możesz opublikować aplikację z poziomu Visual Studio, VS Code lub używając **Azure CLI**:

```bash
# 1. Zbuduj pakiet produkcyjny (Release)
dotnet publish -c Release -o ./publish

# 2. Zaloguj się do Azure CLI
az login

# 3. Spakuj zawartość katalogu publish do archiwum ZIP i wdróż na App Service
compress-archive -Path ./publish/* -DestinationPath deploy.zip
az webapp deploy --resource-group rg-smarttravel-prod --name app-smarttravel-demo --src-path deploy.zip --type zip
```

---

## Krok 5: Weryfikacja Wdrożenia PaaS

1. Otwórz w przeglądarce adres aplikacji PaaS: `https://app-smarttravel-demo.azurewebsites.net`.
2. Zarejestruj nowego użytkownika na produkcyjnym środowisku.
3. Sprawdź, czy weryfikacja tokenu w tabeli `EmailConfirmationTokens` w produkcyjnej bazie Azure SQL przebiegła pomyślnie.
4. Zaloguj się i przetestuj pobieranie danych geograficznych, kursów walut NBP oraz prognozy pogody Open-Meteo.
