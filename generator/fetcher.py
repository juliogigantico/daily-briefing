"""Fetch articles from RSS feeds."""

import re
from datetime import datetime, timezone

import feedparser


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


# Patterns to strip from summaries (promo junk, metadata, CTAs)
_JUNK_PATTERNS = [
    # Guardian / BBC promo patterns
    r"Follow our .{0,60} live blog.*",
    r"Get our breaking news.*",
    r"Subscribe to .*",
    r"Sign up for .*",
    r"Read more at .*",
    r"Click here .*",
    r"Download (?:the|our) (?:free )?app.*",
    r"Listen to .*podcast.*",
    r"Watch (?:the|our) .*",
    # "Continue reading" / "Read the full story"
    r"Continue reading.*",
    r"Read the full (?:story|article).*",
    # Generic trailing CTAs
    r"\s*\|?\s*More stories like this.*",
    r"\.\.\.\s*More\s*$",
]

_JUNK_RE = re.compile("|".join(_JUNK_PATTERNS), re.IGNORECASE)

# Hacker News metadata pattern
_HN_META_RE = re.compile(
    r"Article URL:\s*\S+\s*"
    r"(?:Comments URL:\s*\S+\s*)?"
    r"(?:Points:\s*\d+\s*)?"
    r"(?:#\s*Comments:\s*\d+\s*)?",
    re.IGNORECASE,
)


def _clean_summary(text: str, source_name: str) -> str:
    """Clean up an RSS summary: strip HTML, metadata, and promo junk."""
    text = strip_html(text)

    # Hacker News: strip the metadata block entirely
    if "hacker news" in source_name.lower():
        text = _HN_META_RE.sub("", text).strip()

    # Strip known junk patterns
    text = _JUNK_RE.sub("", text).strip()

    # Truncate long summaries
    if len(text) > 500:
        text = text[:500]

    # Clean up any leftover whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _extract_hn_article_url(entry) -> str | None:
    """Extract the actual article URL from a Hacker News RSS entry."""
    summary = getattr(entry, "summary", "") or ""
    match = re.search(r"Article URL:\s*(https?://\S+)", summary)
    if match:
        return match.group(1)
    links = getattr(entry, "links", [])
    for link in links:
        href = link.get("href", "")
        if href and "news.ycombinator.com" not in href:
            return href
    return None


def _is_latin_text(text: str) -> bool:
    """Check if text is primarily Latin-script (English/German/French/etc).

    Returns False for CJK, Arabic, Cyrillic, Thai, etc.
    """
    if not text:
        return True
    latin_count = 0
    non_latin_count = 0
    for ch in text:
        if ch.isalpha():
            # Latin letters (including accented: ä, ö, ü, é, etc.)
            if ("\u0000" <= ch <= "\u024F") or ("\u1E00" <= ch <= "\u1EFF"):
                latin_count += 1
            else:
                non_latin_count += 1
    total = latin_count + non_latin_count
    if total == 0:
        return True
    return (latin_count / total) >= 0.7


def parse_date(entry) -> datetime | None:
    """Parse publication date from an RSS entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue
    return None


def _extract_image(entry) -> str | None:
    """Extract thumbnail image URL from RSS entry (HTTPS only)."""
    # media:thumbnail (most common for news feeds)
    for thumb in getattr(entry, "media_thumbnail", []):
        url = thumb.get("url", "")
        if url.startswith("https://"):
            return url

    # media:content with type=image
    for m in getattr(entry, "media_content", []):
        if m.get("medium") == "image" or m.get("type", "").startswith("image/"):
            url = m.get("url", "")
            if url.startswith("https://"):
                return url

    # Enclosures
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image/"):
            url = enc.get("href", "") or enc.get("url", "")
            if url.startswith("https://"):
                return url

    # Extract from summary HTML (last resort)
    summary_raw = getattr(entry, "summary", "") or ""
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary_raw)
    if img_match:
        url = img_match.group(1)
        if url.startswith("https://"):
            return url

    return None


def fetch_feed(url: str, source_name: str, category_key: str) -> list[dict]:
    """Fetch and parse a single RSS feed. Returns list of article dicts."""
    is_hn = "hacker news" in source_name.lower()

    try:
        d = feedparser.parse(url)
    except Exception as e:
        print(f"  [FAIL] {source_name}: {e}")
        return []

    if d.bozo and not d.entries:
        print(f"  [FAIL] {source_name}: {d.bozo_exception}")
        return []

    articles = []
    for entry in d.entries:
        title = strip_html(getattr(entry, "title", "")) or ""
        if not title:
            continue

        # Skip non-Latin articles (Chinese, Japanese, Arabic, etc.)
        if not _is_latin_text(title):
            continue

        # For HN: prefer the actual article URL over the HN discussion link
        link = getattr(entry, "link", "")
        if is_hn:
            article_url = _extract_hn_article_url(entry)
            if article_url:
                link = article_url

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
        summary = _clean_summary(summary, source_name)

        # Skip HN entries with no meaningful summary after cleaning
        if is_hn and len(summary) < 10:
            summary = ""

        published = parse_date(entry)
        image = _extract_image(entry)

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "source": source_name,
            "category": category_key,
            "image": image,
        })

    print(f"  [OK]   {source_name}: {len(articles)} articles")
    return articles
