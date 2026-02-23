#!/usr/bin/env python3
"""
gh Skill — GitHub CLI wrapper for AI agents.

Covers:
  gh repo   → repository management
  gh pr     → pull request lifecycle
  gh agent-task → Copilot coding agent tasks (preview, requires OAuth)

Dependency: gh CLI >= 2.80.0
Auth:
  - repo / pr commands: GITHUB_TOKEN or GH_TOKEN (PAT with repo scope) is enough.
  - agent-task commands: OAuth session required. PAT alone is blocked by GitHub.
    The host must have previously completed `gh auth login`.
"""

import sys
import json
import argparse
import subprocess
import base64
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

SKILL_ROOT    = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"  # .github/agents/*.md templates


# ── Low-level helpers ─────────────────────────────────────────────────────────

def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def check_gh():
    """Verify gh is on PATH and >= 2.80.0 (for agent-task support)."""
    try:
        out = subprocess.run(
            ["gh", "--version"], check=True, capture_output=True, text=True
        ).stdout.split()
        # out[2] is e.g. "2.81.0"
        ver = tuple(int(x) for x in out[2].split(".")[:2])
        if ver < (2, 80):
            print(
                f"{YELLOW}Warning: gh {out[2]} detected. "
                f"gh agent-task requires >= 2.80.0. Run: gh upgrade{RESET}"
            )
    except (FileNotFoundError, subprocess.CalledProcessError, IndexError, ValueError):
        _die("'gh' CLI not found. Install from https://cli.github.com/")


def _run(args: list[str], *, input: str | None = None, check: bool = True) -> str:
    """Run gh command (list form, no shell=True). Return stdout."""
    try:
        r = subprocess.run(args, check=check, capture_output=True, text=True, input=input)
        return r.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {' '.join(args)}{RESET}", file=sys.stderr)
        if e.stderr:
            print(f"{RED}{e.stderr.strip()}{RESET}", file=sys.stderr)
        if check:
            sys.exit(1)
        return ""


def _run_tty(args: list[str]) -> None:
    """Run gh command inheriting stdio (for commands that stream output)."""
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        _die(f"Command failed: {' '.join(args)}")


def _resolve_repo(repo: str) -> str:
    """Expand a bare repo name to owner/repo using the gh API."""
    if "/" in repo:
        return repo
    owner = _run(["gh", "api", "user", "--jq", ".login"])
    return f"{owner}/{repo}"


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


# ── gh repo ───────────────────────────────────────────────────────────────────

def repo_list(limit: int = 30, org: str | None = None):
    args = ["gh", "repo", "list", "--limit", str(limit),
            "--json", "name,description,visibility,url,updatedAt"]
    if org:
        args += ["--org", org]
    repos = json.loads(_run(args))
    print(f"{GREEN}Found {len(repos)} repositories:{RESET}")
    for r in repos:
        desc = f"  {r.get('description') or ''}"
        print(f"  {CYAN}{r['name']}{RESET} ({r['visibility'].lower()})  {r['url']}{desc}")


def repo_create(
    name: str,
    private: bool = False,
    description: str = "",
    auto_init: bool = False,
    org: str | None = None,
):
    full_name = f"{org}/{name}" if org else name
    args = ["gh", "repo", "create", full_name,
            "--private" if private else "--public"]
    if description:
        args += ["--description", description]
    if auto_init:
        args.append("--add-readme")
    print(f"{YELLOW}Creating repository '{full_name}'…{RESET}")
    out = _run(args)
    print(f"{GREEN}Created: {out}{RESET}")


def repo_view(repo: str):
    _run_tty(["gh", "repo", "view", _resolve_repo(repo)])


def repo_edit(
    repo: str,
    description: str | None = None,
    visibility: str | None = None,
):
    args = ["gh", "repo", "edit", _resolve_repo(repo)]
    if description is not None:
        args += ["--description", description]
    if visibility:
        args += ["--visibility", visibility]
    _run(args)
    print(f"{GREEN}Updated {repo}{RESET}")


def repo_delete(repo: str, yes: bool = False):
    args = ["gh", "repo", "delete", _resolve_repo(repo)]
    if yes:
        args.append("--yes")
    _run_tty(args)


def repo_clone(repo: str, directory: str | None = None):
    args = ["gh", "repo", "clone", _resolve_repo(repo)]
    if directory:
        args.append(directory)
    _run_tty(args)


# ── gh pr ─────────────────────────────────────────────────────────────────────

