#!/usr/bin/env python3
"""ElevenLabs Voice – OC-0102"""

import argparse
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel


def _headers(json_content=True):
    token = os.environ.get("ELEVENLABS_API_KEY")
    if not token:
        print(f"{RED}Error: ELEVENLABS_API_KEY is not set{RESET}")
        sys.exit(1)
    h = {"xi-api-key": token}
    if json_content:
        h["Content-Type"] = "application/json"
    return h


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def speak(args):
    payload = {
        "text": args.text,
        "model_id": args.model,
        "voice_settings": {
            "stability": args.stability,
            "similarity_boost": args.similarity_boost,
        },
    }
    resp = requests.post(
        f"{BASE_URL}/text-to-speech/{args.voice_id}",
        headers={**_headers(), "Accept": "audio/mpeg"},
        json=payload,
        timeout=60,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {args.output}")


def list_voices(args):
    data = _request("get", "/voices")
    voices = data.get("voices", [])
    print(f"{GREEN}Available voices ({len(voices)} total):{RESET}")
    for v in voices:
        labels = v.get("labels", {})
        accent = labels.get("accent", "")
        gender = labels.get("gender", "")
        category = v.get("category", "")
        meta = " | ".join(filter(None, [gender, accent, category]))
        print(f"  {v['voice_id']}  {v.get('name', 'n/a'):<20}  {meta}")


def clone_voice(args):
    token = os.environ.get("ELEVENLABS_API_KEY")
    if not token:
        print(f"{RED}Error: ELEVENLABS_API_KEY is not set{RESET}")
        sys.exit(1)
    files = []
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"{RED}Error: file '{file_path}' not found{RESET}")
            sys.exit(1)
        files.append(("files", (os.path.basename(file_path), open(file_path, "rb"))))
    data_fields = {"name": args.name}
    if args.description:
        data_fields["description"] = args.description

    resp = requests.post(
        f"{BASE_URL}/voices/add",
        headers={"xi-api-key": token},
        data=data_fields,
        files=files,
        timeout=120,
    )
    # Close file handles
    for _, (_, fh) in files:
        fh.close()

    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()
    print(f"{GREEN}Voice cloned:{RESET} {result.get('voice_id')}")
    print(f"  Name: {args.name}")


def get_voice(args):
    data = _request("get", f"/voices/{args.voice_id}")
    print(f"{GREEN}Voice:{RESET} {data.get('name', 'n/a')}")
    print(f"  ID:       {data.get('voice_id', 'n/a')}")
    print(f"  Category: {data.get('category', 'n/a')}")
    labels = data.get("labels", {})
    for k, v in labels.items():
        print(f"  {k.capitalize()}: {v}")


def delete_voice(args):
    _request("delete", f"/voices/{args.voice_id}")
    print(f"{GREEN}Voice deleted:{RESET} {args.voice_id}")


def list_models(args):
    data = _request("get", "/models")
    models = data if isinstance(data, list) else []
    print(f"{GREEN}Available TTS models:{RESET}")
    for m in models:
        print(f"  {m.get('model_id', 'n/a'):<40}  {m.get('name', 'n/a')}")
        if m.get("description"):
            print(f"    {m['description']}")


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs Voice – OC-0102")
    sub = parser.add_subparsers(dest="command", required=True)

    p_speak = sub.add_parser("speak", help="Convert text to speech")
    p_speak.add_argument("--text", required=True)
    p_speak.add_argument("--voice-id", default=DEFAULT_VOICE_ID)
    p_speak.add_argument("--model", default="eleven_multilingual_v2",
                         choices=["eleven_monolingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2"])
    p_speak.add_argument("--stability", type=float, default=0.5)
    p_speak.add_argument("--similarity-boost", type=float, default=0.75)
    p_speak.add_argument("--output", default="output.mp3")

    sub.add_parser("list-voices", help="List all available voices")

    p_clone = sub.add_parser("clone-voice", help="Create a voice clone from audio samples")
    p_clone.add_argument("--name", required=True)
    p_clone.add_argument("--files", required=True, nargs="+", help="Audio sample files")
    p_clone.add_argument("--description", default=None)

    p_get = sub.add_parser("get-voice", help="Get details of a voice")
    p_get.add_argument("--voice-id", required=True)

    p_del = sub.add_parser("delete-voice", help="Delete a cloned voice")
    p_del.add_argument("--voice-id", required=True)

    sub.add_parser("list-models", help="List available TTS models")

    args = parser.parse_args()
    commands = {
        "speak": speak,
        "list-voices": list_voices,
        "clone-voice": clone_voice,
        "get-voice": get_voice,
        "delete-voice": delete_voice,
        "list-models": list_models,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
