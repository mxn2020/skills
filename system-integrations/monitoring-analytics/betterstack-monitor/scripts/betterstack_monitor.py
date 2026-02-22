#!/usr/bin/env python3
"""Better Stack Monitor – OC-0057"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://uptime.betterstack.com/api/v2"


def _headers():
    token = os.environ.get("BETTERSTACK_API_TOKEN")
    if not token:
        print(f"{RED}Error: BETTERSTACK_API_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_monitors(args):
    data = _request("get", "/monitors")
    for m in data.get("data", []):
        attrs = m.get("attributes", {})
        status = attrs.get("status", "unknown")
        color = GREEN if status == "up" else RED if status == "down" else YELLOW
        print(f"{color}[{status}]{RESET} {m['id']}  {attrs.get('url', 'n/a')}  type={attrs.get('monitor_type', 'n/a')}")


def get_monitor(args):
    data = _request("get", f"/monitors/{args.monitor_id}")
    attrs = data.get("data", {}).get("attributes", {})
    print(f"{GREEN}Monitor {args.monitor_id}{RESET}")
    print(f"  URL:        {attrs.get('url', 'n/a')}")
    print(f"  Status:     {attrs.get('status', 'n/a')}")
    print(f"  Type:       {attrs.get('monitor_type', 'n/a')}")
    print(f"  Check freq: {attrs.get('check_frequency', 'n/a')}s")
    print(f"  Last check: {attrs.get('last_checked_at', 'n/a')}")


def list_incidents(args):
    data = _request("get", "/incidents")
    for inc in data.get("data", []):
        attrs = inc.get("attributes", {})
        status = attrs.get("status", "unknown")
        color = RED if status == "started" else YELLOW if status == "acknowledged" else GREEN
        print(f"{color}[{status}]{RESET} {inc['id']}  {attrs.get('name', 'n/a')}  started={attrs.get('started_at', 'n/a')}")


def acknowledge(args):
    _request("post", f"/incidents/{args.incident_id}/acknowledge")
    print(f"{GREEN}Acknowledged incident {args.incident_id}{RESET}")


def resolve(args):
    _request("post", f"/incidents/{args.incident_id}/resolve")
    print(f"{GREEN}Resolved incident {args.incident_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Better Stack Monitor")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-monitors", help="List uptime monitors")

    p_get = sub.add_parser("get-monitor", help="Get monitor details")
    p_get.add_argument("--monitor-id", required=True)

    sub.add_parser("list-incidents", help="List incidents")

    p_ack = sub.add_parser("acknowledge", help="Acknowledge an incident")
    p_ack.add_argument("--incident-id", required=True)

    p_resolve = sub.add_parser("resolve", help="Resolve an incident")
    p_resolve.add_argument("--incident-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-monitors": list_monitors,
        "get-monitor": get_monitor,
        "list-incidents": list_incidents,
        "acknowledge": acknowledge,
        "resolve": resolve,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
