#!/usr/bin/env python3
"""Whisper Transcriber – OC-0104"""

import argparse
import json
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.openai.com/v1/audio"


def _headers():
    token = os.environ.get("OPENAI_API_KEY")
    if not token:
        print(f"{RED}Error: OPENAI_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}


def _check_input(path):
    if not os.path.exists(path):
        print(f"{RED}Error: input file '{path}' not found{RESET}")
        sys.exit(1)


def transcribe(args):
    _check_input(args.input)
    with open(args.input, "rb") as f:
        data_fields = {
            "model": "whisper-1",
            "response_format": args.format,
        }
        if args.language and args.language != "auto":
            data_fields["language"] = args.language
        if args.prompt:
            data_fields["prompt"] = args.prompt
        resp = requests.post(
            f"{BASE_URL}/transcriptions",
            headers=_headers(),
            files={"file": (os.path.basename(args.input), f)},
            data=data_fields,
            timeout=300,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)

    if args.format == "json":
        result = resp.json()
        text = result.get("text", "")
        lang = result.get("language", "unknown")
        duration = result.get("duration")
        print(f"{GREEN}Transcription complete{RESET}")
        print(f"  Language: {lang}")
        if duration:
            print(f"  Duration: {duration:.1f}s")
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Saved: {args.output}")
        else:
            print(f"\n{text}")
    elif args.format == "verbose_json":
        result = resp.json()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"{GREEN}Saved:{RESET} {args.output}")
        else:
            print(json.dumps(result, indent=2))
    else:
        content = resp.content
        if args.output:
            with open(args.output, "wb") as f:
                f.write(content)
            print(f"{GREEN}Saved:{RESET} {args.output}")
        else:
            print(content.decode("utf-8"))


def translate(args):
    _check_input(args.input)
    with open(args.input, "rb") as f:
        data_fields = {"model": "whisper-1", "response_format": "text"}
        if args.prompt:
            data_fields["prompt"] = args.prompt
        resp = requests.post(
            f"{BASE_URL}/translations",
            headers=_headers(),
            files={"file": (os.path.basename(args.input), f)},
            data=data_fields,
            timeout=300,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    text = resp.text
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{GREEN}Saved:{RESET} {args.output}")
    else:
        print(text)


def detect_language(args):
    _check_input(args.input)
    with open(args.input, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/transcriptions",
            headers=_headers(),
            files={"file": (os.path.basename(args.input), f)},
            data={"model": "whisper-1", "response_format": "verbose_json"},
            timeout=300,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()
    lang = result.get("language", "unknown")
    duration = result.get("duration")
    print(f"{GREEN}Detected language:{RESET} {lang}")
    if duration:
        print(f"  Duration: {duration:.1f}s")
    segments = result.get("segments", [])
    if segments:
        avg_log_prob = sum(s.get("avg_logprob", 0) for s in segments) / len(segments)
        confidence = min(100, max(0, int((avg_log_prob + 1) * 100)))
        print(f"  Confidence: ~{confidence}%")


def main():
    parser = argparse.ArgumentParser(description="Whisper Transcriber – OC-0104")
    sub = parser.add_subparsers(dest="command", required=True)

    p_trans = sub.add_parser("transcribe", help="Transcribe audio to text")
    p_trans.add_argument("--input", required=True)
    p_trans.add_argument("--language", default="auto", help="Language code or 'auto'")
    p_trans.add_argument("--format", default="json",
                         choices=["json", "text", "srt", "verbose_json", "vtt"])
    p_trans.add_argument("--prompt", default=None, help="Transcription context/prompt")
    p_trans.add_argument("--output", default=None)

    p_translate = sub.add_parser("translate", help="Transcribe and translate audio to English")
    p_translate.add_argument("--input", required=True)
    p_translate.add_argument("--prompt", default=None)
    p_translate.add_argument("--output", default=None)

    p_detect = sub.add_parser("detect-language", help="Detect the language in an audio file")
    p_detect.add_argument("--input", required=True)

    args = parser.parse_args()
    commands = {
        "transcribe": transcribe,
        "translate": translate,
        "detect-language": detect_language,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
