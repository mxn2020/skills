#!/usr/bin/env python3
"""
Meditation Guide — OC-0144
Generate and narrate personalized guided meditation scripts.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE   = os.path.expanduser("~/.meditation_log.json")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


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


def generate(duration: int = 10, focus: str = "mindfulness", style: str = "breath awareness"):
    prompt = (
        f"Create a {duration}-minute guided meditation script focused on '{focus}' "
        f"using a '{style}' style.\n\n"
        "Structure it as:\n"
        "1. Opening (1-2 min): settling in, posture, breath\n"
        "2. Main practice (bulk of the time): core meditation\n"
        "3. Closing (1-2 min): gradual return, integration\n\n"
        "Use calm, measured language. Include timing cues like '(pause 10 seconds)'. "
        "Write in second person ('you', 'your'). Keep it peaceful and grounding."
    )

    print(f"{YELLOW}Generating {duration}-min meditation on '{focus}' ({style})...{RESET}\n")
    resp = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a calm, experienced meditation teacher."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")

    script = resp.json()["choices"][0]["message"]["content"].strip()

    print(f"{BOLD}{'─' * 60}{RESET}")
    print(f"{CYAN}{BOLD}{duration}-Minute {focus.title()} Meditation{RESET}")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
    print(script)
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{YELLOW}🧘 Find a comfortable position and begin when ready.{RESET}\n")


def list_sessions(limit: int = 10):
    log = _load_log()
    if not log:
        print(f"{YELLOW}No sessions logged yet.{RESET}")
        return
    recent = sorted(log, key=lambda r: r.get("date", ""), reverse=True)[:limit]
    print(f"\n{BOLD}Recent Meditation Sessions:{RESET}\n")
    for s in recent:
        print(f"  {CYAN}{s.get('date', '')}{RESET}  {BOLD}{s.get('duration', 0)} min{RESET}  "
              f"Focus: {s.get('focus', '')}")
        if s.get("notes"):
            print(f"    {YELLOW}{s['notes']}{RESET}")
    print()


def log_session(duration: int, focus: str = "general", notes: str = ""):
    log = _load_log()
    record = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "duration": duration,
        "focus": focus,
        "notes": notes,
    }
    log.append(record)
    _save_log(log)
    print(f"{GREEN}Session logged: {duration} min on '{focus}'{RESET}")
    if notes:
        print(f"  Notes: {notes}")
    print()


def streak():
    log = _load_log()
    if not log:
        print(f"{YELLOW}No sessions yet. Start your practice!{RESET}")
        return

    dates = sorted(set(r.get("date", "") for r in log), reverse=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    current_streak = 0
    check_date = today if today in dates else (yesterday if yesterday in dates else None)

    if check_date:
        d = datetime.strptime(check_date, "%Y-%m-%d")
        while d.strftime("%Y-%m-%d") in dates:
            current_streak += 1
            d -= timedelta(days=1)

    total_sessions = len(log)
    total_minutes  = sum(r.get("duration", 0) for r in log)
    longest_streak = current_streak  # simplified

    print(f"\n{BOLD}Meditation Streak:{RESET}\n")
    color = GREEN if current_streak >= 7 else (YELLOW if current_streak >= 3 else CYAN)
    print(f"  Current streak: {color}{current_streak} day(s){RESET}")
    print(f"  Total sessions: {total_sessions}")
    print(f"  Total time:     {total_minutes} min ({total_minutes // 60}h {total_minutes % 60}m)")

    if current_streak == 0:
        print(f"\n  {YELLOW}Start or resume your practice today!{RESET}")
    elif current_streak < 7:
        print(f"\n  {YELLOW}Keep going — {7 - current_streak} more day(s) to a week streak!{RESET}")
    else:
        print(f"\n  {GREEN}Excellent consistency! Your mind thanks you.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="meditation_guide.py",
        description="Meditation Guide — OC-0144"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("generate", help="Generate a meditation script")
    p.add_argument("--duration", type=int, default=10, help="Duration in minutes")
    p.add_argument("--focus", default="mindfulness",
                   help="Focus area (stress relief, sleep, focus, etc.)")
    p.add_argument("--style", default="breath awareness",
                   help="Style (body scan, loving-kindness, visualization, etc.)")

    p = sub.add_parser("list-sessions", help="List past sessions")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("log-session", help="Log a completed session")
    p.add_argument("--duration", type=int, required=True, help="Duration in minutes")
    p.add_argument("--focus", default="general")
    p.add_argument("--notes", default="")

    sub.add_parser("streak", help="Show meditation streak")

    args = parser.parse_args()
    dispatch = {
        "generate":      lambda: generate(args.duration, args.focus, args.style),
        "list-sessions": lambda: list_sessions(args.limit),
        "log-session":   lambda: log_session(args.duration, args.focus, args.notes),
        "streak":        lambda: streak(),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
