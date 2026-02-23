#!/usr/bin/env python3
"""Strapi API Client - Manage dynamic content types."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

STRAPI_URL = os.environ.get("STRAPI_URL", "").rstrip("/")
API_TOKEN = os.environ.get("STRAPI_API_TOKEN", "")


def headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_content_types(args):
    resp = requests.get(f"{STRAPI_URL}/api/content-type-builder/content-types", headers=headers())
    resp.raise_for_status()
    types = resp.json().get("data", [])
    if not types:
        warn("No content types found.")
        return
    for ct in types:
        uid = ct.get("uid", "N/A")
        if uid.startswith("api::"):
            print(f"  {GREEN}{uid}{RESET}")


def list_entries(args):
    resp = requests.get(f"{STRAPI_URL}/api/{args.type}", headers=headers())
    resp.raise_for_status()
    items = resp.json().get("data", [])
    if not items:
        warn("No entries found.")
        return
    for item in items:
        eid = item.get("id", "N/A")
        attrs = item.get("attributes", {})
        label = attrs.get("title", attrs.get("name", str(eid)))
        print(f"  {GREEN}{eid}{RESET}  {label}")


def get_entry(args):
    resp = requests.get(f"{STRAPI_URL}/api/{args.type}/{args.id}", headers=headers())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def create_entry(args):
    data = json.loads(args.data)
    resp = requests.post(f"{STRAPI_URL}/api/{args.type}", headers=headers(), json={"data": data})
    resp.raise_for_status()
    eid = resp.json().get("data", {}).get("id", "unknown")
    success(f"Entry created: {eid}")


def update_entry(args):
    data = json.loads(args.data)
    resp = requests.put(f"{STRAPI_URL}/api/{args.type}/{args.id}", headers=headers(), json={"data": data})
    resp.raise_for_status()
    success(f"Entry '{args.id}' updated.")


def delete_entry(args):
    resp = requests.delete(f"{STRAPI_URL}/api/{args.type}/{args.id}", headers=headers())
    resp.raise_for_status()
    success(f"Entry '{args.id}' deleted.")


def main():
    if not STRAPI_URL or not API_TOKEN:
        fail("STRAPI_URL and STRAPI_API_TOKEN environment variables are required.")

    parser = argparse.ArgumentParser(description="Strapi API Client")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-content-types", help="List content types")

    p_list = sub.add_parser("list-entries", help="List entries")
    p_list.add_argument("--type", required=True)

    p_get = sub.add_parser("get-entry", help="Get an entry")
    p_get.add_argument("--type", required=True)
    p_get.add_argument("--id", required=True)

    p_create = sub.add_parser("create", help="Create an entry")
    p_create.add_argument("--type", required=True)
    p_create.add_argument("--data", required=True, help="JSON object of fields")

    p_update = sub.add_parser("update", help="Update an entry")
    p_update.add_argument("--type", required=True)
    p_update.add_argument("--id", required=True)
    p_update.add_argument("--data", required=True, help="JSON object of fields")

    p_del = sub.add_parser("delete", help="Delete an entry")
    p_del.add_argument("--type", required=True)
    p_del.add_argument("--id", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-content-types": list_content_types,
         "list-entries": list_entries,
         "get-entry": get_entry,
         "create": create_entry,
         "update": update_entry,
         "delete": delete_entry}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
