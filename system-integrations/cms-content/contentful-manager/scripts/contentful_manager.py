#!/usr/bin/env python3
"""Contentful Entry Manager - Publish or archive content entries."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SPACE_ID = os.environ.get("CONTENTFUL_SPACE_ID", "")
TOKEN = os.environ.get("CONTENTFUL_MANAGEMENT_TOKEN", "")
BASE = f"https://api.contentful.com/spaces/{SPACE_ID}/environments/master"


def headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def get_version(entry_id):
    resp = requests.get(f"{BASE}/entries/{entry_id}", headers=headers())
    resp.raise_for_status()
    return resp.json()["sys"]["version"]


def list_entries(args):
    params = {"limit": 25}
    if args.content_type:
        params["content_type"] = args.content_type
    resp = requests.get(f"{BASE}/entries", headers=headers(), params=params)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        warn("No entries found.")
        return
    for e in items:
        eid = e["sys"]["id"]
        ct = e["sys"].get("contentType", {}).get("sys", {}).get("id", "unknown")
        print(f"  {GREEN}{eid}{RESET}  type={ct}")


def get_entry(args):
    resp = requests.get(f"{BASE}/entries/{args.entry_id}", headers=headers())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def publish(args):
    version = get_version(args.entry_id)
    h = headers()
    h["X-Contentful-Version"] = str(version)
    resp = requests.put(f"{BASE}/entries/{args.entry_id}/published", headers=h)
    resp.raise_for_status()
    success(f"Entry '{args.entry_id}' published.")


def unpublish(args):
    h = headers()
    resp = requests.delete(f"{BASE}/entries/{args.entry_id}/published", headers=h)
    resp.raise_for_status()
    success(f"Entry '{args.entry_id}' unpublished.")


def archive(args):
    version = get_version(args.entry_id)
    h = headers()
    h["X-Contentful-Version"] = str(version)
    resp = requests.put(f"{BASE}/entries/{args.entry_id}/archived", headers=h)
    resp.raise_for_status()
    success(f"Entry '{args.entry_id}' archived.")


def create_entry(args):
    fields = json.loads(args.fields)
    h = headers()
    h["X-Contentful-Content-Type"] = args.content_type
    resp = requests.post(f"{BASE}/entries", headers=h, json={"fields": fields})
    resp.raise_for_status()
    eid = resp.json()["sys"]["id"]
    success(f"Entry created: {eid}")


def main():
    if not SPACE_ID or not TOKEN:
        fail("CONTENTFUL_SPACE_ID and CONTENTFUL_MANAGEMENT_TOKEN are required.")

    parser = argparse.ArgumentParser(description="Contentful Entry Manager")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list-entries", help="List entries")
    p_list.add_argument("--content-type", default=None)

    p_get = sub.add_parser("get-entry", help="Get an entry")
    p_get.add_argument("--entry-id", required=True)

    p_pub = sub.add_parser("publish", help="Publish an entry")
    p_pub.add_argument("--entry-id", required=True)

    p_unpub = sub.add_parser("unpublish", help="Unpublish an entry")
    p_unpub.add_argument("--entry-id", required=True)

    p_arch = sub.add_parser("archive", help="Archive an entry")
    p_arch.add_argument("--entry-id", required=True)

    p_create = sub.add_parser("create-entry", help="Create a new entry")
    p_create.add_argument("--content-type", required=True)
    p_create.add_argument("--fields", required=True, help="JSON object of fields")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-entries": list_entries,
         "get-entry": get_entry,
         "publish": publish,
         "unpublish": unpublish,
         "archive": archive,
         "create-entry": create_entry}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
