#!/usr/bin/env python3
"""
Stripe Webhook Debugger (OC-0070)
Inspect webhook events, manage endpoints, and replay failed deliveries.
"""

import sys
import os
import json
import argparse
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.stripe.com/v1"


def get_headers():
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        print(f"{RED}Error: STRIPE_SECRET_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def api_request(method, endpoint, params=None, data=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.request(method, url, headers=get_headers(), params=params, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)


def list_events(args):
    print(f"{YELLOW}Listing webhook events...{RESET}")
    params = {"limit": args.limit}
    if args.type:
        params["type"] = args.type
    result = api_request("GET", "events", params=params)
    events = result.get("data", [])
    print(f"{GREEN}Found {len(events)} event(s):{RESET}")
    for e in events:
        print(f"  {e['id']}  type={e['type']}  created={e['created']}")


def get_event(args):
    print(f"{YELLOW}Fetching event {args.event_id}...{RESET}")
    result = api_request("GET", f"events/{args.event_id}")
    print(f"{GREEN}Event {result['id']}:{RESET}")
    print(f"  Type:    {result['type']}")
    print(f"  Created: {result['created']}")
    print(f"  Data:    {json.dumps(result.get('data', {}).get('object', {}), indent=2)[:500]}")


def list_endpoints(args):
    print(f"{YELLOW}Listing webhook endpoints...{RESET}")
    result = api_request("GET", "webhook_endpoints", params={"limit": args.limit})
    endpoints = result.get("data", [])
    print(f"{GREEN}Found {len(endpoints)} endpoint(s):{RESET}")
    for ep in endpoints:
        status = ep.get("status", "unknown")
        print(f"  {ep['id']}  url={ep['url']}  status={status}")


def create_endpoint(args):
    print(f"{YELLOW}Creating webhook endpoint {args.url}...{RESET}")
    data = {"url": args.url}
    if args.events:
        for i, ev in enumerate(args.events):
            data[f"enabled_events[{i}]"] = ev
    else:
        data["enabled_events[]"] = "*"
    result = api_request("POST", "webhook_endpoints", data=data)
    print(f"{GREEN}Endpoint created: {result['id']}  url={result['url']}{RESET}")


def replay(args):
    print(f"{YELLOW}Fetching event {args.event_id} for replay...{RESET}")
    event = api_request("GET", f"events/{args.event_id}")
    endpoints = api_request("GET", "webhook_endpoints", params={"limit": 100})
    eps = endpoints.get("data", [])
    if not eps:
        print(f"{RED}No webhook endpoints configured.{RESET}")
        sys.exit(1)
    payload = json.dumps(event)
    for ep in eps:
        if ep.get("status") != "enabled":
            continue
        url = ep["url"]
        print(f"{YELLOW}Replaying to {url}...{RESET}")
        try:
            resp = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=15)
            print(f"{GREEN}  -> {resp.status_code}{RESET}")
        except requests.exceptions.RequestException as e:
            print(f"{RED}  -> Failed: {e}{RESET}")
    print(f"{GREEN}Replay complete.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Stripe Webhook Debugger (OC-0070)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("list-events", help="List recent events")
    sp.add_argument("--type", help="Filter by event type")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("get-event", help="Get event details")
    sp.add_argument("event_id", help="Event ID")

    sp = subparsers.add_parser("list-endpoints", help="List webhook endpoints")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("create-endpoint", help="Create a webhook endpoint")
    sp.add_argument("url", help="Endpoint URL")
    sp.add_argument("--events", nargs="+", help="Event types to subscribe to")

    sp = subparsers.add_parser("replay", help="Replay an event")
    sp.add_argument("event_id", help="Event ID to replay")

    args = parser.parse_args()
    commands = {
        "list-events": list_events,
        "get-event": get_event,
        "list-endpoints": list_endpoints,
        "create-endpoint": create_endpoint,
        "replay": replay,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
