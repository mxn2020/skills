#!/usr/bin/env python3
"""
News Aggregator — OC-0157
Pull and summarize headlines by topic from RSS/APIs.
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL = "https://newsapi.org/v2"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    key = os.environ.get("NEWS_API_KEY", "")
    if not key:
        _die("NEWS_API_KEY is not set. Get a free key at newsapi.org")
    return {"X-Api-Key": key}


def _request(endpoint: str, params: dict) -> dict:
    resp = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    if not resp.ok:
        data = resp.json()
        _die(f"NewsAPI {resp.status_code}: {data.get('message', resp.text[:200])}")
    return resp.json()


def _print_article(article: dict, num: int = None):
    title  = article.get("title", "(no title)")
    source = (article.get("source") or {}).get("name", "")
    url    = article.get("url", "")
    desc   = article.get("description") or ""
    pub    = article.get("publishedAt", "")[:10]

    prefix = f"{CYAN}[{num}]{RESET} " if num else "  "
    print(f"\n{prefix}{BOLD}{title}{RESET}")
    print(f"  {YELLOW}{source}{RESET}  |  {pub}")
    if desc:
        print(f"  {desc[:120]}")
    print(f"  {url}")


def headlines(category: str = "general", country: str = "us", max_results: int = 10):
    valid_categories = ["business", "entertainment", "general", "health",
                        "science", "sports", "technology"]
    if category not in valid_categories:
        _die(f"Invalid category. Use: {', '.join(valid_categories)}")

    print(f"\n{YELLOW}Fetching {category} headlines ({country.upper()})...{RESET}")
    data = _request("top-headlines", {
        "category": category,
        "country": country,
        "pageSize": min(max_results, 20),
    })

    articles = data.get("articles", [])
    total = data.get("totalResults", 0)

    if not articles:
        print(f"{YELLOW}No headlines found.{RESET}")
        return

    print(f"\n{GREEN}{BOLD}Top {len(articles)} {category.capitalize()} Headlines{RESET}")
    print(f"{GREEN}Total available: {total}{RESET}")
    for i, art in enumerate(articles, 1):
        _print_article(art, i)
    print()


def search(query: str, max_results: int = 10, days_ago: int = 7):
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    print(f"\n{YELLOW}Searching news: '{query}'...{RESET}")
    data = _request("everything", {
        "q": query,
        "from": from_date,
        "sortBy": "relevancy",
        "pageSize": min(max_results, 20),
        "language": "en",
    })

    articles = data.get("articles", [])
    total = data.get("totalResults", 0)

    if not articles:
        print(f"{YELLOW}No news found for '{query}'.{RESET}")
        return

    print(f"\n{GREEN}Found {total} article(s) for '{query}' (showing {len(articles)}):{RESET}")
    for i, art in enumerate(articles, 1):
        _print_article(art, i)
    print()


def digest(topics_str: str):
    topics = [t.strip() for t in topics_str.split(",") if t.strip()]

    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}News Digest — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}{RESET}")
    print(f"{BOLD}{'='*55}{RESET}")

    for topic in topics:
        print(f"\n{CYAN}{BOLD}── {topic.upper()} ──{RESET}")
        try:
            from_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
            data = _request("everything", {
                "q": topic,
                "from": from_date,
                "sortBy": "relevancy",
                "pageSize": 3,
                "language": "en",
            })
            articles = data.get("articles", [])
            if not articles:
                print(f"  {YELLOW}No recent news.{RESET}")
                continue
            for art in articles:
                title  = art.get("title", "")
                source = (art.get("source") or {}).get("name", "")
                print(f"  • {BOLD}{title[:80]}{RESET}  [{YELLOW}{source}{RESET}]")
        except SystemExit:
            print(f"  {RED}Could not fetch news.{RESET}")

    print(f"\n{BOLD}{'='*55}{RESET}\n")


def sources(category: str = None, language: str = "en", country: str = "us"):
    params = {"language": language, "country": country}
    if category:
        params["category"] = category

    print(f"{YELLOW}Fetching news sources...{RESET}")
    data = _request("top-headlines/sources", params)
    src_list = data.get("sources", [])

    if not src_list:
        print(f"{YELLOW}No sources found.{RESET}")
        return

    print(f"\n{GREEN}Found {len(src_list)} source(s):{RESET}\n")
    for src in src_list:
        name = src.get("name", "")
        sid  = src.get("id", "")
        cat  = src.get("category", "")
        url  = src.get("url", "")
        print(f"  {CYAN}{sid}{RESET}  {BOLD}{name}{RESET}  [{cat}]")
        print(f"    {url}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="news_aggregator.py",
        description="News Aggregator — OC-0157"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("headlines", help="Get top headlines")
    p.add_argument("--category", default="general",
                   choices=["business", "entertainment", "general",
                            "health", "science", "sports", "technology"])
    p.add_argument("--country", default="us")
    p.add_argument("--max-results", type=int, default=10)

    p = sub.add_parser("search", help="Search news by keyword")
    p.add_argument("--query", required=True)
    p.add_argument("--max-results", type=int, default=10)
    p.add_argument("--days", type=int, default=7, help="Search last N days")

    p = sub.add_parser("digest", help="Generate multi-topic digest")
    p.add_argument("--topics", required=True, help="Comma-separated topics")

    p = sub.add_parser("sources", help="List available news sources")
    p.add_argument("--category", default=None)
    p.add_argument("--language", default="en")
    p.add_argument("--country", default="us")

    args = parser.parse_args()
    dispatch = {
        "headlines": lambda: headlines(args.category, args.country, args.max_results),
        "search":    lambda: search(args.query, args.max_results, args.days),
        "digest":    lambda: digest(args.topics),
        "sources":   lambda: sources(args.category, args.language, args.country),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
