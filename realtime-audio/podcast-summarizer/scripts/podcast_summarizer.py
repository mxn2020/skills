#!/usr/bin/env python3
"""Podcast Summarizer – OC-0113"""

import argparse
import os
import sys
import tempfile
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_BASE = "https://api.openai.com/v1"


def _key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k:
        print(f"{RED}Error: OPENAI_API_KEY not set{RESET}")
        sys.exit(1)
    return k


def _transcribe(file_path):
    print(f"{YELLOW}Transcribing ...{RESET}")
    with open(file_path, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {_key()}"},
            files={"file": fh},
            data={"model": "whisper-1"},
        )
    if not resp.ok:
        print(f"{RED}Transcription error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json().get("text", "")


def _summarize(text, length):
    instructions = {
        "brief": "Summarize in 3-5 bullet points.",
        "medium": "Write a 2-3 paragraph summary covering the main topics, key insights, and conclusions.",
        "detailed": "Write a detailed summary with sections: Overview, Key Topics, Notable Quotes/Stats, Conclusions, and Recommended Action.",
    }
    prompt = f"{instructions[length]}\n\nTranscript:\n{text[:8000]}"
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    if not resp.ok:
        print(f"{RED}Summary error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]


def summarize_file(args):
    text = _transcribe(args.file)
    print(f"{YELLOW}Generating {args.length} summary ...{RESET}")
    summary = _summarize(text, args.length)
    print(f"\n{GREEN}Summary:{RESET}\n{summary}")


def summarize_url(args):
    print(f"{YELLOW}Downloading {args.url} ...{RESET}")
    resp = requests.get(args.url, stream=True)
    if not resp.ok:
        print(f"{RED}Download error ({resp.status_code}){RESET}")
        sys.exit(1)
    suffix = ".mp3" if "mp3" in args.url else ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in resp.iter_content(1024 * 1024):
            tmp.write(chunk)
        tmp_path = tmp.name
    try:
        text = _transcribe(tmp_path)
        summary = _summarize(text, args.length)
        print(f"\n{GREEN}Summary:{RESET}\n{summary}")
    finally:
        os.unlink(tmp_path)


def fetch_rss(args):
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        print(f"{RED}xml.etree.ElementTree not available{RESET}")
        sys.exit(1)
    print(f"{YELLOW}Fetching RSS feed ...{RESET}")
    resp = requests.get(args.feed_url, headers={"User-Agent": "OpenClaw/1.0"})
    if not resp.ok:
        print(f"{RED}RSS fetch error: {resp.status_code}{RESET}")
        sys.exit(1)
    root = ET.fromstring(resp.content)
    items = root.findall(".//item")[:args.limit]
    print(f"{GREEN}Recent episodes:{RESET}")
    for i, item in enumerate(items, 1):
        title = item.findtext("title", "No title")
        pubdate = item.findtext("pubDate", "")
        enclosure = item.find("enclosure")
        url = enclosure.get("url", "N/A") if enclosure is not None else "N/A"
        print(f"  {i}. {title}")
        print(f"     Date: {pubdate}")
        print(f"     URL : {url[:80]}")


def extract_topics(args):
    text = _transcribe(args.file)
    prompt = (
        "Extract the main topics and themes from this podcast transcript. "
        "Return as a numbered list of specific topics with 1-sentence descriptions.\n\n"
        + text[:6000]
    )
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    result = resp.json()["choices"][0]["message"]["content"]
    print(f"{GREEN}Key topics:{RESET}")
    print(result)


def main():
    parser = argparse.ArgumentParser(description="Podcast Summarizer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_f = sub.add_parser("summarize-file")
    p_f.add_argument("--file", required=True)
    p_f.add_argument("--length", choices=["brief", "medium", "detailed"], default="medium")

    p_u = sub.add_parser("summarize-url")
    p_u.add_argument("--url", required=True)
    p_u.add_argument("--length", choices=["brief", "medium", "detailed"], default="medium")

    p_r = sub.add_parser("fetch-rss")
    p_r.add_argument("--feed-url", required=True)
    p_r.add_argument("--limit", type=int, default=5)

    p_t = sub.add_parser("extract-topics")
    p_t.add_argument("--file", required=True)

    args = parser.parse_args()
    dispatch = {
        "summarize-file": summarize_file,
        "summarize-url": summarize_url,
        "fetch-rss": fetch_rss,
        "extract-topics": extract_topics,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
