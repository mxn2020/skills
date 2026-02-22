#!/usr/bin/env python3
"""
Dream Journal — OC-0172
Log and interpret dreams using symbolic analysis.
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE   = os.path.expanduser("~/.dream_journal.json")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str) -> str:
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a thoughtful dream analyst with knowledge of Jungian psychology, "
                        "symbolism, and modern dream theory. Provide insightful, respectful "
                        "interpretations without being prescriptive."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 600,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _load_log() -> list:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_log(data: list):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_dream(dream_text: str, mood: str = "", lucid: bool = False):
    log = _load_log()
    did = str(uuid.uuid4())[:8]
    record = {
        "id": did,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M"),
        "dream": dream_text,
        "mood": mood,
        "lucid": lucid,
        "interpretation": None,
    }
    log.append(record)
    _save_log(log)

    print(f"{GREEN}Dream logged:{RESET}")
    print(f"  ID:    {CYAN}{did}{RESET}")
    print(f"  Date:  {record['date']} {record['time']}")
    if mood:
        print(f"  Mood:  {mood}")
    if lucid:
        print(f"  Type:  Lucid dream")
    print(f"\n  {dream_text[:100]}...")
    print()


def interpret(dream_id: str):
    log = _load_log()
    entry = next((e for e in log if e.get("id") == dream_id), None)
    if not entry:
        _die(f"Dream '{dream_id}' not found. Use 'list' to see IDs.")

    dream_text = entry.get("dream", "")
    prompt = (
        f"Analyze this dream: '{dream_text}'\n\n"
        "Provide:\n"
        "1. **Key Symbols** — What major symbols appear and their common meanings\n"
        "2. **Emotional Themes** — The emotional undercurrents\n"
        "3. **Possible Interpretations** — 2-3 different perspectives\n"
        "4. **Questions to Reflect On** — 2-3 introspective questions\n\n"
        "Be thoughtful and avoid being overly definitive — dreams are personal."
    )
    print(f"{YELLOW}Interpreting dream {dream_id}...{RESET}\n")
    result = _complete(prompt)

    # Save interpretation
    entry["interpretation"] = result
    _save_log(log)

    print(f"{BOLD}Dream Interpretation:{RESET}\n")
    print(result)
    print()


def list_dreams(limit: int = 10):
    log = _load_log()
    if not log:
        print(f"{YELLOW}No dreams recorded yet.{RESET}")
        return

    recent = sorted(log, key=lambda e: e.get("date", ""), reverse=True)[:limit]
    print(f"\n{BOLD}Dream Journal ({len(log)} total):{RESET}\n")
    for entry in recent:
        did     = entry.get("id", "")
        date    = entry.get("date", "")
        preview = entry.get("dream", "")[:70]
        has_int = "✓" if entry.get("interpretation") else " "
        lucid   = f"{CYAN}[lucid]{RESET} " if entry.get("lucid") else ""
        print(f"  {CYAN}{did}{RESET}  {date}  {lucid}{GREEN}{has_int} interpreted{RESET}")
        print(f"    {preview}...")
        print()


def themes(days: int = 30):
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [e for e in log if e.get("date", "") >= cutoff]

    if not recent:
        print(f"{YELLOW}No dreams in the last {days} days.{RESET}")
        return

    combined = " ".join(e.get("dream", "")[:200] for e in recent)

    prompt = (
        f"Analyze {len(recent)} dream descriptions and identify recurring themes.\n\n"
        "Provide:\n"
        "1. **Top 3 Recurring Themes** with frequency and meaning\n"
        "2. **Dominant Emotions** across dreams\n"
        "3. **Recurring Symbols** (if any)\n"
        "4. **Overall Pattern** — what this period of dreaming might reflect\n\n"
        f"Dreams:\n{combined[:3000]}"
    )
    print(f"{YELLOW}Analyzing themes in {len(recent)} dreams from the last {days} days...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Recurring Themes:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="dream_journal.py",
        description="Dream Journal — OC-0172"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log", help="Log a dream")
    p.add_argument("--dream", required=True, help="Dream description")
    p.add_argument("--mood", default="", help="Your mood upon waking")
    p.add_argument("--lucid", action="store_true", help="Was it a lucid dream?")

    p = sub.add_parser("interpret", help="Interpret a dream")
    p.add_argument("--dream-id", required=True)

    p = sub.add_parser("list", help="List past dreams")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("themes", help="Analyze recurring themes")
    p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()
    dispatch = {
        "log":       lambda: log_dream(args.dream, args.mood, args.lucid),
        "interpret": lambda: interpret(args.dream_id),
        "list":      lambda: list_dreams(args.limit),
        "themes":    lambda: themes(args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
