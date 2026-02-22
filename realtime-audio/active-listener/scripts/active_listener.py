#!/usr/bin/env python3
"""Active Listener – OC-0109"""

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


def _headers():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print(f"{RED}Error: OPENAI_API_KEY not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _transcribe_verbose(file_path):
    with open(file_path, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers={"Authorization": _headers()["Authorization"]},
            files={"file": fh},
            data={"model": "whisper-1", "response_format": "verbose_json"},
        )
    if not resp.ok:
        print(f"{RED}Transcription error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def _chat(prompt, system="You are a dialogue analysis assistant."):
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers=_headers(),
        json={"model": "gpt-4o-mini",
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": prompt}]},
    )
    if not resp.ok:
        print(f"{RED}API error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]


def detect_pauses(args):
    print(f"{YELLOW}Transcribing {args.file} with timestamps ...{RESET}")
    data = _transcribe_verbose(args.file)
    segments = data.get("segments", [])
    pauses = []
    for i in range(1, len(segments)):
        gap = segments[i]["start"] - segments[i - 1]["end"]
        if gap >= args.threshold:
            pauses.append({"at": segments[i - 1]["end"], "duration": round(gap, 2)})
    print(f"{GREEN}Found {len(pauses)} pauses > {args.threshold}s:{RESET}")
    for p in pauses:
        print(f"  t={p['at']:.1f}s  gap={p['duration']}s")


def extract_turns(args):
    with open(args.transcript_file) as f:
        text = f.read()
    result = _chat(
        f"Split this transcript into speaker turns. Label each turn as Speaker A or Speaker B "
        f"based on conversational structure. Return as numbered list.\n\n{text}"
    )
    print(f"{GREEN}Speaker turns:{RESET}")
    print(result)


def summarize_turns(args):
    with open(args.transcript_file) as f:
        text = f.read()
    result = _chat(
        f"Summarize each key point or topic shift in this conversation transcript. "
        f"Format as bullet points with timestamps if available.\n\n{text}"
    )
    print(f"{GREEN}Turn summaries:{RESET}")
    print(result)


def analyze_dialogue(args):
    print(f"{YELLOW}Running full dialogue analysis on {args.file} ...{RESET}")
    data = _transcribe_verbose(args.file)
    text = data.get("text", "")
    segments = data.get("segments", [])

    # Detect pauses
    pauses = []
    for i in range(1, len(segments)):
        gap = segments[i]["start"] - segments[i - 1]["end"]
        if gap >= 1.0:
            pauses.append(gap)

    print(f"\n{GREEN}Transcript preview:{RESET} {text[:300]}...")
    print(f"\n{GREEN}Pauses > 1.0s:{RESET} {len(pauses)}")

    summary = _chat(f"Provide a concise dialogue summary with key topics and action items:\n\n{text}")
    print(f"\n{GREEN}Dialogue Summary:{RESET}")
    print(summary)


def main():
    parser = argparse.ArgumentParser(description="Active Listener")
    sub = parser.add_subparsers(dest="command", required=True)

    p_d = sub.add_parser("detect-pauses")
    p_d.add_argument("--file", required=True)
    p_d.add_argument("--threshold", type=float, default=0.5)

    p_e = sub.add_parser("extract-turns")
    p_e.add_argument("--transcript-file", required=True)

    p_s = sub.add_parser("summarize-turns")
    p_s.add_argument("--transcript-file", required=True)

    p_a = sub.add_parser("analyze-dialogue")
    p_a.add_argument("--file", required=True)

    args = parser.parse_args()
    dispatch = {
        "detect-pauses": detect_pauses,
        "extract-turns": extract_turns,
        "summarize-turns": summarize_turns,
        "analyze-dialogue": analyze_dialogue,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
