import re
from datetime import datetime, timezone

import feedparser
from dateutil import parser as dateparser


USER_AGENT = "DailyBriefing/1.0 (+https://github.com)"
FETCH_TIMEOUT = 15


def strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_date(entry) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (ValueError, OverflowError):
                continue

    for field in ("published", "updated"):
        raw = getattr(entry, field, None)
        if raw:
            try:
                return dateparser.parse(raw).astimezone(timezone.utc)
            except (ValueError, TypeError):
                continue

    return None


def fetch_feed(url: str, source_name: str, category_key: str) -> list[dict]:
    try:
        feed = feedparser.parse(
            url,
            agent=USER_AGENT,
            request_headers={"Accept": "application/rss+xml, application/xml, text/xml"},
        )
    except Exception as e:
        print(f"  [FAIL] {source_name}: {e}")
        return []

    if feed.bozo and not feed.entries:
        print(f"  [FAIL] {source_name}: {feed.bozo_exception}")
        return []

    articles = []
    for entry in feed.entries:
        title = strip_html(getattr(entry, "title", ""))
        if not title:
            continue

        link = getattr(entry, "link", "")
        summary = strip_html(
            getattr(entry, "summary", "") or getattr(entry, "description", "")
        )
        if len(summary) > 500:
            summary = summary[:497] + "..."

        published = parse_date(entry)

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "source": source_name,
            "category": category_key,
        })

    print(f"  [OK]   {source_name}: {len(articles)} articles")
    return articles
