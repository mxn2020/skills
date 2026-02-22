#!/usr/bin/env python3
"""
DynamoDB Item Browser - Query NoSQL data efficiently.
Uses AWS CLI via subprocess.
"""

import sys
import os
import json
import argparse
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_aws(cmd_args):
    """Run an AWS CLI command and return parsed JSON output."""
    full_cmd = ["aws", "dynamodb"] + cmd_args + ["--output", "json"]
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        print(f"{RED}Error: AWS CLI not found. Install it first.{RESET}")
        sys.exit(1)

    if result.returncode != 0:
        print(f"{RED}AWS CLI error: {result.stderr.strip()}{RESET}")
        sys.exit(1)

    if result.stdout.strip():
        return json.loads(result.stdout)
    return None


def list_tables(region=None):
    print(f"{YELLOW}Listing DynamoDB tables...{RESET}")
    cmd = ["list-tables"]
    if region:
        cmd.extend(["--region", region])

    data = run_aws(cmd)
    tables = data.get("TableNames", [])
    print(f"{GREEN}Found {len(tables)} tables:{RESET}")
    for t in tables:
        print(f"  {t}")


def scan(table, limit=25, region=None):
    print(f"{YELLOW}Scanning '{table}' (limit={limit})...{RESET}")
    cmd = ["scan", "--table-name", table, "--max-items", str(limit)]
    if region:
        cmd.extend(["--region", region])

    data = run_aws(cmd)
    items = data.get("Items", [])
    print(f"{GREEN}Found {len(items)} items:{RESET}")
    for item in items:
        print(f"  {json.dumps(item, default=str)}")


def query(table, key_condition, values, region=None):
    print(f"{YELLOW}Querying '{table}'...{RESET}")
    cmd = ["query", "--table-name", table,
           "--key-condition-expression", key_condition,
           "--expression-attribute-values", values]
    if region:
        cmd.extend(["--region", region])

    data = run_aws(cmd)
    items = data.get("Items", [])
    print(f"{GREEN}Found {len(items)} items:{RESET}")
    for item in items:
        print(f"  {json.dumps(item, default=str)}")


def get_item(table, key, region=None):
    print(f"{YELLOW}Getting item from '{table}'...{RESET}")
    cmd = ["get-item", "--table-name", table, "--key", key]
    if region:
        cmd.extend(["--region", region])

    data = run_aws(cmd)
    item = data.get("Item")
    if item:
        print(f"{GREEN}Item:{RESET}")
        print(f"  {json.dumps(item, indent=2, default=str)}")
    else:
        print(f"{YELLOW}Item not found.{RESET}")


def put_item(table, item, region=None):
    print(f"{YELLOW}Putting item into '{table}'...{RESET}")
    cmd = ["put-item", "--table-name", table, "--item", item]
    if region:
        cmd.extend(["--region", region])

    run_aws(cmd)
    print(f"{GREEN}Item written successfully.{RESET}")


def delete_item(table, key, region=None):
    print(f"{YELLOW}Deleting item from '{table}'...{RESET}")
    cmd = ["delete-item", "--table-name", table, "--key", key]
    if region:
        cmd.extend(["--region", region])

    run_aws(cmd)
    print(f"{GREEN}Item deleted.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="DynamoDB Item Browser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-tables", help="List all tables")
    p_list.add_argument("--region", help="AWS region")

    p_scan = subparsers.add_parser("scan", help="Scan a table")
    p_scan.add_argument("--table", required=True, help="Table name")
    p_scan.add_argument("--limit", type=int, default=25, help="Max items")
    p_scan.add_argument("--region", help="AWS region")

    p_query = subparsers.add_parser("query", help="Query by key condition")
    p_query.add_argument("--table", required=True, help="Table name")
    p_query.add_argument("--key-condition", required=True, help="Key condition expression")
    p_query.add_argument("--values", required=True, help="Expression attribute values (JSON)")
    p_query.add_argument("--region", help="AWS region")

    p_get = subparsers.add_parser("get-item", help="Get a specific item")
    p_get.add_argument("--table", required=True, help="Table name")
    p_get.add_argument("--key", required=True, help="Key as JSON")
    p_get.add_argument("--region", help="AWS region")

    p_put = subparsers.add_parser("put-item", help="Put an item")
    p_put.add_argument("--table", required=True, help="Table name")
    p_put.add_argument("--item", required=True, help="Item as JSON")
    p_put.add_argument("--region", help="AWS region")

    p_del = subparsers.add_parser("delete-item", help="Delete an item")
    p_del.add_argument("--table", required=True, help="Table name")
    p_del.add_argument("--key", required=True, help="Key as JSON")
    p_del.add_argument("--region", help="AWS region")

    args = parser.parse_args()

    if args.command == "list-tables":
        list_tables(args.region)
    elif args.command == "scan":
        scan(args.table, args.limit, args.region)
    elif args.command == "query":
        query(args.table, args.key_condition, args.values, args.region)
    elif args.command == "get-item":
        get_item(args.table, args.key, args.region)
    elif args.command == "put-item":
        put_item(args.table, args.item, args.region)
    elif args.command == "delete-item":
        delete_item(args.table, args.key, args.region)


if __name__ == "__main__":
    main()
