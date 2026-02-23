#!/usr/bin/env python3
"""PagerDuty Incident Creator – OC-0079"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.pagerduty.com"


def _headers(write=False):
    token = os.environ.get("PAGERDUTY_API_KEY")
    if not token:
        print(f"{RED}Error: PAGERDUTY_API_KEY is not set{RESET}")
        sys.exit(1)
    hdrs = {"Authorization": f"Token token={token}", "Content-Type": "application/json"}
    if write:
        email = os.environ.get("PAGERDUTY_FROM_EMAIL")
        if not email:
            print(f"{RED}Error: PAGERDUTY_FROM_EMAIL is not set{RESET}")
            sys.exit(1)
        hdrs["From"] = email
    return hdrs


def _request(method, path, write=False, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(write=write), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def create_incident(args):
    payload = {
        "incident": {
            "type": "incident",
            "title": args.title,
            "service": {"id": args.service_id, "type": "service_reference"},
            "urgency": args.urgency,
            "body": {"type": "incident_body", "details": args.details or ""},
        }
    }
    data = _request("post", "/incidents", write=True, json=payload)
    inc = data["incident"]
    print(f"{GREEN}Created incident {inc['id']}{RESET}: {inc['title']}")
    print(f"  Status:  {inc.get('status', 'n/a')}")
    print(f"  Urgency: {inc.get('urgency', 'n/a')}")


def list_incidents(args):
    params = {"limit": args.limit}
    if args.status:
        params["statuses[]"] = args.status
    data = _request("get", "/incidents", params=params)
    for inc in data.get("incidents", []):
        status = inc.get("status", "unknown")
        color = RED if status == "triggered" else YELLOW if status == "acknowledged" else GREEN
        print(f"{color}[{status}]{RESET} {inc['id']}  {inc['title']}  urgency={inc.get('urgency', 'n/a')}")


def get_incident(args):
    data = _request("get", f"/incidents/{args.incident_id}")
    inc = data["incident"]
    print(f"{GREEN}Incident {inc['id']}{RESET}: {inc['title']}")
    print(f"  Status:     {inc.get('status', 'n/a')}")
    print(f"  Urgency:    {inc.get('urgency', 'n/a')}")
    print(f"  Service:    {inc.get('service', {}).get('summary', 'n/a')}")
    print(f"  Created:    {inc.get('created_at', 'n/a')}")
    print(f"  Assignments: {', '.join(a.get('assignee', {}).get('summary', '') for a in inc.get('assignments', []))}")


def acknowledge(args):
    payload = {
        "incident": {
            "type": "incident_reference",
            "status": "acknowledged",
        }
    }
    _request("put", f"/incidents/{args.incident_id}", write=True, json=payload)
    print(f"{GREEN}Acknowledged incident {args.incident_id}{RESET}")


def resolve(args):
    payload = {
        "incident": {
            "type": "incident_reference",
            "status": "resolved",
        }
    }
    _request("put", f"/incidents/{args.incident_id}", write=True, json=payload)
    print(f"{GREEN}Resolved incident {args.incident_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="PagerDuty Incident Creator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create-incident", help="Create a new incident")
    p_create.add_argument("--title", required=True, help="Incident title")
    p_create.add_argument("--service-id", required=True, help="PagerDuty service ID")
    p_create.add_argument("--urgency", choices=["high", "low"], default="high")
    p_create.add_argument("--details", default="", help="Incident body details")

    p_list = sub.add_parser("list-incidents", help="List incidents")
    p_list.add_argument("--status", choices=["triggered", "acknowledged", "resolved"])
    p_list.add_argument("--limit", type=int, default=25)

    p_get = sub.add_parser("get-incident", help="Get incident details")
    p_get.add_argument("--incident-id", required=True)

    p_ack = sub.add_parser("acknowledge", help="Acknowledge an incident")
    p_ack.add_argument("--incident-id", required=True)

    p_resolve = sub.add_parser("resolve", help="Resolve an incident")
    p_resolve.add_argument("--incident-id", required=True)

    args = parser.parse_args()
    commands = {
        "create-incident": create_incident,
        "list-incidents": list_incidents,
        "get-incident": get_incident,
        "acknowledge": acknowledge,
        "resolve": resolve,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
