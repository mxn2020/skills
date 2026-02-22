#!/usr/bin/env python3
"""Meeting Scribe – OC-0110"""

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


def _chat(prompt):
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    if not resp.ok:
        print(f"{RED}API error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]


def transcribe(args):
    print(f"{YELLOW}Transcribing {args.file} ...{RESET}")
    with open(args.file, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {_key()}"},
            files={"file": fh},
            data={"model": "whisper-1"},
        )
    if not resp.ok:
        print(f"{RED}Transcription error: {resp.text}{RESET}")
        sys.exit(1)
    text = resp.json().get("text", "")
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"{GREEN}Transcript saved to {args.output}{RESET}")
    else:
        print(f"{GREEN}Transcript:{RESET}\n{text}")


def extract_action_items(args):
    with open(args.transcript_file) as f:
        text = f.read()
    result = _chat(
        f"Extract all action items from this meeting transcript. "
        f"Format as: '- [ ] [Owner] Action item description'\n\n{text}"
    )
    print(f"{GREEN}Action Items:{RESET}")
    print(result)


def generate_summary(args):
    with open(args.transcript_file) as f:
        text = f.read()
    if args.format == "brief":
        prompt = f"Summarize this meeting in 3-5 bullet points:\n\n{text}"
    elif args.format == "detailed":
        prompt = (f"Provide a detailed meeting summary with sections: Attendees (inferred), "
                  f"Key Discussions, Decisions Made, Action Items, Next Steps.\n\n{text}")
    else:
        prompt = f"Summarize this meeting:\n\n{text}"
    result = _chat(prompt)
    print(f"{GREEN}Summary ({args.format}):{RESET}")
    print(result)


def export_notes(args):
    with open(args.transcript_file) as f:
        text = f.read()
    summary = _chat(f"Create structured meeting notes (summary + action items):\n\n{text}")
    fmt = args.output_format
    if fmt == "md":
        content = f"# Meeting Notes\n\n{summary}\n"
    elif fmt == "txt":
        content = f"MEETING NOTES\n{'='*40}\n{summary}\n"
    else:
        content = json.dumps({"notes": summary}, indent=2)
    output = args.output or f"meeting_notes.{fmt}"
    with open(output, "w") as f:
        f.write(content)
    print(f"{GREEN}Notes exported to {output}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Meeting Scribe")
    sub = parser.add_subparsers(dest="command", required=True)

    p_t = sub.add_parser("transcribe")
    p_t.add_argument("--file", required=True)
    p_t.add_argument("--output", default=None)

    p_a = sub.add_parser("extract-action-items")
    p_a.add_argument("--transcript-file", required=True)

    p_s = sub.add_parser("generate-summary")
    p_s.add_argument("--transcript-file", required=True)
    p_s.add_argument("--format", choices=["brief", "detailed", "standard"], default="standard")

    p_e = sub.add_parser("export-notes")
    p_e.add_argument("--transcript-file", required=True)
    p_e.add_argument("--output-format", choices=["md", "txt", "json"], default="md")
    p_e.add_argument("--output", default=None)

    args = parser.parse_args()
    dispatch = {
        "transcribe": transcribe,
        "extract-action-items": extract_action_items,
        "generate-summary": generate_summary,
        "export-notes": export_notes,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
