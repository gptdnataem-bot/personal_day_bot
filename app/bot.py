from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from . import storage
from .modules import weather, news, currency, quote

router = Router()

@router.message(Command("start"))
async def cmd_start(msg: types.Message):
    storage.upsert_user(msg.from_user.id)
    await msg.answer(
        "Привет! Я пришлю твой персональный дайджест: погода (Яндекс), курсы, короткие новости и цитата дня.\n\n"
        "Сначала укажи город: напиши \n/city Москва\n\n"
        "И время рассылки в формате ЧЧ:ММ, например:\n/time 09:00\n\n"
        "Подписки на темы новостей: /follow Трамп — присылать новые новости по теме\n"
        "/subs — список подписок, /unfollow Трамп — удалить\n\n"
        "Когда готов — пришлю дайджест командой /daily"
    )

@router.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "/start — начать\n"
        "/city <город> — установить город для погоды\n"
        "/time <ЧЧ:ММ> — время ежедневной рассылки\n"
        "/daily — прислать дайджест сейчас\n"
        "/settings — показать текущие настройки\n"
        "/follow <запрос> — подписаться на тему\n"
        "/unfollow <запрос> — удалить подписку\n"
        "/subs — список подписок"
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

@router.message(Command("follow"))
async def cmd_follow(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Укажи тему: /follow Трамп")
        return
    q = parts[1].strip()
    ok = storage.add_subscription(msg.from_user.id, q)
    if ok:
        await msg.reply(f"Подписка добавлена: «{q}». Как только выйдет что‑то новое — пришлю.")
    else:
        await msg.reply("Не удалось добавить подписку.")

@router.message(Command("unfollow"))
async def cmd_unfollow(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Укажи тему: /unfollow Трамп")
        return
    q = parts[1].strip()
    storage.remove_subscription(msg.from_user.id, q)
    await msg.reply(f"Подписка удалена: «{q}».")

@router.message(Command("subs"))
async def cmd_subs(msg: types.Message):
    subs = storage.list_subscriptions(msg.from_user.id)
    if not subs:
        await msg.reply("У тебя пока нет подписок. Добавь: /follow Трамп")
        return
    text = "Твои подписки:\n" + "\n".join([f"• {s}" for s in subs])
    await msg.reply(text)

def render_digest_text(u):
    parts = []
    w = weather.fetch_weather(u.get('city') or 'Амстердам')
    if w:
        parts.append(f"🌤 <b>Погода</b>\n{w}")
    c = currency.fetch_currencies()
    if c:
        parts.append(f"💱 <b>Курсы</b>\n{c}")
    parts.append(f"💡 {quote.random_quote()}")
    return "\n\n".join(parts)

async def send_news_cards(msg: types.Message, items):
    for it in items:
        kb = InlineKeyboardBuilder()
        if it.get("link"):
            kb.button(text="Открыть новость", url=it["link"])
        await msg.answer(
            f"🗞 <b>{it['title']}</b>\nИсточник: {it.get('source','')}",
            reply_markup=kb.as_markup() if it.get("link") else None,
            parse_mode="HTML"
        )

@router.message(Command("daily"))
async def cmd_daily(msg: types.Message):
    u = storage.get_user(msg.from_user.id) or {"city":"Амстердам","notify_hour":9,"notify_min":0}
    digest = render_digest_text(u)
    await msg.reply(digest, parse_mode="HTML")
    items = news.fetch_news(limit=5, per_feed=3)
    if items:
        await send_news_cards(msg, items)
