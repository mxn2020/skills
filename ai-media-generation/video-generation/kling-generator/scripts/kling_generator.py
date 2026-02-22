#!/usr/bin/env python3
"""Kling Generator – OC-0097"""

import argparse
import base64
import hashlib
import hmac
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.klingai.com"


def _get_jwt_token():
    """Generate JWT token from Kling access key and secret key."""
    import json
    import struct

    access_key = os.environ.get("KLING_ACCESS_KEY")
    secret_key = os.environ.get("KLING_SECRET_KEY")
    if not access_key:
        print(f"{RED}Error: KLING_ACCESS_KEY is not set{RESET}")
        sys.exit(1)
    if not secret_key:
        print(f"{RED}Error: KLING_SECRET_KEY is not set{RESET}")
        sys.exit(1)

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": access_key,
        "exp": now + 1800,
        "nbf": now - 5,
    }

    def b64url(data):
        if isinstance(data, dict):
            data = json.dumps(data, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header_b64 = b64url(header)
    payload_b64 = b64url(payload)
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        secret_key.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{signing_input}.{sig_b64}"


def _headers():
    token = _get_jwt_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_task(task_id, endpoint, max_wait=600):
    print(f"{YELLOW}Polling task {task_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"{endpoint}/{task_id}")
        result = data.get("data", data)
        status = result.get("task_status", "unknown")
        if status == "succeed":
            return result
        if status in ("failed",):
            print(f"{RED}Task failed: {result.get('task_status_msg', 'Unknown error')}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for task{RESET}")
    sys.exit(1)


def _download(url, output_path):
    resp = requests.get(url, timeout=300)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _image_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def text_to_video(args):
    payload = {
        "model_name": "kling-v1",
        "prompt": args.prompt,
        "duration": str(args.duration),
        "mode": args.mode,
        "aspect_ratio": args.aspect_ratio,
    }
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["cfg_scale"] = 0.5
        payload["seed"] = args.seed

    data = _request("post", "/v1/videos/text2video", json=payload)
    result = data.get("data", data)
    task_id = result.get("task_id")
    if not task_id:
        print(f"{RED}No task ID returned. Response: {data}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Task created:{RESET} {task_id}")
    result = _poll_task(task_id, "/v1/videos/text2video")
    works = result.get("task_result", {}).get("videos", [])
    os.makedirs(args.output_dir, exist_ok=True)
    for i, work in enumerate(works):
        url = work.get("url")
        if url:
            out_path = os.path.join(args.output_dir, f"kling_{task_id}_{i}.mp4")
            _download(url, out_path)


def image_to_video(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "model_name": "kling-v1",
        "image": _image_to_b64(args.input),
        "duration": str(args.duration),
        "mode": args.mode,
    }
    if args.prompt:
        payload["prompt"] = args.prompt
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt

    data = _request("post", "/v1/videos/image2video", json=payload)
    result = data.get("data", data)
    task_id = result.get("task_id")
    if not task_id:
        print(f"{RED}No task ID returned. Response: {data}{RESET}")
        sys.exit(1)
    print(f"{GREEN}Task created:{RESET} {task_id}")
    result = _poll_task(task_id, "/v1/videos/image2video")
    works = result.get("task_result", {}).get("videos", [])
    os.makedirs(args.output_dir, exist_ok=True)
    for i, work in enumerate(works):
        url = work.get("url")
        if url:
            out_path = os.path.join(args.output_dir, f"kling_{task_id}_{i}.mp4")
            _download(url, out_path)


def get_task(args):
    data = _request("get", f"/v1/videos/text2video/{args.task_id}")
    result = data.get("data", data)
    status = result.get("task_status", "unknown")
    color = GREEN if status == "succeed" else YELLOW
    print(f"{color}Status:{RESET} {status}")
    print(f"  Task ID: {result.get('task_id', 'n/a')}")
    for v in result.get("task_result", {}).get("videos", []):
        print(f"  Video: {v.get('url', 'n/a')}")


def list_tasks(args):
    data = _request("get", f"/v1/videos/text2video?pageSize={args.limit}")
    tasks = data.get("data", {}).get("list") or []
    print(f"{GREEN}Recent tasks:{RESET}")
    for task in tasks:
        status = task.get("task_status", "unknown")
        color = GREEN if status == "succeed" else YELLOW
        print(f"  {color}{status}{RESET}  {task.get('task_id', 'n/a')}  {task.get('created_at', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Kling Generator – OC-0097")
    sub = parser.add_subparsers(dest="command", required=True)

    p_t2v = sub.add_parser("text-to-video", help="Generate a video from a text prompt")
    p_t2v.add_argument("--prompt", required=True)
    p_t2v.add_argument("--negative-prompt", default=None)
    p_t2v.add_argument("--duration", type=int, default=5, choices=[5, 10])
    p_t2v.add_argument("--mode", default="std", choices=["std", "pro"])
    p_t2v.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16", "1:1"])
    p_t2v.add_argument("--seed", type=int, default=None)
    p_t2v.add_argument("--output-dir", default=".")

    p_i2v = sub.add_parser("image-to-video", help="Animate an image into a video")
    p_i2v.add_argument("--input", required=True)
    p_i2v.add_argument("--prompt", default=None)
    p_i2v.add_argument("--negative-prompt", default=None)
    p_i2v.add_argument("--duration", type=int, default=5, choices=[5, 10])
    p_i2v.add_argument("--mode", default="std", choices=["std", "pro"])
    p_i2v.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-task", help="Get task status and result")
    p_get.add_argument("--task-id", required=True)

    p_list = sub.add_parser("list-tasks", help="List recent tasks")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "text-to-video": text_to_video,
        "image-to-video": image_to_video,
        "get-task": get_task,
        "list-tasks": list_tasks,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