def pr_create(
    title: str,
    body: str = "",
    base: str = "",
    head: str = "",
    draft: bool = False,
    assignees: list[str] | None = None,
    labels: list[str] | None = None,
    repo: str | None = None,
):
    args = ["gh", "pr", "create", "--title", title]
    if body:        args += ["--body", body]
    if base:        args += ["--base", base]
    if head:        args += ["--head", head]
    if draft:       args.append("--draft")
    if assignees:   args += ["--assignee", ",".join(assignees)]
    if labels:      args += ["--label", ",".join(labels)]
    if repo:        args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_list(
    state: str = "open",
    limit: int = 20,
    author: str | None = None,
    label: str | None = None,
    base: str | None = None,
    repo: str | None = None,
):
    args = ["gh", "pr", "list",
            "--state", state,
            "--limit", str(limit),
            "--json", "number,title,author,state,headRefName,baseRefName,url,isDraft"]
    if author: args += ["--author", author]
    if label:  args += ["--label", label]
    if base:   args += ["--base", base]
    if repo:   args += ["--repo", _resolve_repo(repo)]
    prs = json.loads(_run(args))
    if not prs:
        print(f"{YELLOW}No pull requests found.{RESET}")
        return
    print(f"{GREEN}Found {len(prs)} PR(s):{RESET}")
    for pr in prs:
        draft = " [DRAFT]" if pr.get("isDraft") else ""
        print(
            f"  #{pr['number']}  {CYAN}{pr['title']}{RESET}{draft}\n"
            f"    {pr['headRefName']} → {pr['baseRefName']} | "
            f"@{pr['author']['login']} | {pr['url']}"
        )


def pr_view(number: str, repo: str | None = None):
    args = ["gh", "pr", "view", str(number), "--comments"]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_merge(
    number: str,
    method: str = "merge",
    delete_branch: bool = True,
    repo: str | None = None,
):
    flag = {"merge": "--merge", "squash": "--squash", "rebase": "--rebase"}.get(method, "--merge")
    args = ["gh", "pr", "merge", str(number), flag]
    if delete_branch: args.append("--delete-branch")
    if repo:          args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_review(
    number: str,
    action: str = "approve",
    body: str = "",
    repo: str | None = None,
):
    flag = {
        "approve":         "--approve",
        "request-changes": "--request-changes",
        "comment":         "--comment",
    }.get(action, "--comment")
    args = ["gh", "pr", "review", str(number), flag]
    if body: args += ["--body", body]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_checks(number: str, repo: str | None = None):
    args = ["gh", "pr", "checks", str(number)]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_comment(number: str, body: str, repo: str | None = None):
    args = ["gh", "pr", "comment", str(number), "--body", body]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_edit(
    number: str,
    title: str | None = None,
    body: str | None = None,
    base: str | None = None,
    add_labels: list[str] | None = None,
    add_assignees: list[str] | None = None,
    repo: str | None = None,
):
    args = ["gh", "pr", "edit", str(number)]
    if title:         args += ["--title", title]
    if body:          args += ["--body", body]
    if base:          args += ["--base", base]
    if add_labels:    args += ["--add-label", ",".join(add_labels)]
    if add_assignees: args += ["--add-assignee", ",".join(add_assignees)]
    if repo:          args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_close(
    number: str,
    comment: str = "",
    delete_branch: bool = False,
    repo: str | None = None,
):
    args = ["gh", "pr", "close", str(number)]
    if comment:       args += ["--comment", comment]
    if delete_branch: args.append("--delete-branch")
    if repo:          args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_ready(number: str, repo: str | None = None):
    """Mark a draft PR as ready for review."""
    args = ["gh", "pr", "ready", str(number)]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


def pr_diff(number: str, repo: str | None = None):
    args = ["gh", "pr", "diff", str(number)]
    if repo: args += ["--repo", _resolve_repo(repo)]
    _run_tty(args)


# ── gh agent-task ─────────────────────────────────────────────────────────────
#
# What this does:
#   Delegates a coding task to the GitHub Copilot coding agent. The agent runs
#   remotely in a sandboxed GitHub environment, makes code changes, and opens
#   a pull request. Progress is tracked via `gh agent-task view`.
#
# Custom agents:
#   A .github/agents/<name>.md file in the target repo customises the agent's
#   persona, tools and instructions. Install them with `agent-config install`
#   (see below). Pass the name (without .md) via --custom-agent.
#
# Auth requirement:
#   gh agent-task currently requires an OAuth session (not just a PAT).
#   Exit code 4 = authentication required.

