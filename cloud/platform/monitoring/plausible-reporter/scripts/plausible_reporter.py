#!/usr/bin/env python3
"""Plausible Analytics Reporter – OC-0058"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _config():
    url = os.environ.get("PLAUSIBLE_URL")
    key = os.environ.get("PLAUSIBLE_API_KEY")
    if not url or not key:
        print(f"{RED}Error: PLAUSIBLE_URL and PLAUSIBLE_API_KEY must be set{RESET}")
        sys.exit(1)
    return url.rstrip("/"), key


def _request(method, path, **kwargs):
    url, key = _config()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    resp = getattr(requests, method)(f"{url}{path}", headers=headers, **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def realtime(args):
    data = _request("get", f"/api/v1/stats/realtime/visitors", params={"site_id": args.site_id})
    print(f"{GREEN}Real-time visitors on {args.site_id}: {data}{RESET}")


def aggregate(args):
    params = {
        "site_id": args.site_id,
        "period": args.period,
        "metrics": args.metrics,
    }
    data = _request("get", "/api/v1/stats/aggregate", params=params)
    results = data.get("results", data)
    print(f"{GREEN}Aggregate for {args.site_id} ({args.period}):{RESET}")
    if isinstance(results, dict):
        for metric, val in results.items():
            value = val.get("value", val) if isinstance(val, dict) else val
            print(f"  {metric}: {value}")
    else:
        print(f"  {results}")


def timeseries(args):
    params = {
        "site_id": args.site_id,
        "period": args.period,
        "metrics": args.metrics,
    }
    data = _request("get", "/api/v1/stats/timeseries", params=params)
    for point in data.get("results", []):
        date = point.get("date", "n/a")
        visitors = point.get("visitors", 0)
        print(f"{YELLOW}{date}{RESET}  visitors={visitors}")


def breakdown(args):
    params = {
        "site_id": args.site_id,
        "period": args.period,
        "property": args.property,
        "metrics": args.metrics,
        "limit": args.limit,
    }
    data = _request("get", "/api/v1/stats/breakdown", params=params)
    for row in data.get("results", []):
        prop_val = row.get(args.property.split(":")[-1], "n/a")
        visitors = row.get("visitors", 0)
        print(f"{GREEN}{prop_val}{RESET}  visitors={visitors}")


def list_sites(args):
    data = _request("get", "/api/v1/sites")
    for site in data.get("sites", data if isinstance(data, list) else []):
        domain = site.get("domain", "n/a") if isinstance(site, dict) else site
        print(f"{GREEN}{domain}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Plausible Analytics Reporter")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rt = sub.add_parser("realtime", help="Real-time visitors")
    p_rt.add_argument("--site-id", required=True)

    p_agg = sub.add_parser("aggregate", help="Aggregate stats")
    p_agg.add_argument("--site-id", required=True)
    p_agg.add_argument("--period", default="30d")
    p_agg.add_argument("--metrics", default="visitors,pageviews,bounce_rate,visit_duration")

    p_ts = sub.add_parser("timeseries", help="Time series data")
    p_ts.add_argument("--site-id", required=True)
    p_ts.add_argument("--period", default="7d")
    p_ts.add_argument("--metrics", default="visitors")

    p_bd = sub.add_parser("breakdown", help="Breakdown by property")
    p_bd.add_argument("--site-id", required=True)
    p_bd.add_argument("--property", required=True, help="e.g. visit:source, visit:country")
    p_bd.add_argument("--period", default="30d")
    p_bd.add_argument("--metrics", default="visitors")
    p_bd.add_argument("--limit", type=int, default=10)

    sub.add_parser("list-sites", help="List sites")

    args = parser.parse_args()
    commands = {
        "realtime": realtime,
        "aggregate": aggregate,
        "timeseries": timeseries,
        "breakdown": breakdown,
        "list-sites": list_sites,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
