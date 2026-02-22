#!/usr/bin/env python3
"""
Language Tutor — OC-0175
Run interactive vocabulary drills and grammar corrections.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PROGRESS_FILE = os.path.expanduser("~/.language_tutor_progress.json")
OPENAI_URL    = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str, system_msg: str = "") -> str:
    system = system_msg or "You are a patient, encouraging language tutor."
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 600,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _load_progress() -> dict:
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"sessions": [], "stats": {}}


def _save_progress(data: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def vocab_drill(language: str, level: str = "beginner", count: int = 10,
                topic: str = ""):
    topic_hint = f" on the topic of '{topic}'" if topic else ""
    prompt = (
        f"Create {count} vocabulary flashcards for {language} ({level} level){topic_hint}.\n\n"
        "Format EXACTLY as JSON array:\n"
        '[{"word": "...", "translation": "...", "example": "...", "pronunciation": "..."}]\n\n'
        "Include pronunciation guide for non-Latin scripts."
    )
    print(f"\n{YELLOW}Preparing {count} {language.capitalize()} vocabulary cards ({level})...{RESET}\n")
    raw = _complete(prompt)

    # Extract JSON
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    cards = []
    if start >= 0 and end > 0:
        try:
            cards = json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    if not cards:
        print(f"{YELLOW}Generating drill in plain format...{RESET}\n")
        print(raw)
        return

    score = 0
    print(f"{BOLD}{language.capitalize()} Vocabulary Drill{RESET}\n")
    print("Press Enter to reveal answer, or type your guess.\n")

    for i, card in enumerate(cards, 1):
        word  = card.get("word", "")
        trans = card.get("translation", "")
        ex    = card.get("example", "")
        pron  = card.get("pronunciation", "")

        print(f"{CYAN}[{i}/{count}]{RESET} {BOLD}{word}{RESET}")
        if pron:
            print(f"       ({pron})")

        try:
            guess = input("  Your translation: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not guess:
            print(f"  Answer: {GREEN}{trans}{RESET}")
        elif guess.lower() in trans.lower() or trans.lower() in guess.lower():
            print(f"  {GREEN}Correct! {trans}{RESET}")
            score += 1
        else:
            print(f"  {RED}Incorrect.{RESET} Answer: {GREEN}{trans}{RESET}")

        if ex:
            print(f"  Example: {YELLOW}{ex}{RESET}")
        print()

    total = min(len(cards), count)
    pct   = int(score / total * 100) if total else 0
    color = GREEN if pct >= 80 else (YELLOW if pct >= 60 else RED)
    print(f"{BOLD}Score: {color}{score}/{total} ({pct}%){RESET}")

    # Save progress
    prog = _load_progress()
    prog.setdefault("sessions", []).append({
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "language": language,
        "type": "vocab",
        "level": level,
        "score": score,
        "total": total,
    })
    _save_progress(prog)
    print()


def grammar_check(text: str, language: str = "english"):
    prompt = (
        f"Check the {language} grammar in this sentence: '{text}'\n\n"
        "Provide:\n"
        "1. **Corrected sentence** (if errors exist)\n"
        "2. **Errors found** — list each error with explanation\n"
        "3. **Grammar rule** — the relevant rule for each error\n"
        "4. **Alternative phrasing** (if applicable)\n\n"
        "If the sentence is correct, confirm it and explain why it's correct."
    )
    print(f"\n{YELLOW}Checking grammar...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Grammar Check:{RESET}\n")
    print(result)
    print()


def translate(text: str, from_lang: str, to_lang: str, explain: bool = False):
    explain_note = (
        "\n\nAlso provide:\n"
        "- Literal translation vs. natural translation (if different)\n"
        "- Cultural context or nuance\n"
        "- Alternative translations"
    ) if explain else ""

    prompt = (
        f"Translate from {from_lang} to {to_lang}: '{text}'"
        + explain_note
    )
    result = _complete(prompt)
    print(f"\n{BOLD}Translation ({from_lang} → {to_lang}):{RESET}\n")
    print(result)
    print()


def lesson(language: str, topic: str, level: str = "intermediate"):
    prompt = (
        f"Teach a {level}-level mini-lesson on '{topic}' in {language}.\n\n"
        "Format:\n"
        "## Explanation (2-3 sentences)\n\n"
        "## Rules\n"
        "(numbered list of key rules)\n\n"
        "## Examples\n"
        "(5 example sentences with translations)\n\n"
        "## Common Mistakes to Avoid\n"
        "(2-3 common errors)\n\n"
        "## Quick Practice\n"
        "(2 fill-in-the-blank exercises with answers)"
    )
    print(f"\n{YELLOW}Preparing {language.capitalize()} lesson on '{topic}'...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}{language.capitalize()} Lesson: {topic}{RESET}\n")
    print(result)
    print()


def progress():
    prog = _load_progress()
    sessions = prog.get("sessions", [])
    if not sessions:
        print(f"{YELLOW}No learning sessions recorded yet.{RESET}")
        return

    print(f"\n{BOLD}Learning Progress:{RESET}\n")
    by_lang: dict = {}
    for s in sessions:
        lang = s.get("language", "unknown")
        by_lang.setdefault(lang, {"sessions": 0, "score": 0, "total": 0})
        by_lang[lang]["sessions"] += 1
        by_lang[lang]["score"]    += s.get("score", 0)
        by_lang[lang]["total"]    += s.get("total", 0)

    for lang, stats in by_lang.items():
        total    = stats["total"]
        score    = stats["score"]
        pct      = int(score / total * 100) if total else 0
        sessions_count = stats["sessions"]
        color = GREEN if pct >= 80 else (YELLOW if pct >= 60 else RED)
        print(f"  {CYAN}{lang.capitalize()}{RESET}  "
              f"{sessions_count} session(s)  "
              f"Accuracy: {color}{pct}%{RESET} ({score}/{total})")

    print(f"\n  Total sessions: {len(sessions)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="language_tutor.py",
        description="Language Tutor — OC-0175"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("vocab-drill", help="Run vocabulary quiz")
    p.add_argument("--language", required=True)
    p.add_argument("--level", default="beginner",
                   choices=["beginner", "intermediate", "advanced"])
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--topic", default="")

    p = sub.add_parser("grammar-check", help="Check and correct grammar")
    p.add_argument("--text", required=True)
    p.add_argument("--language", default="english")

    p = sub.add_parser("translate", help="Translate with explanation")
    p.add_argument("--text", required=True)
    p.add_argument("--from-lang", required=True)
    p.add_argument("--to-lang", required=True)
    p.add_argument("--explain", action="store_true")

    p = sub.add_parser("lesson", help="Get a grammar lesson")
    p.add_argument("--language", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--level", default="intermediate",
                   choices=["beginner", "intermediate", "advanced"])

    sub.add_parser("progress", help="View learning progress")

    args = parser.parse_args()
    dispatch = {
        "vocab-drill":    lambda: vocab_drill(args.language, args.level,
                                               args.count, args.topic),
        "grammar-check":  lambda: grammar_check(args.text, args.language),
        "translate":      lambda: translate(args.text, args.from_lang,
                                             args.to_lang, args.explain),
        "lesson":         lambda: lesson(args.language, args.topic, args.level),
        "progress":       lambda: progress(),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
