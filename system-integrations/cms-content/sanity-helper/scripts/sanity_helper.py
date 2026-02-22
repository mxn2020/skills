#!/usr/bin/env python3
"""Sanity Studio Helper - Trigger webhooks or clear datasets."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "")
TOKEN = os.environ.get("SANITY_TOKEN", "")
DATASET = os.environ.get("SANITY_DATASET", "production")
API_VERSION = "2024-01-01"
BASE = f"https://{PROJECT_ID}.api.sanity.io/v{API_VERSION}"


def headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_documents(args):
    query = f'*[_type == "{args.type}"]' if args.type else "*[]"
    query += "[0...25]{_id, _type, _updatedAt}"
    params = {"query": query}
    resp = requests.get(f"{BASE}/data/query/{DATASET}", headers=headers(), params=params)
    resp.raise_for_status()
    docs = resp.json().get("result", [])
    if not docs:
        warn("No documents found.")
        return
    for d in docs:
        print(f"  {GREEN}{d['_id']}{RESET}  type={d.get('_type', 'N/A')}")


def get_document(args):
    resp = requests.get(f"{BASE}/data/doc/{DATASET}/{args.id}", headers=headers())
    resp.raise_for_status()
    docs = resp.json().get("documents", [])
    if not docs:
        warn("Document not found.")
        return
    print(json.dumps(docs[0], indent=2))


def create_document(args):
    doc = json.loads(args.doc)
    body = {"mutations": [{"create": doc}]}
    resp = requests.post(f"{BASE}/data/mutate/{DATASET}", headers=headers(), json=body)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    doc_id = results[0]["id"] if results else "unknown"
    success(f"Document created: {doc_id}")


def patch_document(args):
    set_fields = json.loads(args.set)
    body = {"mutations": [{"patch": {"id": args.id, "set": set_fields}}]}
    resp = requests.post(f"{BASE}/data/mutate/{DATASET}", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Document '{args.id}' patched.")


def delete_document(args):
    body = {"mutations": [{"delete": {"id": args.id}}]}
    resp = requests.post(f"{BASE}/data/mutate/{DATASET}", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Document '{args.id}' deleted.")


def trigger_webhook(args):
    resp = requests.post(args.url, headers={"Content-Type": "application/json"}, json={})
    resp.raise_for_status()
    success(f"Webhook triggered: {args.url}")


def main():
    if not PROJECT_ID or not TOKEN:
        fail("SANITY_PROJECT_ID and SANITY_TOKEN environment variables are required.")

    parser = argparse.ArgumentParser(description="Sanity Studio Helper")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list-documents", help="List documents")
    p_list.add_argument("--type", default=None)

    p_get = sub.add_parser("get-document", help="Get a document")
    p_get.add_argument("--id", required=True)

    p_create = sub.add_parser("create", help="Create a document")
    p_create.add_argument("--doc", required=True, help="JSON document object")

    p_patch = sub.add_parser("patch", help="Patch a document")
    p_patch.add_argument("--id", required=True)
    p_patch.add_argument("--set", required=True, help="JSON object of fields to set")

    p_del = sub.add_parser("delete", help="Delete a document")
    p_del.add_argument("--id", required=True)

    p_wh = sub.add_parser("trigger-webhook", help="Trigger a deploy webhook")
    p_wh.add_argument("--url", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-documents": list_documents,
         "get-document": get_document,
         "create": create_document,
         "patch": patch_document,
         "delete": delete_document,
         "trigger-webhook": trigger_webhook}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
