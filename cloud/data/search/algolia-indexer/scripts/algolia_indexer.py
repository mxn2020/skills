#!/usr/bin/env python3
"""Algolia Indexer - Push content updates to search indices."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

APP_ID = os.environ.get("ALGOLIA_APP_ID", "")
API_KEY = os.environ.get("ALGOLIA_API_KEY", "")


def base_url():
    return f"https://{APP_ID}-dsn.algolia.net/1"


def headers():
    return {
        "X-Algolia-Application-Id": APP_ID,
        "X-Algolia-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_indices():
    resp = requests.get(f"{base_url()}/indexes", headers=headers())
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        warn("No indices found.")
        return
    for idx in items:
        print(f"  {GREEN}{idx['name']}{RESET}  entries={idx.get('entries', 0)}")


def search(args):
    body = {"query": args.query}
    resp = requests.post(f"{base_url()}/indexes/{args.index}/query", headers=headers(), json=body)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])
    if not hits:
        warn("No results found.")
        return
    for hit in hits:
        oid = hit.get("objectID", "N/A")
        snippet = {k: v for k, v in hit.items() if k not in ("objectID", "_highlightResult", "_snippetResult")}
        print(f"  {GREEN}{oid}{RESET}: {json.dumps(snippet, default=str)[:120]}")


def add_records(args):
    records = json.loads(args.records)
    body = {"requests": [{"action": "addObject", "body": r} for r in records]}
    resp = requests.post(f"{base_url()}/indexes/{args.index}/batch", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Added {len(records)} record(s) to '{args.index}'.")


def delete_record(args):
    resp = requests.delete(f"{base_url()}/indexes/{args.index}/{args.object_id}", headers=headers())
    resp.raise_for_status()
    success(f"Deleted record '{args.object_id}' from '{args.index}'.")


def get_settings(args):
    resp = requests.get(f"{base_url()}/indexes/{args.index}/settings", headers=headers())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def set_settings(args):
    settings = json.loads(args.settings)
    resp = requests.put(f"{base_url()}/indexes/{args.index}/settings", headers=headers(), json=settings)
    resp.raise_for_status()
    success(f"Settings updated for '{args.index}'.")


def main():
    if not APP_ID or not API_KEY:
        fail("ALGOLIA_APP_ID and ALGOLIA_API_KEY environment variables are required.")

    parser = argparse.ArgumentParser(description="Algolia Indexer")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-indices", help="List all indices")

    p_s = sub.add_parser("search", help="Search an index")
    p_s.add_argument("--index", required=True)
    p_s.add_argument("--query", required=True)

    p_add = sub.add_parser("add-records", help="Add records")
    p_add.add_argument("--index", required=True)
    p_add.add_argument("--records", required=True, help="JSON array of records")

    p_del = sub.add_parser("delete-record", help="Delete a record")
    p_del.add_argument("--index", required=True)
    p_del.add_argument("--object-id", required=True)

    p_gs = sub.add_parser("get-settings", help="Get index settings")
    p_gs.add_argument("--index", required=True)

    p_ss = sub.add_parser("set-settings", help="Update index settings")
    p_ss.add_argument("--index", required=True)
    p_ss.add_argument("--settings", required=True, help="JSON object of settings")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-indices": lambda a: list_indices(),
         "search": search,
         "add-records": add_records,
         "delete-record": delete_record,
         "get-settings": get_settings,
         "set-settings": set_settings}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
