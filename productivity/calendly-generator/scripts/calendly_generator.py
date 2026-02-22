#!/usr/bin/env python3
"""
Calendly Link Generator — OC-0134
Create one-off scheduling links with custom constraints via Calendly API.
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

BASE_URL = "https://api.calendly.com"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("CALENDLY_TOKEN", "")
    if not token:
        _die("CALENDLY_TOKEN environment variable is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    if resp.status_code == 204:
        return {}
    return resp.json()


def _get_current_user_uri() -> str:
    data = _request("GET", "users/me")
    return data["resource"]["uri"]


def list_event_types():
    user_uri = _get_current_user_uri()
    data = _request("GET", "event_types", params={"user": user_uri, "active": "true"})
    items = data.get("collection", [])
    if not items:
        print(f"{YELLOW}No event types found.{RESET}")
        return
    print(f"{GREEN}Found {len(items)} event type(s):{RESET}")
    for et in items:
        slug = et.get("slug", "")
        name = et.get("name", "")
        duration = et.get("duration", "?")
        uri = et.get("uri", "")
        print(f"  {CYAN}{name}{RESET} ({duration} min) — slug: {slug}")
        print(f"    URI: {uri}")


def create_link(event_type_uri: str, max_event_count: int = 1):
    body = {
        "max_event_count": max_event_count,
        "owner": event_type_uri,
        "owner_type": "EventType",
    }
    data = _request("POST", "one_off_event_type_invites", json=body)
    resource = data.get("resource", {})
    link = resource.get("booking_url", "N/A")
    uri = resource.get("uri", "N/A")
    print(f"{GREEN}Scheduling link created:{RESET}")
    print(f"  URL:  {link}")
    print(f"  URI:  {uri}")
    print(f"  Max uses: {max_event_count}")


def list_links():
    user_uri = _get_current_user_uri()
    data = _request("GET", "one_off_event_type_invites", params={"user": user_uri})
    items = data.get("collection", [])
    if not items:
        print(f"{YELLOW}No single-use links found.{RESET}")
        return
    print(f"{GREEN}Found {len(items)} link(s):{RESET}")
    for link in items:
        status = link.get("status", "unknown")
        url = link.get("booking_url", "N/A")
        uri = link.get("uri", "")
        color = GREEN if status == "active" else RED
        print(f"  [{color}{status}{RESET}] {url}")
        print(f"    URI: {uri}")


def deactivate_link(link_uri: str):
    # Extract UUID from URI
    uid = link_uri.rstrip("/").split("/")[-1]
    _request("DELETE", f"one_off_event_type_invites/{uid}")
    print(f"{GREEN}Link deactivated: {link_uri}{RESET}")


def get_scheduled_events(days: int = 7):
    user_uri = _get_current_user_uri()
    now = datetime.now(timezone.utc)
    max_time = now + timedelta(days=days)
    params = {
        "user": user_uri,
        "min_start_time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_start_time": max_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "active",
        "count": 50,
    }
    data = _request("GET", "scheduled_events", params=params)
    items = data.get("collection", [])
    if not items:
        print(f"{YELLOW}No scheduled events in the next {days} day(s).{RESET}")
        return
    print(f"{GREEN}Found {len(items)} scheduled event(s) in the next {days} day(s):{RESET}")
    for evt in items:
        name = evt.get("name", "(no name)")
        start = evt.get("start_time", "")[:16]
        end = evt.get("end_time", "")[:16]
        print(f"  {CYAN}{name}{RESET}  {start} → {end}")


def main():
    parser = argparse.ArgumentParser(
        prog="calendly_generator.py",
        description="Calendly Link Generator — OC-0134"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-event-types", help="List all event types")

    p = sub.add_parser("create-link", help="Create a single-use scheduling link")
    p.add_argument("--event-type-uri", required=True, help="Event type URI from list-event-types")
    p.add_argument("--max-event-count", type=int, default=1, help="Max number of bookings (default: 1)")

    sub.add_parser("list-links", help="List single-use links")

    p = sub.add_parser("deactivate-link", help="Deactivate a scheduling link")
    p.add_argument("--link-uri", required=True, help="URI of the link to deactivate")

    p = sub.add_parser("get-scheduled-events", help="List upcoming scheduled events")
    p.add_argument("--days", type=int, default=7, help="Days ahead to look (default: 7)")

    args = parser.parse_args()
    dispatch = {
        "list-event-types":   lambda: list_event_types(),
        "create-link":        lambda: create_link(args.event_type_uri, args.max_event_count),
        "list-links":         lambda: list_links(),
        "deactivate-link":    lambda: deactivate_link(args.link_uri),
        "get-scheduled-events": lambda: get_scheduled_events(args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
