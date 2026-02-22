#!/usr/bin/env python3
"""Zotero Manager - Manage Zotero library collections, items, and bibliographies."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

ZOTERO_API_KEY = os.environ.get("ZOTERO_API_KEY", "")
ZOTERO_USER_ID = os.environ.get("ZOTERO_USER_ID", "")
ZOTERO_BASE = "https://api.zotero.org"


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _check_env():
    if not ZOTERO_API_KEY or not ZOTERO_USER_ID:
        fail("ZOTERO_API_KEY and ZOTERO_USER_ID environment variables are required.")


def _headers(accept="application/json"):
    return {
        "Zotero-API-Key": ZOTERO_API_KEY,
        "Zotero-API-Version": "3",
        "Accept": accept,
    }


def _request(method, path, params=None, payload=None, accept="application/json"):
    url = f"{ZOTERO_BASE}/users/{ZOTERO_USER_ID}/{path}"
    resp = requests.request(
        method, url,
        headers=_headers(accept),
        params=params,
        json=payload,
        timeout=20
    )
    resp.raise_for_status()
    if accept == "application/json" and resp.text.strip():
        return resp.json()
    return resp.text


def list_collections(args):
    data = _request("GET", "collections")
    if not data:
        warn("No collections found.")
        return
    print(f"\n{GREEN}Zotero Collections:{RESET}\n")
    for col in data:
        key = col.get("key", "")
        name = col.get("data", {}).get("name", "")
        num_items = col.get("meta", {}).get("numItems", 0)
        print(f"  {YELLOW}{key}{RESET}  {name}  ({num_items} items)")
    print()


def add_item(args):
    item_data = {
        "itemType": args.item_type or "webpage",
        "title": args.title,
        "url": args.url or "",
        "date": str(args.year) if args.year else "",
        "collections": [args.collection_key] if args.collection_key else [],
    }
    if args.authors:
        creators = []
        for author in args.authors.split(";"):
            author = author.strip()
            parts = author.split(",")
            if len(parts) >= 2:
                creators.append({
                    "creatorType": "author",
                    "lastName": parts[0].strip(),
                    "firstName": parts[1].strip(),
                })
            else:
                creators.append({"creatorType": "author", "name": author})
        item_data["creators"] = creators

    payload = [item_data]
    data = _request("POST", "items", payload=payload)
    if data and "successful" in data:
        for k, v in data["successful"].items():
            success(f"Item added: key={v.get('key', '')} title={args.title}")
    else:
        warn(f"Response: {json.dumps(data, indent=2)}")


def search_items(args):
    params = {"q": args.query}
    if args.collection_key:
        path = f"collections/{args.collection_key}/items"
    else:
        path = "items"
    data = _request("GET", path, params=params)
    if not data:
        warn("No items found.")
        return
    print(f"\n{GREEN}Search results for '{args.query}':{RESET}\n")
    for item in data:
        d = item.get("data", {})
        key = item.get("key", "")
        title = d.get("title", "N/A")
        item_type = d.get("itemType", "")
        date = d.get("date", "")
        print(f"  {YELLOW}{key}{RESET}  [{item_type}] {title}  ({date})")
    print()


def export_bibliography(args):
    if not args.collection_key:
        fail("--collection-key is required for export-bibliography.")
    fmt = args.format or "bibtex"
    accept_map = {
        "bibtex": "application/x-bibtex",
        "ris": "application/x-research-info-systems",
        "chicago": "text/x-bibliography; style=chicago-note-bibliography",
        "apa": "text/x-bibliography; style=apa",
    }
    accept = accept_map.get(fmt, "application/x-bibtex")
    path = f"collections/{args.collection_key}/items"
    params = {"format": fmt if fmt in ("bibtex", "ris") else "bib",
              "style": fmt if fmt in ("chicago", "apa") else None}
    params = {k: v for k, v in params.items() if v}

    text = _request("GET", path, params=params, accept=accept)
    out_file = f"bibliography_{args.collection_key}.{fmt}"
    with open(out_file, "w") as f:
        f.write(text if isinstance(text, str) else json.dumps(text, indent=2))
    success(f"Bibliography exported to: {out_file}")


def get_item(args):
    data = _request("GET", f"items/{args.item_key}")
    d = data.get("data", {})
    print(f"\n{GREEN}Item: {d.get('title', 'N/A')}{RESET}\n")
    print(f"  Key:       {data.get('key', '')}")
    print(f"  Type:      {d.get('itemType', '')}")
    print(f"  Date:      {d.get('date', '')}")
    print(f"  URL:       {d.get('url', '')}")
    creators = d.get("creators", [])
    if creators:
        author_names = []
        for c in creators:
            if "lastName" in c:
                author_names.append(f"{c['lastName']}, {c.get('firstName', '')}")
            else:
                author_names.append(c.get("name", ""))
        print(f"  Authors:   {'; '.join(author_names)}")
    print(f"  Abstract:  {d.get('abstractNote', '')[:200]}")
    tags = d.get("tags", [])
    if tags:
        print(f"  Tags:      {', '.join(t['tag'] for t in tags)}")
    print()


def main():
    _check_env()
    parser = argparse.ArgumentParser(description="Zotero Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-collections", help="List all Zotero collections")

    p_add = sub.add_parser("add-item", help="Add a new item to the library")
    p_add.add_argument("--title", required=True, help="Item title")
    p_add.add_argument("--url", help="Item URL")
    p_add.add_argument("--authors", help="Authors (semicolon-separated, format: Last, First)")
    p_add.add_argument("--year", help="Publication year")
    p_add.add_argument("--item-type", default="webpage",
                       choices=["webpage", "journalArticle", "book", "conferencePaper", "report"],
                       help="Item type")
    p_add.add_argument("--collection-key", help="Collection key to add item to")

    p_search = sub.add_parser("search-items", help="Search items in library")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--collection-key", help="Limit search to a collection")

    p_exp = sub.add_parser("export-bibliography", help="Export bibliography for a collection")
    p_exp.add_argument("--collection-key", required=True, help="Collection key")
    p_exp.add_argument("--format", default="bibtex",
                       choices=["bibtex", "ris", "chicago", "apa"], help="Export format")

    p_get = sub.add_parser("get-item", help="Get details of a specific item")
    p_get.add_argument("--item-key", required=True, help="Item key")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        dispatch = {
            "list-collections": list_collections,
            "add-item": add_item,
            "search-items": search_items,
            "export-bibliography": export_bibliography,
            "get-item": get_item,
        }
        dispatch[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text[:200]}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
