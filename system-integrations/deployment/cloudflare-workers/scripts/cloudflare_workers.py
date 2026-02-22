#!/usr/bin/env python3
"""Cloudflare Worker Manager – OC-0018"""

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

BASE_URL = "https://api.cloudflare.com/client/v4"


def _headers():
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print(f"{RED}Error: CLOUDFLARE_API_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _account_id():
    aid = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not aid:
        print(f"{RED}Error: CLOUDFLARE_ACCOUNT_ID is not set{RESET}")
        sys.exit(1)
    return aid


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def list_workers(args):
    data = _request("get", f"/accounts/{_account_id()}/workers/scripts")
    for w in data.get("result", []):
        print(f"{GREEN}{w['id']}{RESET}  modified={w.get('modified_on', 'n/a')}")


def deploy(args):
    with open(args.script, "r") as f:
        script_content = f.read()
    headers = _headers()
    headers["Content-Type"] = "application/javascript"
    resp = requests.put(
        f"{BASE_URL}/accounts/{_account_id()}/workers/scripts/{args.name}",
        headers=headers,
        data=script_content,
    )
    if not resp.ok:
        print(f"{RED}Deploy failed ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Worker '{args.name}' deployed successfully{RESET}")


def get_worker(args):
    data = _request("get", f"/accounts/{_account_id()}/workers/scripts/{args.name}")
    result = data.get("result", {})
    print(f"{GREEN}{args.name}{RESET}")
    print(f"  Modified: {result.get('modified_on', 'n/a')}")
    print(f"  Created:  {result.get('created_on', 'n/a')}")
    print(f"  ETag:     {result.get('etag', 'n/a')}")


def delete(args):
    _request("delete", f"/accounts/{_account_id()}/workers/scripts/{args.name}")
    print(f"{GREEN}Worker '{args.name}' deleted{RESET}")


def tail_logs(args):
    print(f"{YELLOW}Starting log tail for '{args.name}' (Ctrl+C to stop)...{RESET}")
    # Create a tail
    data = _request("post", f"/accounts/{_account_id()}/workers/scripts/{args.name}/tails")
    tail_id = data.get("result", {}).get("id")
    tail_url = data.get("result", {}).get("url")
    if not tail_url:
        print(f"{RED}Could not create tail session{RESET}")
        sys.exit(1)
    print(f"{GREEN}Tail URL: {tail_url}{RESET}")
    print(f"Connect via WebSocket to stream logs. Tail ID: {tail_id}")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare Worker Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-workers", help="List workers")

    p_deploy = sub.add_parser("deploy", help="Deploy worker")
    p_deploy.add_argument("--name", required=True)
    p_deploy.add_argument("--script", required=True, help="Path to JS file")

    p_get = sub.add_parser("get-worker", help="Get worker metadata")
    p_get.add_argument("--name", required=True)

    p_del = sub.add_parser("delete", help="Delete worker")
    p_del.add_argument("--name", required=True)

    p_tail = sub.add_parser("tail-logs", help="Tail worker logs")
    p_tail.add_argument("--name", required=True)

    args = parser.parse_args()
    commands = {
        "list-workers": list_workers,
        "deploy": deploy,
        "get-worker": get_worker,
        "delete": delete,
        "tail-logs": tail_logs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
