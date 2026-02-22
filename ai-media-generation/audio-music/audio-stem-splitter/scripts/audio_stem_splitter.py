#!/usr/bin/env python3
"""Audio Stem Splitter – OC-0105"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.replicate.com/v1"
DEMUCS_MODEL = "meta/demucs"
DEMUCS_VERSION = "25a173108cff36ef9f80f854c162d01df9e6528be175794b81158fa03836d953"

STEM_CHOICES = ["vocals", "bass", "drums", "other", "all"]
ALL_STEMS = ["vocals", "bass", "drums", "other"]


def _headers():
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print(f"{RED}Error: REPLICATE_API_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_prediction(prediction_id, max_wait=600):
    print(f"{YELLOW}Polling prediction {prediction_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"/predictions/{prediction_id}")
        status = data.get("status", "unknown")
        if status == "succeeded":
            return data
        if status in ("failed", "canceled"):
            print(f"{RED}Prediction {status}: {data.get('error', 'Unknown error')}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for prediction{RESET}")
    sys.exit(1)


def _audio_to_data_url(path):
    import base64
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"mp3": "audio/mpeg", "wav": "audio/wav", "flac": "audio/flac", "ogg": "audio/ogg"}.get(ext, "audio/mpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def _download(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        return False
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")
    return True


def _run_demucs(input_path, stems_to_extract, output_dir):
    if not os.path.exists(input_path):
        print(f"{RED}Error: input file '{input_path}' not found{RESET}")
        sys.exit(1)
    print(f"{YELLOW}Uploading audio and starting separation...{RESET}")
    input_data_url = _audio_to_data_url(input_path)
    payload = {
        "version": DEMUCS_VERSION,
        "input": {
            "audio": input_data_url,
            "stems": "all",
        },
    }
    data = _request("post", "/predictions", json=payload)
    prediction_id = data.get("id")
    if not prediction_id:
        print(f"{RED}No prediction ID returned{RESET}")
        sys.exit(1)
    result = _poll_prediction(prediction_id)
    output = result.get("output", {})
    if not output:
        print(f"{YELLOW}No output returned. Result:{RESET}")
        print(result)
        return

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    downloaded = 0
    for stem in ALL_STEMS:
        if stem not in stems_to_extract and "all" not in stems_to_extract:
            continue
        stem_url = output.get(stem)
        if stem_url:
            out_path = os.path.join(output_dir, f"{base_name}_{stem}.wav")
            if _download(stem_url, out_path):
                downloaded += 1
        else:
            print(f"{YELLOW}No output for stem: {stem}{RESET}")
    print(f"{GREEN}Done:{RESET} {downloaded} stems saved to {output_dir}")


def split(args):
    stems = ["all"] if args.stems == "all" else [args.stems]
    _run_demucs(args.input, stems, args.output_dir)


def split_four_stems(args):
    _run_demucs(args.input, ["all"], args.output_dir)


def list_models(args):
    print(f"{GREEN}Available stem separation models:{RESET}")
    models = [
        ("demucs", "meta/demucs", "Facebook's Demucs – high quality 4-stem separation"),
        ("demucs v3", "meta/demucs:htdemucs", "Hybrid Transformer Demucs – state-of-the-art"),
        ("spleeter", "deezer-research/spleeter", "Deezer Spleeter – fast 2 or 5 stem separation"),
    ]
    for name, model_id, desc in models:
        print(f"  {name:<15}  {model_id:<35}  {desc}")
    print()
    print(f"{YELLOW}This skill uses:{RESET} {DEMUCS_MODEL} (version: {DEMUCS_VERSION[:12]}...)")


def main():
    parser = argparse.ArgumentParser(description="Audio Stem Splitter – OC-0105")
    sub = parser.add_subparsers(dest="command", required=True)

    p_split = sub.add_parser("split", help="Split audio into selected stems")
    p_split.add_argument("--input", required=True)
    p_split.add_argument("--stems", default="all", choices=STEM_CHOICES)
    p_split.add_argument("--output-dir", default=".")

    p_four = sub.add_parser("split-four-stems", help="Split into vocals, bass, drums, other")
    p_four.add_argument("--input", required=True)
    p_four.add_argument("--output-dir", default=".")

    sub.add_parser("list-models", help="Show available stem separation models")

    args = parser.parse_args()
    commands = {
        "split": split,
        "split-four-stems": split_four_stems,
        "list-models": list_models,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
