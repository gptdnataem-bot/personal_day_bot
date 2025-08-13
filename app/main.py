import asyncio
from aiogram import Bot, Dispatcher
from .config import BOT_TOKEN
from . import storage
from .bot import router
from .scheduler import setup_jobs

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Put it into .env")
    storage.init_db()
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    setup_jobs(bot)
    print("Bot started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
