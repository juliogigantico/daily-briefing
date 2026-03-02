"""Process, filter, and rank articles."""

import re
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher


# Keywords that signal OFF-TOPIC content per category.
# If an article title+summary matches these, it gets penalized.
_OFFTOPIC_KEYWORDS = {
    "tech": [
        r"\brecipe\b", r"\bcooking\b", r"\bwine\b", r"\bsports?\b",
        r"\bfootball\b", r"\bsoccer\b", r"\bcricket\b",
    ],
    "science": [
        r"\bopinion\b", r"\beditorial\b", r"\bcommentary\b",
        r"\bvirtue\b", r"\bmeekness\b", r"\bspiritual\b",
        r"\breligion\b", r"\bfaith\b", r"\bprayer\b",
        r"\bhoroscope\b", r"\bastrology\b",
    ],
    "environment": [
        r"\bsports?\b", r"\bfootball\b", r"\bcelebrities?\b",
    ],
    "economy": [
        r"\brecipe\b", r"\bcelebrities?\b", r"\bhoroscope\b",
    ],
}

# Keywords that signal ON-TOPIC content (boost relevance)
_ONTOPIC_KEYWORDS = {
    "tech": [
        r"\bAI\b", r"\bartificial intelligence\b", r"\bmachine learning\b",
        r"\bstartup\b", r"\bsoftware\b", r"\bapp\b", r"\bcloud\b",
        r"\bcyber\b", r"\bdata\b", r"\bchip\b", r"\bsemiconductor\b",
        r"\brobot\b", r"\bautomation\b", r"\bcrypto\b", r"\bblockchain\b",
        r"\btech\b", r"\bdigital\b", r"\binternet\b", r"\bprivacy\b",
        r"\bopen.?source\b", r"\bAPI\b", r"\bLLM\b", r"\bGPT\b",
    ],
    "science": [
        r"\bresearch\b", r"\bstudy\b", r"\bscientists?\b", r"\bdiscovery\b",
        r"\bexperiment\b", r"\bNASA\b", r"\bspace\b", r"\bphysics\b",
        r"\bbiology\b", r"\bchemistry\b", r"\bgenome\b", r"\bcell\b",
        r"\bclimate\b", r"\bevolution\b", r"\bfossil\b", r"\bquantum\b",
        r"\bmedicine\b", r"\bvaccine\b", r"\bcancer\b",
    ],
    "environment": [
        r"\bclimate\b", r"\bemissions?\b", r"\bcarbon\b", r"\bwarming\b",
        r"\brenewable\b", r"\bsolar\b", r"\bwind\b", r"\benergy\b",
        r"\bbiodiversity\b", r"\bforest\b", r"\bocean\b", r"\bpollution\b",
        r"\brecycl\b", r"\bsustainab\b",
    ],
    "economy": [
        r"\bmarket\b", r"\bstock\b", r"\bGDP\b", r"\binflation\b",
        r"\btrade\b", r"\btariff\b", r"\bbank\b", r"\binterest rate\b",
        r"\beconom\b", r"\brecession\b", r"\bjobs?\b", r"\bunemployment\b",
        r"\bcurrenc\b", r"\bbond\b", r"\binvestor\b",
    ],
}


def _relevance_score(article: dict) -> float:
    """Score article relevance to its category. Higher = more relevant."""
    category = article.get("category", "")
    text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    score = 1.0  # baseline

    # Check off-topic keywords (penalize)
    for pattern in _OFFTOPIC_KEYWORDS.get(category, []):
        if re.search(pattern, text, re.IGNORECASE):
            score -= 0.5

    # Check on-topic keywords (boost)
    matches = 0
    for pattern in _ONTOPIC_KEYWORDS.get(category, []):
        if re.search(pattern, text, re.IGNORECASE):
            matches += 1
    score += min(matches * 0.3, 1.5)  # cap the boost

    # Penalize articles with very short or empty summaries
    summary = article.get("summary", "")
    if len(summary) < 20:
        score -= 0.3

    return score


def filter_fresh(articles: list[dict], hours: int = 36) -> list[dict]:
    """Keep only articles published within the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    fresh = []
    for a in articles:
        pub = a.get("published")
        if pub is None:
            fresh.append(a)  # keep articles without dates
        elif pub >= cutoff:
            fresh.append(a)
    return fresh


def deduplicate(articles: list[dict], threshold: float = 0.65) -> list[dict]:
    """Remove near-duplicate articles based on title similarity."""
    unique = []
    seen_titles = []
    for a in articles:
        title = a.get("title", "")
        is_dup = False
        for seen in seen_titles:
            if SequenceMatcher(None, title.lower(), seen.lower()).ratio() > threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(a)
            seen_titles.append(title)
    return unique


def process_articles(
    articles: list[dict],
    max_articles: int = 5,
    high_relevance_threshold: float = 2.0,
) -> list[dict]:
    """Full processing pipeline: filter, deduplicate, score, sort, trim.

    Source diversity rules:
    - 1st article from any source: gets in normally
    - 2nd article from the same source: only if relevance >= high_relevance_threshold
    - 3rd+ article from the same source: never (hard cap at 2)
    """
    # 1. Freshness filter
    articles = filter_fresh(articles)

    # 2. Deduplicate
    articles = deduplicate(articles)

    # 3. Score relevance and sort by (relevance DESC, date DESC)
    for a in articles:
        a["_relevance"] = _relevance_score(a)

    articles.sort(
        key=lambda a: (
            a.get("_relevance", 0),
            a.get("published") or datetime.min.replace(tzinfo=timezone.utc),
        ),
        reverse=True,
    )

    # 4. Select articles with source diversity enforcement
    result = []
    cat_counts = {}       # category -> total count
    source_counts = {}    # (category, source) -> count

    for a in articles:
        cat = a.get("category", "")
        source = a.get("source", "")
        relevance = a.get("_relevance", 0)

        cat_counts.setdefault(cat, 0)
        source_counts.setdefault((cat, source), 0)

        # Skip if category is full
        if cat_counts[cat] >= max_articles:
            continue

        times_used = source_counts[(cat, source)]

        # Hard cap: never more than 2 from the same source
        if times_used >= 2:
            continue

        # 2nd article from same source: only if highly relevant
        if times_used == 1 and relevance < high_relevance_threshold:
            continue

        # Clean up internal scoring field
        a.pop("_relevance", None)
        result.append(a)
        cat_counts[cat] += 1
        source_counts[(cat, source)] += 1

    return result
