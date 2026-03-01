import requests


# Open-Meteo WMO weather codes → emoji + description
WMO_CODES = {
    0: ("\u2600\uFE0F", "Clear sky"),
    1: ("\U0001F324\uFE0F", "Mainly clear"),
    2: ("\u26C5", "Partly cloudy"),
    3: ("\u2601\uFE0F", "Overcast"),
    45: ("\U0001F32B\uFE0F", "Foggy"),
    48: ("\U0001F32B\uFE0F", "Rime fog"),
    51: ("\U0001F326\uFE0F", "Light drizzle"),
    53: ("\U0001F326\uFE0F", "Drizzle"),
    55: ("\U0001F327\uFE0F", "Dense drizzle"),
    61: ("\U0001F327\uFE0F", "Light rain"),
    63: ("\U0001F327\uFE0F", "Rain"),
    65: ("\U0001F327\uFE0F", "Heavy rain"),
    71: ("\U0001F328\uFE0F", "Light snow"),
    73: ("\u2744\uFE0F", "Snow"),
    75: ("\u2744\uFE0F", "Heavy snow"),
    80: ("\U0001F326\uFE0F", "Light showers"),
    81: ("\U0001F327\uFE0F", "Showers"),
    82: ("\U0001F327\uFE0F", "Heavy showers"),
    85: ("\U0001F328\uFE0F", "Snow showers"),
    86: ("\u2744\uFE0F", "Heavy snow showers"),
    95: ("\u26C8\uFE0F", "Thunderstorm"),
    96: ("\u26C8\uFE0F", "Thunderstorm with hail"),
    99: ("\u26C8\uFE0F", "Thunderstorm with heavy hail"),
}


def get_berlin_weather() -> dict | None:
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 52.52,
                "longitude": 13.41,
                "current": "temperature_2m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "timezone": "Europe/Berlin",
                "forecast_days": 2,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [FAIL] Weather: {e}")
        return None

    current = data.get("current", {})
    daily = data.get("daily", {})

    if not current or not daily:
        return None

    code = current.get("weather_code", 3)
    emoji, description = WMO_CODES.get(code, ("\u2601\uFE0F", "Cloudy"))

    today_high = round(daily["temperature_2m_max"][0]) if daily.get("temperature_2m_max") else None
    today_low = round(daily["temperature_2m_min"][0]) if daily.get("temperature_2m_min") else None
    tomorrow_high = round(daily["temperature_2m_max"][1]) if len(daily.get("temperature_2m_max", [])) > 1 else None
    tomorrow_low = round(daily["temperature_2m_min"][1]) if len(daily.get("temperature_2m_min", [])) > 1 else None

    result = {
        "temp": round(current["temperature_2m"]),
        "description": description,
        "emoji": emoji,
        "today_high": today_high,
        "today_low": today_low,
        "tomorrow_high": tomorrow_high,
        "tomorrow_low": tomorrow_low,
    }

    print(f"  [OK]   Weather: {result['temp']}\u00b0C, {result['description']}")
    return result
