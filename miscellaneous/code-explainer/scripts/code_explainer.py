#!/usr/bin/env python3
"""
Code Explainer — OC-0177
Narrate what a code snippet does in plain English for non-developers.
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


def _complete(prompt: str, system_msg: str = "", max_tokens: int = 800) -> str:
    system = system_msg or (
        "You are an expert software educator who explains code clearly to people "
        "of all technical backgrounds. Be accurate but accessible."
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
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _read_input(file: str = None, code: str = None) -> str:
    if code:
        return code
    if file:
        if not os.path.exists(file):
            _die(f"File not found: {file}")
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    _die("Provide --file or --code.")


def _detect_language(code: str, filename: str = "") -> str:
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".java": "Java", ".cs": "C#", ".cpp": "C++", ".c": "C",
        ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
        ".sh": "Shell/Bash", ".sql": "SQL", ".html": "HTML",
        ".css": "CSS", ".r": "R", ".swift": "Swift", ".kt": "Kotlin",
    }
    if filename:
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
    return "unknown language"


def explain(file: str = None, code: str = None, audience: str = "general"):
    raw = _read_input(file, code)[:4000]
    lang = _detect_language(raw, file or "")

    audience_map = {
        "general": "a non-technical person",
        "business": "a business stakeholder",
        "junior": "a junior developer",
        "student": "a computer science student",
    }
    target = audience_map.get(audience, audience_map["general"])

    prompt = (
        f"Explain this {lang} code to {target}.\n\n"
        "Structure:\n"
        "**What It Does** (1-2 sentences summary)\n\n"
        "**How It Works** (step-by-step walkthrough, no jargon)\n\n"
        "**Key Concepts** (brief definitions of any technical terms used)\n\n"
        "**Real-World Analogy** (compare to something non-technical)\n\n"
        f"Code:\n```\n{raw}\n```"
    )
    print(f"{YELLOW}Explaining {lang} code...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Code Explanation:{RESET}\n")
    print(result)
    print()


def eli5(file: str = None, code: str = None):
    raw = _read_input(file, code)[:3000]
    lang = _detect_language(raw, file or "")

    prompt = (
        f"Explain this {lang} code as if I'm 5 years old.\n\n"
        "Use simple words, fun analogies, and avoid ALL technical jargon.\n"
        "Imagine you're explaining what a computer program does to a curious child.\n\n"
        f"Code:\n```\n{raw}\n```"
    )
    print(f"{YELLOW}ELI5: Explaining code simply...{RESET}\n")
    result = _complete(prompt, max_tokens=500)
    print(f"{BOLD}Simple Explanation:{RESET}\n")
    print(result)
    print()


def annotate(file: str = None, code: str = None, output: str = None):
    raw = _read_input(file, code)[:4000]
    lang = _detect_language(raw, file or "")

    prompt = (
        f"Add clear, helpful inline comments to this {lang} code.\n\n"
        "Guidelines:\n"
        "- Add a comment before each major block explaining WHAT it does\n"
        "- Add inline comments for non-obvious lines\n"
        "- Keep comments concise but informative\n"
        "- Don't over-comment obvious things\n\n"
        "Return ONLY the annotated code with comments, no other text.\n\n"
        f"Code:\n{raw}"
    )
    print(f"{YELLOW}Annotating code...{RESET}\n")
    result = _complete(prompt, max_tokens=1500)

    # Strip markdown code fences if present
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"{GREEN}Annotated code saved to: {output}{RESET}")
    else:
        print(f"{BOLD}Annotated Code:{RESET}\n")
        print(result)
    print()


def complexity(file: str = None, code: str = None):
    raw = _read_input(file, code)[:4000]
    lang = _detect_language(raw, file or "")

    prompt = (
        f"Analyze the complexity and quality of this {lang} code.\n\n"
        "Provide:\n"
        "**Complexity Metrics:**\n"
        "- Lines of code: X\n"
        "- Estimated cyclomatic complexity: [Low/Medium/High]\n"
        "- Nesting depth: [Shallow/Moderate/Deep]\n\n"
        "**Code Smells** (issues found):\n"
        "(list any problems like long functions, repeated code, unclear naming)\n\n"
        "**Strengths** (what's done well):\n\n"
        "**Improvement Suggestions** (3 specific recommendations):\n\n"
        f"Code:\n```\n{raw}\n```"
    )
    print(f"{YELLOW}Analyzing code complexity...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Complexity Analysis:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="code_explainer.py",
        description="Code Explainer — OC-0177"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("explain", help="Explain code in plain English")
    p.add_argument("--file", default=None)
    p.add_argument("--code", default=None, help="Inline code string")
    p.add_argument("--audience", default="general",
                   choices=["general", "business", "junior", "student"])

    p = sub.add_parser("eli5", help="Explain Like I'm 5")
    p.add_argument("--file", default=None)
    p.add_argument("--code", default=None)

    p = sub.add_parser("annotate", help="Add inline comments to code")
    p.add_argument("--file", default=None)
    p.add_argument("--code", default=None)
    p.add_argument("--output", default=None, help="Save to this file")

    p = sub.add_parser("complexity", help="Analyze code complexity")
    p.add_argument("--file", default=None)
    p.add_argument("--code", default=None)

    args = parser.parse_args()
    dispatch = {
        "explain":    lambda: explain(args.file, args.code, args.audience),
        "eli5":       lambda: eli5(args.file, args.code),
        "annotate":   lambda: annotate(args.file, args.code, args.output),
        "complexity": lambda: complexity(args.file, args.code),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
