import requests
from .geocode import geocode_city
from ..config import YANDEX_WEATHER_API_KEY

def fetch_weather(city: str, lang: str = 'ru_RU'):
    if not YANDEX_WEATHER_API_KEY:
        return None
    geo = geocode_city(city)
    if not geo:
        return None
    url = "https://api.weather.yandex.ru/v2/forecast"
    headers = {"X-Yandex-API-Key": YANDEX_WEATHER_API_KEY}
    params = {
        "lat": geo["lat"],
        "lon": geo["lon"],
        "lang": lang,
        "limit": 1,
        "hours": False
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        fact = data.get("fact") or {}
        condition = fact.get("condition", "")
        cond_map = {
            "clear": "ясно",
            "partly-cloudy": "малооблачно",
            "cloudy": "облачно с прояснениями",
            "overcast": "пасмурно",
            "drizzle": "морось",
            "light-rain": "небольшой дождь",
            "rain": "дождь",
            "moderate-rain": "умеренный дождь",
            "heavy-rain": "сильный дождь",
            "showers": "ливень",
            "light-snow": "небольшой снег",
            "snow": "снег",
            "snow-showers": "снегопад",
            "hail": "град",
            "thunderstorm": "гроза",
            "thunderstorm-with-rain": "дождь с грозой",
            "thunderstorm-with-hail": "гроза с градом",
        }
        desc = cond_map.get(condition, condition).capitalize() if condition else "—"
        temp = round(fact.get("temp", 0))
        feels = round(fact.get("feels_like", temp))
        wind = fact.get("wind_speed", 0)
        city_name = city
        return f"{city_name}: {desc}, {temp}°C (ощущается как {feels}°C), ветер {wind} м/с"
    except Exception:
        return None
