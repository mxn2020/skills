#!/usr/bin/env python3
"""
Patent Search Tool — OC-0156
Query patent databases (USPTO PatentsView / Google Patents) for prior art.
"""

import sys
import argparse
import urllib.parse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# USPTO PatentsView API (free, no auth required)
PATENTS_VIEW_URL = "https://search.patentsview.org/api/v1/patent/"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _pv_request(params: dict) -> dict:
    resp = requests.get(
        PATENTS_VIEW_URL,
        params=params,
        timeout=30,
        headers={"Accept": "application/json"},
    )
    if not resp.ok:
        _die(f"PatentsView API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _print_patent(p: dict):
    pid   = p.get("patent_id", "")
    title = p.get("patent_title", "")
    date  = p.get("patent_date", "")
    kind  = p.get("patent_kind", "")

    inventors = [
        f"{inv.get('inventor_name_first', '')} {inv.get('inventor_name_last', '')}".strip()
        for inv in (p.get("inventors") or [])[:3]
    ]
    assignees = [
        a.get("assignee_organization", a.get("assignee_name_last", ""))
        for a in (p.get("assignees") or [])[:2]
    ]
    abstract = (p.get("patent_abstract") or "")[:200]

    print(f"\n  {CYAN}{pid}{RESET}  {BOLD}{title}{RESET}")
    print(f"    Date: {date}  |  Kind: {kind}")
    if assignees:
        print(f"    Assignee: {', '.join(a for a in assignees if a)}")
    if inventors:
        print(f"    Inventors: {', '.join(inventors)}")
    if abstract:
        print(f"    {abstract}...")


def search(query: str, max_results: int = 10):
    print(f"{YELLOW}Searching patents: '{query}'...{RESET}")
    params = {
        "q": f'{{"_text_any":{{"patent_title":"{query}","patent_abstract":"{query}"}}}}',
        "f": '["patent_id","patent_title","patent_date","patent_kind","patent_abstract","inventors","assignees"]',
        "o": f'{{"per_page":{min(max_results, 25)}}}',
    }
    data = _pv_request(params)
    patents = data.get("patents") or []

    if not patents:
        print(f"{YELLOW}No patents found for '{query}'.{RESET}")
        return

    print(f"\n{GREEN}Found {data.get('total_patent_count', len(patents))} patent(s) "
          f"(showing {len(patents)}):{RESET}")
    for p in patents:
        _print_patent(p)
    print()


def get_patent(patent_id: str):
    # Normalize ID
    pid = patent_id.upper().replace("US", "").lstrip("0")
    print(f"{YELLOW}Fetching patent: US{pid}{RESET}")
    params = {
        "q": f'{{"patent_id":"{pid}"}}',
        "f": '["patent_id","patent_title","patent_date","patent_kind","patent_abstract","patent_claims","inventors","assignees","cpcs"]',
    }
    data = _pv_request(params)
    patents = data.get("patents") or []

    if not patents:
        print(f"{YELLOW}Patent not found: {patent_id}{RESET}")
        return

    p = patents[0]
    _print_patent(p)

    # Print claims
    claims = p.get("patent_claims", "")
    if claims:
        print(f"\n  {BOLD}Independent Claims (first 500 chars):{RESET}")
        print(f"  {claims[:500]}...")

    # CPC codes
    cpcs = [c.get("cpc_group_id", "") for c in (p.get("cpcs") or [])[:5]]
    if cpcs:
        print(f"\n  {BOLD}CPC Classifications:{RESET} {', '.join(cpcs)}")
    print()


def prior_art(description: str, max_results: int = 10):
    print(f"{YELLOW}Searching for prior art...{RESET}")
    # Extract key terms from description
    words = [w for w in description.lower().split() if len(w) > 4][:5]
    query = " ".join(words)

    print(f"  Search terms: {CYAN}{query}{RESET}")
    search(query, max_results)

    print(f"\n{YELLOW}Note: Also search Google Patents manually for:{RESET}")
    encoded = urllib.parse.quote(description[:100])
    print(f"  https://patents.google.com/?q={encoded}&before=priority:20240101")
    print()


def list_by_assignee(assignee: str, max_results: int = 20):
    print(f"{YELLOW}Searching patents by assignee: '{assignee}'...{RESET}")
    params = {
        "q": f'{{"_contains":{{"assignee_organization":"{assignee}"}}}}',
        "f": '["patent_id","patent_title","patent_date","patent_kind","assignees"]',
        "o": f'{{"per_page":{min(max_results, 25)},"sort":[{{"patent_date":"desc"}}]}}',
    }
    data = _pv_request(params)
    patents = data.get("patents") or []

    if not patents:
        print(f"{YELLOW}No patents found for assignee '{assignee}'.{RESET}")
        return

    total = data.get("total_patent_count", len(patents))
    print(f"\n{GREEN}Found {total} patent(s) for '{assignee}' (showing {len(patents)}):{RESET}")
    for p in patents:
        _print_patent(p)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="patent_search.py",
        description="Patent Search Tool — OC-0156"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="Search patents by keyword")
    p.add_argument("--query", required=True)
    p.add_argument("--max-results", type=int, default=10)

    p = sub.add_parser("get-patent", help="Get patent details")
    p.add_argument("--patent-id", required=True, help="Patent number (e.g. US10000000)")

    p = sub.add_parser("prior-art", help="Search for prior art")
    p.add_argument("--description", required=True, help="Invention description")
    p.add_argument("--max-results", type=int, default=10)

    p = sub.add_parser("list-by-assignee", help="List patents by company/inventor")
    p.add_argument("--assignee", required=True, help="Company or inventor name")
    p.add_argument("--max-results", type=int, default=20)

    args = parser.parse_args()
    dispatch = {
        "search":          lambda: search(args.query, args.max_results),
        "get-patent":      lambda: get_patent(args.patent_id),
        "prior-art":       lambda: prior_art(args.description, args.max_results),
        "list-by-assignee": lambda: list_by_assignee(args.assignee, args.max_results),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
