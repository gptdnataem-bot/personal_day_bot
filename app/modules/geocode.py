import requests

def geocode_city(city: str):
    if not city:
        return None
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}
        headers = {"User-Agent": "personal-day-bot/1.0"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        display = data[0].get("display_name", city)
        return {"lat": lat, "lon": lon, "name": display}
    except Exception:
        return None
