from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel

# Daty w bazie są naiwne (UTC) – dodajemy 'Z', aby przeglądarka poprawnie je zinterpretowała.
UtcDatetime = Annotated[datetime, PlainSerializer(lambda d: d.isoformat() + "Z", return_type=str)]


class CamelModel(BaseModel):
    """Serializacja do camelCase – identycznie jak System.Text.Json w wersji C#."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RegisterRequest(CamelModel):
    email: str = ""
    password: str = ""


class LoginRequest(CamelModel):
    email: str = ""
    password: str = ""


class AuthResponse(CamelModel):
    success: bool
    message: str = ""
    token: Optional[str] = None
    email: Optional[str] = None
    activation_link: Optional[str] = None


class UserProfileDto(CamelModel):
    id: int
    email: str
    is_email_confirmed: bool
    created_at: UtcDatetime


class CountryInfoDto(CamelModel):
    name: str = ""
    official_name: str = ""
    capital: str = ""
    population: int = 0
    region: str = ""
    flag_url: str = ""
    flag_emoji: str = ""
    currency_code: str = ""
    currency_name: str = ""
    currency_symbol: str = ""
    capital_latitude: float = 0.0
    capital_longitude: float = 0.0


class CurrencyRateDto(CamelModel):
    currency_code: str = ""
    base_currency: str = "PLN"
    rate_to_pln: float = 0.0
    rate_date: str = ""
    note: str = ""


class WeatherDto(CamelModel):
    location_name: str = ""
    temperature_c: float = 0.0
    wind_speed_kmh: float = 0.0
    weather_code: int = 0
    weather_description: str = ""


class TravelDashboardResponse(CamelModel):
    country: str = ""
    geo_data: Optional[CountryInfoDto] = None
    currency_data: Optional[CurrencyRateDto] = None
    weather_data: Optional[WeatherDto] = None
    fetched_at: UtcDatetime


class SearchLogDto(CamelModel):
    id: int
    query: str
    searched_at: UtcDatetime
