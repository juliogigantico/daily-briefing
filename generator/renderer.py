import shutil
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
OUTPUT_DIR = PROJECT_ROOT / "docs"

BERLIN_TZ = ZoneInfo("Europe/Berlin")

GREETINGS = {
    "morning": [
        ("Good morning", "☀️"),
        ("Rise & read", "📰"),
        ("Morning brew", "☕"),
        ("Fresh off the press", "✨"),
        ("Top of the morning", "🌤️"),
        ("Let's catch up", "🗞️"),
        ("New day, new stories", "🌅"),
    ],
    "afternoon": [
        ("Good afternoon", "👋"),
        ("Afternoon check-in", "📋"),
        ("Midday update", "🔆"),
    ],
    "evening": [
        ("Good evening", "🌙"),
        ("Evening edition", "🌆"),
        ("Wind down", "🫖"),
    ],
    "night": [
        ("Night owl edition", "🦉"),
        ("Late night read", "🌃"),
    ],
}


def get_greeting() -> str:
    """Return a greeting with emoji that changes every day."""
    now_utc = datetime.now(timezone.utc)
    berlin_hour = now_utc.astimezone(BERLIN_TZ).hour

    if 5 <= berlin_hour < 12:
        pool = GREETINGS["morning"]
    elif 12 <= berlin_hour < 18:
        pool = GREETINGS["afternoon"]
    elif 18 <= berlin_hour < 22:
        pool = GREETINGS["evening"]
    else:
        pool = GREETINGS["night"]

    day_of_year = now_utc.timetuple().tm_yday
    text, emoji = pool[day_of_year % len(pool)]
    return f"{emoji} {text}"


def time_ago(published: datetime | None) -> str:
    if published is None:
        return "recently"

    now = datetime.now(timezone.utc)
    diff = now - published
    hours = int(diff.total_seconds() / 3600)

    if hours < 1:
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago" if mins > 0 else "just now"
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def first_sentence(text: str, max_len: int = 160) -> str:
    """Extract the first sentence from a text, truncated to max_len."""
    if not text:
        return ""
    for sep in (". ", "! ", "? "):
        idx = text.find(sep)
        if 0 < idx < max_len:
            return text[: idx + 1]
    if len(text) > max_len:
        space = text.rfind(" ", 0, max_len)
        return text[: space if space > 40 else max_len] + "…"
    return text


def make_tldr(articles: list[dict]) -> dict:
    """Build a proper summary: flowing paragraph from top excerpts + remaining headlines."""
    if not articles:
        return {}

    # Collect first-sentence excerpts from the top 3 articles (the real info)
    sentences = []
    for article in articles[:3]:
        summary = article.get("summary", "").strip()
        sentence = first_sentence(summary)
        if sentence and len(sentence) > 25:
            sentences.append(sentence)

    # Build a flowing paragraph — sequential sentences read naturally
    paragraph = " ".join(sentences) if sentences else ""

    # Remaining article titles as quick-reference "also" list
    used = min(len(sentences), 3)
    also = []
    for article in articles[used:]:
        title = article.get("title", "").strip()
        if title:
            also.append(title)

    if not paragraph and not also:
        return {}

    return {
        "paragraph": paragraph,
        "also": also,
        "count": len(articles),
    }


def render_newspaper(categories_data: dict, weather: dict | None, category_config: dict):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    template = env.get_template("newspaper.html")

    css_path = STATIC_DIR / "style.css"
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    # Add time_ago and build TL;DR per category
    category_tldrs = {}
    for key, articles in categories_data.items():
        for article in articles:
            article["time_ago"] = time_ago(article.get("published"))
        category_tldrs[key] = make_tldr(articles)

    now_utc = datetime.now(timezone.utc)
    now_berlin = now_utc.astimezone(BERLIN_TZ)
    date_str = f"{now_berlin.strftime('%A')}, {now_berlin.day} {now_berlin.strftime('%B %Y')}"
    time_str = now_utc.strftime("%H:%M UTC")
    date_short = now_berlin.strftime("%d.%m.%Y")

    html = template.render(
        categories=categories_data,
        category_config=category_config,
        category_tldrs=category_tldrs,
        weather=weather,
        css=css_content,
        date_str=date_str,
        time_str=time_str,
        date_short=date_short,
        greeting=get_greeting(),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")

    for filename in ("manifest.json", "sw.js"):
        src = STATIC_DIR / filename
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / filename)

    icons_src = STATIC_DIR / "icons"
    icons_dst = OUTPUT_DIR / "icons"
    if icons_src.exists():
        if icons_dst.exists():
            shutil.rmtree(icons_dst)
        shutil.copytree(icons_src, icons_dst)

    print(f"  [OK]   Output written to {OUTPUT_DIR / 'index.html'}")
