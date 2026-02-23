#!/usr/bin/env python3
"""Wikipedia Deep Dive - Search, fetch, and summarize Wikipedia articles."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _wiki_api(lang, params):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params["format"] = "json"
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _headers_openai():
    if not OPENAI_API_KEY:
        fail("OPENAI_API_KEY environment variable is required for summarize.")
    return {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}


def _openai_complete(prompt, model="gpt-4o-mini"):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
    }
    resp = requests.post(OPENAI_URL, headers=_headers_openai(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _request(method, url, headers=None, payload=None):
    resp = requests.request(method, url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def search(args):
    lang = args.lang or "en"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": args.query,
        "srlimit": args.limit or 5,
    }
    data = _wiki_api(lang, params)
    results = data.get("query", {}).get("search", [])
    if not results:
        warn("No results found.")
        return
    print(f"\n{GREEN}Wikipedia search results for: {args.query}{RESET}\n")
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        snippet = r.get("snippet", "").replace('<span class="searchmatch">', "").replace("</span>", "")
        print(f"  {YELLOW}{i}.{RESET} {title}")
        print(f"     https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}")
        print(f"     {snippet[:120]}...")
        print()


def fetch_article(args):
    lang = args.lang or "en"
    params = {
        "action": "query",
        "titles": args.title,
        "prop": "extracts|info",
        "exintro": False,
        "explaintext": True,
        "inprop": "url",
        "redirects": True,
    }
    data = _wiki_api(lang, params)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        fail(f"Article not found: {args.title}")
    title = page.get("title", "")
    url = page.get("fullurl", "")
    extract = page.get("extract", "")
    print(f"\n{GREEN}{title}{RESET}\n")
    print(f"  URL: {url}\n")
    lines = extract.splitlines()
    for line in lines[:80]:
        if line.strip():
            print(f"  {line}")
    if len(lines) > 80:
        warn(f"\n  ... article continues ({len(lines)} total lines)")
    return {"title": title, "url": url, "extract": extract}


def summarize(args):
    lang = "en"
    params = {
        "action": "query",
        "titles": args.title,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": True,
    }
    data = _wiki_api(lang, params)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        fail(f"Article not found: {args.title}")
    extract = page.get("extract", "")[:3000]
    length = args.length or "detailed"

    if length == "brief":
        instruction = "in 2-3 sentences"
    else:
        instruction = "in a detailed paragraph covering the main topic, key concepts, and significance"

    prompt = (
        f"Summarize the following Wikipedia article {instruction}.\n\n"
        f"Title: {args.title}\n\nContent:\n{extract}"
    )
    print(f"{YELLOW}Summarizing: {args.title}{RESET}\n")
    summary = _openai_complete(prompt)
    print(f"{GREEN}Summary ({length}):{RESET}\n")
    print(summary)
    print()


def extract_links(args):
    lang = "en"
    params = {
        "action": "query",
        "titles": args.title,
        "prop": "links",
        "pllimit": args.max or 20,
        "redirects": True,
    }
    data = _wiki_api(lang, params)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        fail(f"Article not found: {args.title}")
    links = page.get("links", [])
    print(f"\n{GREEN}Links in '{args.title}':{RESET}\n")
    for i, lnk in enumerate(links, 1):
        title = lnk.get("title", "")
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        print(f"  {i:3}. {title:<50} {url}")
    print()
    success(f"Found {len(links)} links.")


def get_sections(args):
    lang = "en"
    params = {
        "action": "parse",
        "page": args.title,
        "prop": "sections",
        "redirects": True,
    }
    data = _wiki_api(lang, params)
    if "error" in data:
        fail(f"Could not fetch sections: {data['error'].get('info', '')}")
    sections = data.get("parse", {}).get("sections", [])
    title = data.get("parse", {}).get("title", args.title)
    print(f"\n{GREEN}Sections of '{title}':{RESET}\n")
    for s in sections:
        level = int(s.get("level", 2))
        indent = "  " * (level - 1)
        anchor = s.get("anchor", "")
        line = s.get("line", "")
        print(f"  {indent}{'#' * level} {line}")
    print()
    success(f"Found {len(sections)} sections.")


def main():
    parser = argparse.ArgumentParser(description="Wikipedia Deep Dive")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search Wikipedia")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--lang", default="en", help="Wikipedia language code")
    p_search.add_argument("--limit", type=int, default=5, help="Number of results")

    p_fetch = sub.add_parser("fetch-article", help="Fetch article content")
    p_fetch.add_argument("--title", required=True, help="Article title")
    p_fetch.add_argument("--lang", default="en", help="Wikipedia language code")

    p_sum = sub.add_parser("summarize", help="Summarize article with AI")
    p_sum.add_argument("--title", required=True, help="Article title")
    p_sum.add_argument("--length", default="detailed", choices=["brief", "detailed"],
                       help="Summary length")

    p_links = sub.add_parser("extract-links", help="Extract links from article")
    p_links.add_argument("--title", required=True, help="Article title")
    p_links.add_argument("--max", type=int, default=20, help="Max links to return")

    p_sections = sub.add_parser("get-sections", help="List article sections")
    p_sections.add_argument("--title", required=True, help="Article title")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        dispatch = {
            "search": search,
            "fetch-article": fetch_article,
            "summarize": summarize,
            "extract-links": extract_links,
            "get-sections": get_sections,
        }
        dispatch[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text[:200]}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
