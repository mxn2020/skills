#!/usr/bin/env python3
"""
RevenueCat Customer Lookup (OC-0072)
Check in-app purchase status, offerings, entitlements, and subscriptions.
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

BASE_URL = "https://api.revenuecat.com/v1"


def get_headers():
    key = os.environ.get("REVENUECAT_API_KEY")
    if not key:
        print(f"{RED}Error: REVENUECAT_API_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def api_request(method, endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.request(method, url, headers=get_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)


def get_customer(args):
    print(f"{YELLOW}Fetching customer {args.app_user_id}...{RESET}")
    result = api_request("GET", f"subscribers/{args.app_user_id}")
    subscriber = result.get("subscriber", {})
    print(f"{GREEN}Customer profile:{RESET}")
    print(f"  First seen:       {subscriber.get('first_seen', 'N/A')}")
    print(f"  Management URL:   {subscriber.get('management_url', 'N/A')}")
    subs = subscriber.get("subscriptions", {})
    if subs:
        print(f"  Subscriptions ({len(subs)}):")
        for pid, info in subs.items():
            print(f"    {pid}  expires={info.get('expires_date', 'N/A')}  store={info.get('store', 'N/A')}")
    entitlements = subscriber.get("entitlements", {})
    if entitlements:
        print(f"  Entitlements ({len(entitlements)}):")
        for eid, info in entitlements.items():
            print(f"    {eid}  expires={info.get('expires_date', 'N/A')}")


def list_offerings(args):
    print(f"{YELLOW}Listing offerings...{RESET}")
    result = api_request("GET", "offerings")
    offerings = result.get("offerings", result.get("data", []))
    if isinstance(offerings, list):
        print(f"{GREEN}Found {len(offerings)} offering(s):{RESET}")
        for o in offerings:
            oid = o.get("id", o.get("identifier", "N/A"))
            print(f"  {oid}  {o.get('description', o.get('lookup_key', ''))}")
    else:
        print(f"{GREEN}Offerings:{RESET}")
        print(f"  {json.dumps(offerings, indent=2)[:500]}")


def list_entitlements(args):
    print(f"{YELLOW}Fetching entitlements for {args.app_user_id}...{RESET}")
    result = api_request("GET", f"subscribers/{args.app_user_id}")
    entitlements = result.get("subscriber", {}).get("entitlements", {})
    if not entitlements:
        print(f"{YELLOW}No active entitlements found.{RESET}")
        return
    print(f"{GREEN}Found {len(entitlements)} entitlement(s):{RESET}")
    for eid, info in entitlements.items():
        print(f"  {eid}")
        print(f"    Product:  {info.get('product_identifier', 'N/A')}")
        print(f"    Expires:  {info.get('expires_date', 'N/A')}")
        print(f"    Store:    {info.get('store', 'N/A')}")


def get_subscription(args):
    print(f"{YELLOW}Fetching subscriptions for {args.app_user_id}...{RESET}")
    result = api_request("GET", f"subscribers/{args.app_user_id}")
    subs = result.get("subscriber", {}).get("subscriptions", {})
    if args.product_id:
        subs = {k: v for k, v in subs.items() if k == args.product_id}
    if not subs:
        print(f"{YELLOW}No matching subscriptions found.{RESET}")
        return
    print(f"{GREEN}Found {len(subs)} subscription(s):{RESET}")
    for pid, info in subs.items():
        print(f"  {pid}")
        print(f"    Store:            {info.get('store', 'N/A')}")
        print(f"    Purchase date:    {info.get('purchase_date', 'N/A')}")
        print(f"    Expires:          {info.get('expires_date', 'N/A')}")
        print(f"    Auto-renew:       {info.get('auto_resume_date', 'N/A')}")
        print(f"    Unsubscribed:     {info.get('unsubscribe_detected_at', 'N/A')}")


def list_products(args):
    print(f"{YELLOW}Listing products...{RESET}")
    result = api_request("GET", "products", params={"limit": args.limit})
    items = result.get("items", result.get("data", []))
    if isinstance(items, list):
        print(f"{GREEN}Found {len(items)} product(s):{RESET}")
        for p in items:
            pid = p.get("id", p.get("identifier", "N/A"))
            print(f"  {pid}  {p.get('title', p.get('name', ''))}")
    else:
        print(f"{GREEN}Products:{RESET}")
        print(f"  {json.dumps(items, indent=2)[:500]}")


def main():
    parser = argparse.ArgumentParser(description="RevenueCat Customer Lookup (OC-0072)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("get-customer", help="Get customer profile")
    sp.add_argument("app_user_id", help="App user ID")

    subparsers.add_parser("list-offerings", help="List offerings")

    sp = subparsers.add_parser("list-entitlements", help="List customer entitlements")
    sp.add_argument("app_user_id", help="App user ID")

    sp = subparsers.add_parser("get-subscription", help="Get subscription details")
    sp.add_argument("app_user_id", help="App user ID")
    sp.add_argument("--product-id", help="Filter by product identifier")

    sp = subparsers.add_parser("list-products", help="List products")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()
    commands = {
        "get-customer": get_customer,
        "list-offerings": list_offerings,
        "list-entitlements": list_entitlements,
        "get-subscription": get_subscription,
        "list-products": list_products,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
