#!/usr/bin/env python3
"""PostHog Feature Flag Manager – OC-0055"""

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
    url = os.environ.get("POSTHOG_URL")
    key = os.environ.get("POSTHOG_API_KEY")
    if not url or not key:
        print(f"{RED}Error: POSTHOG_URL and POSTHOG_API_KEY must be set{RESET}")
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


def list_flags(args):
    data = _request("get", "/api/feature_flag/")
    for flag in data.get("results", []):
        active = flag.get("active", False)
        color = GREEN if active else YELLOW
        status = "active" if active else "inactive"
        print(f"{color}[{status}]{RESET} {flag['id']}  key={flag.get('key', 'n/a')}  rollout={flag.get('rollout_percentage', 'n/a')}")


def create_flag(args):
    payload = {
        "key": args.key,
        "name": args.name or args.key,
        "active": True,
        "filters": {
            "groups": [{"rollout_percentage": args.rollout}],
        },
    }
    data = _request("post", "/api/feature_flag/", json=payload)
    print(f"{GREEN}Created flag {data.get('id')}: {data.get('key')}{RESET}")


def update_flag(args):
    payload = {}
    if args.active is not None:
        payload["active"] = args.active.lower() == "true"
    if args.rollout is not None:
        payload["filters"] = {"groups": [{"rollout_percentage": args.rollout}]}
    _request("patch", f"/api/feature_flag/{args.flag_id}/", json=payload)
    print(f"{GREEN}Updated flag {args.flag_id}{RESET}")


def delete_flag(args):
    _request("delete", f"/api/feature_flag/{args.flag_id}/")
    print(f"{GREEN}Deleted flag {args.flag_id}{RESET}")


def evaluate(args):
    url, key = _config()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    resp = requests.post(
        f"{url}/decide/?v=3",
        headers=headers,
        json={"api_key": key, "distinct_id": args.distinct_id},
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    flags = data.get("featureFlags", {})
    if args.key in flags:
        value = flags[args.key]
        color = GREEN if value else YELLOW
        print(f"{color}{args.key} = {value}{RESET}")
    else:
        print(f"{YELLOW}{args.key} not found in evaluation{RESET}")


def main():
    parser = argparse.ArgumentParser(description="PostHog Feature Flag Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-flags", help="List feature flags")

    p_create = sub.add_parser("create-flag", help="Create a feature flag")
    p_create.add_argument("--key", required=True, help="Flag key")
    p_create.add_argument("--name", help="Display name")
    p_create.add_argument("--rollout", type=int, default=100, help="Rollout percentage")

    p_update = sub.add_parser("update-flag", help="Update a feature flag")
    p_update.add_argument("--flag-id", required=True)
    p_update.add_argument("--active", help="true or false")
    p_update.add_argument("--rollout", type=int, help="Rollout percentage")

    p_delete = sub.add_parser("delete-flag", help="Delete a feature flag")
    p_delete.add_argument("--flag-id", required=True)

    p_eval = sub.add_parser("evaluate", help="Evaluate flag for a user")
    p_eval.add_argument("--key", required=True, help="Flag key")
    p_eval.add_argument("--distinct-id", required=True, help="User distinct ID")

    args = parser.parse_args()
    commands = {
        "list-flags": list_flags,
        "create-flag": create_flag,
        "update-flag": update_flag,
        "delete-flag": delete_flag,
        "evaluate": evaluate,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
