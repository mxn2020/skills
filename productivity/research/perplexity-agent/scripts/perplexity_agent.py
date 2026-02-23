#!/usr/bin/env python3
"""
Perplexity Query Agent — OC-0155
Use Perplexity's API for grounded, citation-backed answers.
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

BASE_URL = "https://api.perplexity.ai"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not key:
        _die("PERPLEXITY_API_KEY is not set.")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _query(model: str, messages: list, search_context: bool = True) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "return_citations": True,
        "return_images": False,
    }
    if search_context:
        payload["search_recency_filter"] = "month"

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=_headers(),
        json=payload,
        timeout=60,
    )
    if not resp.ok:
        _die(f"Perplexity API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _print_result(data: dict, show_citations: bool = True):
    choices = data.get("choices", [])
    if not choices:
        print(f"{YELLOW}No response received.{RESET}")
        return

    message = choices[0].get("message", {})
    content = message.get("content", "")
    citations = data.get("citations", [])

    print(f"\n{content}\n")

    if show_citations and citations:
        print(f"{BOLD}Sources:{RESET}")
        for i, cite in enumerate(citations, 1):
            url = cite if isinstance(cite, str) else cite.get("url", "")
            title = "" if isinstance(cite, str) else cite.get("title", "")
            print(f"  [{i}] {CYAN}{title or url}{RESET}")
            if title and url:
                print(f"      {url}")
    print()


def search(query: str):
    print(f"{YELLOW}Searching: {query}{RESET}\n")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful research assistant. Provide accurate, "
                "well-sourced answers. Be concise but thorough."
            ),
        },
        {"role": "user", "content": query},
    ]
    data = _query("llama-3.1-sonar-small-128k-online", messages)
    _print_result(data)


def deep_research(query: str):
    print(f"{YELLOW}Deep research: {query}{RESET}\n")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert research assistant. Provide comprehensive, "
                "detailed answers with multiple perspectives. Structure your "
                "response with clear sections. Cite your sources thoroughly."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Please provide a thorough research summary on: {query}\n\n"
                "Include: key findings, different viewpoints, recent developments, "
                "and important caveats or limitations."
            ),
        },
    ]
    data = _query("llama-3.1-sonar-large-128k-online", messages)
    _print_result(data)


def summarize_topic(topic: str, depth: str = "brief"):
    depth_map = {
        "brief": "Provide a concise 3-paragraph overview",
        "standard": "Provide a structured overview with 5-7 key points",
        "detailed": "Provide a comprehensive structured summary with subtopics",
    }
    instruction = depth_map.get(depth, depth_map["brief"])

    print(f"{YELLOW}Summarizing topic: {topic} ({depth}){RESET}\n")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a knowledgeable subject matter expert. "
                "Create well-structured, informative summaries."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Topic: {topic}\n\n"
                f"{instruction} of this topic. Include current state, "
                "key concepts, major players or developments, and future outlook."
            ),
        },
    ]
    data = _query("llama-3.1-sonar-large-128k-online", messages)
    _print_result(data)


def main():
    parser = argparse.ArgumentParser(
        prog="perplexity_agent.py",
        description="Perplexity Query Agent — OC-0155"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="Search with citation-backed answer")
    p.add_argument("--query", required=True)

    p = sub.add_parser("deep-research", help="Detailed research with citations")
    p.add_argument("--query", required=True)

    p = sub.add_parser("summarize-topic", help="Generate structured topic summary")
    p.add_argument("--topic", required=True)
    p.add_argument("--depth", default="brief", choices=["brief", "standard", "detailed"])

    args = parser.parse_args()
    dispatch = {
        "search":          lambda: search(args.query),
        "deep-research":   lambda: deep_research(args.query),
        "summarize-topic": lambda: summarize_topic(args.topic, args.depth),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
