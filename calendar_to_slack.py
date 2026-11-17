import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

SOURCE = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TZ = ZoneInfo("Europe/Stockholm")

def fetch_events():
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        events = json.load(response)
    if not isinstance(events, list):
        raise ValueError("Calendar source did not return a list")
    return events

def format_report(events, now):
    today = now.astimezone(TZ).date()
    filtered = []
    for event in events:
        if str(event.get("impact", "")).casefold() != "high":
            continue
        try:
            timestamp = datetime.fromisoformat(str(event["date"]).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("Missing timezone")
            local_time = timestamp.astimezone(TZ)
        except (KeyError, TypeError, ValueError):
            continue
        if local_time.date() == today:
            filtered.append((local_time, event))
    filtered.sort(key=lambda entry: entry[0])
    lines = [f"*Today's high-impact economic calendar – {today:%Y-%m-%d}*", "🔴 High Impact | Stockholm time"]
    if not filtered:
        lines.append("No high-impact events are listed for today.")
    for local_time, event in filtered:
        title = str(event.get("title", "Unknown event"))
        country = event.get("country", "–")
        forecast = event.get("forecast") or "Not available"
        previous = event.get("previous") or "Not available"
        lines.append(f"*{local_time:%H:%M} | {country} | {title}*\nForecast: {forecast} | Previous: {previous}")
    lines.append("Source: Forex Factory. Calendar details may change.")
    return "\n\n".join(lines)

def main():
    now = datetime.now(TZ)
    report = format_report(fetch_events(), now)
    if os.environ.get("DRY_RUN") == "1":
        print(report)
        return
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("Add GitHub Secret SLACK_WEBHOOK_URL")
    request = urllib.request.Request(
        webhook,
        data=json.dumps({"text": report}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Slack HTTP {response.status}")
    print("Report sent to Slack")

if __name__ == "__main__":
    main()
