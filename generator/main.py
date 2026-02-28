import os
from datetime import datetime, timezone

from generator.feeds import CATEGORIES
from generator.fetcher import fetch_feed
from generator.processor import process_articles
from generator.weather import get_berlin_weather
from generator.renderer import render_newspaper


def main():
    print(f"\n{'=' * 50}")
    print(f"Daily Briefing — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'=' * 50}")

    print("\nFetching weather...")
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
    weather = get_berlin_weather(api_key)

    print("\nFetching feeds...")
    categories_data = {}

    for key, config in CATEGORIES.items():
        print(f"\n[{config['title']}]")
        all_articles = []

        for feed in config["feeds"]:
            articles = fetch_feed(feed["url"], feed["name"], key)
            all_articles.extend(articles)

        processed = process_articles(all_articles, config["max_articles"])
        categories_data[key] = processed
        print(f"  => {len(processed)} articles selected")

    print("\nRendering newspaper...")
    render_newspaper(categories_data, weather, CATEGORIES)

    total = sum(len(arts) for arts in categories_data.values())
    print(f"\nDone. {total} articles across {len(categories_data)} categories.")


if __name__ == "__main__":
    main()
