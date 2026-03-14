from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from generator.feeds import CATEGORIES
from generator.fetcher import fetch_feed
from generator.processor import process_articles, deduplicate_across
from generator.weather import get_berlin_weather
from generator.renderer import render_newspaper
from generator.make_icons import main as generate_icons


def main():
    print(f"\n{'=' * 50}")
    print(f"my news — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'=' * 50}")

    print("\nGenerating icons...")
    generate_icons()

    print("\nFetching weather...")
    weather = get_berlin_weather()

    # Collect all feed tasks
    feed_tasks = []
    for key, config in CATEGORIES.items():
        for feed in config["feeds"]:
            feed_tasks.append((feed["url"], feed["name"], key))

    # Fetch all feeds in parallel
    print(f"\nFetching {len(feed_tasks)} feeds...")
    raw_articles = {key: [] for key in CATEGORIES}
    feed_results = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_feed, url, name, key): (name, key)
            for url, name, key in feed_tasks
        }
        for future in as_completed(futures):
            name, key = futures[future]
            try:
                articles = future.result()
                raw_articles[key].extend(articles)
                feed_results[name] = len(articles)
            except Exception as e:
                print(f"  [FAIL] {name}: {e}")
                feed_results[name] = 0

    # Cross-category dedup (before processing, so empty slots can be refilled)
    raw_articles = deduplicate_across(raw_articles)

    # Process each category
    print("\nProcessing...")
    categories_data = {}
    for key, config in CATEGORIES.items():
        processed = process_articles(raw_articles[key], config["max_articles"])
        categories_data[key] = processed
        print(f"  [{config['title']}] {len(processed)} articles")

    # Feed health check
    empty_feeds = [name for name, count in feed_results.items() if count == 0]
    if empty_feeds:
        print(f"\n[WARN] {len(empty_feeds)} feeds returned 0 articles:")
        for name in sorted(empty_feeds):
            print(f"  - {name}")

    print("\nRendering newspaper...")
    render_newspaper(categories_data, weather, CATEGORIES)

    total = sum(len(arts) for arts in categories_data.values())
    print(f"\nDone. {total} articles across {len(categories_data)} categories.")


if __name__ == "__main__":
    main()
