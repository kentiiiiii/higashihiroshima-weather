"""Send Higashihiroshima's daily forecast to an ntfy topic."""

from datetime import date, timedelta
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LATITUDE = 34.426
LONGITUDE = 132.743
TIMEZONE = "Asia/Tokyo"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()

WEATHER_CODES = {
    0: "快晴", 1: "おおむね晴れ", 2: "晴れ時々くもり", 3: "くもり",
    45: "霧", 48: "霧氷を伴う霧", 51: "弱い霧雨", 53: "霧雨",
    55: "強い霧雨", 56: "弱い着氷性の霧雨", 57: "強い着氷性の霧雨",
    61: "弱い雨", 63: "雨", 65: "強い雨", 66: "弱い着氷性の雨",
    67: "強い着氷性の雨", 71: "弱い雪", 73: "雪", 75: "大雪",
    77: "細氷", 80: "弱いにわか雨", 81: "にわか雨", 82: "強いにわか雨",
    85: "弱いにわか雪", 86: "強いにわか雪", 95: "雷雨",
    96: "ひょうを伴う雷雨", 99: "強いひょうを伴う雷雨",
}


def get_json(url: str, params: dict) -> dict:
    request = Request(f"{url}?{urlencode(params)}", headers={"User-Agent": "higashihiroshima-weather-bot/1.0"})
    with urlopen(request, timeout=25) as response:
        return json.load(response)


def main() -> None:
    if not NTFY_TOPIC:
        raise RuntimeError("NTFY_TOPIC is not configured in GitHub Actions secrets.")

    forecast = get_json(FORECAST_URL, {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": TIMEZONE,
        "forecast_days": 2,
    })
    day = forecast["daily"]["time"][0]
    today = date.fromisoformat(day)
    yesterday = today - timedelta(days=1)
    archive = get_json(ARCHIVE_URL, {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": yesterday.isoformat(),
        "end_date": yesterday.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": TIMEZONE,
    })

    daily = forecast["daily"]
    high = round(daily["temperature_2m_max"][0])
    low = round(daily["temperature_2m_min"][0])
    code = daily["weather_code"][0]
    description = WEATHER_CODES.get(code, "天気情報")
    old_daily = archive.get("daily", {})
    old_highs = old_daily.get("temperature_2m_max") or []
    old_lows = old_daily.get("temperature_2m_min") or []

    lines = [f"東広島市の今日の天気（{today.month}/{today.day}）", description, f"最高 {high}℃ / 最低 {low}℃"]
    if old_highs and old_lows and old_highs[0] is not None and old_lows[0] is not None:
        high_diff = high - round(old_highs[0])
        low_diff = low - round(old_lows[0])
        lines.append(f"前日実績比：最高 {high_diff:+}℃ / 最低 {low_diff:+}℃")
    else:
        lines.append("前日の気温データを取得できませんでした")
    message = "\n".join(lines) + "\n\nWeather data: Open-Meteo (CC BY 4.0)"

    request = Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Higashihiroshima weather", "Priority": "default", "Tags": "partly_sunny"},
        method="POST",
    )
    with urlopen(request, timeout=25) as response:
        if response.status >= 300:
            raise RuntimeError(f"ntfy returned HTTP {response.status}")
    print("Weather notification sent.")


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError, RuntimeError) as exc:
        print(f"Notification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
