#!/usr/bin/env python3
"""Grafana Alert Manager – OC-0052"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _config():
    url = os.environ.get("GRAFANA_URL")
    key = os.environ.get("GRAFANA_API_KEY")
    if not url or not key:
        print(f"{RED}Error: GRAFANA_URL and GRAFANA_API_KEY must be set{RESET}")
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


def list_alerts(args):
    data = _request("get", "/api/alertmanager/grafana/api/v2/alerts")
    for alert in data:
        status = alert.get("status", {}).get("state", "unknown")
        color = RED if status == "active" else YELLOW
        labels = alert.get("labels", {})
        name = labels.get("alertname", "unnamed")
        print(f"{color}[{status}]{RESET} {name}  instance={labels.get('instance', 'n/a')}")


def silence(args):
    name, value = args.matcher.split("=", 1)
    duration_map = {"1h": 1, "2h": 2, "4h": 4, "8h": 8, "24h": 24}
    hours = duration_map.get(args.duration, 2)
    now = datetime.now(timezone.utc)
    payload = {
        "matchers": [{"name": name, "value": value, "isRegex": False}],
        "startsAt": now.isoformat(),
        "endsAt": (now + timedelta(hours=hours)).isoformat(),
        "createdBy": args.created_by,
        "comment": args.comment,
    }
    data = _request("post", "/api/alertmanager/grafana/api/v2/silences", json=payload)
    print(f"{GREEN}Silence created: {data.get('silenceID', 'n/a')}{RESET}")


def acknowledge(args):
    # Grafana treats acknowledgment as a short silence
    now = datetime.now(timezone.utc)
    payload = {
        "matchers": [{"name": "alertname", "value": args.alert_id, "isRegex": False}],
        "startsAt": now.isoformat(),
        "endsAt": (now + timedelta(hours=1)).isoformat(),
        "createdBy": "openclaw",
        "comment": "Acknowledged via OpenClaw",
    }
    data = _request("post", "/api/alertmanager/grafana/api/v2/silences", json=payload)
    print(f"{GREEN}Acknowledged alert {args.alert_id} (silence={data.get('silenceID', 'n/a')}){RESET}")


def list_silences(args):
    data = _request("get", "/api/alertmanager/grafana/api/v2/silences")
    for s in data:
        status = s.get("status", {}).get("state", "unknown")
        color = GREEN if status == "active" else YELLOW
        matchers = ", ".join(f"{m['name']}={m['value']}" for m in s.get("matchers", []))
        print(f"{color}[{status}]{RESET} {s['id']}  {matchers}  ends={s.get('endsAt', 'n/a')}")


def delete_silence(args):
    _request("delete", f"/api/alertmanager/grafana/api/v2/silence/{args.silence_id}")
    print(f"{GREEN}Deleted silence {args.silence_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Grafana Alert Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-alerts", help="List firing alerts")

    p_silence = sub.add_parser("silence", help="Create a silence")
    p_silence.add_argument("--matcher", required=True, help="label=value matcher")
    p_silence.add_argument("--duration", default="2h", choices=["1h", "2h", "4h", "8h", "24h"])
    p_silence.add_argument("--created-by", default="openclaw")
    p_silence.add_argument("--comment", default="Silenced via OpenClaw")

    p_ack = sub.add_parser("acknowledge", help="Acknowledge a firing alert")
    p_ack.add_argument("--alert-id", required=True)

    sub.add_parser("list-silences", help="List active silences")

    p_del = sub.add_parser("delete-silence", help="Delete a silence")
    p_del.add_argument("--silence-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-alerts": list_alerts,
        "silence": silence,
        "acknowledge": acknowledge,
        "list-silences": list_silences,
        "delete-silence": delete_silence,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
