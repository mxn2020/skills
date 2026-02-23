#!/usr/bin/env python3
"""
Symptom Checker — OC-0146
Basic triage based on described symptoms. NOT a substitute for medical advice.
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

LOG_FILE   = os.path.expanduser("~/.symptom_log.json")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

DISCLAIMER = (
    f"\n{YELLOW}⚠  DISCLAIMER: This tool provides general information only and is NOT "
    f"a substitute for professional medical advice, diagnosis, or treatment. "
    f"Always consult a qualified healthcare provider for medical concerns.{RESET}\n"
)

EMERGENCY_SYMPTOMS = [
    "chest pain", "difficulty breathing", "shortness of breath", "stroke",
    "seizure", "unconscious", "severe bleeding", "allergic reaction",
    "anaphylaxis", "heart attack", "suicidal", "overdose",
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
                        "You are a medical information assistant providing general health information. "
                        "Always include appropriate disclaimers and recommend consulting a doctor. "
                        "Never provide a definitive diagnosis."
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


def check(symptoms: str):
    print(DISCLAIMER)
    # Check for emergency keywords first
    lower_syms = symptoms.lower()
    for emergency in EMERGENCY_SYMPTOMS:
        if emergency in lower_syms:
            print(f"{RED}{BOLD}⚠ POTENTIAL EMERGENCY DETECTED{RESET}")
            print(f"{RED}Symptoms mentioning '{emergency}' may require IMMEDIATE medical attention.{RESET}")
            print(f"{RED}Call emergency services (911/112) or go to the nearest emergency room.{RESET}\n")

    prompt = (
        f"A person reports these symptoms: {symptoms}\n\n"
        "Provide:\n"
        "1. Possible common explanations (not a diagnosis)\n"
        "2. Urgency level (Low/Medium/High/Emergency) with brief reason\n"
        "3. Self-care suggestions if appropriate\n"
        "4. Clear recommendation on when to see a doctor\n\n"
        "Be concise and include appropriate medical disclaimers."
    )

    print(f"{YELLOW}Analyzing symptoms: {symptoms}{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Symptom Analysis:{RESET}\n")
    print(result)
    print()


def urgent(symptoms: str):
    print(DISCLAIMER)
    lower = symptoms.lower()
    for emergency in EMERGENCY_SYMPTOMS:
        if emergency in lower:
            print(f"{RED}{BOLD}🚨 SEEK EMERGENCY CARE IMMEDIATELY{RESET}")
            print(f"{RED}Symptoms include '{emergency}' which may indicate a life-threatening condition.{RESET}")
            print(f"{RED}Call 911 or go to the nearest emergency room NOW.{RESET}")
            return

    prompt = (
        f"Symptoms: {symptoms}\n\n"
        "Is this an emergency requiring immediate care? "
        "Respond with: URGENT, SEE DOCTOR TODAY, MONITOR AT HOME, or NOT URGENT. "
        "Give a one-line reason. Be direct and conservative (err on side of caution)."
    )
    result = _complete(prompt)
    print(f"{BOLD}Urgency Assessment:{RESET}")
    if "URGENT" in result or "EMERGENCY" in result:
        print(f"{RED}{result}{RESET}")
    elif "TODAY" in result:
        print(f"{YELLOW}{result}{RESET}")
    else:
        print(f"{GREEN}{result}{RESET}")
    print()


def log_symptom(symptom: str, severity: int = 5, notes: str = ""):
    if not 1 <= severity <= 10:
        _die("Severity must be 1-10.")
    log = _load_log()
    record = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M"),
        "symptom": symptom,
        "severity": severity,
        "notes": notes,
    }
    log.append(record)
    _save_log(log)

    sev_color = RED if severity >= 8 else (YELLOW if severity >= 5 else GREEN)
    print(f"{GREEN}Symptom logged:{RESET}")
    print(f"  Symptom:  {symptom}")
    print(f"  Severity: {sev_color}{severity}/10{RESET}")
    if notes:
        print(f"  Notes:    {notes}")
    print()


def history(days: int = 7):
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [r for r in log if r.get("date", "") >= cutoff]

    if not recent:
        print(f"{YELLOW}No symptoms logged in the last {days} days.{RESET}")
        return

    print(f"\n{BOLD}Symptom History — Last {days} Days:{RESET}\n")
    recent.sort(key=lambda r: r.get("date", "") + r.get("time", ""))
    for r in recent:
        sev = r.get("severity", 0)
        sev_color = RED if sev >= 8 else (YELLOW if sev >= 5 else GREEN)
        print(f"  {CYAN}{r.get('date')} {r.get('time', '')}{RESET}  "
              f"{BOLD}{r.get('symptom', '')}{RESET}  "
              f"severity: {sev_color}{sev}/10{RESET}")
        if r.get("notes"):
            print(f"    {r['notes']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="symptom_checker.py",
        description="Symptom Checker — OC-0146 (NOT medical advice)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check", help="Analyze symptoms")
    p.add_argument("--symptoms", required=True, help="Describe your symptoms")

    p = sub.add_parser("urgent", help="Quick urgency assessment")
    p.add_argument("--symptoms", required=True)

    p = sub.add_parser("log-symptom", help="Log a symptom")
    p.add_argument("--symptom", required=True)
    p.add_argument("--severity", type=int, default=5, help="Severity 1-10")
    p.add_argument("--notes", default="")

    p = sub.add_parser("history", help="View symptom history")
    p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()
    dispatch = {
        "check":        lambda: check(args.symptoms),
        "urgent":       lambda: urgent(args.symptoms),
        "log-symptom":  lambda: log_symptom(args.symptom, args.severity, args.notes),
        "history":      lambda: history(args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
