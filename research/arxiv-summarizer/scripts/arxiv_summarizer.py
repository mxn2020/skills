#!/usr/bin/env python3
"""arXiv Summarizer - Search, fetch, and summarize academic papers from arXiv."""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ARXIV_API_URL = "https://export.arxiv.org/api/query"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

NS = {"atom": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _headers_openai():
    if not OPENAI_API_KEY:
        fail("OPENAI_API_KEY environment variable is required.")
    return {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}


def _request(url, params=None):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


def _openai_complete(prompt, model="gpt-4o-mini"):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
    }
    resp = requests.post(OPENAI_URL, headers=_headers_openai(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _parse_entries(xml_text):
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", NS):
        arxiv_id = entry.findtext("atom:id", "", NS)
        if "/" in arxiv_id:
            arxiv_id = arxiv_id.rstrip("/").split("/")[-1]
        title = entry.findtext("atom:title", "", NS).strip().replace("\n", " ")
        summary = entry.findtext("atom:summary", "", NS).strip().replace("\n", " ")
        published = entry.findtext("atom:published", "", NS)
        authors = [a.findtext("atom:name", "", NS) for a in entry.findall("atom:author", NS)]
        categories = [c.get("term", "") for c in entry.findall("atom:category")]
        entries.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "published": published,
            "authors": authors,
            "categories": categories,
        })
    return entries


def search(args):
    query = args.query
    if args.category:
        query = f"cat:{args.category} AND all:{query}"
    params = {
        "search_query": query,
        "max_results": args.max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    print(f"{YELLOW}Searching arXiv: {args.query}{RESET}\n")
    xml_text = _request(ARXIV_API_URL, params)
    entries = _parse_entries(xml_text)
    if not entries:
        warn("No papers found.")
        return
    for i, e in enumerate(entries, 1):
        print(f"  {GREEN}{i}. {e['title']}{RESET}")
        print(f"     ID: {e['id']}")
        print(f"     Authors: {', '.join(e['authors'][:3])}")
        print(f"     Published: {e['published'][:10]}")
        print(f"     {e['summary'][:150]}...")
        print()


def fetch_paper(args):
    params = {"id_list": args.arxiv_id, "max_results": 1}
    xml_text = _request(ARXIV_API_URL, params)
    entries = _parse_entries(xml_text)
    if not entries:
        fail(f"Paper not found: {args.arxiv_id}")
    e = entries[0]
    print(f"\n{GREEN}Paper: {e['title']}{RESET}\n")
    print(f"  ID:         {e['id']}")
    print(f"  Published:  {e['published'][:10]}")
    print(f"  Authors:    {', '.join(e['authors'])}")
    print(f"  Categories: {', '.join(e['categories'])}")
    print(f"\n  Abstract:\n")
    print(f"  {e['summary']}\n")
    return e


def summarize(args):
    params = {"id_list": args.arxiv_id, "max_results": 1}
    xml_text = _request(ARXIV_API_URL, params)
    entries = _parse_entries(xml_text)
    if not entries:
        fail(f"Paper not found: {args.arxiv_id}")
    e = entries[0]

    length = args.length or "detailed"
    length_instructions = {
        "brief": "in 2-3 sentences",
        "detailed": "in a detailed paragraph covering methods, results, and significance",
        "bullet-points": "as a list of bullet points covering: objective, methods, key findings, and significance",
    }
    instruction = length_instructions.get(length, length_instructions["detailed"])

    prompt = (
        f"Summarize the following academic paper {instruction}.\n\n"
        f"Title: {e['title']}\n"
        f"Authors: {', '.join(e['authors'])}\n"
        f"Abstract: {e['summary']}"
    )
    print(f"{YELLOW}Summarizing: {e['title']}{RESET}\n")
    summary = _openai_complete(prompt)
    print(f"{GREEN}Summary ({length}):{RESET}\n")
    print(summary)
    print()


def list_recent(args):
    category = args.category or "cs.AI"
    days = args.days or 7
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y%m%d")
    query = f"cat:{category} AND submittedDate:[{cutoff}0000 TO *]"
    params = {
        "search_query": query,
        "max_results": args.max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    print(f"{YELLOW}Recent papers in {category} (last {days} days):{RESET}\n")
    xml_text = _request(ARXIV_API_URL, params)
    entries = _parse_entries(xml_text)
    if not entries:
        warn("No recent papers found.")
        return
    for i, e in enumerate(entries, 1):
        print(f"  {GREEN}{i}. {e['title']}{RESET}")
        print(f"     ID: {e['id']}  |  Published: {e['published'][:10]}")
        print(f"     Authors: {', '.join(e['authors'][:3])}")
        print()


def export(args):
    params = {"id_list": args.arxiv_id, "max_results": 1}
    xml_text = _request(ARXIV_API_URL, params)
    entries = _parse_entries(xml_text)
    if not entries:
        fail(f"Paper not found: {args.arxiv_id}")
    e = entries[0]
    fmt = args.format or "md"

    if fmt == "md":
        content = f"# {e['title']}\n\n"
        content += f"- **arXiv ID**: {e['id']}\n"
        content += f"- **Published**: {e['published'][:10]}\n"
        content += f"- **Authors**: {', '.join(e['authors'])}\n"
        content += f"- **Categories**: {', '.join(e['categories'])}\n\n"
        content += f"## Abstract\n\n{e['summary']}\n\n"
        content += f"## Links\n\n"
        content += f"- [arXiv Abstract](https://arxiv.org/abs/{e['id']})\n"
        content += f"- [PDF](https://arxiv.org/pdf/{e['id']}.pdf)\n"
    else:
        content = f"Title: {e['title']}\n"
        content += f"arXiv ID: {e['id']}\n"
        content += f"Published: {e['published'][:10]}\n"
        content += f"Authors: {', '.join(e['authors'])}\n"
        content += f"Categories: {', '.join(e['categories'])}\n\n"
        content += f"Abstract:\n{e['summary']}\n"

    output_path = args.output or f"{args.arxiv_id}.{fmt}"
    with open(output_path, "w") as f:
        f.write(content)
    success(f"Paper exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="arXiv Summarizer")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search arXiv papers")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--max-results", type=int, default=5, help="Max results")
    p_search.add_argument("--category", help="arXiv category (e.g. cs.AI)")

    p_fetch = sub.add_parser("fetch-paper", help="Fetch paper metadata and abstract")
    p_fetch.add_argument("--arxiv-id", required=True, help="arXiv paper ID")

    p_sum = sub.add_parser("summarize", help="Generate AI summary of a paper")
    p_sum.add_argument("--arxiv-id", required=True, help="arXiv paper ID")
    p_sum.add_argument("--length", default="detailed",
                       choices=["brief", "detailed", "bullet-points"], help="Summary length")

    p_recent = sub.add_parser("list-recent", help="List recently submitted papers")
    p_recent.add_argument("--category", default="cs.AI", help="arXiv category")
    p_recent.add_argument("--days", type=int, default=7, help="Days to look back")
    p_recent.add_argument("--max-results", type=int, default=5, help="Max results")

    p_export = sub.add_parser("export", help="Export paper details to file")
    p_export.add_argument("--arxiv-id", required=True, help="arXiv paper ID")
    p_export.add_argument("--output", help="Output file path")
    p_export.add_argument("--format", default="md", choices=["md", "txt"], help="Output format")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        dispatch = {
            "search": search,
            "fetch-paper": fetch_paper,
            "summarize": summarize,
            "list-recent": list_recent,
            "export": export,
        }
        dispatch[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text[:200]}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
