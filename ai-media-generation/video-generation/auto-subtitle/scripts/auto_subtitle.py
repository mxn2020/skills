#!/usr/bin/env python3
"""Auto Subtitle – OC-0099"""

import argparse
import json
import os
import subprocess
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


def _check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"{RED}Error: ffmpeg is not installed or not in PATH{RESET}")
        sys.exit(1)


def _check_input(path):
    if not os.path.exists(path):
        print(f"{RED}Error: file '{path}' not found{RESET}")
        sys.exit(1)


def _transcribe_api(input_path, language, response_format, prompt=None):
    with open(input_path, "rb") as f:
        data = {
            "model": "whisper-1",
            "response_format": response_format,
        }
        if language and language != "auto":
            data["language"] = language
        if prompt:
            data["prompt"] = prompt
        resp = requests.post(
            f"{BASE_URL}/transcriptions",
            headers=_headers(),
            files={"file": (os.path.basename(input_path), f)},
            data=data,
            timeout=300,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.content if response_format in ("srt", "vtt", "text") else resp.text


def transcribe(args):
    _check_input(args.input)
    content = _transcribe_api(args.input, args.language, args.output_format, args.prompt)
    output = args.output or f"output.{args.output_format}"
    if isinstance(content, bytes):
        with open(output, "wb") as f:
            f.write(content)
    else:
        with open(output, "w", encoding="utf-8") as f:
            if args.output_format == "json":
                f.write(content)
            else:
                f.write(content if isinstance(content, str) else content.decode())
    print(f"{GREEN}Saved:{RESET} {output}")


def burn_subtitles(args):
    _check_ffmpeg()
    _check_input(args.video)
    _check_input(args.subtitles)

    output = args.output or f"captioned_{os.path.basename(args.video)}"
    position_filter = "MarginV=25" if args.position == "bottom" else "MarginV=0,Alignment=6"
    subtitle_filter = (
        f"subtitles={args.subtitles}:force_style='FontSize={args.font_size},"
        f"PrimaryColour=&H{_color_to_ass(args.font_color)},"
        f"BackColour=&H{_color_to_ass(args.bg_color.split('@')[0])},"
        f"BorderStyle=4,{position_filter}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", args.video,
        "-vf", subtitle_filter,
        "-c:a", "copy",
        output,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{RED}ffmpeg error:{RESET} {e.stderr}")
        sys.exit(1)
    print(f"{GREEN}Saved:{RESET} {output}")


def _color_to_ass(color_name):
    """Convert color name to ASS hex format (AABBGGRR)."""
    colors = {
        "white": "00FFFFFF",
        "black": "00000000",
        "yellow": "0000FFFF",
        "red": "000000FF",
        "blue": "00FF0000",
    }
    return colors.get(color_name.lower(), "00FFFFFF")


def generate_srt(args):
    _check_input(args.input)
    print(f"{YELLOW}Transcribing {args.input}...{RESET}")
    content = _transcribe_api(args.input, args.language, "srt")
    output = args.output or "output.srt"
    if isinstance(content, bytes):
        with open(output, "wb") as f:
            f.write(content)
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content if isinstance(content, str) else content.decode())
    print(f"{GREEN}Saved:{RESET} {output}")


def main():
    parser = argparse.ArgumentParser(description="Auto Subtitle – OC-0099")
    sub = parser.add_subparsers(dest="command", required=True)

    p_trans = sub.add_parser("transcribe", help="Transcribe audio/video to subtitle file")
    p_trans.add_argument("--input", required=True)
    p_trans.add_argument("--language", default="auto", help="Language code or 'auto'")
    p_trans.add_argument("--output-format", default="srt", choices=["srt", "vtt", "json", "txt"])
    p_trans.add_argument("--prompt", default=None, help="Prompt to improve transcription accuracy")
    p_trans.add_argument("--output", default=None)

    p_burn = sub.add_parser("burn-subtitles", help="Burn subtitles permanently into a video")
    p_burn.add_argument("--video", required=True)
    p_burn.add_argument("--subtitles", required=True, help="SRT or VTT subtitle file")
    p_burn.add_argument("--output", default=None)
    p_burn.add_argument("--font-size", type=int, default=24)
    p_burn.add_argument("--font-color", default="white")
    p_burn.add_argument("--bg-color", default="black@0.5")
    p_burn.add_argument("--position", default="bottom", choices=["top", "bottom"])

    p_srt = sub.add_parser("generate-srt", help="Transcribe and save directly as SRT")
    p_srt.add_argument("--input", required=True)
    p_srt.add_argument("--language", default="auto")
    p_srt.add_argument("--output", default="output.srt")

    args = parser.parse_args()
    commands = {
        "transcribe": transcribe,
        "burn-subtitles": burn_subtitles,
        "generate-srt": generate_srt,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
