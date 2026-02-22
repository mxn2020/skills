#!/usr/bin/env python3
"""Midjourney Prompter – OC-0083"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.useapi.net/v2"


def _headers():
    token = os.environ.get("MIDJOURNEY_API_KEY")
    if not token:
        print(f"{RED}Error: MIDJOURNEY_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _download_image(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download image: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _poll_job(job_id, max_wait=300):
    print(f"{YELLOW}Polling job {job_id}...{RESET}")
    for _ in range(max_wait // 10):
        data = _request("get", f"/midjourney/jobs/{job_id}")
        status = data.get("status", "unknown")
        if status == "completed":
            return data
        if status in ("failed", "cancelled"):
            print(f"{RED}Job {status}: {data.get('error', 'Unknown error')}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}, waiting...{RESET}")
        time.sleep(10)
    print(f"{RED}Timed out waiting for job{RESET}")
    sys.exit(1)


def imagine(args):
    prompt_parts = [args.prompt]
    prompt_parts.append(f"--ar {args.ar}")
    prompt_parts.append(f"--q {args.quality}")
    prompt_parts.append(f"--stylize {args.stylize}")
    full_prompt = " ".join(prompt_parts)

    payload = {"prompt": full_prompt}
    data = _request("post", "/midjourney/imagine", json=payload)
    job_id = data.get("jobid")
    if not job_id:
        print(f"{RED}No job ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Job created:{RESET} {job_id}")
    result = _poll_job(job_id)
    image_url = result.get("imageURL") or (result.get("attachments") or [{}])[0].get("url")
    if image_url:
        _download_image(image_url, args.output)
    else:
        print(f"{YELLOW}Job complete. Image URL not available. Result:{RESET}")
        print(result)


def upscale(args):
    payload = {"jobid": args.job_id, "button": f"U{args.index}"}
    data = _request("post", "/midjourney/button", json=payload)
    new_job_id = data.get("jobid")
    print(f"{GREEN}Upscale job created:{RESET} {new_job_id}")
    result = _poll_job(new_job_id)
    image_url = result.get("imageURL") or (result.get("attachments") or [{}])[0].get("url")
    if image_url:
        output = f"upscale_{args.job_id}_{args.index}.png"
        _download_image(image_url, output)


def variations(args):
    payload = {"jobid": args.job_id, "button": f"V{args.index}"}
    data = _request("post", "/midjourney/button", json=payload)
    new_job_id = data.get("jobid")
    print(f"{GREEN}Variation job created:{RESET} {new_job_id}")
    result = _poll_job(new_job_id)
    image_url = result.get("imageURL") or (result.get("attachments") or [{}])[0].get("url")
    if image_url:
        output = f"variation_{args.job_id}_{args.index}.png"
        _download_image(image_url, output)


def status(args):
    data = _request("get", f"/midjourney/jobs/{args.job_id}")
    job_status = data.get("status", "unknown")
    color = GREEN if job_status == "completed" else YELLOW
    print(f"{color}Status:{RESET} {job_status}")
    print(f"  Job ID: {data.get('jobid', 'n/a')}")
    print(f"  Created: {data.get('created', 'n/a')}")
    if data.get("imageURL"):
        print(f"  Image URL: {data['imageURL']}")


def list_jobs(args):
    data = _request("get", f"/midjourney/jobs?maxResults={args.limit}")
    jobs = data.get("jobs") or data.get("items") or []
    if not jobs:
        print(f"{YELLOW}No jobs found{RESET}")
        return
    print(f"{GREEN}Recent jobs:{RESET}")
    for job in jobs:
        job_status = job.get("status", "unknown")
        color = GREEN if job_status == "completed" else YELLOW
        print(f"  {color}{job_status}{RESET}  {job.get('jobid', 'n/a')}  {job.get('prompt', '')[:60]}")


def main():
    parser = argparse.ArgumentParser(description="Midjourney Prompter – OC-0083")
    sub = parser.add_subparsers(dest="command", required=True)

    p_imagine = sub.add_parser("imagine", help="Generate an image from a prompt")
    p_imagine.add_argument("--prompt", required=True)
    p_imagine.add_argument("--ar", default="1:1", help="Aspect ratio (e.g. 16:9)")
    p_imagine.add_argument("--quality", default="1", choices=["0.25", "0.5", "1", "2"])
    p_imagine.add_argument("--stylize", type=int, default=100)
    p_imagine.add_argument("--output", default="output.png")

    p_upscale = sub.add_parser("upscale", help="Upscale a specific image from a job")
    p_upscale.add_argument("--job-id", required=True)
    p_upscale.add_argument("--index", type=int, default=1, choices=[1, 2, 3, 4])

    p_var = sub.add_parser("variations", help="Create variations of a job image")
    p_var.add_argument("--job-id", required=True)
    p_var.add_argument("--index", type=int, default=1, choices=[1, 2, 3, 4])

    p_status = sub.add_parser("status", help="Get job status")
    p_status.add_argument("--job-id", required=True)

    p_list = sub.add_parser("list-jobs", help="List recent jobs")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "imagine": imagine,
        "upscale": upscale,
        "variations": variations,
        "status": status,
        "list-jobs": list_jobs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
