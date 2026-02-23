#!/usr/bin/env python3
"""
GitLab Pipeline Monitor - Watch CI/CD pipeline status and report failures.
Uses GitLab REST API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

STATUS_COLORS = {
    "success": GREEN,
    "failed": RED,
    "running": YELLOW,
    "pending": YELLOW,
    "canceled": RED,
    "skipped": YELLOW,
    "manual": YELLOW,
    "created": YELLOW,
}


def get_config():
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        print(f"{RED}Error: GITLAB_TOKEN environment variable not set.{RESET}")
        sys.exit(1)
    url = os.environ.get("GITLAB_URL", "https://gitlab.com").rstrip("/")
    return url, token


def api_request(method, endpoint, token, base_url, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"PRIVATE-TOKEN": token}
    url = f"{base_url}/api/v4{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def encode_project(project):
    """URL-encode a project path for the GitLab API."""
    try:
        from urllib.parse import quote
    except ImportError:
        from urllib import quote
    return quote(project, safe="")


def list_pipelines(project, status=None, limit=20, ref=None):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Listing pipelines for {project}...{RESET}")

    params = {"per_page": limit}
    if status:
        params["status"] = status
    if ref:
        params["ref"] = ref

    pipelines = api_request("GET", f"/projects/{encoded}/pipelines", token, base_url, params=params)
    print(f"{GREEN}Found {len(pipelines)} pipelines:{RESET}")
    for p in pipelines:
        color = STATUS_COLORS.get(p["status"], RESET)
        print(f"  #{p['id']} [{color}{p['status']}{RESET}] ref={p['ref']} ({p['created_at']})")


def get_pipeline(project, pipeline_id):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Getting pipeline #{pipeline_id} for {project}...{RESET}")

    p = api_request("GET", f"/projects/{encoded}/pipelines/{pipeline_id}", token, base_url)
    color = STATUS_COLORS.get(p["status"], RESET)
    print(f"\n{GREEN}Pipeline #{p['id']}{RESET}")
    print(f"  Status:     {color}{p['status']}{RESET}")
    print(f"  Ref:        {p['ref']}")
    print(f"  SHA:        {p['sha'][:12]}")
    print(f"  Created:    {p['created_at']}")
    print(f"  Updated:    {p.get('updated_at', 'N/A')}")
    print(f"  Duration:   {p.get('duration', 'N/A')}s")
    print(f"  URL:        {p.get('web_url', 'N/A')}")


def get_jobs(project, pipeline_id):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Listing jobs for pipeline #{pipeline_id} in {project}...{RESET}")

    jobs = api_request("GET", f"/projects/{encoded}/pipelines/{pipeline_id}/jobs", token, base_url,
                       params={"per_page": 100})
    print(f"{GREEN}Found {len(jobs)} jobs:{RESET}")
    for j in jobs:
        color = STATUS_COLORS.get(j["status"], RESET)
        duration = f"{j.get('duration', 0):.1f}s" if j.get("duration") else "N/A"
        print(f"  {j['name']} (ID: {j['id']}) [{color}{j['status']}{RESET}] stage={j['stage']} duration={duration}")


def retry_job(project, job_id):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Retrying job {job_id} in {project}...{RESET}")

    result = api_request("POST", f"/projects/{encoded}/jobs/{job_id}/retry", token, base_url)
    print(f"{GREEN}Job {job_id} retried. New job ID: {result.get('id', 'N/A')}{RESET}")


def cancel_pipeline(project, pipeline_id):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Cancelling pipeline #{pipeline_id} in {project}...{RESET}")

    api_request("POST", f"/projects/{encoded}/pipelines/{pipeline_id}/cancel", token, base_url)
    print(f"{GREEN}Pipeline #{pipeline_id} cancelled.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="GitLab Pipeline Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-pipelines", help="List pipelines")
    p_list.add_argument("--project", required=True, help="GitLab project path (group/project)")
    p_list.add_argument("--status", choices=["running", "pending", "success", "failed", "canceled"])
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--ref", help="Filter by branch/tag")

    p_get = subparsers.add_parser("get-pipeline", help="Get pipeline details")
    p_get.add_argument("--project", required=True)
    p_get.add_argument("--pipeline-id", required=True, type=int)

    p_jobs = subparsers.add_parser("get-jobs", help="List jobs in a pipeline")
    p_jobs.add_argument("--project", required=True)
    p_jobs.add_argument("--pipeline-id", required=True, type=int)

    p_retry = subparsers.add_parser("retry-job", help="Retry a failed job")
    p_retry.add_argument("--project", required=True)
    p_retry.add_argument("--job-id", required=True, type=int)

    p_cancel = subparsers.add_parser("cancel-pipeline", help="Cancel a pipeline")
    p_cancel.add_argument("--project", required=True)
    p_cancel.add_argument("--pipeline-id", required=True, type=int)

    args = parser.parse_args()

    if args.command == "list-pipelines":
        list_pipelines(args.project, args.status, args.limit, args.ref)
    elif args.command == "get-pipeline":
        get_pipeline(args.project, args.pipeline_id)
    elif args.command == "get-jobs":
        get_jobs(args.project, args.pipeline_id)
    elif args.command == "retry-job":
        retry_job(args.project, args.job_id)
    elif args.command == "cancel-pipeline":
        cancel_pipeline(args.project, args.pipeline_id)


if __name__ == "__main__":
    main()
