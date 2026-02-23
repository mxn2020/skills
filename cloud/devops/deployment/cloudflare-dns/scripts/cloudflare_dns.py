#!/usr/bin/env python3
"""Cloudflare DNS Manager – OC-0019"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.cloudflare.com/client/v4"


def _headers():
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print(f"{RED}Error: CLOUDFLARE_API_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def list_zones(args):
    data = _request("get", "/zones", params={"per_page": args.limit})
    for z in data.get("result", []):
        status = z.get("status", "n/a")
        color = GREEN if status == "active" else YELLOW
        print(f"{color}{z['name']}{RESET}  id={z['id']}  status={status}")


def list_records(args):
    params = {"per_page": args.limit}
    if args.type:
        params["type"] = args.type
    data = _request("get", f"/zones/{args.zone_id}/dns_records", params=params)
    for r in data.get("result", []):
        proxied = "proxied" if r.get("proxied") else "dns-only"
        print(f"{GREEN}{r['type']:6s}{RESET}  {r['name']:40s}  -> {r['content']}  ({proxied})")


def create_record(args):
    payload = {
        "type": args.type,
        "name": args.name,
        "content": args.content,
        "ttl": args.ttl,
        "proxied": args.proxied,
    }
    data = _request("post", f"/zones/{args.zone_id}/dns_records", json=payload)
    rec = data.get("result", {})
    print(f"{GREEN}Created:{RESET} {rec.get('type')} {rec.get('name')} -> {rec.get('content')}  id={rec.get('id')}")


def update_record(args):
    # Fetch existing record to preserve fields
    existing = _request("get", f"/zones/{args.zone_id}/dns_records/{args.record_id}")
    rec = existing.get("result", {})
    payload = {
        "type": args.type or rec.get("type"),
        "name": args.name or rec.get("name"),
        "content": args.content,
        "ttl": args.ttl or rec.get("ttl", 1),
    }
    data = _request("put", f"/zones/{args.zone_id}/dns_records/{args.record_id}", json=payload)
    updated = data.get("result", {})
    print(f"{GREEN}Updated:{RESET} {updated.get('name')} -> {updated.get('content')}")


def delete_record(args):
    _request("delete", f"/zones/{args.zone_id}/dns_records/{args.record_id}")
    print(f"{GREEN}Deleted record {args.record_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare DNS Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_zones = sub.add_parser("list-zones", help="List zones")
    p_zones.add_argument("--limit", type=int, default=50)

    p_records = sub.add_parser("list-records", help="List DNS records")
    p_records.add_argument("--zone-id", required=True)
    p_records.add_argument("--type", default=None, help="Filter by record type")
    p_records.add_argument("--limit", type=int, default=100)

    p_create = sub.add_parser("create-record", help="Create DNS record")
    p_create.add_argument("--zone-id", required=True)
    p_create.add_argument("--type", required=True, help="A, AAAA, CNAME, etc.")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--content", required=True)
    p_create.add_argument("--ttl", type=int, default=1, help="TTL (1=auto)")
    p_create.add_argument("--proxied", action="store_true")

    p_update = sub.add_parser("update-record", help="Update DNS record")
    p_update.add_argument("--zone-id", required=True)
    p_update.add_argument("--record-id", required=True)
    p_update.add_argument("--content", required=True)
    p_update.add_argument("--type", default=None)
    p_update.add_argument("--name", default=None)
    p_update.add_argument("--ttl", type=int, default=None)

    p_delete = sub.add_parser("delete-record", help="Delete DNS record")
    p_delete.add_argument("--zone-id", required=True)
    p_delete.add_argument("--record-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-zones": list_zones,
        "list-records": list_records,
        "create-record": create_record,
        "update-record": update_record,
        "delete-record": delete_record,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
