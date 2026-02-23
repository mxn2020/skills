#!/usr/bin/env python3
"""
Lemon Squeezy License Check (OC-0071)
Verify license keys, manage activations, and list products.
"""

import sys
import os
import json
import argparse
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.lemonsqueezy.com/v1"
VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses"


def get_headers():
    key = os.environ.get("LEMONSQUEEZY_API_KEY")
    if not key:
        print(f"{RED}Error: LEMONSQUEEZY_API_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {key}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }


def api_request(method, url, params=None, json_data=None):
    try:
        resp = requests.request(method, url, headers=get_headers(), params=params, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)


def validate_key(args):
    print(f"{YELLOW}Validating license key...{RESET}")
    url = f"{VALIDATE_URL}/validate"
    data = {"license_key": args.license_key}
    try:
        resp = requests.post(url, json=data, headers={"Accept": "application/json"}, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)

    valid = result.get("valid", False)
    if valid:
        print(f"{GREEN}License is VALID{RESET}")
    else:
        print(f"{RED}License is INVALID — {result.get('error', 'unknown reason')}{RESET}")
    meta = result.get("license_key", {})
    if meta:
        print(f"  Status:      {meta.get('status', 'N/A')}")
        print(f"  Activations: {meta.get('activation_usage', 0)}/{meta.get('activation_limit', 'unlimited')}")


def list_licenses(args):
    print(f"{YELLOW}Listing licenses...{RESET}")
    result = api_request("GET", f"{BASE_URL}/license-keys", params={"page[size]": args.limit})
    items = result.get("data", [])
    print(f"{GREEN}Found {len(items)} license(s):{RESET}")
    for item in items:
        attrs = item.get("attributes", {})
        print(f"  {item['id']}  key={attrs.get('key', 'N/A')}  status={attrs.get('status', 'N/A')}")


def activate(args):
    print(f"{YELLOW}Activating license...{RESET}")
    url = f"{VALIDATE_URL}/activate"
    data = {"license_key": args.license_key, "instance_name": args.instance_name}
    try:
        resp = requests.post(url, json=data, headers={"Accept": "application/json"}, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)

    if result.get("activated"):
        inst = result.get("instance", {})
        print(f"{GREEN}Activated — instance_id={inst.get('id', 'N/A')}{RESET}")
    else:
        print(f"{RED}Activation failed: {result.get('error', 'unknown')}{RESET}")


def deactivate(args):
    print(f"{YELLOW}Deactivating license instance...{RESET}")
    url = f"{VALIDATE_URL}/deactivate"
    data = {"license_key": args.license_key, "instance_id": args.instance_id}
    try:
        resp = requests.post(url, json=data, headers={"Accept": "application/json"}, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)

    if result.get("deactivated"):
        print(f"{GREEN}Instance deactivated successfully.{RESET}")
    else:
        print(f"{RED}Deactivation failed: {result.get('error', 'unknown')}{RESET}")


def list_products(args):
    print(f"{YELLOW}Listing products...{RESET}")
    result = api_request("GET", f"{BASE_URL}/products", params={"page[size]": args.limit})
    items = result.get("data", [])
    print(f"{GREEN}Found {len(items)} product(s):{RESET}")
    for item in items:
        attrs = item.get("attributes", {})
        print(f"  {item['id']}  {attrs.get('name', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Lemon Squeezy License Check (OC-0071)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("validate-key", help="Validate a license key")
    sp.add_argument("license_key", help="License key to validate")

    sp = subparsers.add_parser("list-licenses", help="List all licenses")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("activate", help="Activate a license")
    sp.add_argument("license_key", help="License key")
    sp.add_argument("--instance-name", required=True, help="Instance name")

    sp = subparsers.add_parser("deactivate", help="Deactivate a license instance")
    sp.add_argument("license_key", help="License key")
    sp.add_argument("--instance-id", required=True, help="Instance ID")

    sp = subparsers.add_parser("list-products", help="List products")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()
    commands = {
        "validate-key": validate_key,
        "list-licenses": list_licenses,
        "activate": activate,
        "deactivate": deactivate,
        "list-products": list_products,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
