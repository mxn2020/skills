#!/usr/bin/env python3
"""
Google Calendar — OC-0133
Manage Google Calendar events and check availability via REST API.
"""

import os
import sys
import argparse
from datetime import datetime, timezone
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

BASE_URL = "https://www.googleapis.com/calendar/v3"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("GOOGLE_CALENDAR_TOKEN", "")
    if not token:
        _die("GOOGLE_CALENDAR_TOKEN environment variable is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _cal_id() -> str:
    return os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=_headers(), timeout=30, **kwargs)
    if resp.status_code == 204:
        return {}
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_events(calendar_id: str = None, time_min: str = None,
                time_max: str = None, max_results: int = 10):
    cal = calendar_id or _cal_id()
    if not time_min:
        time_min = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"maxResults": max_results, "orderBy": "startTime",
              "singleEvents": "true", "timeMin": time_min}
    if time_max:
        params["timeMax"] = time_max
    data = _request("GET", f"calendars/{cal}/events", params=params)
    events = data.get("items", [])
    if not events:
        print(f"{YELLOW}No events found.{RESET}")
        return
    print(f"{GREEN}Found {len(events)} event(s):{RESET}")
    for evt in events:
        start = (evt.get("start") or {}).get("dateTime") or \
                (evt.get("start") or {}).get("date", "")
        end   = (evt.get("end") or {}).get("dateTime") or \
                (evt.get("end") or {}).get("date", "")
        print(f"  {CYAN}{evt['id']}{RESET}  {evt.get('summary', '(no title)')}")
        print(f"    {start[:16]} → {end[:16]}")


def create_event(title: str, start: str, end: str, description: str = "",
                 attendees: str = ""):
    body = {"summary": title,
            "start":   {"dateTime": start, "timeZone": "UTC"},
            "end":     {"dateTime": end,   "timeZone": "UTC"}}
    if description:
        body["description"] = description
    if attendees:
        body["attendees"] = [{"email": e.strip()} for e in attendees.split(",")]
    evt = _request("POST", f"calendars/{_cal_id()}/events", json=body)
    print(f"{GREEN}Created event: {evt['id']}{RESET}")
    print(f"  {evt.get('summary')}  {start} → {end}")
    print(f"  Link: {evt.get('htmlLink', 'N/A')}")


def update_event(event_id: str, title: str = None, start: str = None, end: str = None):
    evt = _request("GET", f"calendars/{_cal_id()}/events/{event_id}")
    if title:
        evt["summary"] = title
    if start:
        evt["start"] = {"dateTime": start, "timeZone": "UTC"}
    if end:
        evt["end"] = {"dateTime": end, "timeZone": "UTC"}
    updated = _request("PUT", f"calendars/{_cal_id()}/events/{event_id}", json=evt)
    print(f"{GREEN}Updated event: {updated.get('summary', event_id)}{RESET}")


def delete_event(event_id: str):
    _request("DELETE", f"calendars/{_cal_id()}/events/{event_id}")
    print(f"{GREEN}Deleted event {event_id}{RESET}")


def check_availability(start: str, end: str):
    body = {"timeMin": start, "timeMax": end,
            "items": [{"id": _cal_id()}]}
    data = _request("POST", "freeBusy", json=body)
    busy_slots = (data.get("calendars", {}).get(_cal_id(), {})
                      .get("busy", []))
    if not busy_slots:
        print(f"{GREEN}Time slot is AVAILABLE: {start} → {end}{RESET}")
    else:
        print(f"{RED}Time slot is BUSY. Conflicts:{RESET}")
        for slot in busy_slots:
            print(f"  {slot['start']} → {slot['end']}")


def main():
    parser = argparse.ArgumentParser(prog="google_calendar.py",
                                     description="Google Calendar — OC-0133")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-events", help="List upcoming events")
    p.add_argument("--calendar-id", default=None)
    p.add_argument("--time-min", default=None)
    p.add_argument("--time-max", default=None)
    p.add_argument("--max-results", type=int, default=10)

    p = sub.add_parser("create-event", help="Create a calendar event")
    p.add_argument("--title", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--attendees", default="", help="Comma-separated emails")

    p = sub.add_parser("update-event", help="Update an event")
    p.add_argument("--event-id", required=True)
    p.add_argument("--title", default=None)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)

    p = sub.add_parser("delete-event", help="Delete an event")
    p.add_argument("--event-id", required=True)

    p = sub.add_parser("check-availability", help="Check if time is free")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)

    args = parser.parse_args()
    dispatch = {
        "list-events":        lambda: list_events(args.calendar_id, args.time_min,
                                                   args.time_max, args.max_results),
        "create-event":       lambda: create_event(args.title, args.start, args.end,
                                                    args.description, args.attendees),
        "update-event":       lambda: update_event(args.event_id, args.title,
                                                    args.start, args.end),
        "delete-event":       lambda: delete_event(args.event_id),
        "check-availability": lambda: check_availability(args.start, args.end),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
