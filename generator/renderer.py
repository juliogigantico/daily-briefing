import shutil
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
OUTPUT_DIR = PROJECT_ROOT / "docs"


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


def make_tldr(articles: list[dict]) -> str:
    if not articles:
        return ""

    # Build a real summary from the top articles' summaries and titles
    parts = []
    for article in articles[:4]:
        summary = article.get("summary", "").strip()
        title = article.get("title", "").strip()
        source = article.get("source", "")
        # Use the summary if available, otherwise the title
        text = summary if len(summary) > 40 else title
        if text:
            parts.append(text)

    if not parts:
        return ""

    # Join all snippets into a flowing brief
    return " \u2014 ".join(parts)


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

    now = datetime.now(timezone.utc)
    date_str = f"{now.strftime('%A')}, {now.day} {now.strftime('%B %Y')}"
    time_str = now.strftime("%H:%M UTC")
    date_short = now.strftime("%d.%m.%Y")

    html = template.render(
        categories=categories_data,
        category_config=category_config,
        category_tldrs=category_tldrs,
        weather=weather,
        css=css_content,
        date_str=date_str,
        time_str=time_str,
        date_short=date_short,
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
