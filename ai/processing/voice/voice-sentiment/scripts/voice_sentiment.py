#!/usr/bin/env python3
"""Voice Sentiment Analyzer – OC-0108"""

import argparse
import json
import os
import sys
import glob
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


def _transcribe(file_path):
    with open(file_path, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers={"Authorization": _headers()["Authorization"]},
            files={"file": fh},
            data={"model": "whisper-1"},
        )
    if not resp.ok:
        print(f"{RED}Transcription error: {resp.text}{RESET}")
        sys.exit(1)
    return resp.json().get("text", "")


def _analyze_sentiment(text):
    prompt = (
        "Analyze the following text for emotional tone and sentiment. "
        "Return a JSON object with keys: sentiment (positive/negative/neutral/mixed), "
        "emotions (list of top 3 detected emotions), stress_level (low/medium/high), "
        "confidence (0.0-1.0), summary (one sentence). Text: " + text
    )
    resp = requests.post(
        f"{OPENAI_BASE}/chat/completions",
        headers=_headers(),
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}],
              "response_format": {"type": "json_object"}},
    )
    if not resp.ok:
        print(f"{RED}Analysis error: {resp.text}{RESET}")
        sys.exit(1)
    return json.loads(resp.json()["choices"][0]["message"]["content"])


def _print_analysis(result, label=""):
    if label:
        print(f"\n{YELLOW}{label}{RESET}")
    print(f"  Sentiment   : {GREEN}{result.get('sentiment','?')}{RESET}")
    print(f"  Emotions    : {', '.join(result.get('emotions', []))}")
    print(f"  Stress level: {result.get('stress_level','?')}")
    print(f"  Confidence  : {result.get('confidence', 0):.0%}")
    print(f"  Summary     : {result.get('summary','')}")


def analyze_file(args):
    print(f"{YELLOW}Transcribing {args.file} ...{RESET}")
    text = _transcribe(args.file)
    print(f"{GREEN}Transcript:{RESET} {text[:200]}{'...' if len(text) > 200 else ''}")
    print(f"{YELLOW}Analyzing sentiment ...{RESET}")
    result = _analyze_sentiment(text)
    _print_analysis(result)


def analyze_text(args):
    print(f"{YELLOW}Analyzing text ...{RESET}")
    result = _analyze_sentiment(args.text)
    _print_analysis(result)


def batch_analyze(args):
    patterns = ["*.mp3", "*.wav", "*.m4a", "*.ogg", "*.webm"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(args.dir, p)))
    if not files:
        print(f"{YELLOW}No audio files found in {args.dir}{RESET}")
        return
    results = {}
    for f in files:
        print(f"{YELLOW}Processing {os.path.basename(f)} ...{RESET}")
        text = _transcribe(f)
        result = _analyze_sentiment(text)
        results[os.path.basename(f)] = result
        _print_analysis(result, os.path.basename(f))
    if args.output:
        with open(args.output, "w") as out:
            json.dump(results, out, indent=2)
        print(f"\n{GREEN}Report saved to {args.output}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Voice Sentiment Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_f = sub.add_parser("analyze-file")
    p_f.add_argument("--file", required=True)

    p_t = sub.add_parser("analyze-text")
    p_t.add_argument("--text", required=True)

    p_b = sub.add_parser("batch-analyze")
    p_b.add_argument("--dir", required=True)
    p_b.add_argument("--output", default=None)

    args = parser.parse_args()
    dispatch = {
        "analyze-file": analyze_file,
        "analyze-text": analyze_text,
        "batch-analyze": batch_analyze,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
