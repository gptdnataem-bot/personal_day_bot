import requests
from ..config import OPENWEATHER_API_KEY

def fetch_weather(city: str, lang: str = 'ru'):
    if not OPENWEATHER_API_KEY or not city:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": lang
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"])
    feels = round(data["main"]["feels_like"])
    wind = data["wind"]["speed"]
    return f"{city}: {desc}, {temp}°C (ощущается как {feels}°C), ветер {wind} м/с"
