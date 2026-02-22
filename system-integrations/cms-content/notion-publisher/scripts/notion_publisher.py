#!/usr/bin/env python3
"""Notion Page Publisher - Create and update Notion pages."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

API_KEY = os.environ.get("NOTION_API_KEY", "")
BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def get_title(page):
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            parts = prop.get("title", [])
            return parts[0].get("text", {}).get("content", "Untitled") if parts else "Untitled"
    return "Untitled"


def search_pages(args):
    body = {"query": args.query, "page_size": 25}
    resp = requests.post(f"{BASE}/search", headers=headers(), json=body)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        warn("No results found.")
        return
    for r in results:
        obj_type = r.get("object", "unknown")
        title = get_title(r) if obj_type == "page" else r.get("title", [{}])[0].get("text", {}).get("content", "Untitled") if r.get("title") else "Untitled"
        print(f"  {GREEN}{r['id']}{RESET}  [{obj_type}] {title}")


def get_page(args):
    resp = requests.get(f"{BASE}/pages/{args.page_id}", headers=headers())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def create_page(args):
    properties = json.loads(args.properties)
    body = {"parent": {"page_id": args.parent_id}, "properties": properties}
    resp = requests.post(f"{BASE}/pages", headers=headers(), json=body)
    resp.raise_for_status()
    page_id = resp.json().get("id", "unknown")
    success(f"Page created: {page_id}")


def update_page(args):
    properties = json.loads(args.properties)
    body = {"properties": properties}
    resp = requests.patch(f"{BASE}/pages/{args.page_id}", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Page '{args.page_id}' updated.")


def append_blocks(args):
    blocks = json.loads(args.blocks)
    body = {"children": blocks}
    resp = requests.patch(f"{BASE}/blocks/{args.page_id}/children", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Blocks appended to page '{args.page_id}'.")


def get_database(args):
    body = {"page_size": 25}
    resp = requests.post(f"{BASE}/databases/{args.database_id}/query", headers=headers(), json=body)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        warn("No results in database.")
        return
    for r in results:
        title = get_title(r)
        print(f"  {GREEN}{r['id']}{RESET}  {title}")


def main():
    if not API_KEY:
        fail("NOTION_API_KEY environment variable is required.")

    parser = argparse.ArgumentParser(description="Notion Page Publisher")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search pages and databases")
    p_search.add_argument("--query", required=True)

    p_get = sub.add_parser("get-page", help="Get a page")
    p_get.add_argument("--page-id", required=True)

    p_create = sub.add_parser("create-page", help="Create a page")
    p_create.add_argument("--parent-id", required=True)
    p_create.add_argument("--properties", required=True, help="JSON object of properties")

    p_update = sub.add_parser("update-page", help="Update page properties")
    p_update.add_argument("--page-id", required=True)
    p_update.add_argument("--properties", required=True, help="JSON object of properties")

    p_blocks = sub.add_parser("append-blocks", help="Append blocks to a page")
    p_blocks.add_argument("--page-id", required=True)
    p_blocks.add_argument("--blocks", required=True, help="JSON array of block objects")

    p_db = sub.add_parser("get-database", help="Query a database")
    p_db.add_argument("--database-id", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"search": search_pages,
         "get-page": get_page,
         "create-page": create_page,
         "update-page": update_page,
         "append-blocks": append_blocks,
         "get-database": get_database}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
