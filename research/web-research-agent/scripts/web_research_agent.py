#!/usr/bin/env python3
"""Web Research Agent - Search, scrape, and synthesize web content using Serper and OpenAI."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

SERPER_URL = "https://google.serper.dev/search"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _headers_serper():
    if not SERPER_API_KEY:
        fail("SERPER_API_KEY environment variable is required.")
    return {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}


def _headers_openai():
    if not OPENAI_API_KEY:
        fail("OPENAI_API_KEY environment variable is required.")
    return {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}


def _request(method, url, headers, payload=None):
    resp = requests.request(method, url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _openai_complete(prompt, model="gpt-4o-mini"):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
    }
    data = _request("POST", OPENAI_URL, _headers_openai(), payload)
    return data["choices"][0]["message"]["content"].strip()


def search(args):
    payload = {"q": args.query, "num": args.num_results}
    data = _request("POST", SERPER_URL, _headers_serper(), payload)
    organic = data.get("organic", [])
    if not organic:
        warn("No results found.")
        return
    print(f"\n{GREEN}Search results for: {args.query}{RESET}\n")
    results = []
    for i, item in enumerate(organic[:args.num_results], 1):
        title = item.get("title", "N/A")
        link = item.get("link", "N/A")
        snippet = item.get("snippet", "")
        print(f"  {YELLOW}{i}.{RESET} {title}")
        print(f"     {link}")
        if snippet:
            print(f"     {snippet[:120]}...")
        print()
        results.append({"title": title, "link": link, "snippet": snippet})
    return results


def scrape(args):
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        fail("beautifulsoup4 is required: pip install beautifulsoup4")

    print(f"{YELLOW}Scraping: {args.url}{RESET}")
    headers_req = {
        "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0)"
    }
    resp = requests.get(args.url, headers=headers_req, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    extract = args.extract or "text"
    if extract == "text":
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.splitlines() if len(l) > 30]
        print(f"\n{GREEN}Extracted text ({len(lines)} lines):{RESET}\n")
        for line in lines[:50]:
            print(f"  {line}")
        if len(lines) > 50:
            warn(f"  ... {len(lines) - 50} more lines")
    elif extract == "links":
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text_lnk = a.get_text(strip=True)
            if href.startswith("http"):
                links.append({"text": text_lnk, "url": href})
        print(f"\n{GREEN}Found {len(links)} links:{RESET}\n")
        for lnk in links[:30]:
            print(f"  {lnk['text'][:50]:<50} {lnk['url']}")
    elif extract == "headings":
        headings = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
            headings.append({"level": tag.name, "text": tag.get_text(strip=True)})
        print(f"\n{GREEN}Found {len(headings)} headings:{RESET}\n")
        for h in headings:
            indent = "  " * (int(h["level"][1]) - 1)
            print(f"  {indent}{h['level'].upper()}: {h['text']}")
    else:
        fail(f"Unknown extract mode: {extract}. Use text, links, or headings.")


def synthesize(args):
    payload = {"q": args.query, "num": args.num_sources}
    data = _request("POST", SERPER_URL, _headers_serper(), payload)
    organic = data.get("organic", [])
    if not organic:
        fail("No search results found.")

    sources = []
    for item in organic[:args.num_sources]:
        sources.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })

    context = "\n\n".join(
        f"Source {i+1}: {s['title']}\nURL: {s['url']}\nSnippet: {s['snippet']}"
        for i, s in enumerate(sources)
    )
    prompt = (
        f"You are a research assistant. Synthesize the following web search results "
        f"into a comprehensive summary about: {args.query}\n\n{context}\n\n"
        f"Provide a well-structured synthesis with key findings, important details, "
        f"and relevant conclusions."
    )
    print(f"{YELLOW}Synthesizing {len(sources)} sources for: {args.query}{RESET}\n")
    summary = _openai_complete(prompt)
    print(f"{GREEN}Synthesis:{RESET}\n")
    print(summary)
    print()

    output = {"query": args.query, "sources": sources, "synthesis": summary}
    out_file = f"synthesis_{args.query[:30].replace(' ', '_')}.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)
    success(f"Synthesis saved to: {out_file}")


def export_report(args):
    if not os.path.exists(args.synthesis_file):
        fail(f"Synthesis file not found: {args.synthesis_file}")

    with open(args.synthesis_file) as f:
        data = json.load(f)

    query = data.get("query", "Research Report")
    synthesis = data.get("synthesis", "")
    sources = data.get("sources", [])
    fmt = args.format or "md"

    if fmt == "md":
        content = f"# Research Report: {query}\n\n"
        content += f"## Summary\n\n{synthesis}\n\n"
        content += "## Sources\n\n"
        for i, s in enumerate(sources, 1):
            content += f"{i}. [{s['title']}]({s['url']})\n"
    else:
        content = f"RESEARCH REPORT: {query}\n\n"
        content += f"SUMMARY\n{'='*40}\n{synthesis}\n\n"
        content += f"SOURCES\n{'='*40}\n"
        for i, s in enumerate(sources, 1):
            content += f"{i}. {s['title']} - {s['url']}\n"

    output_path = args.output or f"report.{fmt}"
    with open(output_path, "w") as f:
        f.write(content)
    success(f"Report exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Web Research Agent")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search the web via Serper")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--num-results", type=int, default=5, help="Number of results")

    p_scrape = sub.add_parser("scrape", help="Scrape content from a URL")
    p_scrape.add_argument("--url", required=True, help="URL to scrape")
    p_scrape.add_argument("--extract", default="text", choices=["text", "links", "headings"],
                          help="What to extract")

    p_syn = sub.add_parser("synthesize", help="Search, scrape, and synthesize with AI")
    p_syn.add_argument("--query", required=True, help="Research query")
    p_syn.add_argument("--num-sources", type=int, default=3, help="Number of sources to use")

    p_exp = sub.add_parser("export-report", help="Export synthesis to file")
    p_exp.add_argument("--synthesis-file", required=True, help="Path to synthesis JSON file")
    p_exp.add_argument("--output", help="Output file path")
    p_exp.add_argument("--format", default="md", choices=["md", "txt"], help="Output format")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        dispatch = {
            "search": search,
            "scrape": scrape,
            "synthesize": synthesize,
            "export-report": export_report,
        }
        dispatch[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text[:200]}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
