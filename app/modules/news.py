import feedparser
from datetime import datetime, timezone
from typing import List, Dict
from ..config import RSS_FEEDS

def fetch_news(limit: int = 5) -> List[Dict]:
    items = []
    for feed in RSS_FEEDS[:10]:  # ограничим для MVP
        try:
            parsed = feedparser.parse(feed)
            for e in parsed.entries[:5]:
                title = e.get("title")
                link = e.get("link")
                published = e.get("published") or e.get("updated") or ""
                items.append({"title": title, "link": link, "published": published, "source": parsed.feed.get("title", "RSS")})
        except Exception:
            continue
    # Упрощенная сортировка: по наличию даты в начале списка
    return items[:limit]

def format_news(items: List[Dict]) -> str:
    if not items:
        return "Новостей пока нет."
    out = []
    for i, it in enumerate(items, 1):
        line = f"{i}. {it['title']} — {it.get('source', '')}\n{it['link']}"
        out.append(line)
    return "\n\n".join(out)
