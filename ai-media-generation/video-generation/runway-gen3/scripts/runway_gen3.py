#!/usr/bin/env python3
"""Runway Gen-3 – OC-0094"""

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

BASE_URL = "https://api.dev.runwayml.com/v1"


def _headers():
    token = os.environ.get("RUNWAYML_API_SECRET")
    if not token:
        print(f"{RED}Error: RUNWAYML_API_SECRET is not set{RESET}")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-09-13",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_task(task_id, max_wait=600):
    print(f"{YELLOW}Polling task {task_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"/tasks/{task_id}")
        status = data.get("status", "unknown")
        if status == "SUCCEEDED":
            return data
        if status in ("FAILED", "CANCELLED"):
            print(f"{RED}Task {status}: {data.get('failure', 'Unknown error')}{RESET}")
            sys.exit(1)
        progress = data.get("progress", 0)
        print(f"{YELLOW}  status={status} progress={progress:.0%}...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for task{RESET}")
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


def generate(args):
    payload = {
        "model": "gen3a_turbo",
        "promptText": args.prompt,
        "duration": args.duration,
        "ratio": args.ratio,
    }
    if args.negative_prompt:
        payload["promptNegative"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed

    data = _request("post", "/image_to_video", json=payload)
    task_id = data.get("id")
    if not task_id:
        print(f"{RED}No task ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Task created:{RESET} {task_id}")
    result = _poll_task(task_id)
    output_urls = result.get("output", [])
    os.makedirs(args.output_dir, exist_ok=True)
    for i, url in enumerate(output_urls):
        out_path = os.path.join(args.output_dir, f"runway_{task_id}_{i}.mp4")
        _download(url, out_path)


def image_to_video(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "model": "gen3a_turbo",
        "promptImage": _image_to_data_url(args.input),
        "promptText": args.prompt,
        "duration": args.duration,
        "ratio": args.ratio,
    }
    if args.seed is not None:
        payload["seed"] = args.seed

    data = _request("post", "/image_to_video", json=payload)
    task_id = data.get("id")
    if not task_id:
        print(f"{RED}No task ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Task created:{RESET} {task_id}")
    result = _poll_task(task_id)
    output_urls = result.get("output", [])
    os.makedirs(args.output_dir, exist_ok=True)
    for i, url in enumerate(output_urls):
        out_path = os.path.join(args.output_dir, f"runway_{task_id}_{i}.mp4")
        _download(url, out_path)


def get_task(args):
    data = _request("get", f"/tasks/{args.task_id}")
    status = data.get("status", "unknown")
    color = GREEN if status == "SUCCEEDED" else YELLOW
    print(f"{color}Status:{RESET} {status}")
    print(f"  ID: {data.get('id', 'n/a')}")
    print(f"  Created: {data.get('createdAt', 'n/a')}")
    progress = data.get("progress")
    if progress is not None:
        print(f"  Progress: {progress:.0%}")
    for url in data.get("output", []):
        print(f"  Output: {url}")


def list_tasks(args):
    data = _request("get", f"/tasks?limit={args.limit}")
    tasks = data.get("tasks") or data.get("data") or []
    print(f"{GREEN}Recent tasks:{RESET}")
    for task in tasks:
        status = task.get("status", "unknown")
        color = GREEN if status == "SUCCEEDED" else YELLOW
        print(f"  {color}{status}{RESET}  {task.get('id', 'n/a')}  {task.get('createdAt', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Runway Gen-3 – OC-0094")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate a video from a text prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--duration", type=int, default=5, choices=[5, 10])
    p_gen.add_argument("--ratio", default="1280:768", choices=["1280:768", "768:1280"])
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--output-dir", default=".")

    p_i2v = sub.add_parser("image-to-video", help="Animate an image with a text prompt")
    p_i2v.add_argument("--input", required=True)
    p_i2v.add_argument("--prompt", required=True)
    p_i2v.add_argument("--duration", type=int, default=5, choices=[5, 10])
    p_i2v.add_argument("--ratio", default="1280:768", choices=["1280:768", "768:1280"])
    p_i2v.add_argument("--seed", type=int, default=None)
    p_i2v.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-task", help="Get task status and result")
    p_get.add_argument("--task-id", required=True)

    p_list = sub.add_parser("list-tasks", help="List recent tasks")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "image-to-video": image_to_video,
        "get-task": get_task,
        "list-tasks": list_tasks,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
