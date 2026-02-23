#!/usr/bin/env python3
"""
Meeting Prep Briefer — OC-0135
Summarize attendees, agenda, and relevant docs before a meeting.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

GCAL_BASE = "https://www.googleapis.com/calendar/v3"
OPENAI_BASE = "https://api.openai.com/v1"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _gcal_headers() -> dict:
    token = os.environ.get("GOOGLE_CALENDAR_TOKEN", "")
    if not token:
        _die("GOOGLE_CALENDAR_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}"}


def _openai_headers() -> dict:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _gcal_request(path: str, params: dict = None) -> dict:
    resp = requests.get(
        f"{GCAL_BASE}/{path.lstrip('/')}",
        headers=_gcal_headers(), params=params or {}, timeout=30
    )
    if not resp.ok:
        _die(f"Calendar API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _ai_summarize(prompt: str) -> str:
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
    }
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers=_openai_headers(), json=body, timeout=60
    )
    if not resp.ok:
        return f"(AI summary unavailable: {resp.status_code})"
    return resp.json()["choices"][0]["message"]["content"].strip()


def list_upcoming(hours: int = 24):
    cal_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    now = datetime.now(timezone.utc)
    max_time = now + timedelta(hours=hours)
    data = _gcal_request(
        f"calendars/{cal_id}/events",
        params={
            "timeMin": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timeMax": max_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "orderBy": "startTime",
            "singleEvents": "true",
            "maxResults": 20,
        }
    )
    events = data.get("items", [])
    if not events:
        print(f"{YELLOW}No meetings in the next {hours} hour(s).{RESET}")
        return
    print(f"{GREEN}Upcoming meetings (next {hours}h):{RESET}")
    for evt in events:
        start = (evt.get("start") or {}).get("dateTime", "")[:16]
        title = evt.get("summary", "(no title)")
        eid = evt.get("id", "")
        attendee_count = len(evt.get("attendees", []))
        print(f"  {CYAN}{start}{RESET}  {BOLD}{title}{RESET}  ({attendee_count} attendee(s))")
        print(f"    ID: {eid}")


def brief(event_id: str):
    cal_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    evt = _gcal_request(f"calendars/{cal_id}/events/{event_id}")

    title = evt.get("summary", "(no title)")
    start = (evt.get("start") or {}).get("dateTime", "")
    end   = (evt.get("end") or {}).get("dateTime", "")
    desc  = evt.get("description", "")
    location = evt.get("location", "")
    attendees = evt.get("attendees", [])
    organizer = evt.get("organizer", {})

    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}MEETING BRIEF: {title}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

    print(f"{BOLD}When:{RESET}  {start[:16]} → {end[:16]}")
    if location:
        print(f"{BOLD}Where:{RESET} {location}")
    print(f"{BOLD}Organizer:{RESET} {organizer.get('email', 'unknown')}")

    if attendees:
        print(f"\n{BOLD}Attendees ({len(attendees)}):{RESET}")
        for att in attendees:
            status = att.get("responseStatus", "unknown")
            color = GREEN if status == "accepted" else (YELLOW if status == "tentative" else RED)
            print(f"  {color}[{status}]{RESET} {att.get('email', '')}")

    if desc:
        print(f"\n{BOLD}Agenda / Description:{RESET}")
        print(f"  {desc[:500]}")

    # AI summary
    prompt = (
        f"Meeting: '{title}'\n"
        f"Time: {start[:16]} to {end[:16]}\n"
        f"Attendees: {', '.join(a.get('email','') for a in attendees)}\n"
        f"Description: {desc[:300]}\n\n"
        "In 3-5 bullet points, provide a concise pre-meeting briefing: "
        "key topics to prepare for, likely discussion points, and any action items to bring."
    )
    print(f"\n{BOLD}AI Prep Notes:{RESET}")
    summary = _ai_summarize(prompt)
    for line in summary.split("\n"):
        print(f"  {line}")
    print()


def summarize_doc(url: str):
    print(f"{YELLOW}Fetching document: {url}{RESET}")
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "MeetingPrepBriefer/1.0"})
        if not resp.ok:
            _die(f"Could not fetch document: HTTP {resp.status_code}")
        text = resp.text[:3000]
    except requests.RequestException as e:
        _die(f"Request failed: {e}")

    prompt = (
        f"Summarize the following document content in 5 bullet points for a meeting participant:\n\n{text}"
    )
    print(f"\n{BOLD}Document Summary:{RESET}")
    summary = _ai_summarize(prompt)
    for line in summary.split("\n"):
        print(f"  {line}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="meeting_prep_briefer.py",
        description="Meeting Prep Briefer — OC-0135"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-upcoming", help="List meetings in the next N hours")
    p.add_argument("--hours", type=int, default=24, help="Hours ahead (default: 24)")

    p = sub.add_parser("brief", help="Generate prep briefing for an event")
    p.add_argument("--event-id", required=True, help="Google Calendar event ID")

    p = sub.add_parser("summarize-doc", help="Summarize a document URL for context")
    p.add_argument("--url", required=True, help="Document URL to summarize")

    args = parser.parse_args()
    dispatch = {
        "list-upcoming":  lambda: list_upcoming(args.hours),
        "brief":          lambda: brief(args.event_id),
        "summarize-doc":  lambda: summarize_doc(args.url),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
