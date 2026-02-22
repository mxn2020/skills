#!/usr/bin/env python3
"""Mixpanel Cohort Analyzer – OC-0054"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://mixpanel.com/api/2.0"
EXPORT_URL = "https://data.mixpanel.com/api/2.0"


def _auth():
    sa = os.environ.get("MIXPANEL_SERVICE_ACCOUNT")
    secret = os.environ.get("MIXPANEL_SECRET")
    project_id = os.environ.get("MIXPANEL_PROJECT_ID")
    if not sa or not secret or not project_id:
        print(f"{RED}Error: MIXPANEL_PROJECT_ID, MIXPANEL_SERVICE_ACCOUNT, and MIXPANEL_SECRET must be set{RESET}")
        sys.exit(1)
    return sa, secret, project_id


def _request(method, path, base=None, **kwargs):
    sa, secret, project_id = _auth()
    url = f"{base or BASE_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers["Accept"] = "application/json"
    resp = getattr(requests, method)(url, auth=(sa, secret), headers=headers, **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def query_events(args):
    _, _, project_id = _auth()
    params = {
        "project_id": project_id,
        "event": json.dumps([args.event]),
        "type": "general",
        "unit": "day",
        "from_date": args.from_date,
        "to_date": args.to_date,
    }
    data = _request("get", "/events", params=params)
    values = data.get("data", {}).get("values", {})
    for event_name, dates in values.items():
        print(f"{GREEN}{event_name}{RESET}")
        for date, count in sorted(dates.items()):
            print(f"  {date}: {count}")


def retention(args):
    _, _, project_id = _auth()
    params = {
        "project_id": project_id,
        "born_event": args.event,
        "event": args.event,
        "unit": "week",
        "from_date": args.from_date,
        "to_date": args.to_date,
    }
    data = _request("get", "/retention", params=params)
    for row in data.get("results", []):
        date = row.get("date", "n/a")
        counts = row.get("counts", [])
        pct = [f"{c:.0%}" if isinstance(c, float) else str(c) for c in counts[:6]]
        print(f"{YELLOW}{date}{RESET}  {' | '.join(pct)}")


def funnels(args):
    _, _, project_id = _auth()
    params = {"project_id": project_id, "funnel_id": args.funnel_id}
    data = _request("get", "/funnels", params=params)
    steps = data.get("data", {}).get("steps", [])
    for step in steps:
        count = step.get("count", 0)
        pct = step.get("step_conv_ratio", 0)
        print(f"{GREEN}{step.get('event', 'n/a')}{RESET}  count={count}  conversion={pct:.1%}")


def list_cohorts(args):
    _, _, project_id = _auth()
    params = {"project_id": project_id}
    data = _request("get", "/cohorts/list", params=params)
    for c in data:
        print(f"{GREEN}{c['id']}{RESET}  {c.get('name', 'Unnamed')}  count={c.get('count', 'n/a')}")


def export(args):
    _, _, project_id = _auth()
    params = {
        "project_id": project_id,
        "from_date": args.from_date,
        "to_date": args.to_date,
    }
    sa, secret, _ = _auth()
    resp = requests.get(f"{EXPORT_URL}/export", auth=(sa, secret), params=params, stream=True)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    count = 0
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            print(line)
            count += 1
    print(f"{GREEN}Exported {count} events{RESET}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Mixpanel Cohort Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_events = sub.add_parser("query-events", help="Query event counts")
    p_events.add_argument("--event", required=True)
    p_events.add_argument("--from-date", required=True, help="YYYY-MM-DD")
    p_events.add_argument("--to-date", required=True, help="YYYY-MM-DD")

    p_ret = sub.add_parser("retention", help="Get retention data")
    p_ret.add_argument("--event", required=True)
    p_ret.add_argument("--from-date", required=True)
    p_ret.add_argument("--to-date", required=True)

    p_fun = sub.add_parser("funnels", help="Query funnel data")
    p_fun.add_argument("--funnel-id", required=True)

    sub.add_parser("list-cohorts", help="List cohorts")

    p_export = sub.add_parser("export", help="Export raw events")
    p_export.add_argument("--from-date", required=True)
    p_export.add_argument("--to-date", required=True)

    args = parser.parse_args()
    commands = {
        "query-events": query_events,
        "retention": retention,
        "funnels": funnels,
        "list-cohorts": list_cohorts,
        "export": export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
