#!/usr/bin/env python3
"""Webflow CMS Updater - Push collection item changes."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

API_TOKEN = os.environ.get("WEBFLOW_API_TOKEN", "")
BASE = "https://api.webflow.com/v2"


def headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_sites(args):
    resp = requests.get(f"{BASE}/sites", headers=headers())
    resp.raise_for_status()
    sites = resp.json().get("sites", [])
    if not sites:
        warn("No sites found.")
        return
    for s in sites:
        print(f"  {GREEN}{s['id']}{RESET}  {s.get('displayName', s.get('name', 'N/A'))}")


def list_collections(args):
    resp = requests.get(f"{BASE}/sites/{args.site_id}/collections", headers=headers())
    resp.raise_for_status()
    cols = resp.json().get("collections", [])
    if not cols:
        warn("No collections found.")
        return
    for c in cols:
        print(f"  {GREEN}{c['id']}{RESET}  {c.get('displayName', c.get('name', 'N/A'))}")


def list_items(args):
    resp = requests.get(f"{BASE}/collections/{args.collection_id}/items", headers=headers())
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        warn("No items found.")
        return
    for item in items:
        name = item.get("fieldData", {}).get("name", item.get("id"))
        print(f"  {GREEN}{item['id']}{RESET}  {name}")


def create_item(args):
    fields = json.loads(args.fields)
    body = {"fieldData": fields}
    resp = requests.post(f"{BASE}/collections/{args.collection_id}/items", headers=headers(), json=body)
    resp.raise_for_status()
    item_id = resp.json().get("id", "unknown")
    success(f"Item created: {item_id}")


def update_item(args):
    fields = json.loads(args.fields)
    body = {"fieldData": fields}
    resp = requests.patch(
        f"{BASE}/collections/{args.collection_id}/items/{args.item_id}",
        headers=headers(), json=body,
    )
    resp.raise_for_status()
    success(f"Item '{args.item_id}' updated.")


def publish_site(args):
    body = {}
    if args.domains:
        body["domains"] = json.loads(args.domains)
    resp = requests.post(f"{BASE}/sites/{args.site_id}/publish", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Site '{args.site_id}' published.")


def main():
    if not API_TOKEN:
        fail("WEBFLOW_API_TOKEN environment variable is required.")

    parser = argparse.ArgumentParser(description="Webflow CMS Updater")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-sites", help="List sites")

    p_cols = sub.add_parser("list-collections", help="List collections")
    p_cols.add_argument("--site-id", required=True)

    p_items = sub.add_parser("list-items", help="List items")
    p_items.add_argument("--collection-id", required=True)

    p_create = sub.add_parser("create-item", help="Create an item")
    p_create.add_argument("--collection-id", required=True)
    p_create.add_argument("--fields", required=True, help="JSON object of field data")

    p_update = sub.add_parser("update-item", help="Update an item")
    p_update.add_argument("--collection-id", required=True)
    p_update.add_argument("--item-id", required=True)
    p_update.add_argument("--fields", required=True, help="JSON object of field data")

    p_pub = sub.add_parser("publish", help="Publish site")
    p_pub.add_argument("--site-id", required=True)
    p_pub.add_argument("--domains", default=None, help="JSON array of domains (optional)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-sites": list_sites,
         "list-collections": list_collections,
         "list-items": list_items,
         "create-item": create_item,
         "update-item": update_item,
         "publish": publish_site}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
