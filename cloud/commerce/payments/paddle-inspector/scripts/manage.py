#!/usr/bin/env python3
"""
Paddle Subscription Inspector (OC-0074)
Audit billing history, manage subscriptions, and list transactions.
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

BASE_URL = "https://api.paddle.com"


def get_headers():
    key = os.environ.get("PADDLE_API_KEY")
    if not key:
        print(f"{RED}Error: PADDLE_API_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def api_request(method, endpoint, params=None, json_data=None):
    url = f"{BASE_URL}/{endpoint}"
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


def list_subscriptions(args):
    print(f"{YELLOW}Listing subscriptions...{RESET}")
    params = {"per_page": args.limit}
    if args.status:
        params["status"] = args.status
    result = api_request("GET", "subscriptions", params=params)
    subs = result.get("data", [])
    print(f"{GREEN}Found {len(subs)} subscription(s):{RESET}")
    for s in subs:
        print(f"  {s['id']}  status={s.get('status', 'N/A')}  customer={s.get('customer_id', 'N/A')}")


def get_subscription(args):
    print(f"{YELLOW}Fetching subscription {args.subscription_id}...{RESET}")
    result = api_request("GET", f"subscriptions/{args.subscription_id}")
    sub = result.get("data", result)
    print(f"{GREEN}Subscription {sub.get('id')}:{RESET}")
    print(f"  Status:          {sub.get('status', 'N/A')}")
    print(f"  Customer:        {sub.get('customer_id', 'N/A')}")
    print(f"  Started:         {sub.get('started_at', 'N/A')}")
    print(f"  Next billed:     {sub.get('next_billed_at', 'N/A')}")
    print(f"  Current period:  {sub.get('current_billing_period', {}).get('starts_at', 'N/A')} -> {sub.get('current_billing_period', {}).get('ends_at', 'N/A')}")
    items = sub.get("items", [])
    if items:
        print(f"  Items ({len(items)}):")
        for item in items:
            price = item.get("price", {})
            print(f"    {price.get('id', 'N/A')}  {price.get('description', '')}  {price.get('unit_price', {}).get('amount', 'N/A')} {price.get('unit_price', {}).get('currency_code', '')}")


def cancel(args):
    print(f"{YELLOW}Cancelling subscription {args.subscription_id}...{RESET}")
    effective = "immediately" if args.immediate else "next_billing_period"
    data = {"effective_from": effective}
    result = api_request("POST", f"subscriptions/{args.subscription_id}/cancel", json_data=data)
    sub = result.get("data", result)
    print(f"{GREEN}Subscription {sub.get('id')} — status: {sub.get('status', 'canceled')}{RESET}")


def pause(args):
    print(f"{YELLOW}Pausing subscription {args.subscription_id}...{RESET}")
    data = {"effective_from": "next_billing_period"}
    result = api_request("POST", f"subscriptions/{args.subscription_id}/pause", json_data=data)
    sub = result.get("data", result)
    print(f"{GREEN}Subscription {sub.get('id')} — status: {sub.get('status', 'paused')}{RESET}")


def resume(args):
    print(f"{YELLOW}Resuming subscription {args.subscription_id}...{RESET}")
    data = {"effective_from": "immediately"}
    result = api_request("POST", f"subscriptions/{args.subscription_id}/resume", json_data=data)
    sub = result.get("data", result)
    print(f"{GREEN}Subscription {sub.get('id')} — status: {sub.get('status', 'active')}{RESET}")


def list_transactions(args):
    print(f"{YELLOW}Listing transactions...{RESET}")
    params = {"per_page": args.limit}
    if args.subscription_id:
        params["subscription_id"] = args.subscription_id
    result = api_request("GET", "transactions", params=params)
    txns = result.get("data", [])
    print(f"{GREEN}Found {len(txns)} transaction(s):{RESET}")
    for t in txns:
        total = t.get("details", {}).get("totals", {}).get("total", "N/A")
        print(f"  {t['id']}  status={t.get('status', 'N/A')}  total={total}  billed_at={t.get('billed_at', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Paddle Subscription Inspector (OC-0074)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("list-subscriptions", help="List subscriptions")
    sp.add_argument("--status", help="Filter by status")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("get-subscription", help="Get subscription details")
    sp.add_argument("subscription_id", help="Subscription ID")

    sp = subparsers.add_parser("cancel", help="Cancel a subscription")
    sp.add_argument("subscription_id", help="Subscription ID")
    sp.add_argument("--immediate", action="store_true", help="Cancel immediately")

    sp = subparsers.add_parser("pause", help="Pause a subscription")
    sp.add_argument("subscription_id", help="Subscription ID")

    sp = subparsers.add_parser("resume", help="Resume a paused subscription")
    sp.add_argument("subscription_id", help="Subscription ID")

    sp = subparsers.add_parser("list-transactions", help="List transactions")
    sp.add_argument("--subscription-id", help="Filter by subscription ID")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()
    commands = {
        "list-subscriptions": list_subscriptions,
        "get-subscription": get_subscription,
        "cancel": cancel,
        "pause": pause,
        "resume": resume,
        "list-transactions": list_transactions,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
