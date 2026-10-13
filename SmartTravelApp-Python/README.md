# SmartTravelApp – wersja Python (FastAPI)

Ten sam frontend (`static/`) i te same endpointy co wersja C#, ale backend w Pythonie.

## Uruchomienie

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

- Aplikacja: http://localhost:5000
- Swagger: http://localhost:5000/docs

## Endpointy

| Metoda | URL | Opis |
|---|---|---|
| POST | `/api/auth/register` | rejestracja + link aktywacyjny (symulowany e-mail w logu) |
| GET | `/api/auth/confirm-email?token=` | aktywacja konta |
| POST | `/api/auth/login` | logowanie, zwraca JWT |
| GET | `/api/auth/me` | profil (JWT) |
| GET | `/api/dashboard/destination?country=` | geo + kurs NBP + pogoda Open-Meteo (JWT) |
| GET | `/api/dashboard/history` | ostatnie 10 zapytań (JWT) |

## Konfiguracja (zmienne środowiskowe)

`DATABASE_URL` (domyślnie SQLite `smarttravel.db`), `JWT_KEY`, `JWT_ISSUER`, `JWT_AUDIENCE`.
