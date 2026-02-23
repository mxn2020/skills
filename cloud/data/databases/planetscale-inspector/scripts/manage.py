#!/usr/bin/env python3
"""
PlanetScale Schema Inspector - Check migrations and schema diffs.
Uses PlanetScale API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.planetscale.com/v1"


def get_config():
    token = os.environ.get("PLANETSCALE_TOKEN")
    org = os.environ.get("PLANETSCALE_ORG")
    if not token:
        print(f"{RED}Error: PLANETSCALE_TOKEN environment variable not set.{RESET}")
        sys.exit(1)
    if not org:
        print(f"{RED}Error: PLANETSCALE_ORG environment variable not set.{RESET}")
        sys.exit(1)
    return token, org


def api_request(method, endpoint, token, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = f"{BASE_URL}{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_databases():
    token, org = get_config()
    print(f"{YELLOW}Listing databases for org '{org}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases", token)
    dbs = data.get("data", [])
    print(f"{GREEN}Found {len(dbs)} databases:{RESET}")
    for db in dbs:
        print(f"  {db['name']}  region={db.get('region', 'N/A')}  created={db.get('created_at', 'N/A')}")


def list_branches(database):
    token, org = get_config()
    print(f"{YELLOW}Listing branches for '{database}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases/{database}/branches", token)
    branches = data.get("data", [])
    print(f"{GREEN}Found {len(branches)} branches:{RESET}")
    for b in branches:
        production = " (production)" if b.get("production") else ""
        print(f"  {b['name']}{production}  created={b.get('created_at', 'N/A')}")


def get_schema(database, branch):
    token, org = get_config()
    print(f"{YELLOW}Getting schema for '{database}/{branch}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases/{database}/branches/{branch}/schema", token)
    tables = data.get("data", [])
    print(f"{GREEN}Schema for {database}/{branch} ({len(tables)} tables):{RESET}")
    for t in tables:
        print(f"\n  {t.get('name', 'unknown')}:")
        for col in t.get("columns", []):
            nullable = "NULL" if col.get("nullable") else "NOT NULL"
            print(f"    {col['name']}  {col.get('type', 'N/A')}  {nullable}")


def create_deploy_request(database, branch, into):
    token, org = get_config()
    print(f"{YELLOW}Creating deploy request: {branch} -> {into}...{RESET}")

    body = {"branch": branch, "into_branch": into}
    data = api_request("POST", f"/organizations/{org}/databases/{database}/deploy-requests", token, json_data=body)
    dr = data
    print(f"{GREEN}Deploy request created:{RESET}")
    print(f"  ID:     {dr.get('id', 'N/A')}")
    print(f"  State:  {dr.get('state', 'N/A')}")
    print(f"  Branch: {dr.get('branch', 'N/A')} -> {dr.get('into_branch', 'N/A')}")


def diff(database, branch, base):
    token, org = get_config()
    print(f"{YELLOW}Diffing '{branch}' against '{base}' in '{database}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases/{database}/branches/{branch}/schema/diff",
                       token, params={"base": base})
    diffs = data.get("data", [])
    if not diffs:
        print(f"{GREEN}No schema differences found.{RESET}")
        return

    print(f"{GREEN}Found {len(diffs)} schema changes:{RESET}")
    for d in diffs:
        print(f"\n  Table: {d.get('table', 'N/A')}")
        print(f"  Type:  {d.get('type', 'N/A')}")
        if d.get("statement"):
            print(f"  SQL:   {d['statement']}")


def main():
    parser = argparse.ArgumentParser(description="PlanetScale Schema Inspector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-databases", help="List all databases")

    p_branches = subparsers.add_parser("list-branches", help="List branches")
    p_branches.add_argument("--database", required=True, help="Database name")

    p_schema = subparsers.add_parser("get-schema", help="Get branch schema")
    p_schema.add_argument("--database", required=True, help="Database name")
    p_schema.add_argument("--branch", required=True, help="Branch name")

    p_deploy = subparsers.add_parser("create-deploy-request", help="Create deploy request")
    p_deploy.add_argument("--database", required=True, help="Database name")
    p_deploy.add_argument("--branch", required=True, help="Source branch")
    p_deploy.add_argument("--into", required=True, help="Target branch")

    p_diff = subparsers.add_parser("diff", help="Diff two branches")
    p_diff.add_argument("--database", required=True, help="Database name")
    p_diff.add_argument("--branch", required=True, help="Source branch")
    p_diff.add_argument("--base", required=True, help="Base branch")

    args = parser.parse_args()

    if args.command == "list-databases":
        list_databases()
    elif args.command == "list-branches":
        list_branches(args.database)
    elif args.command == "get-schema":
        get_schema(args.database, args.branch)
    elif args.command == "create-deploy-request":
        create_deploy_request(args.database, args.branch, args.into)
    elif args.command == "diff":
        diff(args.database, args.branch, args.base)


if __name__ == "__main__":
    main()
