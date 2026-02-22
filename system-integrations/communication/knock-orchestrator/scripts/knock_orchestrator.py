#!/usr/bin/env python3
"""Knock Notification Orchestrator – OC-0080"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.knock.app/v1"


def _headers():
    token = os.environ.get("KNOCK_API_KEY")
    if not token:
        print(f"{RED}Error: KNOCK_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def trigger_workflow(args):
    payload = {"recipients": args.recipients}
    if args.data:
        payload["data"] = json.loads(args.data)
    data = _request("post", f"/workflows/{args.workflow_key}/trigger", json=payload)
    run_id = data.get("workflow_run_id", "n/a")
    print(f"{GREEN}Triggered workflow '{args.workflow_key}' for {len(args.recipients)} recipient(s){RESET}")
    print(f"  Run ID: {run_id}")


def list_workflows(args):
    data = _request("get", "/workflows")
    entries = data if isinstance(data, list) else data.get("entries", data.get("items", []))
    for wf in entries:
        status = wf.get("active", True)
        color = GREEN if status else YELLOW
        print(f"{color}[{'active' if status else 'inactive'}]{RESET} {wf.get('key', 'n/a')}  {wf.get('name', '')}")


def get_message(args):
    data = _request("get", f"/messages/{args.message_id}")
    print(f"{GREEN}Message {data.get('id', 'n/a')}{RESET}")
    print(f"  Channel:  {data.get('channel_id', 'n/a')}")
    print(f"  Status:   {data.get('status', 'n/a')}")
    print(f"  Workflow: {data.get('workflow', 'n/a')}")
    print(f"  Inserted: {data.get('inserted_at', 'n/a')}")


def list_messages(args):
    params = {}
    if args.status:
        params["status"] = args.status
    data = _request("get", "/messages", params=params)
    entries = data if isinstance(data, list) else data.get("entries", data.get("items", []))
    for msg in entries:
        status = msg.get("status", "unknown")
        color = GREEN if status == "delivered" else YELLOW
        print(f"{color}[{status}]{RESET} {msg.get('id', 'n/a')}  workflow={msg.get('workflow', 'n/a')}")


def identify_user(args):
    payload = {}
    if args.name:
        payload["name"] = args.name
    if args.email:
        payload["email"] = args.email
    data = _request("put", f"/users/{args.user_id}", json=payload)
    print(f"{GREEN}Identified user {data.get('id', args.user_id)}{RESET}")
    print(f"  Name:  {data.get('name', 'n/a')}")
    print(f"  Email: {data.get('email', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Knock Notification Orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_trigger = sub.add_parser("trigger-workflow", help="Trigger a notification workflow")
    p_trigger.add_argument("--workflow-key", required=True, help="Workflow key to trigger")
    p_trigger.add_argument("--recipients", nargs="+", required=True, help="Recipient user IDs")
    p_trigger.add_argument("--data", default=None, help="JSON string of additional data")

    sub.add_parser("list-workflows", help="List available workflows")

    p_get_msg = sub.add_parser("get-message", help="Get message details")
    p_get_msg.add_argument("--message-id", required=True)

    p_list_msg = sub.add_parser("list-messages", help="List messages")
    p_list_msg.add_argument("--status", default=None, help="Filter by status")

    p_user = sub.add_parser("identify-user", help="Identify or create a user")
    p_user.add_argument("--user-id", required=True)
    p_user.add_argument("--name", default=None)
    p_user.add_argument("--email", default=None)

    args = parser.parse_args()
    commands = {
        "trigger-workflow": trigger_workflow,
        "list-workflows": list_workflows,
        "get-message": get_message,
        "list-messages": list_messages,
        "identify-user": identify_user,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
