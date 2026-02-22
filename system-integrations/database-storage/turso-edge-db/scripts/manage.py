#!/usr/bin/env python3
"""
Turso Edge DB Manager - Manage SQLite at the edge.
Uses Turso Platform API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.turso.tech/v1"


def get_config():
    token = os.environ.get("TURSO_TOKEN")
    org = os.environ.get("TURSO_ORG")
    if not token:
        print(f"{RED}Error: TURSO_TOKEN environment variable not set.{RESET}")
        sys.exit(1)
    if not org:
        print(f"{RED}Error: TURSO_ORG environment variable not set.{RESET}")
        sys.exit(1)
    return token, org


def api_request(method, endpoint, token, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{BASE_URL}{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_databases():
    token, org = get_config()
    print(f"{YELLOW}Listing databases for '{org}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases", token)
    dbs = data.get("databases", [])
    print(f"{GREEN}Found {len(dbs)} databases:{RESET}")
    for db in dbs:
        regions = ", ".join(db.get("regions", []))
        print(f"  {db['Name']}  group={db.get('group', 'N/A')}  regions=[{regions}]")


def create_db(name, group="default"):
    token, org = get_config()
    print(f"{YELLOW}Creating database '{name}'...{RESET}")

    body = {"name": name, "group": group}
    data = api_request("POST", f"/organizations/{org}/databases", token, json_data=body)
    db = data.get("database", {})
    print(f"{GREEN}Database created:{RESET}")
    print(f"  Name:     {db.get('Name', name)}")
    print(f"  Hostname: {db.get('Hostname', 'N/A')}")
    print(f"  DB ID:    {db.get('DbId', 'N/A')}")


def delete_db(database):
    token, org = get_config()
    print(f"{YELLOW}Deleting database '{database}'...{RESET}")

    api_request("DELETE", f"/organizations/{org}/databases/{database}", token)
    print(f"{GREEN}Database '{database}' deleted.{RESET}")


def shell(database, sql):
    token, org = get_config()
    print(f"{YELLOW}Executing SQL on '{database}'...{RESET}")

    # Get database URL for Turso HTTP API
    data = api_request("GET", f"/organizations/{org}/databases/{database}", token)
    db = data.get("database", {})
    hostname = db.get("Hostname", "")
    if not hostname:
        print(f"{RED}Error: Could not resolve database hostname.{RESET}")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    db_url = f"https://{hostname}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"statements": [{"q": sql}]}
    resp = requests.post(f"{db_url}/v2/pipeline", headers=headers, json={"requests": [
        {"type": "execute", "stmt": {"sql": sql}},
        {"type": "close"}
    ]}, timeout=30)

    if resp.status_code >= 400:
        print(f"{RED}SQL error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)

    result = resp.json()
    results = result.get("results", [])
    for r in results:
        res = r.get("response", {}).get("result", {})
        cols = [c.get("name", "?") for c in res.get("cols", [])]
        rows = res.get("rows", [])
        affected = res.get("affected_row_count", 0)

        if cols:
            print(f"{GREEN}Columns: {' | '.join(cols)}{RESET}")
            for row in rows:
                vals = [str(cell.get("value", "NULL")) for cell in row]
                print(f"  {' | '.join(vals)}")
            print(f"{GREEN}{len(rows)} row(s) returned.{RESET}")
        elif affected:
            print(f"{GREEN}{affected} row(s) affected.{RESET}")


def get_stats(database):
    token, org = get_config()
    print(f"{YELLOW}Getting stats for '{database}'...{RESET}")

    data = api_request("GET", f"/organizations/{org}/databases/{database}/stats", token)
    stats = data if isinstance(data, dict) else {}
    print(f"{GREEN}Stats for '{database}':{RESET}")
    for key, value in stats.items():
        if key != "database":
            print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(description="Turso Edge DB Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-databases", help="List all databases")

    p_create = subparsers.add_parser("create-db", help="Create a database")
    p_create.add_argument("--name", required=True, help="Database name")
    p_create.add_argument("--group", default="default", help="Group name")

    p_delete = subparsers.add_parser("delete-db", help="Delete a database")
    p_delete.add_argument("--database", required=True, help="Database name")

    p_shell = subparsers.add_parser("shell", help="Execute SQL")
    p_shell.add_argument("--database", required=True, help="Database name")
    p_shell.add_argument("--sql", required=True, help="SQL statement")

    p_stats = subparsers.add_parser("get-stats", help="Get database stats")
    p_stats.add_argument("--database", required=True, help="Database name")

    args = parser.parse_args()

    if args.command == "list-databases":
        list_databases()
    elif args.command == "create-db":
        create_db(args.name, args.group)
    elif args.command == "delete-db":
        delete_db(args.database)
    elif args.command == "shell":
        shell(args.database, args.sql)
    elif args.command == "get-stats":
        get_stats(args.database)


if __name__ == "__main__":
    main()
