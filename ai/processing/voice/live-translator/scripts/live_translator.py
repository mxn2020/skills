#!/usr/bin/env python3
"""Live Translator – OC-0107"""

import argparse
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

DEEPL_BASE = "https://api-free.deepl.com/v2"
OPENAI_BASE = "https://api.openai.com/v1"

DEEPL_LANGUAGES = [
    "BG","CS","DA","DE","EL","EN","ES","ET","FI","FR","HU","ID","IT",
    "JA","KO","LT","LV","NB","NL","PL","PT","RO","RU","SK","SL","SV",
    "TR","UK","ZH",
]


def _openai_key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k:
        print(f"{RED}Error: OPENAI_API_KEY not set{RESET}")
        sys.exit(1)
    return k


def _deepl_key():
    k = os.environ.get("DEEPL_API_KEY")
    if not k:
        print(f"{RED}Error: DEEPL_API_KEY not set{RESET}")
        sys.exit(1)
    return k


def translate_audio(args):
    print(f"{YELLOW}Transcribing {args.file} ...{RESET}")
    with open(args.file, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {_openai_key()}"},
            files={"file": fh},
            data={"model": "whisper-1"},
        )
    if not resp.ok:
        print(f"{RED}Transcription error: {resp.text}{RESET}")
        sys.exit(1)
    text = resp.json().get("text", "")
    print(f"{GREEN}Transcript:{RESET} {text}")
    print(f"{YELLOW}Translating to {args.target_lang} ...{RESET}")
    _translate_with_deepl(text, args.target_lang)


def translate_text(args):
    _translate_with_deepl(args.text, args.target_lang)


def _translate_with_deepl(text, target_lang):
    resp = requests.post(
        f"{DEEPL_BASE}/translate",
        headers={"Authorization": f"DeepL-Auth-Key {_deepl_key()}"},
        data={"text": text, "target_lang": target_lang.upper()},
    )
    if not resp.ok:
        print(f"{RED}DeepL error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()["translations"][0]
    print(f"{GREEN}Translation ({result['detected_source_language']} → {target_lang.upper()}):{RESET}")
    print(result["text"])


def list_languages(args):
    print(f"{GREEN}Supported DeepL target language codes:{RESET}")
    for i, lang in enumerate(DEEPL_LANGUAGES, 1):
        print(f"  {lang}", end="\n" if i % 8 == 0 else "  ")
    print()


def detect_language(args):
    resp = requests.post(
        f"{DEEPL_BASE}/translate",
        headers={"Authorization": f"DeepL-Auth-Key {_deepl_key()}"},
        data={"text": args.text, "target_lang": "EN"},
    )
    if not resp.ok:
        print(f"{RED}DeepL error: {resp.text}{RESET}")
        sys.exit(1)
    lang = resp.json()["translations"][0]["detected_source_language"]
    print(f"{GREEN}Detected language:{RESET} {lang}")


def main():
    parser = argparse.ArgumentParser(description="Live Translator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_a = sub.add_parser("translate-audio")
    p_a.add_argument("--file", required=True)
    p_a.add_argument("--target-lang", required=True, help="e.g. ES, FR, DE")

    p_t = sub.add_parser("translate-text")
    p_t.add_argument("--text", required=True)
    p_t.add_argument("--target-lang", required=True)

    sub.add_parser("list-languages")

    p_d = sub.add_parser("detect-language")
    p_d.add_argument("--text", required=True)

    args = parser.parse_args()
    dispatch = {
        "translate-audio": translate_audio,
        "translate-text": translate_text,
        "list-languages": list_languages,
        "detect-language": detect_language,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
