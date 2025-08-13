from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
import pytz
from . import storage
from .bot import render_digest
from .config import DEFAULT_TIMEZONE, BOT_TOKEN

scheduler = AsyncIOScheduler()

async def send_daily(bot: Bot, user):
    try:
        digest = render_digest(user)
        await bot.send_message(chat_id=user['user_id'], text=digest)
    except Exception as e:
        # Лог минималистичный для MVP
        print("send_daily error:", e)

def setup_jobs(bot: Bot):
    scheduler.remove_all_jobs()
    users = storage.all_users()
    for u in users:
        tz = u.get('tz') or DEFAULT_TIMEZONE
        trigger = CronTrigger(hour=u.get('notify_hour',9), minute=u.get('notify_min',0), timezone=pytz.timezone(tz))
        scheduler.add_job(send_daily, trigger=trigger, kwargs={"bot": bot, "user": u})
    if not scheduler.running:
        scheduler.start()
