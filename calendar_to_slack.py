import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

SOURCE = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TZ = ZoneInfo("Europe/Stockholm")

TITLE_TRANSLATIONS = {
    "BOE Gov Bailey Speaks": "Tal av Bank of Englands chef Bailey",
    "Fed Chairman Warsh Speaks": "Tal av Fed-chefen Warsh",
    "RBA Gov Bullock Speaks": "Tal av Australiens centralbankschef Bullock",
    "CPI": "KPI (inflation)",
    "Core CPI": "Kärn-KPI",
    "Median CPI": "Median-KPI",
    "Trimmed CPI": "Trimmat KPI",
    "Retail Sales": "Detaljhandel",
    "Core Retail Sales": "Underliggande detaljhandel",
    "Employment Change": "Förändring i sysselsättningen",
    "Unemployment Rate": "Arbetslöshet",
    "Inflation Expectations": "Inflationsförväntningar",
    "FOMC Meeting Minutes": "Protokoll från Feds räntemöte",
    "Non-Farm Employment Change": "Nya jobb utanför jordbruket (NFP)",
    "ADP Non-Farm Employment Change": "ADP: nya jobb i privat sektor",
    "Average Hourly Earnings": "Genomsnittlig timlön",
    "Unemployment Claims": "Nya ansökningar om arbetslöshetsersättning",
    "Federal Funds Rate": "Feds styrränta",
    "FOMC Statement": "Feds räntebesked",
    "FOMC Press Conference": "Feds presskonferens",
    "FOMC Economic Projections": "Feds ekonomiska prognoser",
    "Official Bank Rate": "Styrränta",
    "Monetary Policy Statement": "Penningpolitiskt besked",
    "Monetary Policy Report": "Penningpolitisk rapport",
    "ECB Press Conference": "Europeiska centralbankens presskonferens",
    "Main Refinancing Rate": "ECB:s huvudsakliga refinansieringsränta",
    "Cash Rate": "Styrränta",
    "Overnight Rate": "Styrränta (dagslåneränta)",
    "BOC Rate Statement": "Kanadas centralbanks räntebesked",
    "RBA Rate Statement": "Australiens centralbanks räntebesked",
    "GDP": "BNP",
    "Advance GDP": "Preliminär BNP",
    "Prelim GDP": "Preliminär BNP",
    "Final GDP": "Slutlig BNP",
    "PPI": "Producentprisindex",
    "Core PPI": "Underliggande producentprisindex",
    "Core PCE Price Index": "Kärn-PCE (Feds inflationsmått)",
    "PCE Price Index": "PCE-prisindex",
    "ISM Manufacturing PMI": "ISM:s inköpschefsindex för industrin",
    "ISM Services PMI": "ISM:s inköpschefsindex för tjänstesektorn",
    "Flash Manufacturing PMI": "Preliminärt inköpschefsindex för industrin",
    "Flash Services PMI": "Preliminärt inköpschefsindex för tjänstesektorn",
    "CB Consumer Confidence": "Konsumentförtroende (Conference Board)",
    "Prelim UoM Consumer Sentiment": "Preliminärt konsumentförtroende (Michigan)",
    "JOLTS Job Openings": "Lediga jobb (JOLTS)",
    "Trade Balance": "Handelsbalans",
    "Durable Goods Orders": "Orderingång för varaktiga varor",
    "Core Durable Goods Orders": "Underliggande orderingång för varaktiga varor"
}
PERIOD_TRANSLATIONS = {"m/m": "månadsförändring", "q/q": "kvartalsförändring", "y/y": "årsförändring"}

def translate_title(title):
    base, separator, period = title.rpartition(" ")
    if separator and period in PERIOD_TRANSLATIONS:
        return f"{TITLE_TRANSLATIONS.get(base, base)} ({PERIOD_TRANSLATIONS[period]})"
    return TITLE_TRANSLATIONS.get(title, title)

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
    lines = [f"*Dagens viktiga ekonomiska nyheter – {today:%Y-%m-%d}*", "🔴 Hög påverkan | Svensk tid"]
    if not filtered:
        lines.append("Inga nyheter med hög påverkan är listade för idag.")
    for local_time, event in filtered:
        title = translate_title(str(event.get("title", "Okänd händelse")))
        country = event.get("country", "–")
        forecast = event.get("forecast") or "Ej angivet"
        previous = event.get("previous") or "Ej angivet"
        lines.append(f"*{local_time:%H:%M} | {country} | {title}*\nPrognos: {forecast} | Föregående: {previous}")
    lines.append("Källa: Forex Factory. Kalenderuppgifter kan ändras.")
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
