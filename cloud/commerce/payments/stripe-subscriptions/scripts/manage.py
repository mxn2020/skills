#!/usr/bin/env python3
"""
Stripe Subscription Manager (OC-0069)
Cancel/refund subscriptions, manage products and prices via the Stripe API.
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

BASE_URL = "https://api.stripe.com/v1"


def get_headers():
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        print(f"{RED}Error: STRIPE_SECRET_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def api_request(method, endpoint, params=None, data=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.request(method, url, headers=get_headers(), params=params, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)


def list_subscriptions(args):
    print(f"{YELLOW}Listing subscriptions...{RESET}")
    params = {"limit": args.limit}
    if args.status:
        params["status"] = args.status
    result = api_request("GET", "subscriptions", params=params)
    subs = result.get("data", [])
    print(f"{GREEN}Found {len(subs)} subscription(s):{RESET}")
    for s in subs:
        print(f"  {s['id']}  status={s['status']}  customer={s['customer']}")


def cancel(args):
    print(f"{YELLOW}Cancelling subscription {args.subscription_id}...{RESET}")
    data = {} if args.immediate else {"cancel_at_period_end": "true"}
    endpoint = f"subscriptions/{args.subscription_id}"
    if args.immediate:
        result = api_request("DELETE", endpoint)
    else:
        result = api_request("POST", endpoint, data=data)
    print(f"{GREEN}Subscription {result['id']} status: {result['status']}{RESET}")


def refund(args):
    print(f"{YELLOW}Fetching latest invoice for {args.subscription_id}...{RESET}")
    sub = api_request("GET", f"subscriptions/{args.subscription_id}")
    invoice_id = sub.get("latest_invoice")
    if not invoice_id:
        print(f"{RED}No invoice found on this subscription.{RESET}")
        sys.exit(1)
    invoice = api_request("GET", f"invoices/{invoice_id}")
    charge_id = invoice.get("charge")
    if not charge_id:
        print(f"{RED}No charge found on the latest invoice.{RESET}")
        sys.exit(1)
    data = {"charge": charge_id}
    if args.amount:
        data["amount"] = str(args.amount)
    print(f"{YELLOW}Issuing refund for charge {charge_id}...{RESET}")
    result = api_request("POST", "refunds", data=data)
    print(f"{GREEN}Refund {result['id']} created — amount: {result['amount']} {result['currency']}{RESET}")


def list_products(args):
    print(f"{YELLOW}Listing products...{RESET}")
    result = api_request("GET", "products", params={"limit": args.limit})
    products = result.get("data", [])
    print(f"{GREEN}Found {len(products)} product(s):{RESET}")
    for p in products:
        print(f"  {p['id']}  {p['name']}")


def create_product(args):
    print(f"{YELLOW}Creating product '{args.name}'...{RESET}")
    data = {"name": args.name}
    if args.description:
        data["description"] = args.description
    result = api_request("POST", "products", data=data)
    print(f"{GREEN}Product created: {result['id']} — {result['name']}{RESET}")


def list_prices(args):
    print(f"{YELLOW}Listing prices...{RESET}")
    params = {"limit": args.limit}
    if args.product:
        params["product"] = args.product
    result = api_request("GET", "prices", params=params)
    prices = result.get("data", [])
    print(f"{GREEN}Found {len(prices)} price(s):{RESET}")
    for p in prices:
        amt = p.get("unit_amount", "N/A")
        print(f"  {p['id']}  {amt} {p.get('currency', '')}  recurring={p.get('recurring') is not None}")


def main():
    parser = argparse.ArgumentParser(description="Stripe Subscription Manager (OC-0069)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("list-subscriptions", help="List subscriptions")
    sp.add_argument("--status", help="Filter by status")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("cancel", help="Cancel a subscription")
    sp.add_argument("subscription_id", help="Subscription ID")
    sp.add_argument("--immediate", action="store_true", help="Cancel immediately")

    sp = subparsers.add_parser("refund", help="Refund latest invoice")
    sp.add_argument("subscription_id", help="Subscription ID")
    sp.add_argument("--amount", type=int, help="Partial refund amount in cents")

    sp = subparsers.add_parser("list-products", help="List products")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("create-product", help="Create a product")
    sp.add_argument("name", help="Product name")
    sp.add_argument("--description", help="Product description")

    sp = subparsers.add_parser("list-prices", help="List prices")
    sp.add_argument("--product", help="Filter by product ID")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()
    commands = {
        "list-subscriptions": list_subscriptions,
        "cancel": cancel,
        "refund": refund,
        "list-products": list_products,
        "create-product": create_product,
        "list-prices": list_prices,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
