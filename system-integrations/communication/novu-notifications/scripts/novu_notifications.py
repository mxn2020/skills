#!/usr/bin/env python3
"""Novu Notification Manager – OC-0081"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.novu.co/v1"


def _headers():
    token = os.environ.get("NOVU_API_KEY")
    if not token:
        print(f"{RED}Error: NOVU_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"ApiKey {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def trigger(args):
    payload = {"name": args.workflow, "to": {"subscriberId": args.subscriber_id}}
    if args.payload:
        payload["payload"] = json.loads(args.payload)
    data = _request("post", "/events/trigger", json=payload)
    print(f"{GREEN}Triggered workflow '{args.workflow}' for subscriber '{args.subscriber_id}'{RESET}")
    tx = data.get("data", {}).get("transactionId", "n/a")
    print(f"  Transaction ID: {tx}")


def list_subscribers(args):
    params = {"page": args.page}
    data = _request("get", "/subscribers", params=params)
    for sub in data.get("data", []):
        email = sub.get("email", "n/a")
        name = " ".join(filter(None, [sub.get("firstName", ""), sub.get("lastName", "")]))
        print(f"{YELLOW}{sub.get('subscriberId', 'n/a')}{RESET}  {name or 'n/a'}  email={email}")


def create_subscriber(args):
    payload = {"subscriberId": args.subscriber_id}
    if args.email:
        payload["email"] = args.email
    if args.first_name:
        payload["firstName"] = args.first_name
    if args.last_name:
        payload["lastName"] = args.last_name
    _request("post", "/subscribers", json=payload)
    print(f"{GREEN}Created subscriber '{args.subscriber_id}'{RESET}")


def list_notifications(args):
    params = {"page": args.page}
    data = _request("get", "/notifications", params=params)
    for notif in data.get("data", []):
        channel = notif.get("channel", "n/a")
        status = notif.get("status", "n/a")
        color = GREEN if status == "sent" else YELLOW
        print(f"{color}[{status}]{RESET}  channel={channel}  id={notif.get('_id', 'n/a')}  template={notif.get('_templateId', 'n/a')}")


def list_topics(args):
    params = {"page": args.page}
    data = _request("get", "/topics", params=params)
    for topic in data.get("data", []):
        print(f"{YELLOW}{topic.get('key', 'n/a')}{RESET}  name={topic.get('name', 'n/a')}  subscribers={topic.get('subscribers', [])}")


def main():
    parser = argparse.ArgumentParser(description="Novu Notification Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_trigger = sub.add_parser("trigger", help="Trigger a notification workflow")
    p_trigger.add_argument("--workflow", required=True, help="Workflow/template ID")
    p_trigger.add_argument("--subscriber-id", required=True, help="Target subscriber ID")
    p_trigger.add_argument("--payload", default=None, help="JSON payload string")

    p_lsub = sub.add_parser("list-subscribers", help="List subscribers")
    p_lsub.add_argument("--page", type=int, default=0)

    p_csub = sub.add_parser("create-subscriber", help="Create a new subscriber")
    p_csub.add_argument("--subscriber-id", required=True)
    p_csub.add_argument("--email", default=None)
    p_csub.add_argument("--first-name", default=None)
    p_csub.add_argument("--last-name", default=None)

    p_lnotif = sub.add_parser("list-notifications", help="List sent notifications")
    p_lnotif.add_argument("--page", type=int, default=0)

    p_ltopic = sub.add_parser("list-topics", help="List notification topics")
    p_ltopic.add_argument("--page", type=int, default=0)

    args = parser.parse_args()
    commands = {
        "trigger": trigger,
        "list-subscribers": list_subscribers,
        "create-subscriber": create_subscriber,
        "list-notifications": list_notifications,
        "list-topics": list_topics,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
