from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
import pytz
from . import storage
from .bot import render_digest_text
from .modules import news
from .config import DEFAULT_TIMEZONE
from .modules.notify import scan_and_notify

scheduler = AsyncIOScheduler()

async def send_daily(bot: Bot, user):
    try:
        digest = render_digest_text(user)
        await bot.send_message(chat_id=user['user_id'], text=digest, parse_mode="HTML")
        items = news.fetch_news(limit=5, per_feed=3)
        if items:
            for it in items:
                kb = {"inline_keyboard":[[{"text":"Открыть новость","url": it.get("link","")}]]} if it.get("link") else None
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=f"🗞 <b>{it['title']}</b>\nИсточник: {it.get('source','')}",
                    reply_markup=kb,
                    parse_mode="HTML"
                )
    except Exception as e:
        print("send_daily error:", e)

def setup_jobs(bot: Bot):
    scheduler.remove_all_jobs()
    users = storage.all_users()
    for u in users:
        tz = u.get('tz') or DEFAULT_TIMEZONE
        trigger = CronTrigger(hour=u.get('notify_hour',9), minute=u.get('notify_min',0), timezone=pytz.timezone(tz))
        scheduler.add_job(send_daily, trigger=trigger, kwargs={"bot": bot, "user": u})
    scheduler.add_job(scan_and_notify, trigger=IntervalTrigger(minutes=5), kwargs={"bot": bot})
    if not scheduler.running:
        scheduler.start()
