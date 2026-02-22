#!/usr/bin/env python3
"""
Mental Load Journal — OC-0149
Prompt daily reflection and surface patterns over time.
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

LOG_FILE   = os.path.expanduser("~/.mental_journal.json")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

REFLECTION_PROMPTS = [
    "What was the most challenging thing today, and how did you handle it?",
    "On a scale of 1-10, what's your mental load right now and why?",
    "What three things are taking up the most mental energy today?",
    "Is there anything you're avoiding? What would it take to address it?",
    "What are you grateful for today, even in a small way?",
]


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
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a compassionate journaling coach. Be warm, non-judgmental, "
                        "and insightful. Ask one follow-up question when appropriate."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 400,
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


def reflect():
    from datetime import datetime as dt
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_of_week = dt.now().strftime("%A")

    print(f"\n{BOLD}{CYAN}{'='*55}{RESET}")
    print(f"{BOLD}Mental Load Journal — {today} ({day_of_week}){RESET}")
    print(f"{CYAN}{'='*55}{RESET}\n")

    entries = []
    for i, prompt in enumerate(REFLECTION_PROMPTS, 1):
        print(f"{BOLD}Q{i}: {prompt}{RESET}")
        try:
            response = input("  → ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not response:
            continue
        entries.append({"prompt": prompt, "response": response})

        # AI follow-up
        ai_response = _complete(
            f"The person was asked: '{prompt}'\nThey responded: '{response}'\n\n"
            "Give a brief, warm acknowledgment and one clarifying or deepening question."
        )
        print(f"\n  {CYAN}{ai_response}{RESET}\n")
        try:
            followup = input("  → ").strip()
            if followup:
                entries[-1]["followup"] = followup
        except (EOFError, KeyboardInterrupt):
            print()

    if not entries:
        print(f"{YELLOW}No entries recorded.{RESET}")
        return

    # Mood score
    try:
        print(f"\n{BOLD}Overall mood today (1-10):{RESET}")
        mood = int(input("  → ").strip())
    except (ValueError, EOFError, KeyboardInterrupt):
        mood = 5

    log = _load_log()
    log.append({
        "date": today,
        "type": "reflection",
        "entries": entries,
        "mood": mood,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_log(log)

    print(f"\n{GREEN}Reflection saved. Mood: {mood}/10{RESET}\n")


def journal(text: str):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Get AI insight on the entry
    insight = _complete(
        f"Journal entry: '{text}'\n\n"
        "Provide a brief, empathetic reflection (2-3 sentences) and one gentle insight "
        "about what might be underlying these thoughts or feelings."
    )

    log = _load_log()

    # Simple mood inference
    mood_prompt = (
        f"Rate the emotional tone of this text on a scale 1-10 "
        f"(1=very negative, 10=very positive). Respond with just the number:\n{text}"
    )
    try:
        mood_resp = _complete(mood_prompt)
        mood = int("".join(c for c in mood_resp if c.isdigit())[:1] or "5")
    except (ValueError, TypeError):
        mood = 5

    log.append({
        "date": today,
        "type": "journal",
        "text": text,
        "mood": mood,
        "ai_insight": insight,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_log(log)

    print(f"\n{CYAN}AI Reflection:{RESET}")
    print(f"  {insight}")
    print(f"\n{GREEN}Entry saved (inferred mood: {mood}/10){RESET}\n")


def patterns(days: int = 30):
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [r for r in log if r.get("date", "") >= cutoff]

    if not recent:
        print(f"{YELLOW}No journal entries in the last {days} days.{RESET}")
        return

    # Compile all text
    all_text = []
    for r in recent:
        if r.get("type") == "journal":
            all_text.append(r.get("text", ""))
        elif r.get("type") == "reflection":
            for e in r.get("entries", []):
                all_text.append(e.get("response", ""))

    combined = " ".join(all_text[:3000])
    prompt = (
        f"Analyze these journal entries from the last {days} days and identify:\n"
        "1. Top 3 recurring themes or stressors\n"
        "2. Emotional patterns (what triggers positive/negative states)\n"
        "3. One actionable insight or suggestion\n\n"
        f"Entries: {combined}"
    )

    print(f"{YELLOW}Analyzing {len(recent)} entries over {days} days...{RESET}\n")
    analysis = _complete(prompt)
    print(f"{BOLD}Patterns & Insights:{RESET}\n")
    print(analysis)
    print()


def mood_trend(days: int = 14):
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = sorted(
        [r for r in log if r.get("date", "") >= cutoff and r.get("mood")],
        key=lambda r: r.get("date", ""),
    )

    if not recent:
        print(f"{YELLOW}No mood data for the last {days} days.{RESET}")
        return

    print(f"\n{BOLD}Mood Trend — Last {days} Days:{RESET}\n")
    for r in recent:
        mood = r.get("mood", 5)
        bar_len = mood * 2
        bar = "█" * bar_len
        color = GREEN if mood >= 7 else (YELLOW if mood >= 5 else RED)
        print(f"  {CYAN}{r.get('date')}{RESET}  {color}{bar} {mood}/10{RESET}  "
              f"[{r.get('type', '?')}]")

    moods = [r.get("mood", 5) for r in recent]
    avg = sum(moods) / len(moods)
    print(f"\n  Average: {avg:.1f}/10  |  Best: {max(moods)}/10  |  Lowest: {min(moods)}/10")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="mental_load_journal.py",
        description="Mental Load Journal — OC-0149"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("reflect", help="Start guided daily reflection")

    p = sub.add_parser("journal", help="Write a journal entry")
    p.add_argument("--text", required=True, help="Journal entry text")

    p = sub.add_parser("patterns", help="Surface patterns in entries")
    p.add_argument("--days", type=int, default=30)

    p = sub.add_parser("mood-trend", help="View mood trend")
    p.add_argument("--days", type=int, default=14)

    args = parser.parse_args()
    dispatch = {
        "reflect":    lambda: reflect(),
        "journal":    lambda: journal(args.text),
        "patterns":   lambda: patterns(args.days),
        "mood-trend": lambda: mood_trend(args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
