#!/usr/bin/env python3
"""
Shopify Order Manager (OC-0073)
Fetch, refund, or fulfill orders, and browse products and customers.
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

API_VERSION = "2024-01"


def get_config():
    store = os.environ.get("SHOPIFY_STORE")
    token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
    if not store or not token:
        print(f"{RED}Error: SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN environment variables are required.{RESET}")
        sys.exit(1)
    base_url = f"https://{store}/admin/api/{API_VERSION}"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    return base_url, headers


def api_request(method, endpoint, params=None, json_data=None):
    base_url, headers = get_config()
    url = f"{base_url}/{endpoint}"
    try:
        resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{RESET}")
        sys.exit(1)


def list_orders(args):
    print(f"{YELLOW}Listing orders...{RESET}")
    params = {"limit": args.limit}
    if args.status != "any":
        params["status"] = args.status
    result = api_request("GET", "orders.json", params=params)
    orders = result.get("orders", [])
    print(f"{GREEN}Found {len(orders)} order(s):{RESET}")
    for o in orders:
        total = o.get("total_price", "0.00")
        print(f"  #{o['id']}  {o.get('name', '')}  total={total} {o.get('currency', '')}  status={o.get('financial_status', '')}")


def get_order(args):
    print(f"{YELLOW}Fetching order {args.order_id}...{RESET}")
    result = api_request("GET", f"orders/{args.order_id}.json")
    order = result.get("order", {})
    print(f"{GREEN}Order {order.get('name', order.get('id'))}:{RESET}")
    print(f"  Created:    {order.get('created_at', 'N/A')}")
    print(f"  Status:     {order.get('financial_status', 'N/A')}")
    print(f"  Total:      {order.get('total_price', '0.00')} {order.get('currency', '')}")
    print(f"  Customer:   {order.get('email', 'N/A')}")
    items = order.get("line_items", [])
    if items:
        print(f"  Items ({len(items)}):")
        for li in items:
            print(f"    - {li.get('title', '')} x{li.get('quantity', 1)}  {li.get('price', '0.00')}")


def refund(args):
    print(f"{YELLOW}Fetching order {args.order_id} for refund...{RESET}")
    order_data = api_request("GET", f"orders/{args.order_id}.json")
    order = order_data.get("order", {})
    transactions = api_request("GET", f"orders/{args.order_id}/transactions.json")
    txns = transactions.get("transactions", [])
    parent_id = None
    for t in txns:
        if t.get("kind") == "sale" and t.get("status") == "success":
            parent_id = t["id"]
            break
    if not parent_id:
        print(f"{RED}No successful sale transaction found to refund.{RESET}")
        sys.exit(1)
    refund_data = {
        "refund": {
            "note": args.note or "Refund issued via OpenClaw",
            "transactions": [{"parent_id": parent_id, "amount": order.get("total_price"), "kind": "refund"}],
        }
    }
    print(f"{YELLOW}Issuing refund...{RESET}")
    result = api_request("POST", f"orders/{args.order_id}/refunds.json", json_data=refund_data)
    ref = result.get("refund", {})
    print(f"{GREEN}Refund created: id={ref.get('id')}  status={ref.get('status', 'complete')}{RESET}")


def fulfill(args):
    print(f"{YELLOW}Creating fulfillment for order {args.order_id}...{RESET}")
    order_data = api_request("GET", f"orders/{args.order_id}.json")
    order = order_data.get("order", {})
    line_items = [{"id": li["id"], "quantity": li["quantity"]} for li in order.get("line_items", [])]
    fulfillment = {"fulfillment": {"line_items": line_items}}
    if args.tracking_number:
        fulfillment["fulfillment"]["tracking_number"] = args.tracking_number
    if args.tracking_company:
        fulfillment["fulfillment"]["tracking_company"] = args.tracking_company
    result = api_request("POST", f"orders/{args.order_id}/fulfillments.json", json_data=fulfillment)
    ful = result.get("fulfillment", {})
    print(f"{GREEN}Fulfillment created: id={ful.get('id')}  status={ful.get('status', 'success')}{RESET}")


def list_products(args):
    print(f"{YELLOW}Listing products...{RESET}")
    result = api_request("GET", "products.json", params={"limit": args.limit})
    products = result.get("products", [])
    print(f"{GREEN}Found {len(products)} product(s):{RESET}")
    for p in products:
        print(f"  {p['id']}  {p.get('title', '')}  status={p.get('status', '')}")


def list_customers(args):
    print(f"{YELLOW}Listing customers...{RESET}")
    result = api_request("GET", "customers.json", params={"limit": args.limit})
    customers = result.get("customers", [])
    print(f"{GREEN}Found {len(customers)} customer(s):{RESET}")
    for c in customers:
        print(f"  {c['id']}  {c.get('email', 'N/A')}  {c.get('first_name', '')} {c.get('last_name', '')}")


def main():
    parser = argparse.ArgumentParser(description="Shopify Order Manager (OC-0073)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp = subparsers.add_parser("list-orders", help="List orders")
    sp.add_argument("--status", default="any", help="Filter by status")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("get-order", help="Get order details")
    sp.add_argument("order_id", help="Order ID")

    sp = subparsers.add_parser("refund", help="Refund an order")
    sp.add_argument("order_id", help="Order ID")
    sp.add_argument("--note", help="Refund note")

    sp = subparsers.add_parser("fulfill", help="Fulfill an order")
    sp.add_argument("order_id", help="Order ID")
    sp.add_argument("--tracking-number", help="Tracking number")
    sp.add_argument("--tracking-company", help="Shipping carrier")

    sp = subparsers.add_parser("list-products", help="List products")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    sp = subparsers.add_parser("list-customers", help="List customers")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    args = parser.parse_args()
    commands = {
        "list-orders": list_orders,
        "get-order": get_order,
        "refund": refund,
        "fulfill": fulfill,
        "list-products": list_products,
        "list-customers": list_customers,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
