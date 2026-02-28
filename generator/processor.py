from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher


FRESHNESS_HOURS = 36
SIMILARITY_THRESHOLD = 0.65


def filter_fresh(articles: list[dict], hours: int = FRESHNESS_HOURS) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    fresh = []
    no_date = []

    for article in articles:
        if article["published"] is None:
            no_date.append(article)
        elif article["published"] >= cutoff:
            fresh.append(article)

    return fresh + no_date


def deduplicate(articles: list[dict], threshold: float = SIMILARITY_THRESHOLD) -> list[dict]:
    if not articles:
        return []

    kept = [articles[0]]

    for article in articles[1:]:
        title_lower = article["title"].lower()
        is_duplicate = False

        for existing in kept:
            ratio = SequenceMatcher(None, title_lower, existing["title"].lower()).ratio()
            if ratio >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            kept.append(article)

    return kept


def process_articles(articles: list[dict], max_articles: int = 5) -> list[dict]:
    fresh = filter_fresh(articles)

    dated = [a for a in fresh if a["published"] is not None]
    undated = [a for a in fresh if a["published"] is None]
    dated.sort(key=lambda a: a["published"], reverse=True)
    sorted_articles = dated + undated

    unique = deduplicate(sorted_articles)

    return unique[:max_articles]
