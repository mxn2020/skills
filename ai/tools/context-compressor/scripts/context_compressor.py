#!/usr/bin/env python3
"""Context Compressor – OC-0117"""

import argparse
import json
import os
import sys
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


def _count_tokens(text):
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return len(text) // 4


def _summarize(text, target_tokens):
    word_limit = target_tokens * 0.75
    prompt = (f"Summarize the following text in approximately {int(word_limit)} words or fewer, "
              f"preserving all critical information, key facts, and context:\n\n{text[:20000]}")
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    if not resp.ok:
        print(f"{RED}API error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]


def compress(args):
    with open(args.file) as f:
        text = f.read()
    original_tokens = _count_tokens(text)
    print(f"{YELLOW}Original: {original_tokens:,} tokens. Target: {args.target_tokens:,}{RESET}")
    if original_tokens <= args.target_tokens:
        print(f"{GREEN}Already within target.{RESET}")
        print(text)
        return
    compressed = _summarize(text, args.target_tokens)
    new_tokens = _count_tokens(compressed)
    print(f"{GREEN}Compressed: {new_tokens:,} tokens (reduction: {100*(1-new_tokens/original_tokens):.0f}%){RESET}")
    print()
    print(compressed)
    if args.output:
        with open(args.output, "w") as f:
            f.write(compressed)
        print(f"\n{GREEN}Saved to {args.output}{RESET}")


def summarize_history(args):
    with open(args.file) as f:
        data = json.load(f)
    messages = data if isinstance(data, list) else data.get("messages", [])
    conversation = "\n".join(f"{m.get('role','?').upper()}: {m.get('content','')}" for m in messages)
    prompt = (f"Summarize this conversation history into a compressed context that preserves "
              f"all important information, decisions, and state:\n\n{conversation[:15000]}")
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    result = resp.json()["choices"][0]["message"]["content"]
    print(f"{GREEN}Compressed history ({len(messages)} messages → summary):{RESET}")
    print(result)


def truncate(args):
    with open(args.file) as f:
        text = f.read()
    strategy = args.strategy
    max_chars = args.max_tokens * 4
    if len(text) <= max_chars:
        print(text)
        return
    if strategy == "head":
        result = text[:max_chars]
    elif strategy == "tail":
        result = text[-max_chars:]
    else:  # middle
        half = max_chars // 2
        result = text[:half] + "\n...[truncated]...\n" + text[-half:]
    print(f"{YELLOW}Truncated from {len(text)} to {len(result)} chars ({args.strategy}){RESET}")
    print(result)


def estimate_tokens(args):
    with open(args.file) as f:
        text = f.read()
    tokens = _count_tokens(text)
    print(f"  File   : {args.file}")
    print(f"  Chars  : {len(text):,}")
    print(f"  Tokens : {GREEN}{tokens:,}{RESET}")
    print(f"  Cost (gpt-4o input): ${tokens * 2.50 / 1_000_000:.6f}")


def main():
    parser = argparse.ArgumentParser(description="Context Compressor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_c = sub.add_parser("compress")
    p_c.add_argument("--file", required=True)
    p_c.add_argument("--target-tokens", type=int, required=True)
    p_c.add_argument("--output", default=None)

    p_h = sub.add_parser("summarize-history")
    p_h.add_argument("--file", required=True)

    p_t = sub.add_parser("truncate")
    p_t.add_argument("--file", required=True)
    p_t.add_argument("--max-tokens", type=int, required=True)
    p_t.add_argument("--strategy", choices=["head", "tail", "middle"], default="tail")

    p_e = sub.add_parser("estimate-tokens")
    p_e.add_argument("--file", required=True)

    args = parser.parse_args()
    dispatch = {
        "compress": compress,
        "summarize-history": summarize_history,
        "truncate": truncate,
        "estimate-tokens": estimate_tokens,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
