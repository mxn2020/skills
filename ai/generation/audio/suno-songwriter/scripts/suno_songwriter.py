#!/usr/bin/env python3
"""Suno Songwriter – OC-0100"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://studio-api.suno.ai/api"


def _headers():
    cookie = os.environ.get("SUNO_COOKIE")
    if not cookie:
        print(f"{RED}Error: SUNO_COOKIE is not set{RESET}")
        sys.exit(1)
    return {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_songs(song_ids, max_wait=300):
    print(f"{YELLOW}Waiting for songs to be ready...{RESET}")
    for _ in range(max_wait // 10):
        time.sleep(10)
        ids_param = ",".join(song_ids)
        data = _request("get", f"/feed/?ids={ids_param}")
        songs = data if isinstance(data, list) else data.get("songs", [])
        completed = [s for s in songs if s.get("status") == "complete"]
        if len(completed) >= len(song_ids):
            return completed
        print(f"{YELLOW}  {len(completed)}/{len(song_ids)} complete...{RESET}")
    print(f"{RED}Timed out waiting for songs{RESET}")
    sys.exit(1)


def generate(args):
    payload = {
        "prompt": args.prompt,
        "make_instrumental": args.make_instrumental,
        "mv": "chirp-v3-5",
    }
    data = _request("post", "/generate/v2/", json=payload)
    clips = data.get("clips") or data.get("songs") or []
    if not clips:
        print(f"{RED}No songs returned. Response: {data}{RESET}")
        sys.exit(1)
    song_ids = [c.get("id") for c in clips if c.get("id")]
    print(f"{GREEN}Generation started:{RESET} {', '.join(song_ids)}")

    if args.wait:
        songs = _poll_songs(song_ids)
        os.makedirs(args.output_dir, exist_ok=True)
        for song in songs:
            song_id = song.get("id")
            title = song.get("title", song_id) or song_id
            audio_url = song.get("audio_url")
            if audio_url:
                out_path = os.path.join(args.output_dir, f"{song_id}.mp3")
                resp = requests.get(audio_url, timeout=120)
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                print(f"{GREEN}Saved:{RESET} {out_path}  ({title})")
    else:
        print(f"{YELLOW}Use 'get-song --song-id <id>' to check status{RESET}")
        for sid in song_ids:
            print(f"  {sid}")


def get_song(args):
    data = _request("get", f"/feed/?ids={args.song_id}")
    songs = data if isinstance(data, list) else data.get("songs", [])
    if not songs:
        print(f"{YELLOW}No song found with ID {args.song_id}{RESET}")
        return
    song = songs[0]
    status = song.get("status", "unknown")
    color = GREEN if status == "complete" else YELLOW
    print(f"{color}Status:{RESET} {status}")
    print(f"  ID:    {song.get('id', 'n/a')}")
    print(f"  Title: {song.get('title', 'n/a')}")
    print(f"  Tags:  {song.get('tags', 'n/a')}")
    audio_url = song.get("audio_url")
    if audio_url:
        print(f"  Audio: {audio_url}")


def list_songs(args):
    data = _request("get", f"/feed/?page=0")
    songs = data if isinstance(data, list) else data.get("songs", [])
    songs = songs[: args.limit]
    print(f"{GREEN}Recent songs:{RESET}")
    for song in songs:
        status = song.get("status", "unknown")
        color = GREEN if status == "complete" else YELLOW
        title = song.get("title", "Untitled")
        print(f"  {color}{status}{RESET}  {song.get('id', 'n/a')}  {title}")


def download(args):
    data = _request("get", f"/feed/?ids={args.song_id}")
    songs = data if isinstance(data, list) else data.get("songs", [])
    if not songs:
        print(f"{RED}Song not found: {args.song_id}{RESET}")
        sys.exit(1)
    song = songs[0]
    audio_url = song.get("audio_url")
    if not audio_url:
        print(f"{RED}No audio URL available for song {args.song_id} (status: {song.get('status')}){RESET}")
        sys.exit(1)
    resp = requests.get(audio_url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {args.output}")


def main():
    parser = argparse.ArgumentParser(description="Suno Songwriter – OC-0100")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate a new song from a prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--make-instrumental", action="store_true")
    p_gen.add_argument("--wait", action="store_true", help="Poll until generation is complete")
    p_gen.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-song", help="Get song details and status")
    p_get.add_argument("--song-id", required=True)

    p_list = sub.add_parser("list-songs", help="List recent songs")
    p_list.add_argument("--limit", type=int, default=10)

    p_dl = sub.add_parser("download", help="Download a song to MP3")
    p_dl.add_argument("--song-id", required=True)
    p_dl.add_argument("--output", default="output.mp3")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "get-song": get_song,
        "list-songs": list_songs,
        "download": download,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
