import requests


# Open-Meteo WMO weather codes → emoji + description
WMO_CODES = {
    0: ("\u2600\uFE0F", "Clear"),
    1: ("\U0001F324\uFE0F", "Mostly clear"),
    2: ("\u26C5", "Partly cloudy"),
    3: ("\u2601\uFE0F", "Overcast"),
    45: ("\U0001F32B\uFE0F", "Fog"),
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
    96: ("\u26C8\uFE0F", "Thunderstorm + hail"),
    99: ("\u26C8\uFE0F", "Heavy thunderstorm"),
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
                "hourly": "temperature_2m,precipitation_probability,weather_code",
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
    hourly = data.get("hourly", {})

    if not current or not daily:
        return None

    code = current.get("weather_code", 3)
    emoji, description = WMO_CODES.get(code, ("\u2601\uFE0F", "Cloudy"))

    today_high = round(daily["temperature_2m_max"][0]) if daily.get("temperature_2m_max") else None
    today_low = round(daily["temperature_2m_min"][0]) if daily.get("temperature_2m_min") else None
    tomorrow_high = round(daily["temperature_2m_max"][1]) if len(daily.get("temperature_2m_max", [])) > 1 else None
    tomorrow_low = round(daily["temperature_2m_min"][1]) if len(daily.get("temperature_2m_min", [])) > 1 else None

    # Build hourly forecast for the next ~15 hours (from current hour)
    hours = []
    if hourly.get("time"):
        now_str = current.get("time", "")[:13]  # "2025-03-01T07" format
        start_idx = 0
        for i, t in enumerate(hourly["time"]):
            if t[:13] >= now_str:
                start_idx = i
                break

        temps = hourly.get("temperature_2m", [])
        rain_probs = hourly.get("precipitation_probability", [])
        codes = hourly.get("weather_code", [])

        for i in range(start_idx, min(start_idx + 15, len(hourly["time"]))):
            hour_str = hourly["time"][i]  # "2025-03-01T08:00"
            hour_label = hour_str[11:13]  # "08"
            h_emoji, _ = WMO_CODES.get(codes[i] if i < len(codes) else 3, ("\u2601\uFE0F", ""))

            hours.append({
                "hour": f"{hour_label}:00",
                "temp": round(temps[i]) if i < len(temps) else None,
                "rain": rain_probs[i] if i < len(rain_probs) else 0,
                "emoji": h_emoji,
            })

    result = {
        "temp": round(current["temperature_2m"]),
        "description": description,
        "emoji": emoji,
        "today_high": today_high,
        "today_low": today_low,
        "tomorrow_high": tomorrow_high,
        "tomorrow_low": tomorrow_low,
        "hours": hours,
    }

    print(f"  [OK]   Weather: {result['temp']}\u00b0C, {result['description']}, {len(hours)} hourly points")
    return result
