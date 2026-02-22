#!/usr/bin/env python3
"""
Supabase Table Editor - Run safe read/write operations on Supabase tables.
Uses Supabase PostgREST API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_config():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url:
        print(f"{RED}Error: SUPABASE_URL environment variable not set.{RESET}")
        sys.exit(1)
    if not key:
        print(f"{RED}Error: SUPABASE_SERVICE_KEY environment variable not set.{RESET}")
        sys.exit(1)
    return url.rstrip("/"), key


def api_request(method, endpoint, key, base_url, params=None, json_data=None, headers_extra=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}", "apikey": key, "Content-Type": "application/json"}
    if headers_extra:
        headers.update(headers_extra)
    url = f"{base_url}/rest/v1{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp


def list_tables():
    base_url, key = get_config()
    print(f"{YELLOW}Listing tables...{RESET}")

    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    resp = requests.get(f"{base_url}/rest/v1/", headers=headers, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)

    # OpenAPI spec lists paths as table names
    spec = resp.json()
    paths = spec.get("paths", {})
    tables = [p.lstrip("/") for p in paths if p != "/"]
    print(f"{GREEN}Found {len(tables)} tables:{RESET}")
    for t in sorted(tables):
        print(f"  {t}")


def query(table, select="*", filt=None, order=None, limit=50):
    base_url, key = get_config()
    print(f"{YELLOW}Querying '{table}'...{RESET}")

    params = {"select": select, "limit": limit}
    if filt:
        col, rest = filt.split("=", 1)
        params[col] = rest
    if order:
        params["order"] = order

    resp = api_request("GET", f"/{table}", key, base_url, params=params,
                       headers_extra={"Prefer": "count=exact"})
    rows = resp.json()
    count = resp.headers.get("content-range", "?")
    print(f"{GREEN}Returned {len(rows)} rows (range: {count}):{RESET}")
    for row in rows:
        print(f"  {json.dumps(row, default=str)}")


def insert(table, data):
    base_url, key = get_config()
    print(f"{YELLOW}Inserting into '{table}'...{RESET}")

    parsed = json.loads(data)
    resp = api_request("POST", f"/{table}", key, base_url, json_data=parsed,
                       headers_extra={"Prefer": "return=representation"})
    result = resp.json()
    print(f"{GREEN}Inserted:{RESET}")
    print(f"  {json.dumps(result, default=str)}")


def update(table, filt, data):
    base_url, key = get_config()
    print(f"{YELLOW}Updating '{table}' where {filt}...{RESET}")

    parsed = json.loads(data)
    col, rest = filt.split("=", 1)
    params = {col: rest}
    resp = api_request("PATCH", f"/{table}", key, base_url, params=params, json_data=parsed,
                       headers_extra={"Prefer": "return=representation"})
    result = resp.json()
    print(f"{GREEN}Updated {len(result)} rows:{RESET}")
    for row in result:
        print(f"  {json.dumps(row, default=str)}")


def delete(table, filt):
    base_url, key = get_config()
    print(f"{YELLOW}Deleting from '{table}' where {filt}...{RESET}")

    col, rest = filt.split("=", 1)
    params = {col: rest}
    resp = api_request("DELETE", f"/{table}", key, base_url, params=params,
                       headers_extra={"Prefer": "return=representation"})
    result = resp.json()
    print(f"{GREEN}Deleted {len(result)} rows.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Supabase Table Editor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-tables", help="List all tables")

    p_query = subparsers.add_parser("query", help="Query rows")
    p_query.add_argument("--table", required=True, help="Table name")
    p_query.add_argument("--select", default="*", help="Columns to select")
    p_query.add_argument("--filter", help="PostgREST filter (e.g., status=eq.active)")
    p_query.add_argument("--order", help="Order by (e.g., created_at.desc)")
    p_query.add_argument("--limit", type=int, default=50, help="Max rows")

    p_insert = subparsers.add_parser("insert", help="Insert a row")
    p_insert.add_argument("--table", required=True, help="Table name")
    p_insert.add_argument("--data", required=True, help="JSON data")

    p_update = subparsers.add_parser("update", help="Update rows")
    p_update.add_argument("--table", required=True, help="Table name")
    p_update.add_argument("--filter", required=True, help="PostgREST filter")
    p_update.add_argument("--data", required=True, help="JSON data")

    p_delete = subparsers.add_parser("delete", help="Delete rows")
    p_delete.add_argument("--table", required=True, help="Table name")
    p_delete.add_argument("--filter", required=True, help="PostgREST filter")

    args = parser.parse_args()

    if args.command == "list-tables":
        list_tables()
    elif args.command == "query":
        query(args.table, args.select, args.filter, args.order, args.limit)
    elif args.command == "insert":
        insert(args.table, args.data)
    elif args.command == "update":
        update(args.table, args.filter, args.data)
    elif args.command == "delete":
        delete(args.table, args.filter)


if __name__ == "__main__":
    main()
