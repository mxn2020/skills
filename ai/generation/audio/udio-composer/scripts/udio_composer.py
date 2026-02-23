#!/usr/bin/env python3
"""Udio Composer – OC-0101"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://www.udio.com/api"


def _headers():
    token = os.environ.get("UDIO_AUTH_TOKEN")
    if not token:
        print(f"{RED}Error: UDIO_AUTH_TOKEN is not set{RESET}")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_track(track_id, max_wait=300):
    print(f"{YELLOW}Waiting for track {track_id}...{RESET}")
    for _ in range(max_wait // 10):
        time.sleep(10)
        data = _request("get", f"/songs/{track_id}")
        song = data.get("song") or data
        status = song.get("finished") or song.get("status")
        if status is True or status == "complete":
            return song
        print(f"{YELLOW}  status={status}...{RESET}")
    print(f"{RED}Timed out waiting for track{RESET}")
    sys.exit(1)


def generate(args):
    payload = {
        "prompt": args.prompt,
        "samplerOptions": {"seed": args.seed} if args.seed is not None else {},
    }
    if args.negative_prompt:
        payload["negativePrompt"] = args.negative_prompt

    data = _request("post", "/generate-proxy", json=payload)
    track_ids = data.get("trackIds") or [data.get("id")] or []
    if not track_ids or not track_ids[0]:
        print(f"{RED}No track ID returned. Response: {data}{RESET}")
        sys.exit(1)
    track_id = track_ids[0]
    print(f"{GREEN}Track generation started:{RESET} {track_id}")

    if args.wait:
        song = _poll_track(track_id)
        os.makedirs(args.output_dir, exist_ok=True)
        audio_url = song.get("song_path") or song.get("audio_url")
        if audio_url:
            out_path = os.path.join(args.output_dir, f"{track_id}.mp3")
            resp = requests.get(audio_url, timeout=120)
            with open(out_path, "wb") as f:
                f.write(resp.content)
            print(f"{GREEN}Saved:{RESET} {out_path}")
    else:
        print(f"{YELLOW}Use 'get-track --track-id {track_id}' to check status{RESET}")


def get_track(args):
    data = _request("get", f"/songs/{args.track_id}")
    song = data.get("song") or data
    finished = song.get("finished")
    color = GREEN if finished else YELLOW
    print(f"{color}Finished:{RESET} {finished}")
    print(f"  ID:    {song.get('id', 'n/a')}")
    print(f"  Title: {song.get('title', 'n/a')}")
    audio_url = song.get("song_path") or song.get("audio_url")
    if audio_url:
        print(f"  Audio: {audio_url}")


def list_tracks(args):
    data = _request("get", f"/songs?pageIndex=0&pageSize={args.limit}")
    songs = data.get("songs") or data if isinstance(data, list) else []
    print(f"{GREEN}Recent tracks:{RESET}")
    for song in songs[:args.limit]:
        finished = song.get("finished")
        color = GREEN if finished else YELLOW
        title = song.get("title", "Untitled")
        print(f"  {color}{'done' if finished else 'pending'}{RESET}  {song.get('id', 'n/a')}  {title}")


def download(args):
    data = _request("get", f"/songs/{args.track_id}")
    song = data.get("song") or data
    audio_url = song.get("song_path") or song.get("audio_url")
    if not audio_url:
        print(f"{RED}No audio URL available for track {args.track_id}{RESET}")
        sys.exit(1)
    resp = requests.get(audio_url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {args.output}")


def main():
    parser = argparse.ArgumentParser(description="Udio Composer – OC-0101")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate a new music track")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--wait", action="store_true", help="Poll until generation is complete")
    p_gen.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-track", help="Get track details and status")
    p_get.add_argument("--track-id", required=True)

    p_list = sub.add_parser("list-tracks", help="List recent tracks")
    p_list.add_argument("--limit", type=int, default=10)

    p_dl = sub.add_parser("download", help="Download a track to MP3")
    p_dl.add_argument("--track-id", required=True)
    p_dl.add_argument("--output", default="output.mp3")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "get-track": get_track,
        "list-tracks": list_tracks,
        "download": download,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
