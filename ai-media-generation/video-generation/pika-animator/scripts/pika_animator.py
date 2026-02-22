#!/usr/bin/env python3
"""Pika Animator – OC-0095"""

import argparse
import base64
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.pika.art/v1"


def _headers():
    token = os.environ.get("PIKA_API_KEY")
    if not token:
        print(f"{RED}Error: PIKA_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_video(video_id, max_wait=300):
    print(f"{YELLOW}Polling video {video_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"/videos/{video_id}")
        status = data.get("status", "unknown")
        if status in ("succeeded", "completed"):
            return data
        if status in ("failed", "error"):
            print(f"{RED}Video generation failed: {data.get('error', 'Unknown error')}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for video{RESET}")
    sys.exit(1)


def _download(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _image_to_data_url(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def animate(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "image": _image_to_data_url(args.input),
        "options": {
            "frameRate": args.fps,
            "duration": args.duration,
            "motion": args.motion_strength,
        },
    }
    if args.prompt:
        payload["prompt"] = {"text": args.prompt}

    data = _request("post", "/generate/animate", json=payload)
    video_id = data.get("id") or data.get("data", {}).get("id")
    if not video_id:
        print(f"{RED}No video ID returned. Response: {data}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Video job created:{RESET} {video_id}")
    result = _poll_video(video_id)
    video_url = result.get("resultUrl") or result.get("url")
    if video_url:
        os.makedirs(args.output_dir, exist_ok=True)
        out_path = os.path.join(args.output_dir, f"pika_{video_id}.mp4")
        _download(video_url, out_path)
    else:
        print(f"{YELLOW}Job complete. Result:{RESET}")
        print(result)


def text_to_video(args):
    payload = {
        "prompt": {"text": args.prompt},
        "options": {
            "frameRate": args.fps,
            "duration": args.duration,
            "aspectRatio": args.ratio,
        },
    }
    if args.negative_prompt:
        payload["prompt"]["negativeText"] = args.negative_prompt

    data = _request("post", "/generate/text2video", json=payload)
    video_id = data.get("id") or data.get("data", {}).get("id")
    if not video_id:
        print(f"{RED}No video ID returned. Response: {data}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Video job created:{RESET} {video_id}")
    result = _poll_video(video_id)
    video_url = result.get("resultUrl") or result.get("url")
    if video_url:
        os.makedirs(args.output_dir, exist_ok=True)
        out_path = os.path.join(args.output_dir, f"pika_{video_id}.mp4")
        _download(video_url, out_path)
    else:
        print(f"{YELLOW}Job complete. Result:{RESET}")
        print(result)


def get_video(args):
    data = _request("get", f"/videos/{args.video_id}")
    status = data.get("status", "unknown")
    color = GREEN if status in ("succeeded", "completed") else YELLOW
    print(f"{color}Status:{RESET} {status}")
    print(f"  ID: {data.get('id', 'n/a')}")
    url = data.get("resultUrl") or data.get("url")
    if url:
        print(f"  URL: {url}")


def list_videos(args):
    data = _request("get", f"/videos?limit={args.limit}")
    videos = data.get("videos") or data.get("data") or []
    print(f"{GREEN}Recent videos:{RESET}")
    for v in videos:
        status = v.get("status", "unknown")
        color = GREEN if status in ("succeeded", "completed") else YELLOW
        print(f"  {color}{status}{RESET}  {v.get('id', 'n/a')}  {v.get('createdAt', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Pika Animator – OC-0095")
    sub = parser.add_subparsers(dest="command", required=True)

    p_anim = sub.add_parser("animate", help="Animate a static image")
    p_anim.add_argument("--input", required=True)
    p_anim.add_argument("--prompt", default=None)
    p_anim.add_argument("--motion-strength", type=int, default=3, choices=[1, 2, 3, 4, 5])
    p_anim.add_argument("--fps", type=int, default=24, choices=[8, 16, 24])
    p_anim.add_argument("--duration", type=int, default=3, choices=[3, 5, 10])
    p_anim.add_argument("--output-dir", default=".")

    p_t2v = sub.add_parser("text-to-video", help="Generate a video from a text prompt")
    p_t2v.add_argument("--prompt", required=True)
    p_t2v.add_argument("--negative-prompt", default=None)
    p_t2v.add_argument("--fps", type=int, default=24, choices=[8, 16, 24])
    p_t2v.add_argument("--duration", type=int, default=3, choices=[3, 5, 10])
    p_t2v.add_argument("--ratio", default="16:9", choices=["16:9", "9:16", "1:1"])
    p_t2v.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-video", help="Get video status and URL")
    p_get.add_argument("--video-id", required=True)

    p_list = sub.add_parser("list-videos", help="List recent videos")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "animate": animate,
        "text-to-video": text_to_video,
        "get-video": get_video,
        "list-videos": list_videos,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
