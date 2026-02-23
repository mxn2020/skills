#!/usr/bin/env python3
"""MeiliSearch Settings - Configure ranking rules, stop words, and indexes."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

MEILI_URL = os.environ.get("MEILISEARCH_URL", "http://localhost:7700")
API_KEY = os.environ.get("MEILISEARCH_API_KEY", "")


def headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_indexes():
    resp = requests.get(f"{MEILI_URL}/indexes", headers=headers())
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", data) if isinstance(data, dict) else data
    if not results:
        warn("No indexes found.")
        return
    for idx in results:
        print(f"  {GREEN}{idx['uid']}{RESET}  primaryKey={idx.get('primaryKey', 'N/A')}")


def create_index(args):
    body = {"uid": args.uid}
    if args.primary_key:
        body["primaryKey"] = args.primary_key
    resp = requests.post(f"{MEILI_URL}/indexes", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Index '{args.uid}' creation task enqueued.")


def search(args):
    body = {"q": args.query}
    resp = requests.post(f"{MEILI_URL}/indexes/{args.uid}/search", headers=headers(), json=body)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])
    if not hits:
        warn("No results found.")
        return
    for hit in hits:
        print(f"  {json.dumps(hit, default=str)[:150]}")


def get_settings(args):
    resp = requests.get(f"{MEILI_URL}/indexes/{args.uid}/settings", headers=headers())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def update_settings(args):
    settings = json.loads(args.settings)
    resp = requests.patch(f"{MEILI_URL}/indexes/{args.uid}/settings", headers=headers(), json=settings)
    resp.raise_for_status()
    success(f"Settings update enqueued for index '{args.uid}'.")


def add_documents(args):
    documents = json.loads(args.documents)
    resp = requests.post(f"{MEILI_URL}/indexes/{args.uid}/documents", headers=headers(), json=documents)
    resp.raise_for_status()
    count = len(documents) if isinstance(documents, list) else 1
    success(f"Enqueued {count} document(s) for indexing in '{args.uid}'.")


def main():
    parser = argparse.ArgumentParser(description="MeiliSearch Settings Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-indexes", help="List all indexes")

    p_create = sub.add_parser("create-index", help="Create an index")
    p_create.add_argument("--uid", required=True)
    p_create.add_argument("--primary-key", default=None)

    p_s = sub.add_parser("search", help="Search an index")
    p_s.add_argument("--uid", required=True)
    p_s.add_argument("--query", required=True)

    p_gs = sub.add_parser("get-settings", help="Get settings")
    p_gs.add_argument("--uid", required=True)

    p_us = sub.add_parser("update-settings", help="Update settings")
    p_us.add_argument("--uid", required=True)
    p_us.add_argument("--settings", required=True, help="JSON object of settings")

    p_ad = sub.add_parser("add-documents", help="Add documents")
    p_ad.add_argument("--uid", required=True)
    p_ad.add_argument("--documents", required=True, help="JSON array of documents")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-indexes": lambda a: list_indexes(),
         "create-index": create_index,
         "search": search,
         "get-settings": get_settings,
         "update-settings": update_settings,
         "add-documents": add_documents}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
