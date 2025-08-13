from aiogram import Bot
from .news import fetch_news_pool
from .. import storage

def matches_query(text:str, query:str)->bool:
    return query.lower() in (text or "").lower()

async def scan_and_notify(bot: Bot):
    pool = fetch_news_pool(max_items=120, per_feed=10)
    if not pool:
        return
    users = storage.all_users()
    for u in users:
        subs = storage.list_subscriptions(u["user_id"])
        if not subs:
            continue
        for it in pool:
            title = it.get("title","")
            link = it.get("link","")
            h = it.get("url_hash")
            for q in subs:
                if matches_query(title, q):
                    if not storage.was_sent(u["user_id"], h):
                        try:
                            kb = {"inline_keyboard":[[{"text":"Открыть новость","url": link}]]} if link else None
                            await bot.send_message(
                                chat_id=u["user_id"],
                                text=f"🔔 Новое по запросу «{q}»\n<b>{title}</b>\nИсточник: {it.get('source','')}",
                                reply_markup=kb,
                                parse_mode="HTML"
                            )
                            storage.mark_sent(u["user_id"], h)
                        except Exception as e:
                            print("notify error:", e)
