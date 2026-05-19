#!/usr/bin/env python3
"""Fetch New Haven CT government meetings from Legistar and write calendar.ics."""

import hashlib
import sys
from datetime import datetime, timedelta, date

import pytz
import requests
from bs4 import BeautifulSoup, NavigableString
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight

LEGISTAR_URL = "https://newhaven-ct.legistar.com/Calendar.aspx"
TABLE_ID = "ctl00_ContentPlaceHolder1_gridCalendar_ctl00"
TZ = pytz.timezone("America/New_York")
STAR = "★"  # ★
DEFAULT_DURATION = timedelta(hours=2)


def fetch_html():
    resp = requests.get(
        LEGISTAR_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; NewHavenMeetingCalendar/1.0)"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse_location(cell):
    """Return venue text only, stripping the italicised YouTube/viewing note."""
    font = cell.find("font") or cell
    parts = []
    for node in font.children:
        if getattr(node, "name", None) == "br":
            break
        if isinstance(node, NavigableString):
            parts.append(str(node).strip())
    text = " ".join(p for p in parts if p)
    return text or cell.get_text(separator=" ", strip=True).split("Meeting can be")[0].strip()


def parse_meetings(html):
    soup = BeautifulSoup(html, "html.parser")
    grid = soup.find("table", id=TABLE_ID)
    if not grid:
        raise RuntimeError(f"Table #{TABLE_ID} not found — page layout may have changed")

    meetings = []
    rows = grid.find_all("tr")
    for row in rows[1:]:  # skip header
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        name = cells[0].get_text(strip=True)
        date_str = cells[1].get_text(strip=True)
        time_str = cells[3].get_text(strip=True)
        location = parse_location(cells[4])

        if not name or not date_str:
            continue

        try:
            meeting_date = datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            print(f"  Skipping unrecognised date: {date_str!r}", file=sys.stderr)
            continue

        meeting_time = None
        for fmt in ("%I:%M %p", "%I:%M%p"):
            try:
                meeting_time = datetime.strptime(time_str.strip(), fmt).time()
                break
            except ValueError:
                pass

        meetings.append(
            {
                "name": name,
                "date": meeting_date,
                "time": meeting_time,
                "time_str": time_str,
                "location": location,
            }
        )

    return meetings


def make_uid(m):
    key = f"{m['name']}|{m['date']}|{m['time_str']}"
    digest = hashlib.sha1(key.encode()).hexdigest()[:16]
    return f"{digest}@newhaven-ct.legistar.com"


def build_vtimezone():
    tz = Timezone()
    tz.add("TZID", "America/New_York")

    # Daylight saving: second Sunday in March at 02:00
    dst = TimezoneDaylight()
    dst.add("DTSTART", datetime(1970, 3, 8, 2, 0, 0))
    dst.add("RRULE", {"FREQ": "YEARLY", "BYDAY": "2SU", "BYMONTH": 3})
    dst.add("TZNAME", "EDT")
    dst.add("TZOFFSETFROM", timedelta(hours=-5))
    dst.add("TZOFFSETTO", timedelta(hours=-4))
    tz.add_component(dst)

    # Standard time: first Sunday in November at 02:00
    std = TimezoneStandard()
    std.add("DTSTART", datetime(1970, 11, 1, 2, 0, 0))
    std.add("RRULE", {"FREQ": "YEARLY", "BYDAY": "1SU", "BYMONTH": 11})
    std.add("TZNAME", "EST")
    std.add("TZOFFSETFROM", timedelta(hours=-4))
    std.add("TZOFFSETTO", timedelta(hours=-5))
    tz.add_component(std)

    return tz


def build_calendar(meetings):
    cal = Calendar()
    cal.add("PRODID", "-//New Haven CT Meeting Calendar//EN")
    cal.add("VERSION", "2.0")
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("METHOD", "PUBLISH")
    cal.add("X-WR-CALNAME", "New Haven CT Government Meetings")
    cal.add("X-WR-TIMEZONE", "America/New_York")
    cal.add_component(build_vtimezone())

    now_utc = datetime.now(pytz.utc)

    for m in meetings:
        event = Event()

        is_full_board = m["name"].strip() == "Board of Alders"
        summary = f"{STAR} {m['name']}" if is_full_board else m["name"]
        event.add("SUMMARY", summary)
        event.add("UID", make_uid(m))
        event.add("DTSTAMP", now_utc)
        event.add("URL", LEGISTAR_URL)

        if m["time"]:
            dt_start = TZ.localize(datetime.combine(m["date"], m["time"]))
            dt_end = dt_start + DEFAULT_DURATION
            event.add("DTSTART", dt_start)
            event.add("DTEND", dt_end)
        else:
            event.add("DTSTART", m["date"])
            event.add("DTEND", m["date"] + timedelta(days=1))

        if m["location"]:
            event.add("LOCATION", m["location"])

        event.add("DESCRIPTION", f"Source: {LEGISTAR_URL}")
        cal.add_component(event)

    return cal


def main():
    print("Fetching meetings…", file=sys.stderr)
    html = fetch_html()
    meetings = parse_meetings(html)
    print(f"Parsed {len(meetings)} meetings", file=sys.stderr)

    cal = build_calendar(meetings)

    out = "calendar.ics"
    with open(out, "wb") as f:
        f.write(cal.to_ical())
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
