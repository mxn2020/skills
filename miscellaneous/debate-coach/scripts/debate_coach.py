#!/usr/bin/env python3
"""
Debate Coach — OC-0176
Argue both sides of a topic and score the strength of arguments.
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

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str, system_msg: str = "") -> str:
    system = system_msg or (
        "You are an expert debate coach and critical thinking instructor. "
        "Provide balanced, well-reasoned analysis."
    )
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1000,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def both_sides(topic: str, depth: str = "standard"):
    points = 5 if depth == "detailed" else 3

    prompt = (
        f"Present {points} strong arguments FOR and {points} strong arguments AGAINST:\n"
        f"Topic: '{topic}'\n\n"
        "Format:\n"
        "## FOR\n"
        f"(Numbered list of {points} compelling arguments with brief explanation)\n\n"
        "## AGAINST\n"
        f"(Numbered list of {points} compelling arguments with brief explanation)\n\n"
        "## Nuance\n"
        "(2-3 sentences on where both sides have valid points)"
    )
    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}Both Sides: {topic}{RESET}")
    print(f"{BOLD}{'='*55}{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def steelman(argument: str, side: str = "against"):
    prompt = (
        f"Build the strongest possible (steelman) version of the {side} position:\n"
        f"Original argument: '{argument}'\n\n"
        "Provide:\n"
        "1. **Steelman Version** — The most compelling, charitable version of this position\n"
        "2. **Key Evidence** — Best supporting evidence or reasoning\n"
        "3. **Strongest Objection** — The most powerful counter-argument\n"
        "4. **Weaknesses** — Honest assessment of the argument's limitations"
    )
    print(f"{YELLOW}Steelmanning the {side} position...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Steelman Analysis:{RESET}\n")
    print(result)
    print()


def score(argument: str):
    prompt = (
        f"Score this argument on multiple dimensions (1-10 each):\n"
        f"Argument: '{argument}'\n\n"
        "Evaluate:\n"
        "- **Logic** (1-10): Is the reasoning valid and sound?\n"
        "- **Evidence** (1-10): How well-supported are the claims?\n"
        "- **Clarity** (1-10): Is the argument clear and well-structured?\n"
        "- **Persuasiveness** (1-10): Would this convince a neutral audience?\n"
        "- **Fallacies** (0-10, lower = more fallacies): Are logical fallacies present?\n\n"
        "**Overall Score** (1-10)\n\n"
        "**Feedback**: What makes this argument strong/weak?\n"
        "**Improvements**: 2-3 specific ways to strengthen it"
    )
    print(f"{YELLOW}Scoring argument...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Argument Score:{RESET}\n")
    print(result)
    print()


def practice(topic: str, side: str = "for", rounds: int = 3):
    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}Debate Practice: {topic}{RESET}")
    print(f"{BOLD}Your side: {side.upper()}{RESET}")
    print(f"{BOLD}{'='*55}{RESET}\n")
    print(f"  Argue {CYAN}{side.upper()}{RESET} the proposition: '{topic}'")
    print(f"  The AI will play the opposing side for {rounds} rounds.\n")
    print(f"{YELLOW}Press Enter after each argument...{RESET}\n")

    # Opening statement from AI opponent
    opponent_side = "against" if side.lower() == "for" else "for"
    context = [
        f"We are debating: '{topic}'. You are arguing {opponent_side}. "
        "The user is arguing the opposite side. Be challenging but fair."
    ]
    ai_opening = _complete(
        f"Open the debate {opponent_side} the proposition: '{topic}'. Make a strong 3-point opening statement.",
        system_msg=" ".join(context)
    )
    print(f"{CYAN}AI Opponent:{RESET}")
    print(f"  {ai_opening}\n")

    history = [{"role": "user", "content": ai_opening}]

    for rnd in range(1, rounds + 1):
        print(f"{BOLD}Round {rnd} — Your turn:{RESET}")
        try:
            user_arg = input("  Your argument: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_arg:
            continue

        # AI responds
        history.append({"role": "assistant", "content": user_arg})
        messages = [
            {"role": "system", "content": f"You are debating {opponent_side} '{topic}'. Respond to the user's argument."},
        ] + history[-6:]

        resp = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 300},
            timeout=60,
        )
        if resp.ok:
            ai_resp = resp.json()["choices"][0]["message"]["content"].strip()
            history.append({"role": "user", "content": ai_resp})
            print(f"\n{CYAN}AI Opponent:{RESET}")
            print(f"  {ai_resp}\n")

    # Final scoring
    all_user = [m["content"] for m in history if m["role"] == "assistant"]
    if all_user:
        combined = " ".join(all_user)
        print(f"\n{YELLOW}Generating feedback on your performance...{RESET}\n")
        feedback = _complete(
            f"Rate these debate arguments (1-10 scale) and provide constructive feedback:\n{combined}"
        )
        print(f"{BOLD}Performance Feedback:{RESET}\n{feedback}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="debate_coach.py",
        description="Debate Coach — OC-0176"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("both-sides", help="Arguments for and against a topic")
    p.add_argument("--topic", required=True)
    p.add_argument("--depth", default="standard", choices=["standard", "detailed"])

    p = sub.add_parser("steelman", help="Build strongest version of an argument")
    p.add_argument("--argument", required=True)
    p.add_argument("--side", default="against", choices=["for", "against"])

    p = sub.add_parser("score", help="Score an argument's logical strength")
    p.add_argument("--argument", required=True)

    p = sub.add_parser("practice", help="Interactive debate practice")
    p.add_argument("--topic", required=True)
    p.add_argument("--side", default="for", choices=["for", "against"])
    p.add_argument("--rounds", type=int, default=3)

    args = parser.parse_args()
    dispatch = {
        "both-sides": lambda: both_sides(args.topic, args.depth),
        "steelman":   lambda: steelman(args.argument, args.side),
        "score":      lambda: score(args.argument),
        "practice":   lambda: practice(args.topic, args.side, args.rounds),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