def agent_task_create(
    prompt: str,
    repo: str | None = None,
    base: str | None = None,
    custom_agent: str | None = None,
    follow: bool = False,
    from_file: str | None = None,
):
    """
    Create a Copilot coding agent task.

    Maps directly to:
      gh agent-task create [<prompt>] [-F <file>] [-b <branch>]
                           [-a <agent>] [--follow] [-R <repo>]
    """
    if from_file:
        # Pass a prompt file with -F (supports "-" for stdin)
        args = ["gh", "agent-task", "create", "-F", from_file]
    else:
        args = ["gh", "agent-task", "create", prompt]

    if repo:         args += ["-R", _resolve_repo(repo)]
    if base:         args += ["-b", base]
    if custom_agent: args += ["-a", custom_agent]
    if follow:       args.append("--follow")

    print(f"{YELLOW}Creating agent task…{RESET}")
    _run_tty(args)


def agent_task_list(limit: int = 30, web: bool = False):
    """
    List recent Copilot coding agent tasks.

    Maps to: gh agent-task list [-L <n>] [-w]
    Note: gh agent-task list has no --repo flag — it lists tasks for the
    authenticated user across all repos.
    """
    args = ["gh", "agent-task", "list", "-L", str(limit)]
    if web: args.append("--web")
    _run_tty(args)


def agent_task_view(
    session_id: str,
    repo: str | None = None,
    follow: bool = False,
    log: bool = False,
    web: bool = False,
):
    """
    View a Copilot coding agent task session.

    <session_id> may be:
      - A session UUID
      - A PR number (in the current repo, or with --repo)
      - owner/repo#<number>
      - A PR URL
      - A branch name

    Maps to: gh agent-task view [<session-id>|<pr-number>|<pr-url>|<pr-branch>]
                                 [-R <repo>] [--follow] [--log] [-w]
    """
    args = ["gh", "agent-task", "view", str(session_id)]
    if repo:   args += ["-R", _resolve_repo(repo)]
    if follow: args.append("--follow")
    if log:    args.append("--log")
    if web:    args.append("--web")
    _run_tty(args)


# ── agent-config: manage .github/agents/*.md files via GitHub API ─────────────
#
# These are the custom agent persona files consumed by `gh agent-task --custom-agent`.
# We push/pull them via the GitHub Contents API so no local clone is needed.

def agent_config_install(repo: str, agent_name: str):
    """Upload a local template to .github/agents/<name>.md in the target repo."""
    template = TEMPLATES_DIR / f"{agent_name}.md"
    if not template.exists():
        _die(f"Template '{agent_name}.md' not found in {TEMPLATES_DIR}")

    repo = _resolve_repo(repo)
    content = template.read_text()

    # Resolve default branch
    try:
        info   = json.loads(_run(["gh", "repo", "view", repo, "--json", "defaultBranchRef"]))
        branch = info.get("defaultBranchRef", {}).get("name", "main")
    except Exception:
        branch = "main"

    target = f".github/agents/{agent_name}.md"

    # Fetch SHA if file exists (required for PUT-to-update)
    sha = None
    raw = _run(["gh", "api", f"repos/{repo}/contents/{target}"], check=False)
    if raw:
        try:
            sha = json.loads(raw).get("sha")
            print(f"{YELLOW}  Existing file found — updating…{RESET}")
        except Exception:
            pass

    payload = {"message": f"chore: install agent '{agent_name}'",
               "content": _b64(content), "branch": branch}
    if sha:
        payload["sha"] = sha

    try:
        subprocess.run(
            ["gh", "api", f"repos/{repo}/contents/{target}", "-X", "PUT", "--input", "-"],
            input=json.dumps(payload), text=True, check=True, capture_output=True,
        )
        print(f"{GREEN}Installed: {repo}/{target}{RESET}")
    except subprocess.CalledProcessError as e:
        _die(f"Install failed:\n{e.stderr}")


def agent_config_list(repo: str):
    """List .github/agents/*.md files in the target repo."""
    repo = _resolve_repo(repo)
    raw  = _run(["gh", "api", f"repos/{repo}/contents/.github/agents"], check=False)
    if not raw:
        print(f"{YELLOW}No .github/agents/ directory in {repo}.{RESET}")
        return
    files = [f for f in json.loads(raw) if isinstance(f, dict) and f["name"].endswith(".md")]
    if not files:
        print(f"{YELLOW}No agent config files found.{RESET}")
        return
    print(f"{GREEN}Agent configs in {repo}:{RESET}")
    for f in files:
        print(f"  {CYAN}{f['name'].removesuffix('.md')}{RESET}  {f['html_url']}")


