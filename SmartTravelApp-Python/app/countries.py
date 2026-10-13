"""Dane awaryjne krajów (odpowiednik GetFallbackGeoData) oraz mapowanie nazw PL -> EN."""
from typing import Optional

from .schemas import CountryInfoDto

POLISH_TO_ENGLISH = {
    "polska": "Poland", "niemcy": "Germany", "francja": "France", "hiszpania": "Spain",
    "włochy": "Italy", "wielka brytania": "United Kingdom", "anglia": "United Kingdom",
    "stany zjednoczone": "United States", "usa": "United States", "japonia": "Japan",
    "chiny": "China", "kanada": "Canada", "grecja": "Greece", "egipt": "Egypt",
    "turcja": "Turkey", "chorwacja": "Croatia", "czechy": "Czechia", "słowacja": "Slovakia",
    "norwegia": "Norway", "szwecja": "Sweden", "holandia": "Netherlands",
    "szwajcaria": "Switzerland", "austria": "Austria", "portugalia": "Portugal",
    "ukraina": "Ukraine", "brazylia": "Brazil", "meksyk": "Mexico", "australia": "Australia",
    "argentyna": "Argentina", "indie": "India", "korea południowa": "South Korea",
    "tajlandia": "Thailand", "wietnam": "Vietnam",
    "zjednoczone emiraty arabskie": "United Arab Emirates", "islandia": "Iceland",
    "finlandia": "Finland", "dania": "Denmark", "irlandia": "Ireland", "belgia": "Belgium",
}

