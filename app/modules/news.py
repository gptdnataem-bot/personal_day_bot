import feedparser
import hashlib
from typing import List, Dict
from ..config import RSS_FEEDS

def _hash_url(url:str)->str:
    import hashlib
    return hashlib.sha256((url or '').encode('utf-8')).hexdigest()

def fetch_news(limit: int = 5, per_feed:int = 5) -> List[Dict]:
    items = []
    for feed in RSS_FEEDS[:20]:
        try:
            parsed = feedparser.parse(feed)
            for e in parsed.entries[:per_feed]:
                title = e.get("title") or ""
                link = e.get("link") or ""
                published = e.get("published") or e.get("updated") or ""
                items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": parsed.feed.get("title", "RSS"),
                    "url_hash": _hash_url(link),
                })
        except Exception:
            continue
    return items[:limit]

def fetch_news_pool(max_items:int = 120, per_feed:int = 10)->List[Dict]:
    items = []
    for feed in RSS_FEEDS[:50]:
        try:
            parsed = feedparser.parse(feed)
            for e in parsed.entries[:per_feed]:
                title = e.get("title") or ""
                link = e.get("link") or ""
                published = e.get("published") or e.get("updated") or ""
                items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": parsed.feed.get("title", "RSS"),
                    "url_hash": _hash_url(link),
                })
        except Exception:
            continue
    return items[:max_items]

def format_news(items: List[Dict]) -> str:
    if not items:
        return "Новостей пока нет."
    out = []
    for i, it in enumerate(items, 1):
        line = f"{i}. {it['title']} — {it.get('source', '')}\n{it['link']}"
        out.append(line)
    return "\n\n".join(out)
