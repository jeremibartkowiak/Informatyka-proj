from datetime import datetime, timezone
from urllib.parse import quote

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..countries import POLISH_TO_ENGLISH, get_fallback_geo_data
from ..database import UserSearchLog, utcnow
from ..schemas import (
    CountryInfoDto, CurrencyRateDto, SearchLogDto, TravelDashboardResponse, WeatherDto,
)

HEADERS = {"User-Agent": "SmartTravelApp/1.0 (Python FastAPI)"}


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def map_weather_code(code: int) -> str:
    if code == 0:
        return "☀️ Słonecznie / Bezchmurnie"
    if code in (1, 2, 3):
        return "⛅ Częściowe zachmurzenie"
    if code in (45, 48):
        return "🌫️ Mgła"
    if code in (51, 53, 55):
        return "🌧️ Lekka mżawka"
    if code in (61, 63, 65):
        return "🌧️ Opady deszczu"
    if code in (71, 73, 75):
        return "❄️ Opady śniegu"
    if code in (80, 81, 82):
        return "🌦️ Ulewny deszcz"
    if code in (95, 96, 99):
        return "⛈️ Burza z piorunami"
    return "🌡️ Umiarkowane zachmurzenie"


async def fetch_geo_data(client: httpx.AsyncClient, country_name: str) -> CountryInfoDto:
    data = get_fallback_geo_data(country_name)
    try:
        query = POLISH_TO_ENGLISH.get(country_name.strip().lower(), country_name.strip())
        url = (f"https://geocoding-api.open-meteo.com/v1/search?name={quote(query)}"
               f"&count=1&language=en&format=json")
        resp = await client.get(url)
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if results:
            res = results[0]
            if "latitude" in res and "longitude" in res:
                data.capital_latitude = float(res["latitude"])
                data.capital_longitude = float(res["longitude"])
            if (res.get("population") or 0) > 0:
                data.population = int(res["population"])
    except Exception:
        pass
    return data


async def fetch_currency_rate(client: httpx.AsyncClient, currency_code: str) -> CurrencyRateDto:
    if currency_code.upper() == "PLN":
        return CurrencyRateDto(
            currency_code="PLN", base_currency="PLN", rate_to_pln=1.0,
            rate_date=_today(), note="Waluta bazowa (PLN)",
        )
    try:
        resp = await client.get(f"https://api.nbp.pl/api/exchangerates/rates/a/{currency_code.lower()}/?format=json")
        resp.raise_for_status()
        rates = resp.json().get("rates") or []
        if rates:
            return CurrencyRateDto(
                currency_code=currency_code.upper(), base_currency="PLN",
                rate_to_pln=float(rates[0]["mid"]),
                rate_date=rates[0].get("effectiveDate", _today()),
                note="Kurs średni NBP (Narodowy Bank Polski)",
            )
    except Exception:
        pass
    return CurrencyRateDto(
        currency_code=currency_code.upper(), base_currency="PLN", rate_to_pln=4.25,
        rate_date=_today(), note="Szacowany kurs rynkowy",
    )


async def fetch_weather(client: httpx.AsyncClient, capital: str, lat: float, lng: float) -> WeatherDto:
    try:
        resp = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true"
        )
        resp.raise_for_status()
        cw = resp.json().get("current_weather")
        if cw:
            code = int(cw["weathercode"])
            return WeatherDto(
                location_name=capital, temperature_c=float(cw["temperature"]),
                wind_speed_kmh=float(cw["windspeed"]), weather_code=code,
                weather_description=map_weather_code(code),
            )
    except Exception:
        pass
    return WeatherDto(
        location_name=capital, temperature_c=21.5, wind_speed_kmh=12.0,
        weather_code=0, weather_description="Słonecznie / Bezchmurnie",
    )


async def get_dashboard_data(db: Session, country_name: str, user_id: int) -> TravelDashboardResponse:
    if not country_name or not country_name.strip():
        country_name = "Poland"

    db.add(UserSearchLog(user_id=user_id, query=country_name[:100], searched_at=utcnow()))
    db.commit()

    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
        geo = await fetch_geo_data(client, country_name)
        currency = await fetch_currency_rate(client, geo.currency_code)
        weather = await fetch_weather(client, geo.capital, geo.capital_latitude, geo.capital_longitude)

    return TravelDashboardResponse(
        country=country_name, geo_data=geo, currency_data=currency, weather_data=weather,
        fetched_at=utcnow(),
    )


def get_search_history(db: Session, user_id: int) -> list[SearchLogDto]:
    rows = db.scalars(
        select(UserSearchLog).where(UserSearchLog.user_id == user_id)
        .order_by(UserSearchLog.searched_at.desc()).limit(10)
    ).all()
    return [SearchLogDto(id=r.id, query=r.query, searched_at=r.searched_at) for r in rows]
