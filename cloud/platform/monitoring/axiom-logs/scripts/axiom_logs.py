#!/usr/bin/env python3
"""Axiom Log Query – OC-0056"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.axiom.co/v1"


def _headers():
    token = os.environ.get("AXIOM_TOKEN")
    org_id = os.environ.get("AXIOM_ORG_ID")
    if not token or not org_id:
        print(f"{RED}Error: AXIOM_TOKEN and AXIOM_ORG_ID must be set{RESET}")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "X-Axiom-Org-Id": org_id,
        "Content-Type": "application/json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def query(args):
    payload = {
        "apl": args.apl,
        "startTime": args.start_time,
        "endTime": args.end_time,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    data = _request("post", "/datasets/_apl", json=payload)
    matches = data.get("matches", [])
    for match in matches:
        ts = match.get("_time", "n/a")
        row = match.get("data", match)
        print(f"{YELLOW}{ts}{RESET}  {json.dumps(row, default=str)}")
    total = data.get("status", {}).get("rowsMatched", len(matches))
    print(f"{GREEN}Total rows matched: {total}{RESET}", file=sys.stderr)


def list_datasets(args):
    data = _request("get", "/datasets")
    for ds in data:
        print(f"{GREEN}{ds.get('name', 'n/a')}{RESET}  description={ds.get('description', '')}  created={ds.get('created', 'n/a')}")


def ingest(args):
    with open(args.file, "r") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        payload = [payload]
    hdrs = _headers()
    hdrs["Content-Type"] = "application/json"
    resp = requests.post(f"{BASE_URL}/datasets/{args.dataset}/ingest", headers=hdrs, json=payload)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    print(f"{GREEN}Ingested {data.get('ingested', 0)} events into {args.dataset}{RESET}")


def get_dataset(args):
    data = _request("get", f"/datasets/{args.dataset}")
    print(f"{GREEN}{data.get('name', 'n/a')}{RESET}")
    print(f"  Description: {data.get('description', 'n/a')}")
    print(f"  Created:     {data.get('created', 'n/a')}")
    for field in data.get("fields", [])[:15]:
        print(f"  Field: {field.get('name', 'n/a')}  type={field.get('type', 'n/a')}")


def stream(args):
    payload = {
        "apl": f"['{args.dataset}'] | sort by _time desc | limit {args.limit}",
    }
    data = _request("post", "/datasets/_apl", json=payload)
    for match in data.get("matches", []):
        ts = match.get("_time", "n/a")
        row = match.get("data", match)
        print(f"{YELLOW}{ts}{RESET}  {json.dumps(row, default=str)}")


def main():
    parser = argparse.ArgumentParser(description="Axiom Log Query")
    sub = parser.add_subparsers(dest="command", required=True)

    p_query = sub.add_parser("query", help="Run an APL query")
    p_query.add_argument("--dataset", required=True)
    p_query.add_argument("--apl", required=True, help="APL query string")
    p_query.add_argument("--start-time", help="ISO 8601 start time")
    p_query.add_argument("--end-time", help="ISO 8601 end time")

    sub.add_parser("list-datasets", help="List datasets")

    p_ingest = sub.add_parser("ingest", help="Ingest JSON data")
    p_ingest.add_argument("--dataset", required=True)
    p_ingest.add_argument("--file", required=True, help="Path to JSON file")

    p_get = sub.add_parser("get-dataset", help="Get dataset metadata")
    p_get.add_argument("--dataset", required=True)

    p_stream = sub.add_parser("stream", help="Stream recent entries")
    p_stream.add_argument("--dataset", required=True)
    p_stream.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    commands = {
        "query": query,
        "list-datasets": list_datasets,
        "ingest": ingest,
        "get-dataset": get_dataset,
        "stream": stream,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
