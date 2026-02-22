#!/usr/bin/env python3
"""
Airtable Record Sync - Treat Airtable as a lightweight CMS/DB.
Uses Airtable REST API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.airtable.com/v0"
META_URL = "https://api.airtable.com/v0/meta/bases"


def get_config():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    if not api_key:
        print(f"{RED}Error: AIRTABLE_API_KEY environment variable not set.{RESET}")
        sys.exit(1)
    return api_key, base_id


def api_request(method, url, api_key, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_bases():
    api_key, _ = get_config()
    print(f"{YELLOW}Listing bases...{RESET}")

    data = api_request("GET", META_URL, api_key)
    bases = data.get("bases", [])
    print(f"{GREEN}Found {len(bases)} bases:{RESET}")
    for b in bases:
        print(f"  {b['name']} [ID: {b['id']}]")


def list_records(table, view=None, max_records=50, formula=None):
    api_key, base_id = get_config()
    if not base_id:
        print(f"{RED}Error: AIRTABLE_BASE_ID environment variable not set.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Listing records from '{table}'...{RESET}")

    params = {"maxRecords": max_records}
    if view:
        params["view"] = view
    if formula:
        params["filterByFormula"] = formula

    data = api_request("GET", f"{BASE_URL}/{base_id}/{table}", api_key, params=params)
    records = data.get("records", [])
    print(f"{GREEN}Found {len(records)} records:{RESET}")
    for r in records:
        fields = r.get("fields", {})
        print(f"  [{r['id']}] {json.dumps(fields, default=str)}")


def create_record(table, fields):
    api_key, base_id = get_config()
    if not base_id:
        print(f"{RED}Error: AIRTABLE_BASE_ID environment variable not set.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Creating record in '{table}'...{RESET}")

    parsed = json.loads(fields)
    body = {"fields": parsed}
    data = api_request("POST", f"{BASE_URL}/{base_id}/{table}", api_key, json_data=body)
    print(f"{GREEN}Record created:{RESET}")
    print(f"  ID: {data.get('id')}")
    print(f"  Fields: {json.dumps(data.get('fields', {}), default=str)}")


def update_record(table, record_id, fields):
    api_key, base_id = get_config()
    if not base_id:
        print(f"{RED}Error: AIRTABLE_BASE_ID environment variable not set.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Updating record {record_id} in '{table}'...{RESET}")

    parsed = json.loads(fields)
    body = {"fields": parsed}
    data = api_request("PATCH", f"{BASE_URL}/{base_id}/{table}/{record_id}", api_key, json_data=body)
    print(f"{GREEN}Record updated:{RESET}")
    print(f"  ID: {data.get('id')}")
    print(f"  Fields: {json.dumps(data.get('fields', {}), default=str)}")


def delete_record(table, record_id):
    api_key, base_id = get_config()
    if not base_id:
        print(f"{RED}Error: AIRTABLE_BASE_ID environment variable not set.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Deleting record {record_id} from '{table}'...{RESET}")

    data = api_request("DELETE", f"{BASE_URL}/{base_id}/{table}/{record_id}", api_key)
    print(f"{GREEN}Record {record_id} deleted.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Airtable Record Sync")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-bases", help="List all bases")

    p_list = subparsers.add_parser("list-records", help="List records")
    p_list.add_argument("--table", required=True, help="Table name")
    p_list.add_argument("--view", help="View name")
    p_list.add_argument("--max-records", type=int, default=50, help="Max records")
    p_list.add_argument("--formula", help="Filter formula")

    p_create = subparsers.add_parser("create-record", help="Create a record")
    p_create.add_argument("--table", required=True, help="Table name")
    p_create.add_argument("--fields", required=True, help="JSON fields")

    p_update = subparsers.add_parser("update-record", help="Update a record")
    p_update.add_argument("--table", required=True, help="Table name")
    p_update.add_argument("--record-id", required=True, help="Record ID")
    p_update.add_argument("--fields", required=True, help="JSON fields")

    p_delete = subparsers.add_parser("delete-record", help="Delete a record")
    p_delete.add_argument("--table", required=True, help="Table name")
    p_delete.add_argument("--record-id", required=True, help="Record ID")

    args = parser.parse_args()

    if args.command == "list-bases":
        list_bases()
    elif args.command == "list-records":
        list_records(args.table, args.view, args.max_records, args.formula)
    elif args.command == "create-record":
        create_record(args.table, args.fields)
    elif args.command == "update-record":
        update_record(args.table, args.record_id, args.fields)
    elif args.command == "delete-record":
        delete_record(args.table, args.record_id)


if __name__ == "__main__":
    main()
