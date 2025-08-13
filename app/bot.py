from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from . import storage
from .modules import weather, news, currency, quote

router = Router()

@router.message(Command("start"))
async def cmd_start(msg: types.Message):
    storage.upsert_user(msg.from_user.id)
    await msg.answer(
        "Привет! Я пришлю твой персональный дайджест: погода, курсы, короткие новости и цитата дня.\n\n"
        "Сначала укажи город: напиши \n/city Москва\n\n"
        "И время рассылки в формате ЧЧ:ММ, например:\n/time 09:00\n\n"
        "Когда готов — пришлю дайджест командой /daily"
    )

@router.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "/start — начать\n"
        "/city <город> — установить город для погоды\n"
        "/time <ЧЧ:ММ> — время ежедневной рассылки\n"
        "/daily — прислать дайджест сейчас\n"
        "/settings — показать текущие настройки"
    )

@router.message(Command("city"))
async def cmd_city(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Укажи город: /city Москва")
        return
    city = parts[1].strip()
    storage.set_user_settings(msg.from_user.id, city=city)
    await msg.reply(f"Город сохранён: {city}")

@router.message(Command("time"))
async def cmd_time(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2 or ":" not in parts[1]:
        await msg.reply("Укажи время: /time 09:00")
        return
    hh, mm = parts[1].split(":")
    try:
        hh, mm = int(hh), int(mm)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError
    except Exception:
        await msg.reply("Некорректное время. Пример: /time 09:00")
        return
    storage.set_user_settings(msg.from_user.id, notify_hour=hh, notify_min=mm)
    await msg.reply(f"Время рассылки сохранено: {hh:02d}:{mm:02d}")

@router.message(Command("settings"))
async def cmd_settings(msg: types.Message):
    u = storage.get_user(msg.from_user.id) or {}
    text = (
        f"Текущие настройки:\n"
        f"Город: {u.get('city') or 'не задан'}\n"
        f"Время: {u.get('notify_hour',9):02d}:{u.get('notify_min',0):02d}\n"
        f"Часовой пояс: {u.get('tz','Europe/Amsterdam')}"
    )
    await msg.reply(text)

def render_digest(u):
    parts = []
    w = weather.fetch_weather(u.get('city') or 'Amsterdam')
    if w:
        parts.append(f"🌤 Погода: {w}")
    c = currency.fetch_currencies()
    if c:
        parts.append(f"💱 Курсы: {c}")
    n = news.format_news(news.fetch_news(limit=5))
    if n:
        parts.append(f"🗞 Новости:\n{n}")
    parts.append(f"💡 {quote.random_quote()}")
    return "\n\n".join(parts)

@router.message(Command("daily"))
async def cmd_daily(msg: types.Message):
    u = storage.get_user(msg.from_user.id) or {"city":"Amsterdam","notify_hour":9,"notify_min":0}
    digest = render_digest(u)
    await msg.reply(digest)
