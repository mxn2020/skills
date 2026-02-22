#!/usr/bin/env python3
"""
Legal Document Scanner — OC-0171
Summarize TOS changes, lease agreements, and contracts.
NOT legal advice — always consult a qualified attorney.
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
DISCLAIMER = (
    f"\n{YELLOW}⚠  DISCLAIMER: This analysis is for informational purposes only and "
    f"does NOT constitute legal advice. Always consult a qualified attorney "
    f"before making decisions based on legal documents.{RESET}\n"
)


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
        "You are a legal document analyst. Provide clear, accessible summaries "
        "and analysis in plain English. Always include appropriate disclaimers "
        "that this is not legal advice."
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


def _read_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        _die(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def summarize(filepath: str, doc_type: str = "auto"):
    text = _read_file(filepath)[:5000]
    print(DISCLAIMER)

    doc_hint = f"This is a {doc_type}. " if doc_type != "auto" else ""
    prompt = (
        f"{doc_hint}Summarize this legal document in plain English for a non-lawyer.\n\n"
        "Provide:\n"
        "1. **What is this document?** (2 sentences)\n"
        "2. **Key terms and conditions** (5 bullet points)\n"
        "3. **Your rights and obligations** (3-5 points)\n"
        "4. **Important dates or deadlines**\n"
        "5. **One-sentence overall assessment**\n\n"
        f"Document:\n{text}"
    )
    print(f"{YELLOW}Analyzing document...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Document Summary:{RESET}\n")
    print(result)
    print()


def flag_risks(filepath: str):
    text = _read_file(filepath)[:5000]
    print(DISCLAIMER)

    prompt = (
        "Analyze this legal document for potentially problematic or unfair clauses.\n\n"
        "Identify:\n"
        "🔴 **HIGH RISK** — Clauses that significantly limit rights or impose major obligations\n"
        "🟡 **MEDIUM RISK** — Unusual or potentially unfavorable terms\n"
        "🟢 **STANDARD** — Common provisions (brief mention)\n\n"
        "For each risk, explain:\n"
        "- What the clause says\n"
        "- Why it matters\n"
        "- What to watch out for\n\n"
        f"Document:\n{text}"
    )
    print(f"{YELLOW}Flagging risks...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Risk Analysis:{RESET}\n")
    print(result)
    print()


def compare(file_a: str, file_b: str):
    text_a = _read_file(file_a)[:2500]
    text_b = _read_file(file_b)[:2500]
    print(DISCLAIMER)

    prompt = (
        "Compare these two versions of a legal document and identify changes.\n\n"
        "Categorize changes as:\n"
        "🔴 **Significant** — Material changes to rights or obligations\n"
        "🟡 **Notable** — Meaningful additions or removals\n"
        "🟢 **Minor** — Wording changes or clarifications\n\n"
        "List what was added, removed, or modified between versions.\n\n"
        f"--- VERSION A ---\n{text_a}\n\n"
        f"--- VERSION B ---\n{text_b}"
    )
    print(f"{YELLOW}Comparing documents...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Document Comparison:{RESET}\n")
    print(result)
    print()


def extract_clauses(filepath: str, clause_type: str):
    text = _read_file(filepath)[:5000]
    print(DISCLAIMER)

    prompt = (
        f"Extract all '{clause_type}' clauses from this legal document.\n\n"
        "For each clause:\n"
        "1. Quote the relevant text\n"
        "2. Explain what it means in plain English\n"
        "3. Rate its significance: Important / Standard / Routine\n\n"
        f"Document:\n{text}"
    )
    print(f"{YELLOW}Extracting '{clause_type}' clauses...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}{clause_type.title()} Clauses:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="legal_doc_scanner.py",
        description="Legal Document Scanner — OC-0171 (NOT legal advice)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("summarize", help="Plain-English summary")
    p.add_argument("--file", required=True)
    p.add_argument("--type", default="auto", dest="doc_type",
                   help="Document type hint: tos, lease, contract, nda, etc.")

    p = sub.add_parser("flag-risks", help="Identify risky clauses")
    p.add_argument("--file", required=True)

    p = sub.add_parser("compare", help="Compare two document versions")
    p.add_argument("--file-a", required=True)
    p.add_argument("--file-b", required=True)

    p = sub.add_parser("extract-clauses", help="Extract specific clause types")
    p.add_argument("--file", required=True)
    p.add_argument("--clause-type", required=True,
                   help="e.g. termination, payment, liability, confidentiality")

    args = parser.parse_args()
    dispatch = {
        "summarize":       lambda: summarize(args.file, args.doc_type),
        "flag-risks":      lambda: flag_risks(args.file),
        "compare":         lambda: compare(args.file_a, args.file_b),
        "extract-clauses": lambda: extract_clauses(args.file, args.clause_type),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
