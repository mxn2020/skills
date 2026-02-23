#!/usr/bin/env python3
"""Realtime Voice Interface – OC-0106"""

import argparse
import os
import sys
import json
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_BASE = "https://api.openai.com/v1"
ELEVEN_BASE = "https://api.elevenlabs.io/v1"


def _openai_headers():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print(f"{RED}Error: OPENAI_API_KEY not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def _eleven_headers():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print(f"{RED}Error: ELEVENLABS_API_KEY not set{RESET}")
        sys.exit(1)
    return {"xi-api-key": key, "Content-Type": "application/json"}


def transcribe_audio(args):
    if not os.path.exists(args.file):
        print(f"{RED}Error: file not found: {args.file}{RESET}")
        sys.exit(1)
    print(f"{YELLOW}Transcribing {args.file} ...{RESET}")
    with open(args.file, "rb") as fh:
        resp = requests.post(
            f"{OPENAI_BASE}/audio/transcriptions",
            headers=_openai_headers(),
            files={"file": fh},
            data={"model": args.model, "language": args.language or ""},
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    text = resp.json().get("text", "")
    print(f"{GREEN}Transcript:{RESET} {text}")
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"{GREEN}Saved to {args.output}{RESET}")


def synthesize_speech(args):
    print(f"{YELLOW}Synthesizing speech ...{RESET}")
    payload = {
        "text": args.text,
        "model_id": args.tts_model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    resp = requests.post(
        f"{ELEVEN_BASE}/text-to-speech/{args.voice_id}",
        headers={**_eleven_headers(), "Content-Type": "application/json"},
        json=payload,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    output = args.output or "output.mp3"
    with open(output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Audio saved to {output}{RESET}")


def start_session(args):
    print(f"{GREEN}Session Configuration{RESET}")
    print(f"  LLM model  : {args.model}")
    print(f"  STT model  : whisper-1")
    print(f"  TTS voice  : {args.voice_id}")
    print(f"  Target RTT : <500ms")
    print(f"{YELLOW}Session ready. Use transcribe-audio + synthesize-speech to interact.{RESET}")


def get_session_info(args):
    print(f"{GREEN}Realtime Voice Interface – Session Info{RESET}")
    print(f"  STT : OpenAI Whisper (whisper-1)")
    print(f"  LLM : OpenAI GPT-4o (gpt-4o)")
    print(f"  TTS : ElevenLabs (eleven_multilingual_v2)")
    print(f"  Latency target : < 500ms round-trip")
    print(f"  Supported input formats : mp3, mp4, wav, webm, m4a, ogg")


def main():
    parser = argparse.ArgumentParser(description="Realtime Voice Interface")
    sub = parser.add_subparsers(dest="command", required=True)

    p_t = sub.add_parser("transcribe-audio", help="Transcribe audio to text")
    p_t.add_argument("--file", required=True, help="Audio file path")
    p_t.add_argument("--model", default="whisper-1")
    p_t.add_argument("--language", default=None)
    p_t.add_argument("--output", default=None)

    p_s = sub.add_parser("synthesize-speech", help="Text to speech")
    p_s.add_argument("--text", required=True)
    p_s.add_argument("--voice-id", default="21m00Tcm4TlvDq8ikWAM")
    p_s.add_argument("--tts-model", default="eleven_multilingual_v2")
    p_s.add_argument("--output", default="output.mp3")

    p_ss = sub.add_parser("start-session", help="Print session config")
    p_ss.add_argument("--model", default="gpt-4o")
    p_ss.add_argument("--voice-id", default="21m00Tcm4TlvDq8ikWAM")

    sub.add_parser("get-session-info", help="Show session info")

    args = parser.parse_args()
    dispatch = {
        "transcribe-audio": transcribe_audio,
        "synthesize-speech": synthesize_speech,
        "start-session": start_session,
        "get-session-info": get_session_info,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