def agent_config_remove(repo: str, agent_name: str):
    """Delete .github/agents/<name>.md from the target repo."""
    repo   = _resolve_repo(repo)
    target = f".github/agents/{agent_name}.md"
    raw    = _run(["gh", "api", f"repos/{repo}/contents/{target}"], check=False)
    if not raw:
        _die(f"Agent config '{agent_name}' not found in {repo}")
    sha     = json.loads(raw)["sha"]
    payload = json.dumps({"message": f"chore: remove agent '{agent_name}'", "sha": sha})
    subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{target}", "-X", "DELETE", "--input", "-"],
        input=payload, text=True, check=True,
    )
    print(f"{GREEN}Removed {repo}/{target}{RESET}")


# ── CLI parser ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gh_skill.py",
        description=(
            "gh skill: manages GitHub repos, PRs, and Copilot coding agent tasks.\n"
            "Uses the gh CLI exclusively. See SKILL.md for auth requirements."
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # ── repo ──────────────────────────────────────────────────────────────────
    rp = sub.add_parser("repo", help="Repository management  (gh repo)")
    rs = rp.add_subparsers(dest="sub", required=True)

    c = rs.add_parser("list");    c.add_argument("--limit", type=int, default=30); c.add_argument("--org")
    c = rs.add_parser("create");  c.add_argument("name"); c.add_argument("--private", action="store_true"); c.add_argument("--description", default=""); c.add_argument("--auto-init", action="store_true", dest="auto_init"); c.add_argument("--org")
    c = rs.add_parser("view");    c.add_argument("repo")
    c = rs.add_parser("edit");    c.add_argument("repo"); c.add_argument("--description"); c.add_argument("--visibility", choices=["public","private","internal"])
    c = rs.add_parser("delete");  c.add_argument("repo"); c.add_argument("--yes", action="store_true")
    c = rs.add_parser("clone");   c.add_argument("repo"); c.add_argument("directory", nargs="?")

    # ── pr ────────────────────────────────────────────────────────────────────
    pp = sub.add_parser("pr", help="Pull request management  (gh pr)")
    ps = pp.add_subparsers(dest="sub", required=True)

    c = ps.add_parser("create");  c.add_argument("--title", required=True); c.add_argument("--body", default=""); c.add_argument("--base", default=""); c.add_argument("--head", default=""); c.add_argument("--draft", action="store_true"); c.add_argument("--assignee", nargs="*"); c.add_argument("--label", nargs="*"); c.add_argument("--repo")
    c = ps.add_parser("list");    c.add_argument("--state", default="open", choices=["open","closed","merged","all"]); c.add_argument("--limit", type=int, default=20); c.add_argument("--author"); c.add_argument("--label"); c.add_argument("--base"); c.add_argument("--repo")
    c = ps.add_parser("view");    c.add_argument("number"); c.add_argument("--repo")
    c = ps.add_parser("merge");   c.add_argument("number"); c.add_argument("--method", default="merge", choices=["merge","squash","rebase"]); c.add_argument("--no-delete-branch", action="store_true", dest="no_del"); c.add_argument("--repo")
    c = ps.add_parser("review");  c.add_argument("number"); c.add_argument("--action", default="approve", choices=["approve","request-changes","comment"]); c.add_argument("--body", default=""); c.add_argument("--repo")
    c = ps.add_parser("checks");  c.add_argument("number"); c.add_argument("--repo")
    c = ps.add_parser("comment"); c.add_argument("number"); c.add_argument("--body", required=True); c.add_argument("--repo")
    c = ps.add_parser("edit");    c.add_argument("number"); c.add_argument("--title"); c.add_argument("--body"); c.add_argument("--base"); c.add_argument("--add-label", nargs="*", dest="add_label"); c.add_argument("--add-assignee", nargs="*", dest="add_assignee"); c.add_argument("--repo")
    c = ps.add_parser("close");   c.add_argument("number"); c.add_argument("--comment", default=""); c.add_argument("--delete-branch", action="store_true", dest="del_branch"); c.add_argument("--repo")
    c = ps.add_parser("ready");   c.add_argument("number"); c.add_argument("--repo")
    c = ps.add_parser("diff");    c.add_argument("number"); c.add_argument("--repo")

    # ── agent-task ────────────────────────────────────────────────────────────
    at = sub.add_parser(
        "agent-task",
        help=(
            "Copilot coding agent tasks  (gh agent-task — preview, requires OAuth)\n"
            "Creates tasks that run remotely and open a PR when complete."
        ),
    )
    ats = at.add_subparsers(dest="sub", required=True)

    c = ats.add_parser("create",
        help="Create a task. Copilot runs it remotely and opens a PR.")
    c.add_argument("prompt", nargs="?", default="",
        help="Task description. Omit to open an editor, or use --from-file.")
    c.add_argument("-R", "--repo",         help="OWNER/REPO (default: cwd repo)")
    c.add_argument("-b", "--base",         help="Base branch for the resulting PR")
    c.add_argument("-a", "--custom-agent", dest="custom_agent",
        help="Name of a custom agent in .github/agents/<name>.md")
    c.add_argument("--follow",             action="store_true",
        help="Stream live session logs after creation")
    c.add_argument("-F", "--from-file",    dest="from_file",
        help="Read task description from a file (use '-' for stdin)")

    c = ats.add_parser("list",
        help="List recent Copilot coding agent tasks.")
    c.add_argument("-L", "--limit", type=int, default=30)
    c.add_argument("-w", "--web",   action="store_true", help="Open in browser")

    c = ats.add_parser("view",
        help="View a task by session UUID, PR number, PR URL, or branch name.")
    c.add_argument("id", help="Session UUID, PR number, OWNER/REPO#N, PR URL, or branch")
    c.add_argument("-R", "--repo",   help="OWNER/REPO")
    c.add_argument("--follow",       action="store_true", help="Stream live logs")
    c.add_argument("--log",          action="store_true", help="Show full session log")
    c.add_argument("-w", "--web",    action="store_true", help="Open in browser")

    # ── agent-config ──────────────────────────────────────────────────────────
    ac = sub.add_parser(
        "agent-config",
        help=(
            "Manage .github/agents/*.md custom agent configs in a repo.\n"
            "These define custom personas used by `agent-task --custom-agent`."
        ),
    )
    acs = ac.add_subparsers(dest="sub", required=True)

    c = acs.add_parser("install", help="Upload a local template to a repo")
    c.add_argument("repo");  c.add_argument("name", help="Agent template name (no .md)")
    c = acs.add_parser("list",    help="List installed agent configs in a repo")
    c.add_argument("repo")
    c = acs.add_parser("remove",  help="Delete an agent config from a repo")
    c.add_argument("repo");  c.add_argument("name")

    return p


def main():
    args = build_parser().parse_args()
    check_gh()

    if args.cmd == "repo":
        if   args.sub == "list":   repo_list(args.limit, args.org)
        elif args.sub == "create": repo_create(args.name, args.private, args.description, args.auto_init, args.org)
        elif args.sub == "view":   repo_view(args.repo)
        elif args.sub == "edit":   repo_edit(args.repo, args.description, args.visibility)
        elif args.sub == "delete": repo_delete(args.repo, args.yes)
        elif args.sub == "clone":  repo_clone(args.repo, args.directory)

    elif args.cmd == "pr":
        if   args.sub == "create":  pr_create(args.title, args.body, args.base, args.head, args.draft, args.assignee, args.label, args.repo)
        elif args.sub == "list":    pr_list(args.state, args.limit, args.author, args.label, args.base, args.repo)
        elif args.sub == "view":    pr_view(args.number, args.repo)
        elif args.sub == "merge":   pr_merge(args.number, args.method, not args.no_del, args.repo)
        elif args.sub == "review":  pr_review(args.number, args.action, args.body, args.repo)
        elif args.sub == "checks":  pr_checks(args.number, args.repo)
        elif args.sub == "comment": pr_comment(args.number, args.body, args.repo)
        elif args.sub == "edit":    pr_edit(args.number, args.title, args.body, args.base, args.add_label, args.add_assignee, args.repo)
        elif args.sub == "close":   pr_close(args.number, args.comment, args.del_branch, args.repo)
        elif args.sub == "ready":   pr_ready(args.number, args.repo)
        elif args.sub == "diff":    pr_diff(args.number, args.repo)

    elif args.cmd == "agent-task":
        if   args.sub == "create": agent_task_create(args.prompt, args.repo, args.base, args.custom_agent, args.follow, args.from_file)
        elif args.sub == "list":   agent_task_list(args.limit, args.web)
        elif args.sub == "view":   agent_task_view(args.id, args.repo, args.follow, args.log, args.web)

    elif args.cmd == "agent-config":
        if   args.sub == "install": agent_config_install(args.repo, args.name)
        elif args.sub == "list":    agent_config_list(args.repo)
        elif args.sub == "remove":  agent_config_remove(args.repo, args.name)


if __name__ == "__main__":
    main()