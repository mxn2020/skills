#!/usr/bin/env python3
"""Voice Biometrics – OC-0111"""

import argparse
import json
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PROFILES_FILE = os.path.expanduser("~/.openclaw/voice_profiles.json")


def get_config():
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        print(f"{RED}Error: AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set{RESET}")
        sys.exit(1)
    return key, region


def _load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE) as f:
        return json.load(f)


def _save_profiles(profiles):
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def enroll_speaker(args):
    key, region = get_config()
    base = f"https://{region}.api.cognitive.microsoft.com/speaker/verification/v2.0"
    print(f"{YELLOW}Creating profile for '{args.name}' ...{RESET}")
    resp = requests.post(
        f"{base}/text-independent/profiles",
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"},
        json={"locale": "en-us"},
    )
    if not resp.ok:
        print(f"{RED}Error creating profile: {resp.text}{RESET}")
        sys.exit(1)
    profile_id = resp.json()["profileId"]
    with open(args.file, "rb") as fh:
        enroll_resp = requests.post(
            f"{base}/text-independent/profiles/{profile_id}/enrollments",
            headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "audio/wav"},
            data=fh.read(),
        )
    if not enroll_resp.ok:
        print(f"{RED}Enrollment error: {enroll_resp.text}{RESET}")
        sys.exit(1)
    profiles = _load_profiles()
    profiles[args.name] = profile_id
    _save_profiles(profiles)
    print(f"{GREEN}Enrolled '{args.name}' with profile ID: {profile_id}{RESET}")


def identify_speaker(args):
    key, region = get_config()
    profiles = _load_profiles()
    if not profiles:
        print(f"{YELLOW}No enrolled speakers found.{RESET}")
        return
    profile_ids = list(profiles.values())
    base = f"https://{region}.api.cognitive.microsoft.com/speaker/identification/v2.0"
    with open(args.file, "rb") as fh:
        resp = requests.post(
            f"{base}/text-independent/profiles/identifySingleSpeaker?profileIds={','.join(profile_ids)}",
            headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "audio/wav"},
            data=fh.read(),
        )
    if not resp.ok:
        print(f"{RED}Identification error: {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()
    identified_id = result.get("identifiedProfile", {}).get("profileId")
    name = next((n for n, pid in profiles.items() if pid == identified_id), "Unknown")
    score = result.get("identifiedProfile", {}).get("score", 0)
    print(f"{GREEN}Identified speaker:{RESET} {name} (confidence: {score:.2%})")


def verify_speaker(args):
    key, region = get_config()
    profiles = _load_profiles()
    if args.name not in profiles:
        print(f"{RED}Speaker '{args.name}' not enrolled.{RESET}")
        sys.exit(1)
    profile_id = profiles[args.name]
    base = f"https://{region}.api.cognitive.microsoft.com/speaker/verification/v2.0"
    with open(args.file, "rb") as fh:
        resp = requests.post(
            f"{base}/text-independent/profiles/{profile_id}/verify",
            headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "audio/wav"},
            data=fh.read(),
        )
    if not resp.ok:
        print(f"{RED}Verification error: {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()
    decision = result.get("recognitionResult", "Unknown")
    score = result.get("score", 0)
    color = GREEN if decision == "Accept" else RED
    print(f"{color}Verification: {decision}{RESET}  score={score:.2%}")


def list_speakers(args):
    profiles = _load_profiles()
    if not profiles:
        print(f"{YELLOW}No enrolled speakers.{RESET}")
        return
    print(f"{GREEN}Enrolled speakers:{RESET}")
    for name, pid in profiles.items():
        print(f"  {name}  profile_id={pid}")


def main():
    parser = argparse.ArgumentParser(description="Voice Biometrics")
    sub = parser.add_subparsers(dest="command", required=True)

    p_e = sub.add_parser("enroll-speaker")
    p_e.add_argument("--name", required=True)
    p_e.add_argument("--file", required=True)

    p_i = sub.add_parser("identify-speaker")
    p_i.add_argument("--file", required=True)

    p_v = sub.add_parser("verify-speaker")
    p_v.add_argument("--name", required=True)
    p_v.add_argument("--file", required=True)

    sub.add_parser("list-speakers")

    args = parser.parse_args()
    dispatch = {
        "enroll-speaker": enroll_speaker,
        "identify-speaker": identify_speaker,
        "verify-speaker": verify_speaker,
        "list-speakers": list_speakers,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
