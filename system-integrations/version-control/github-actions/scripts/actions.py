#!/usr/bin/env python3
"""
GitHub Actions Trigger - Manually dispatch workflows, monitor runs, and manage CI/CD.
Uses the `gh` CLI for GitHub API interactions.
"""

import sys
import json
import argparse
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

STATUS_COLORS = {
    "completed": GREEN,
    "in_progress": YELLOW,
    "queued": YELLOW,
    "failure": RED,
    "success": GREEN,
    "cancelled": RED,
}


def run_command(command, check=True):
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {command}{RESET}")
        print(f"{RED}Error: {e.stderr}{RESET}")
        if check:
            sys.exit(1)
        return None


def check_dependencies():
    try:
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}Error: 'gh' CLI not found. Please install GitHub CLI.{RESET}")
        sys.exit(1)


def list_workflows(repo):
    print(f"{YELLOW}Listing workflows for {repo}...{RESET}")
    output = run_command(f"gh api repos/{repo}/actions/workflows --jq '.workflows[] | {{id, name, path, state}}'")
    if not output:
        print(f"{YELLOW}No workflows found.{RESET}")
        return

    print(f"{GREEN}Workflows:{RESET}")
    for line in output.strip().split("\n"):
        if not line.strip():
            continue
        wf = json.loads(line)
        state_color = GREEN if wf["state"] == "active" else RED
        print(f"  {wf['name']} (ID: {wf['id']}) [{state_color}{wf['state']}{RESET}]")
        print(f"    Path: {wf['path']}")


def trigger_workflow(repo, workflow, ref="main", inputs=None):
    print(f"{YELLOW}Triggering workflow '{workflow}' on {ref} in {repo}...{RESET}")
    cmd = f"gh workflow run {workflow} --repo {repo} --ref {ref}"
    if inputs:
        try:
            input_dict = json.loads(inputs)
            for key, value in input_dict.items():
                cmd += f" -f {key}={value}"
        except json.JSONDecodeError:
            print(f"{RED}Error: --inputs must be valid JSON.{RESET}")
            sys.exit(1)

    run_command(cmd)
    print(f"{GREEN}Workflow '{workflow}' triggered on {ref}.{RESET}")


def get_run_status(repo, run_id):
    print(f"{YELLOW}Getting status of run {run_id} in {repo}...{RESET}")
    output = run_command(
        f"gh api repos/{repo}/actions/runs/{run_id} "
        f"--jq '{{id, name: .name, status, conclusion, html_url, created_at, updated_at, head_branch}}'"
    )
    run_info = json.loads(output)

    status = run_info.get("status", "unknown")
    conclusion = run_info.get("conclusion", "pending")
    color = STATUS_COLORS.get(conclusion, STATUS_COLORS.get(status, RESET))

    print(f"\n{GREEN}Run #{run_info['id']}: {run_info.get('name', 'N/A')}{RESET}")
    print(f"  Status:     {color}{status}{RESET}")
    print(f"  Conclusion: {color}{conclusion}{RESET}")
    print(f"  Branch:     {run_info.get('head_branch', 'N/A')}")
    print(f"  Created:    {run_info.get('created_at', 'N/A')}")
    print(f"  URL:        {run_info.get('html_url', 'N/A')}")


def list_runs(repo, workflow=None, limit=20, status=None):
    print(f"{YELLOW}Listing workflow runs for {repo}...{RESET}")
    cmd = f"gh run list --repo {repo} --limit {limit} --json databaseId,displayTitle,status,conclusion,workflowName,createdAt"
    if workflow:
        cmd += f" --workflow {workflow}"
    if status:
        cmd += f" --status {status}"

    output = run_command(cmd)
    runs = json.loads(output)

    print(f"{GREEN}Found {len(runs)} runs:{RESET}")
    for r in runs:
        conclusion = r.get("conclusion", "pending")
        status_val = r.get("status", "unknown")
        display = conclusion if conclusion else status_val
        color = STATUS_COLORS.get(display, RESET)
        print(f"  #{r['databaseId']} {r['displayTitle']}")
        print(f"    Workflow: {r['workflowName']} | {color}{display}{RESET} | {r.get('createdAt', '')}")


def cancel_run(repo, run_id):
    print(f"{YELLOW}Cancelling run {run_id} in {repo}...{RESET}")
    run_command(f"gh run cancel {run_id} --repo {repo}")
    print(f"{GREEN}Run {run_id} cancelled.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="GitHub Actions Trigger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list_wf = subparsers.add_parser("list-workflows", help="List workflows")
    p_list_wf.add_argument("--repo", required=True)

    p_trigger = subparsers.add_parser("trigger-workflow", help="Trigger a workflow")
    p_trigger.add_argument("--repo", required=True)
    p_trigger.add_argument("--workflow", required=True, help="Workflow filename or ID")
    p_trigger.add_argument("--ref", default="main", help="Git ref to run on")
    p_trigger.add_argument("--inputs", help="JSON string of workflow inputs")

    p_status = subparsers.add_parser("get-run-status", help="Get run status")
    p_status.add_argument("--repo", required=True)
    p_status.add_argument("--run-id", required=True)

    p_list_runs = subparsers.add_parser("list-runs", help="List workflow runs")
    p_list_runs.add_argument("--repo", required=True)
    p_list_runs.add_argument("--workflow", help="Filter by workflow filename")
    p_list_runs.add_argument("--limit", type=int, default=20)
    p_list_runs.add_argument("--status", choices=["queued", "in_progress", "completed"])

    p_cancel = subparsers.add_parser("cancel-run", help="Cancel a workflow run")
    p_cancel.add_argument("--repo", required=True)
    p_cancel.add_argument("--run-id", required=True)

    args = parser.parse_args()
    check_dependencies()

    if args.command == "list-workflows":
        list_workflows(args.repo)
    elif args.command == "trigger-workflow":
        trigger_workflow(args.repo, args.workflow, args.ref, args.inputs)
    elif args.command == "get-run-status":
        get_run_status(args.repo, args.run_id)
    elif args.command == "list-runs":
        list_runs(args.repo, args.workflow, args.limit, args.status)
    elif args.command == "cancel-run":
        cancel_run(args.repo, args.run_id)


if __name__ == "__main__":
    main()
