#!/usr/bin/env python3
"""Datadog Dashboard Snapshotter – OC-0051"""

import argparse
import json
import os
import sys
import time

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.datadoghq.com/api"


def _keys():
    api_key = os.environ.get("DD_API_KEY")
    app_key = os.environ.get("DD_APP_KEY")
    if not api_key or not app_key:
        print(f"{RED}Error: DD_API_KEY and DD_APP_KEY must be set{RESET}")
        sys.exit(1)
    return api_key, app_key


def _request(method, path, version="v1", **kwargs):
    api_key, app_key = _keys()
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
        "Content-Type": "application/json",
    }
    resp = getattr(requests, method)(f"{BASE_URL}/{version}{path}", headers=headers, **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_dashboards(args):
    data = _request("get", "/dashboard", version="v1")
    for db in data.get("dashboards", []):
        print(f"{GREEN}{db['id']}{RESET}  {db.get('title', 'Untitled')}  layout={db.get('layout_type', 'n/a')}")


def snapshot(args):
    duration_map = {"1h": 3600, "6h": 21600, "1d": 86400, "1w": 604800}
    seconds = duration_map.get(args.start, 3600)
    end = int(time.time())
    start = end - seconds
    params = {"metric_query": args.metric, "start": start, "end": end}
    data = _request("get", "/graph/snapshot", params=params)
    snap_url = data.get("snapshot_url", "")
    if snap_url:
        print(f"{GREEN}Snapshot URL:{RESET} {snap_url}")
    else:
        print(f"{YELLOW}Snapshot pending, check back shortly{RESET}")


def list_monitors(args):
    data = _request("get", "/monitor")
    for m in data:
        state = m.get("overall_state", "unknown")
        color = GREEN if state == "OK" else RED if state == "Alert" else YELLOW
        print(f"{color}[{state}]{RESET} {m['id']}  {m.get('name', 'Unnamed')}")


def get_monitor(args):
    data = _request("get", f"/monitor/{args.monitor_id}")
    print(f"{GREEN}Monitor {data['id']}{RESET}: {data.get('name', 'Unnamed')}")
    print(f"  State:   {data.get('overall_state', 'n/a')}")
    print(f"  Type:    {data.get('type', 'n/a')}")
    print(f"  Query:   {data.get('query', 'n/a')}")
    print(f"  Message: {data.get('message', 'n/a')[:120]}")


def mute_monitor(args):
    _request("post", f"/monitor/{args.monitor_id}/mute")
    print(f"{GREEN}Muted monitor {args.monitor_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Datadog Dashboard Snapshotter")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-dashboards", help="List dashboards")

    p_snap = sub.add_parser("snapshot", help="Snapshot a metric graph")
    p_snap.add_argument("--metric", required=True, help="Metric query string")
    p_snap.add_argument("--start", default="1h", choices=["1h", "6h", "1d", "1w"])

    sub.add_parser("list-monitors", help="List monitors")

    p_get = sub.add_parser("get-monitor", help="Get monitor details")
    p_get.add_argument("--monitor-id", required=True)

    p_mute = sub.add_parser("mute-monitor", help="Mute a monitor")
    p_mute.add_argument("--monitor-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-dashboards": list_dashboards,
        "snapshot": snapshot,
        "list-monitors": list_monitors,
        "get-monitor": get_monitor,
        "mute-monitor": mute_monitor,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
