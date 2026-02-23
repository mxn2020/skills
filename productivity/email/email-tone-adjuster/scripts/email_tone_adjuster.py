#!/usr/bin/env python3
"""
Email Tone Adjuster — OC-0139
Rewrite email drafts to match a target tone using OpenAI.
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

TONE_PROMPTS = {
    "formal": (
        "Rewrite this email in a formal, professional tone. Use complete sentences, "
        "avoid contractions, and maintain a respectful, business-appropriate register."
    ),
    "concise": (
        "Rewrite this email to be extremely concise and direct. Remove all filler words, "
        "keep only essential information, and aim for maximum clarity in minimum words."
    ),
    "friendly": (
        "Rewrite this email in a warm, friendly tone. Be personable, approachable, and "
        "conversational while remaining professional."
    ),
    "professional": (
        "Rewrite this email in a clear, professional tone. Be direct and courteous, "
        "use proper grammar, and ensure the message is well-structured."
    ),
    "assertive": (
        "Rewrite this email in a confident, assertive tone. Be clear about expectations, "
        "use active voice, and avoid wishy-washy language."
    ),
    "empathetic": (
        "Rewrite this email in an empathetic, understanding tone. Acknowledge the recipient's "
        "perspective, be supportive, and show genuine care while still being professional."
    ),
}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 600},
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _read_input(text: str = None, file: str = None) -> str:
    if text:
        return text
    if file:
        try:
            with open(file, "r") as f:
                return f.read()
        except OSError as e:
            _die(f"Could not read file '{file}': {e}")
    _die("Provide either --text or --file.")


def adjust(email_text: str, tone: str):
    if tone not in TONE_PROMPTS:
        available = ", ".join(TONE_PROMPTS.keys())
        _die(f"Unknown tone '{tone}'. Available: {available}")

    instruction = TONE_PROMPTS[tone]
    prompt = f"{instruction}\n\nOriginal email:\n\n{email_text}"

    print(f"{YELLOW}Adjusting tone to: {BOLD}{tone}{RESET}...\n")
    result = _complete(prompt, system="You are an expert email editor. Output only the rewritten email, no preamble.")

    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"{GREEN}Rewritten ({tone}):{RESET}\n")
    print(result)
    print(f"{BOLD}{'─'*60}{RESET}\n")


def analyze(email_text: str):
    prompt = (
        "Analyze the tone and style of this email. Identify:\n"
        "1. Current tone (e.g. formal, casual, passive-aggressive, friendly)\n"
        "2. Sentiment (positive, neutral, negative)\n"
        "3. Clarity (1-10)\n"
        "4. Potential improvements\n\n"
        f"Email:\n{email_text}"
    )
    print(f"{YELLOW}Analyzing email tone...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Tone Analysis:{RESET}\n")
    print(result)
    print()


def suggest_subject(email_text: str, count: int = 3):
    prompt = (
        f"Generate {count} compelling subject line options for this email. "
        "Make them clear, specific, and appropriate for the tone. "
        "Number each option.\n\n"
        f"Email body:\n{email_text}"
    )
    print(f"{YELLOW}Generating {count} subject line suggestion(s)...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Subject Line Suggestions:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="email_tone_adjuster.py",
        description="Email Tone Adjuster — OC-0139"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("adjust", help="Rewrite email in a new tone")
    p.add_argument("--text", default=None, help="Email text inline")
    p.add_argument("--file", default=None, help="Path to email draft file")
    p.add_argument("--tone", required=True,
                   choices=list(TONE_PROMPTS.keys()),
                   help="Target tone")

    p = sub.add_parser("analyze", help="Analyze email tone")
    p.add_argument("--text", default=None)
    p.add_argument("--file", default=None)

    p = sub.add_parser("suggest-subject", help="Generate subject line suggestions")
    p.add_argument("--text", default=None)
    p.add_argument("--file", default=None)
    p.add_argument("--count", type=int, default=3, help="Number of suggestions (default: 3)")

    args = parser.parse_args()
    text = _read_input(getattr(args, "text", None), getattr(args, "file", None))

    dispatch = {
        "adjust":           lambda: adjust(text, args.tone),
        "analyze":          lambda: analyze(text),
        "suggest-subject":  lambda: suggest_subject(text, args.count),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
