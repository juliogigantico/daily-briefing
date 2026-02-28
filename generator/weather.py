from datetime import datetime, timedelta, timezone

import requests


WEATHER_EMOJI = {
    "01d": "\u2600\uFE0F", "01n": "\U0001F319",
    "02d": "\u26C5", "02n": "\U0001F319",
    "03d": "\u2601\uFE0F", "03n": "\u2601\uFE0F",
    "04d": "\u2601\uFE0F", "04n": "\u2601\uFE0F",
    "09d": "\U0001F327\uFE0F", "09n": "\U0001F327\uFE0F",
    "10d": "\U0001F326\uFE0F", "10n": "\U0001F327\uFE0F",
    "11d": "\u26C8\uFE0F", "11n": "\u26C8\uFE0F",
    "13d": "\u2744\uFE0F", "13n": "\u2744\uFE0F",
    "50d": "\U0001F32B\uFE0F", "50n": "\U0001F32B\uFE0F",
}


def get_berlin_weather(api_key: str | None) -> dict | None:
    if not api_key:
        print("  [SKIP] Weather: no API key")
        return None

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"q": "Berlin,DE", "units": "metric", "appid": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [FAIL] Weather: {e}")
        return None

    now = datetime.now(timezone.utc)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    entries = data.get("list", [])
    if not entries:
        return None

    def parse_dt(dt_txt: str) -> datetime:
        return datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    today_entries = [e for e in entries if parse_dt(e["dt_txt"]).date() == today]
    tomorrow_entries = [e for e in entries if parse_dt(e["dt_txt"]).date() == tomorrow]

    current = min(entries, key=lambda e: abs((parse_dt(e["dt_txt"]) - now).total_seconds()))

    icon_code = current["weather"][0].get("icon", "03d")

    result = {
        "temp": round(current["main"]["temp"]),
        "description": current["weather"][0]["description"].title(),
        "emoji": WEATHER_EMOJI.get(icon_code, "\u2601\uFE0F"),
        "today_high": round(max(e["main"]["temp_max"] for e in today_entries)) if today_entries else None,
        "today_low": round(min(e["main"]["temp_min"] for e in today_entries)) if today_entries else None,
        "tomorrow_high": round(max(e["main"]["temp_max"] for e in tomorrow_entries)) if tomorrow_entries else None,
        "tomorrow_low": round(min(e["main"]["temp_min"] for e in tomorrow_entries)) if tomorrow_entries else None,
    }

    print(f"  [OK]   Weather: {result['temp']}\u00b0C, {result['description']}")
    return result
