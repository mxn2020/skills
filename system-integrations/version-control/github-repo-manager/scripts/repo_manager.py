#!/usr/bin/env python3
"""
GitHub Repo Manager — OC-0001
Create, list, delete repos; manage collaborators via the `gh` CLI.
"""

import sys
import json
import argparse
import subprocess

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"


def run_command(command, check=True):
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {command}{RESET}")
        print(f"{RED}Error: {e.stderr.strip()}{RESET}")
        if check:
            sys.exit(1)
        return None


def check_dependencies():
    try:
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}Error: 'gh' CLI not found. Install from https://cli.github.com/{RESET}")
        sys.exit(1)


def list_repos(org=None, limit=30, visibility="all"):
    if org:
        print(f"{YELLOW}Listing repos for org '{org}'...{RESET}")
        cmd = f"gh repo list {org} --limit {limit} --json name,description,visibility,url,updatedAt"
    else:
        print(f"{YELLOW}Listing your repositories...{RESET}")
        cmd = f"gh repo list --limit {limit} --json name,description,visibility,url,updatedAt"
    if visibility in ("public", "private"):
        cmd += f" --visibility {visibility}"
    output = run_command(cmd)
    repos = json.loads(output)
    print(f"{GREEN}Found {len(repos)} repositories:{RESET}")
    for r in repos:
        vis = r.get("visibility", "").lower()
        vis_color = CYAN if vis == "public" else YELLOW
        print(f"  {vis_color}[{vis}]{RESET}  {r['name']}  — {r.get('description', '')}")


def create_repo(name, description="", private=False, org=None):
    print(f"{YELLOW}Creating repository '{name}'...{RESET}")
    cmd = f"gh repo create {name} --confirm"
    if description:
        cmd += f' --description "{description}"'
    if private:
        cmd += " --private"
    else:
        cmd += " --public"
    if org:
        cmd = cmd.replace(f"gh repo create {name}", f"gh repo create {org}/{name}")
    output = run_command(cmd)
    print(f"{GREEN}Repository created: {output}{RESET}")


def delete_repo(repo, confirm=False):
    if not confirm:
        answer = input(f"{YELLOW}Delete '{repo}'? This is irreversible. Type the repo name to confirm: {RESET}")
        if answer.strip() != repo.split("/")[-1]:
            print(f"{RED}Confirmation failed. Aborting.{RESET}")
            sys.exit(1)
    print(f"{YELLOW}Deleting '{repo}'...{RESET}")
    run_command(f"gh repo delete {repo} --yes")
    print(f"{GREEN}Repository '{repo}' deleted.{RESET}")


def get_info(repo):
    print(f"{YELLOW}Fetching info for '{repo}'...{RESET}")
    output = run_command(
        f"gh repo view {repo} --json name,description,visibility,url,"
        f"stargazerCount,forkCount,defaultBranchRef,updatedAt,diskUsage"
    )
    info = json.loads(output)
    branch = (info.get("defaultBranchRef") or {}).get("name", "N/A")
    print(f"\n  {CYAN}Name:{RESET}        {info['name']}")
    print(f"  {CYAN}URL:{RESET}         {info['url']}")
    print(f"  {CYAN}Visibility:{RESET}  {info['visibility']}")
    print(f"  {CYAN}Stars:{RESET}       {info['stargazerCount']}")
    print(f"  {CYAN}Forks:{RESET}       {info['forkCount']}")
    print(f"  {CYAN}Branch:{RESET}      {branch}")
    print(f"  {CYAN}Updated:{RESET}     {info['updatedAt']}")
    print(f"  {CYAN}Size:{RESET}        {info['diskUsage']} KB")
    if info.get("description"):
        print(f"  {CYAN}Description:{RESET} {info['description']}")
    print()


def add_collaborator(repo, user, permission="push"):
    print(f"{YELLOW}Adding '{user}' to '{repo}' with '{permission}' access...{RESET}")
    run_command(f"gh api repos/{repo}/collaborators/{user} -X PUT -f permission={permission}")
    print(f"{GREEN}'{user}' added as collaborator with '{permission}' permission.{RESET}")


def remove_collaborator(repo, user):
    print(f"{YELLOW}Removing '{user}' from '{repo}'...{RESET}")
    run_command(f"gh api repos/{repo}/collaborators/{user} -X DELETE")
    print(f"{GREEN}'{user}' removed from '{repo}'.{RESET}")


def list_collaborators(repo):
    print(f"{YELLOW}Listing collaborators for '{repo}'...{RESET}")
    output = run_command(f"gh api repos/{repo}/collaborators --paginate")
    collabs = json.loads(output)
    if not collabs:
        print(f"  {YELLOW}No collaborators found.{RESET}")
        return
    print(f"{GREEN}Found {len(collabs)} collaborator(s):{RESET}")
    for c in collabs:
        role = c.get("role_name", "N/A")
        print(f"  {c['login']}  — {role}")


def main():
    parser = argparse.ArgumentParser(
        prog="repo_manager.py",
        description="GitHub Repo Manager — OC-0001"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-repos", help="List repositories")
    p.add_argument("--org", default=None, help="Organization name")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--visibility", default="all", choices=["public", "private", "all"])

    p = sub.add_parser("create-repo", help="Create a repository")
    p.add_argument("--name", required=True, help="Repository name")
    p.add_argument("--description", default="")
    p.add_argument("--private", action="store_true", help="Make the repo private")
    p.add_argument("--org", default=None, help="Create under an organization")

    p = sub.add_parser("delete-repo", help="Delete a repository")
    p.add_argument("--repo", required=True, help="Repository (owner/name)")
    p.add_argument("--confirm", action="store_true", help="Skip interactive confirmation")

    p = sub.add_parser("get-info", help="Show repository metadata")
    p.add_argument("--repo", required=True, help="Repository (owner/name)")

    p = sub.add_parser("add-collaborator", help="Add a collaborator")
    p.add_argument("--repo", required=True, help="Repository (owner/name)")
    p.add_argument("--user", required=True, help="GitHub username")
    p.add_argument("--permission", default="push",
                   choices=["pull", "push", "maintain", "triage", "admin"])

    p = sub.add_parser("remove-collaborator", help="Remove a collaborator")
    p.add_argument("--repo", required=True, help="Repository (owner/name)")
    p.add_argument("--user", required=True, help="GitHub username")

    p = sub.add_parser("list-collaborators", help="List collaborators")
    p.add_argument("--repo", required=True, help="Repository (owner/name)")

    args = parser.parse_args()
    check_dependencies()

    if args.command == "list-repos":
        list_repos(args.org, args.limit, args.visibility)
    elif args.command == "create-repo":
        create_repo(args.name, args.description, args.private, args.org)
    elif args.command == "delete-repo":
        delete_repo(args.repo, args.confirm)
    elif args.command == "get-info":
        get_info(args.repo)
    elif args.command == "add-collaborator":
        add_collaborator(args.repo, args.user, args.permission)
    elif args.command == "remove-collaborator":
        remove_collaborator(args.repo, args.user)
    elif args.command == "list-collaborators":
        list_collaborators(args.repo)


if __name__ == "__main__":
    main()