# (aliasy, name, official, capital, population, region, flag, cur_code, cur_name, cur_symbol, lat, lng)
_COUNTRIES = [
    (("polska", "poland"), "Poland", "Republic of Poland", "Warsaw", 37750000, "Europe", "🇵🇱", "PLN", "Polish Złoty", "zł", 52.2297, 21.0122),
    (("united kingdom", "uk", "wielka brytania", "great britain"), "United Kingdom", "United Kingdom of Great Britain and Northern Ireland", "London", 67330000, "Europe", "🇬🇧", "GBP", "British Pound", "£", 51.5074, -0.1278),
    (("united states", "usa", "us", "stany zjednoczone"), "United States", "United States of America", "Washington, D.C.", 331900000, "Americas", "🇺🇸", "USD", "US Dollar", "$", 38.8951, -77.0364),
    (("canada", "kanada"), "Canada", "Canada", "Ottawa", 38250000, "Americas", "🇨🇦", "CAD", "Canadian Dollar", "$", 45.4215, -75.6972),
    (("niemcy", "germany"), "Germany", "Federal Republic of Germany", "Berlin", 83200000, "Europe", "🇩🇪", "EUR", "Euro", "€", 52.5200, 13.4050),
    (("francja", "france"), "France", "French Republic", "Paris", 67750000, "Europe", "🇫🇷", "EUR", "Euro", "€", 48.8566, 2.3522),
    (("hiszpania", "spain"), "Spain", "Kingdom of Spain", "Madrid", 47400000, "Europe", "🇪🇸", "EUR", "Euro", "€", 40.4168, -3.7038),
    (("włochy", "wlochy", "italy"), "Italy", "Italian Republic", "Rome", 59000000, "Europe", "🇮🇹", "EUR", "Euro", "€", 41.9028, 12.4964),
    (("japonia", "japan"), "Japan", "Japan", "Tokyo", 125700000, "Asia", "🇯🇵", "JPY", "Japanese Yen", "¥", 35.6762, 139.6503),
    (("china", "chiny"), "China", "People's Republic of China", "Beijing", 1412000000, "Asia", "🇨🇳", "CNY", "Chinese Yuan", "¥", 39.9042, 116.4074),
    (("australia",), "Australia", "Commonwealth of Australia", "Canberra", 25690000, "Oceania", "🇦🇺", "AUD", "Australian Dollar", "$", -35.2809, 149.1300),
    (("egypt", "egipt"), "Egypt", "Arab Republic of Egypt", "Cairo", 104300000, "Africa", "🇪🇬", "EGP", "Egyptian Pound", "E£", 30.0444, 31.2357),
    (("greece", "grecja"), "Greece", "Hellenic Republic", "Athens", 10640000, "Europe", "🇬🇷", "EUR", "Euro", "€", 37.9838, 23.7275),
    (("turkey", "turcja", "türkiye"), "Turkey", "Republic of Türkiye", "Ankara", 84780000, "Asia", "🇹🇷", "TRY", "Turkish Lira", "₺", 39.9334, 32.8597),
    (("croatia", "chorwacja"), "Croatia", "Republic of Croatia", "Zagreb", 4050000, "Europe", "🇭🇷", "EUR", "Euro", "€", 45.8150, 15.9819),
    (("czechia", "czech republic", "czechy"), "Czechia", "Czech Republic", "Prague", 10510000, "Europe", "🇨🇿", "CZK", "Czech Koruna", "Kč", 50.0755, 14.4378),
    (("slovakia", "słowacja"), "Slovakia", "Slovak Republic", "Bratislava", 5450000, "Europe", "🇸🇰", "EUR", "Euro", "€", 48.1486, 17.1077),
    (("norway", "norwegia"), "Norway", "Kingdom of Norway", "Oslo", 5400000, "Europe", "🇳🇴", "NOK", "Norwegian Krone", "kr", 59.9139, 10.7522),
    (("sweden", "szwecja"), "Sweden", "Kingdom of Sweden", "Stockholm", 10400000, "Europe", "🇸🇪", "SEK", "Swedish Krona", "kr", 59.3293, 18.0686),
    (("netherlands", "holandia"), "Netherlands", "Kingdom of the Netherlands", "Amsterdam", 17530000, "Europe", "🇳🇱", "EUR", "Euro", "€", 52.3676, 4.9041),
    (("switzerland", "szwajcaria"), "Switzerland", "Swiss Confederation", "Bern", 8690000, "Europe", "🇨🇭", "CHF", "Swiss Franc", "CHF", 46.9480, 7.4474),
    (("austria",), "Austria", "Republic of Austria", "Vienna", 8950000, "Europe", "🇦🇹", "EUR", "Euro", "€", 48.2082, 16.3738),
    (("portugal", "portugalia"), "Portugal", "Portuguese Republic", "Lisbon", 10300000, "Europe", "🇵🇹", "EUR", "Euro", "€", 38.7223, -9.1393),
    (("ukraine", "ukraina"), "Ukraine", "Ukraine", "Kyiv", 41130000, "Europe", "🇺🇦", "UAH", "Ukrainian Hryvnia", "₴", 50.4501, 30.5234),
    (("brazil", "brazylia"), "Brazil", "Federative Republic of Brazil", "Brasília", 214300000, "Americas", "🇧🇷", "BRL", "Brazilian Real", "R$", -15.7975, -47.8919),
    (("mexico", "meksyk"), "Mexico", "United Mexican States", "Mexico City", 126700000, "Americas", "🇲🇽", "MXN", "Mexican Peso", "$", 19.4326, -99.1332),
    (("argentina", "argentyna"), "Argentina", "Argentine Republic", "Buenos Aires", 45810000, "Americas", "🇦🇷", "ARS", "Argentine Peso", "$", -34.6037, -58.3816),
    (("india", "indie"), "India", "Republic of India", "New Delhi", 1408000000, "Asia", "🇮🇳", "INR", "Indian Rupee", "₹", 28.6139, 77.2090),
    (("south korea", "korea południowa", "korea poludniowa"), "South Korea", "Republic of Korea", "Seoul", 51740000, "Asia", "🇰🇷", "KRW", "South Korean Won", "₩", 37.5665, 126.9780),
    (("thailand", "tajlandia"), "Thailand", "Kingdom of Thailand", "Bangkok", 71600000, "Asia", "🇹🇭", "THB", "Thai Baht", "฿", 13.7563, 100.5018),
    (("vietnam", "wietnam"), "Vietnam", "Socialist Republic of Vietnam", "Hanoi", 97400000, "Asia", "🇻🇳", "VND", "Vietnamese Đồng", "₫", 21.0285, 105.8542),
    (("united arab emirates", "uae", "zae", "zjednoczone emiraty arabskie"), "United Arab Emirates", "United Arab Emirates", "Abu Dhabi", 9890000, "Middle East", "🇦🇪", "AED", "UAE Dirham", "AED", 24.4539, 54.3773),
    (("iceland", "islandia"), "Iceland", "Iceland", "Reykjavik", 376000, "Europe", "🇮🇸", "ISK", "Icelandic Króna", "kr", 64.1466, -21.9426),
    (("finland", "finlandia"), "Finland", "Republic of Finland", "Helsinki", 5540000, "Europe", "🇫🇮", "EUR", "Euro", "€", 60.1699, 24.9384),
    (("denmark", "dania"), "Denmark", "Kingdom of Denmark", "Copenhagen", 5850000, "Europe", "🇩🇰", "DKK", "Danish Krone", "kr", 55.6761, 12.5683),
    (("ireland", "irlandia"), "Ireland", "Republic of Ireland", "Dublin", 5030000, "Europe", "🇮🇪", "EUR", "Euro", "€", 53.3498, -6.2603),
    (("belgium", "belgia"), "Belgium", "Kingdom of Belgium", "Brussels", 11590000, "Europe", "🇧🇪", "EUR", "Euro", "€", 50.8503, 4.3517),
]

_BY_ALIAS = {alias: row for row in _COUNTRIES for alias in row[0]}


def get_fallback_geo_data(country_name: str) -> CountryInfoDto:
    row: Optional[tuple] = _BY_ALIAS.get(country_name.strip().lower())
    if row:
        _, name, official, capital, pop, region, flag, code, cname, sym, lat, lng = row
        return CountryInfoDto(
            name=name, official_name=official, capital=capital, population=pop, region=region,
            flag_emoji=flag, currency_code=code, currency_name=cname, currency_symbol=sym,
            capital_latitude=lat, capital_longitude=lng,
        )
    return CountryInfoDto(
        name=country_name, official_name=country_name, capital="Capital City",
        population=25000000, region="World", flag_emoji="🌍",
        currency_code="USD", currency_name="US Dollar", currency_symbol="$",
        capital_latitude=52.2297, capital_longitude=21.0122,
    )
