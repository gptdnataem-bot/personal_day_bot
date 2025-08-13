import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
YANDEX_WEATHER_API_KEY = os.getenv("YANDEX_WEATHER_API_KEY", "")
RSS_FEEDS = [u.strip() for u in os.getenv("RSS_FEEDS", "").split(",") if u.strip()]
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Europe/Amsterdam")
