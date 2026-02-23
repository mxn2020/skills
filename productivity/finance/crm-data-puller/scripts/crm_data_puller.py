#!/usr/bin/env python3
"""
CRM Data Puller — OC-0162
Fetch deals and contact data from HubSpot via API.
"""

import os
import sys
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL = "https://api.hubapi.com"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("HUBSPOT_TOKEN", "")
    if not token:
        _die("HUBSPOT_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if not resp.ok:
        _die(f"HubSpot API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def contacts(limit: int = 20):
    data = _request("GET", "crm/v3/objects/contacts", params={
        "limit": min(limit, 100),
        "properties": "firstname,lastname,email,company,phone,createdate",
        "sorts": "createdate",
    })
    results = data.get("results", [])
    if not results:
        print(f"{YELLOW}No contacts found.{RESET}")
        return

    print(f"\n{GREEN}Contacts ({len(results)} shown):{RESET}\n")
    for c in results:
        props = c.get("properties", {})
        name  = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
        email = props.get("email", "")
        co    = props.get("company", "")
        cid   = c.get("id", "")
        print(f"  {CYAN}{cid}{RESET}  {BOLD}{name or '(no name)'}{RESET}")
        if email:
            print(f"    Email: {email}")
        if co:
            print(f"    Company: {co}")
    print()


def deals(stage: str = None, limit: int = 20):
    params = {
        "limit": min(limit, 100),
        "properties": "dealname,amount,dealstage,closedate,pipeline",
    }
    if stage:
        params["filterGroups"] = [{"filters": [
            {"propertyName": "dealstage", "operator": "EQ", "value": stage}
        ]}]
        data = _request("POST", "crm/v3/objects/deals/search", json={
            "filterGroups": [{"filters": [
                {"propertyName": "dealstage", "operator": "EQ", "value": stage}
            ]}],
            "properties": ["dealname", "amount", "dealstage", "closedate"],
            "limit": min(limit, 100),
        })
    else:
        data = _request("GET", "crm/v3/objects/deals", params=params)

    results = data.get("results", [])
    if not results:
        print(f"{YELLOW}No deals found.{RESET}")
        return

    print(f"\n{GREEN}Deals ({len(results)} shown):{RESET}\n")
    for d in results:
        props = d.get("properties", {})
        name  = props.get("dealname", "(no name)")
        amount = props.get("amount", "0") or "0"
        dstage = props.get("dealstage", "")
        close  = props.get("closedate", "")[:10] if props.get("closedate") else ""
        did    = d.get("id", "")
        print(f"  {CYAN}{did}{RESET}  {BOLD}{name}{RESET}")
        print(f"    Amount: ${float(amount):,.2f}  |  Stage: {YELLOW}{dstage}{RESET}  "
              f"|  Close: {close}")
    print()


def pipeline():
    # Get all deals grouped by stage
    data = _request("GET", "crm/v3/objects/deals", params={
        "limit": 100,
        "properties": "dealname,amount,dealstage",
    })
    results = data.get("results", [])
    if not results:
        print(f"{YELLOW}No deals in pipeline.{RESET}")
        return

    stages: dict = {}
    for d in results:
        props  = d.get("properties", {})
        stage  = props.get("dealstage", "unknown")
        amount = float(props.get("amount", 0) or 0)
        stages.setdefault(stage, {"count": 0, "total": 0})
        stages[stage]["count"] += 1
        stages[stage]["total"] += amount

    total_deals = len(results)
    total_value = sum(v["total"] for v in stages.values())

    print(f"\n{BOLD}Deal Pipeline Summary:{RESET}\n")
    print(f"  Total deals: {total_deals}  |  Total value: ${total_value:,.2f}\n")
    for stage, info in sorted(stages.items(), key=lambda x: x[1]["total"], reverse=True):
        count = info["count"]
        total = info["total"]
        bar   = "█" * min(count, 20)
        print(f"  {CYAN}{stage:<25}{RESET}  {count:>3} deals  ${total:>12,.2f}  {GREEN}{bar}{RESET}")
    print()


def search_contact(query: str):
    data = _request("POST", "crm/v3/objects/contacts/search", json={
        "query": query,
        "properties": ["firstname", "lastname", "email", "company", "phone"],
        "limit": 10,
    })
    results = data.get("results", [])
    if not results:
        print(f"{YELLOW}No contacts found for '{query}'.{RESET}")
        return

    print(f"\n{GREEN}Found {len(results)} contact(s) for '{query}':{RESET}\n")
    for c in results:
        props = c.get("properties", {})
        name  = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
        email = props.get("email", "")
        co    = props.get("company", "")
        phone = props.get("phone", "")
        cid   = c.get("id", "")
        print(f"  {CYAN}{cid}{RESET}  {BOLD}{name or '(no name)'}{RESET}")
        if email: print(f"    Email: {email}")
        if co:    print(f"    Company: {co}")
        if phone: print(f"    Phone: {phone}")
        print()


def create_contact(email: str, name: str = "", company: str = "", phone: str = ""):
    parts = name.split(" ", 1)
    first = parts[0] if parts else ""
    last  = parts[1] if len(parts) > 1 else ""

    props = {"email": email}
    if first: props["firstname"] = first
    if last:  props["lastname"] = last
    if company: props["company"] = company
    if phone: props["phone"] = phone

    data = _request("POST", "crm/v3/objects/contacts", json={"properties": props})
    cid = data.get("id", "")
    print(f"{GREEN}Contact created: {BOLD}{name or email}{RESET} (ID: {cid})")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="crm_data_puller.py",
        description="CRM Data Puller — OC-0162"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("contacts", help="List recent contacts")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("deals", help="List deals")
    p.add_argument("--stage", default=None, help="Filter by deal stage")
    p.add_argument("--limit", type=int, default=20)

    sub.add_parser("pipeline", help="Show pipeline summary")

    p = sub.add_parser("search-contact", help="Search contacts")
    p.add_argument("--query", required=True)

    p = sub.add_parser("create-contact", help="Create a new contact")
    p.add_argument("--email", required=True)
    p.add_argument("--name", default="")
    p.add_argument("--company", default="")
    p.add_argument("--phone", default="")

    args = parser.parse_args()
    dispatch = {
        "contacts":       lambda: contacts(args.limit),
        "deals":          lambda: deals(getattr(args, "stage", None), args.limit),
        "pipeline":       lambda: pipeline(),
        "search-contact": lambda: search_contact(args.query),
        "create-contact": lambda: create_contact(
            args.email, args.name, args.company, args.phone),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
