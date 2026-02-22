#!/usr/bin/env python3
"""DigitalOcean Droplet Sniper – OC-0022"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.digitalocean.com/v2"


def _headers():
    token = os.environ.get("DIGITALOCEAN_TOKEN")
    if not token:
        print(f"{RED}Error: DIGITALOCEAN_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_droplets(args):
    data = _request("get", "/droplets", params={"per_page": args.limit})
    for d in data.get("droplets", []):
        status = d.get("status", "unknown")
        color = GREEN if status == "active" else YELLOW
        ip = ""
        for net in d.get("networks", {}).get("v4", []):
            if net.get("type") == "public":
                ip = net.get("ip_address", "")
                break
        print(f"{color}{status}{RESET}  {d['name']}  id={d['id']}  ip={ip}  region={d.get('region', {}).get('slug', 'n/a')}")


def create(args):
    payload = {
        "name": args.name,
        "region": args.region,
        "size": args.size,
        "image": args.image,
        "ssh_keys": args.ssh_keys or [],
        "tags": args.tags or [],
    }
    data = _request("post", "/droplets", json=payload)
    droplet = data.get("droplet", {})
    print(f"{GREEN}Droplet created:{RESET} {droplet.get('name')}  id={droplet.get('id')}")


def destroy(args):
    resp = requests.delete(f"{BASE_URL}/droplets/{args.droplet_id}", headers=_headers())
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Droplet {args.droplet_id} destroyed{RESET}")


def get_droplet(args):
    data = _request("get", f"/droplets/{args.droplet_id}")
    d = data.get("droplet", {})
    print(f"{GREEN}{d.get('name')}{RESET}")
    print(f"  ID:     {d.get('id')}")
    print(f"  Status: {d.get('status')}")
    print(f"  Region: {d.get('region', {}).get('name', 'n/a')}")
    print(f"  Size:   {d.get('size_slug')}")
    print(f"  Image:  {d.get('image', {}).get('slug', 'n/a')}")
    for net in d.get("networks", {}).get("v4", []):
        print(f"  IP ({net.get('type')}): {net.get('ip_address')}")


def list_snapshots(args):
    data = _request("get", "/snapshots", params={"resource_type": "droplet", "per_page": args.limit})
    for s in data.get("snapshots", []):
        print(f"{GREEN}{s['name']}{RESET}  id={s['id']}  size={s.get('size_gigabytes', 0)}GB  created={s.get('created_at', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="DigitalOcean Droplet Sniper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-droplets", help="List droplets")
    p_list.add_argument("--limit", type=int, default=25)

    p_create = sub.add_parser("create", help="Create droplet")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--region", required=True)
    p_create.add_argument("--size", required=True)
    p_create.add_argument("--image", required=True)
    p_create.add_argument("--ssh-keys", nargs="*", default=None)
    p_create.add_argument("--tags", nargs="*", default=None)

    p_destroy = sub.add_parser("destroy", help="Destroy droplet")
    p_destroy.add_argument("--droplet-id", required=True)

    p_get = sub.add_parser("get-droplet", help="Get droplet details")
    p_get.add_argument("--droplet-id", required=True)

    p_snap = sub.add_parser("list-snapshots", help="List snapshots")
    p_snap.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    commands = {
        "list-droplets": list_droplets,
        "create": create,
        "destroy": destroy,
        "get-droplet": get_droplet,
        "list-snapshots": list_snapshots,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
