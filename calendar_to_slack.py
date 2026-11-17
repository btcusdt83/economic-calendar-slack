import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

SOURCE = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TZ = ZoneInfo("Europe/Stockholm")
TRANSLATIONS = {
    "Retail Sales m/m": "Detaljhandel (månadsförändring)",
    "Core Retail Sales m/m": "Underliggande detaljhandel (månadsförändring)",
    "Non-Farm Employment Change": "Nya jobb utanför jordbruket (NFP)",
    "Unemployment Rate": "Arbetslöshet",
    "CPI m/m": "KPI (månadsförändring)",
    "CPI y/y": "KPI (årsförändring)",
    "Core CPI m/m": "Kärn-KPI (månadsförändring)",
    "Federal Funds Rate": "Feds styrränta",
    "GDP q/q": "BNP (kvartalsförändring)",
}

def fetch_events():
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        events = json.load(response)
    if not isinstance(events, list):
        raise ValueError("Kalendern returnerade inte en lista")
    return events

def format_report(events, now):
    today = now.date()
    filtered = []
    for event in events:
        if str(event.get("impact", "")).casefold() != "high":
            continue
        try:
            timestamp = datetime.fromisoformat(str(event["date"]).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("Tidszon saknas")
            local_time = timestamp.astimezone(TZ)
        except (KeyError, TypeError, ValueError):
            continue
        if local_time.date() == today:
            filtered.append((local_time, event))
    filtered.sort(key=lambda entry: entry[0])
    lines = [f"*Dagens viktiga ekonomiska nyheter – {today:%Y-%m-%d}*", "🔴 High Impact | Svensk tid"]
    if not filtered:
        lines.append("Inga nyheter med hög påverkan är listade för idag.")
    for local_time, event in filtered:
        title = str(event.get("title", "Okänd händelse"))
        title = TRANSLATIONS.get(title, title)
        country = event.get("country", "–")
        forecast = event.get("forecast") or "Ej angiven"
        previous = event.get("previous") or "Ej angivet"
        lines.append(f"*{local_time:%H:%M} | {country} | {title}*\nPrognos: {forecast} | Föregående: {previous}")
    lines.append("Källa: Forex Factory. Kalenderuppgifter kan ändras.")
    return "\n\n".join(lines)

def main():
    now = datetime.now(TZ)
    if os.getenv("GITHUB_EVENT_NAME") == "schedule" and now.hour != 8:
        print("Inte 08:00 svensk tid, hoppar över")
        return
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("Lägg till GitHub Secret SLACK_WEBHOOK_URL")
    report = format_report(fetch_events(), now)
    if os.environ.get("DRY_RUN") == "1":
        print(report)
        return
    request = urllib.request.Request(
        webhook,
        data=json.dumps({"text": report}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Slack HTTP {response.status}")
    print("Rapport skickad till Slack")

if __name__ == "__main__":
    main()
