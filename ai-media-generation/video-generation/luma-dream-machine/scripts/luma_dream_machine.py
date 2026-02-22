#!/usr/bin/env python3
"""Luma Dream Machine – OC-0096"""

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

BASE_URL = "https://api.lumalabs.ai/dream-machine/v1"


def _headers():
    token = os.environ.get("LUMAAI_API_KEY")
    if not token:
        print(f"{RED}Error: LUMAAI_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_generation(generation_id, max_wait=600):
    print(f"{YELLOW}Polling generation {generation_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"/generations/{generation_id}")
        state = data.get("state", "unknown")
        if state == "completed":
            return data
        if state in ("failed",):
            failure = data.get("failure_reason", "Unknown error")
            print(f"{RED}Generation failed: {failure}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  state={state}...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for generation{RESET}")
    sys.exit(1)


def _download(url, output_path):
    resp = requests.get(url, timeout=300)
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


def generate(args):
    payload = {
        "prompt": args.prompt,
        "loop": args.loop,
        "aspect_ratio": args.aspect_ratio,
    }
    data = _request("post", "/generations", json=payload)
    generation_id = data.get("id")
    if not generation_id:
        print(f"{RED}No generation ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Generation started:{RESET} {generation_id}")
    result = _poll_generation(generation_id)
    video_url = result.get("assets", {}).get("video")
    if video_url:
        os.makedirs(args.output_dir, exist_ok=True)
        out_path = os.path.join(args.output_dir, f"luma_{generation_id}.mp4")
        _download(video_url, out_path)
    else:
        print(f"{YELLOW}No video URL found. Result:{RESET}")
        print(result)


def image_to_video(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "keyframes": {
            "frame0": {
                "type": "image",
                "url": _image_to_data_url(args.input),
            }
        },
        "loop": args.loop,
    }
    if args.prompt:
        payload["prompt"] = args.prompt

    data = _request("post", "/generations", json=payload)
    generation_id = data.get("id")
    if not generation_id:
        print(f"{RED}No generation ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Generation started:{RESET} {generation_id}")
    result = _poll_generation(generation_id)
    video_url = result.get("assets", {}).get("video")
    if video_url:
        os.makedirs(args.output_dir, exist_ok=True)
        out_path = os.path.join(args.output_dir, f"luma_{generation_id}.mp4")
        _download(video_url, out_path)


def extend(args):
    payload = {
        "keyframes": {
            "frame0": {
                "type": "generation",
                "id": args.generation_id,
            }
        },
    }
    if args.prompt:
        payload["prompt"] = args.prompt

    data = _request("post", "/generations", json=payload)
    new_id = data.get("id")
    if not new_id:
        print(f"{RED}No generation ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Extension started:{RESET} {new_id}")
    result = _poll_generation(new_id)
    video_url = result.get("assets", {}).get("video")
    if video_url:
        os.makedirs(args.output_dir, exist_ok=True)
        out_path = os.path.join(args.output_dir, f"luma_{new_id}.mp4")
        _download(video_url, out_path)


def get_generation(args):
    data = _request("get", f"/generations/{args.generation_id}")
    state = data.get("state", "unknown")
    color = GREEN if state == "completed" else YELLOW
    print(f"{color}State:{RESET} {state}")
    print(f"  ID: {data.get('id', 'n/a')}")
    print(f"  Created: {data.get('created_at', 'n/a')}")
    video_url = data.get("assets", {}).get("video")
    if video_url:
        print(f"  Video: {video_url}")


def list_generations(args):
    data = _request("get", f"/generations?limit={args.limit}")
    gens = data.get("generations") or data if isinstance(data, list) else []
    print(f"{GREEN}Recent generations:{RESET}")
    for g in gens:
        state = g.get("state", "unknown")
        color = GREEN if state == "completed" else YELLOW
        print(f"  {color}{state}{RESET}  {g.get('id', 'n/a')}  {g.get('created_at', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Luma Dream Machine – OC-0096")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate a video from a text prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--loop", action="store_true")
    p_gen.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16", "4:3", "3:4", "21:9", "9:21"])
    p_gen.add_argument("--output-dir", default=".")

    p_i2v = sub.add_parser("image-to-video", help="Create a video starting from an image")
    p_i2v.add_argument("--input", required=True)
    p_i2v.add_argument("--prompt", default=None)
    p_i2v.add_argument("--loop", action="store_true")
    p_i2v.add_argument("--output-dir", default=".")

    p_ext = sub.add_parser("extend", help="Extend an existing video generation")
    p_ext.add_argument("--generation-id", required=True)
    p_ext.add_argument("--prompt", default=None)
    p_ext.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-generation", help="Get generation status and result")
    p_get.add_argument("--generation-id", required=True)

    p_list = sub.add_parser("list-generations", help="List recent generations")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "image-to-video": image_to_video,
        "extend": extend,
        "get-generation": get_generation,
        "list-generations": list_generations,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
