---
name: gh
version: 1.0.0
description: >
  GitHub CLI skill. Use for repository management, pull request lifecycle,
  Copilot coding agent tasks (gh agent-task), and managing custom agent
  configs (.github/agents/*.md). All operations are pure `gh` CLI calls.
---

# gh Skill

This skill wraps the `gh` CLI. It has **nothing to do with the Copilot CLI**
(`copilot` binary). See the separate `copilot` skill for that.

## Concepts

### gh agent-task — Copilot coding agent
`gh agent-task create` delegates a coding task to GitHub's **Copilot coding
agent**. The agent runs **remotely** in a sandboxed GitHub environment, makes
code changes to the repository, and opens a **pull request** when finished.
You track progress with `gh agent-task view`. This is a GitHub platform
feature, not a local tool.

Custom agent personas for it are markdown files stored at
`.github/agents/<name>.md` in the target repo. Manage them with
`agent-config install/list/remove`.

### Authentication
| Command group   | Auth required                              |
|----------------|--------------------------------------------|
| `repo`, `pr`   | `GITHUB_TOKEN` / `GH_TOKEN` PAT (repo scope) |
| `agent-task`   | **OAuth session** — run `gh auth login` first. PAT alone is rejected by GitHub (exit code 4). |
| `agent-config` | PAT with `repo` scope (uses GitHub Contents API) |

---

## Commands

### `repo` — Repository management
```bash
python3 scripts/gh.py repo list [--limit 30] [--org myorg]
python3 scripts/gh.py repo create "my-repo" [--private] [--description "..."] [--auto-init] [--org myorg]
python3 scripts/gh.py repo view  owner/my-repo
python3 scripts/gh.py repo edit  owner/my-repo [--description "New"] [--visibility private|public|internal]
python3 scripts/gh.py repo clone owner/my-repo [local-dir]
python3 scripts/gh.py repo delete owner/my-repo [--yes]
```

### `pr` — Pull request lifecycle
```bash
# Create
python3 scripts/gh.py pr create --title "feat: login" --body "Closes #12" \
  --base main --head feature/login [--draft] [--label bug] [--assignee alice] [--repo owner/repo]

# List / filter
python3 scripts/gh.py pr list [--state open|closed|merged|all] [--limit 20] \
  [--author alice] [--label bug] [--base main] [--repo owner/repo]

# Inspect
python3 scripts/gh.py pr view    <number> [--repo owner/repo]
python3 scripts/gh.py pr diff    <number> [--repo owner/repo]
python3 scripts/gh.py pr checks  <number> [--repo owner/repo]

# Interact
python3 scripts/gh.py pr comment <number> --body "Please rebase" [--repo owner/repo]
python3 scripts/gh.py pr review  <number> --action approve|request-changes|comment \
  [--body "LGTM"] [--repo owner/repo]
python3 scripts/gh.py pr edit    <number> [--title "..."] [--body "..."] [--base main] \
  [--add-label hotfix] [--add-assignee bob] [--repo owner/repo]
python3 scripts/gh.py pr ready   <number> [--repo owner/repo]   # un-draft a PR

# Finalise
python3 scripts/gh.py pr merge <number> [--method merge|squash|rebase] \
  [--no-delete-branch] [--repo owner/repo]
python3 scripts/gh.py pr close <number> [--comment "Won't fix"] \
  [--delete-branch] [--repo owner/repo]
```

### `agent-task` — Copilot coding agent tasks ⚠️ requires OAuth
```bash
# Create a task — Copilot works remotely and opens a PR
python3 scripts/gh.py agent-task create "Refactor auth to use JWT"
python3 scripts/gh.py agent-task create "Add OpenAPI spec" \
  -R owner/my-api -b main -a code-review --follow

# Pass a long task description from a file
python3 scripts/gh.py agent-task create -F task-brief.md

# List recent tasks (all repos, current user)
python3 scripts/gh.py agent-task list [--limit 30] [--web]

# Track a task (by PR number, session UUID, or branch)
python3 scripts/gh.py agent-task view 42
python3 scripts/gh.py agent-task view e2fa49d2-f164-4a56-ab99-498090b8fcdf
python3 scripts/gh.py agent-task view owner/repo#42
python3 scripts/gh.py agent-task view 42 --follow   # stream live logs
python3 scripts/gh.py agent-task view 42 --log       # full session log
```

### `agent-config` — Manage .github/agents/*.md files

These are custom agent persona files. They customise the Copilot coding agent
when referenced by `--custom-agent` in `agent-task create`.
```bash
python3 scripts/gh.py agent-config install owner/my-repo code-review
python3 scripts/gh.py agent-config list    owner/my-repo
python3 scripts/gh.py agent-config remove  owner/my-repo code-review
```

Local templates live in `skills/gh/templates/`. Available: `default`, `code-review`.

---

## Typical AI agent workflow
```bash
# 1. Create repo
python3 scripts/gh.py repo create "auth-service" --private --auto-init --org myorg

# 2. Install a custom agent persona
python3 scripts/gh.py agent-config install myorg/auth-service code-review

# 3. Delegate implementation to Copilot coding agent (opens a PR when done)
python3 scripts/gh.py agent-task create \
  "Implement JWT authentication with FastAPI. Add pytest tests. Update README." \
  -R myorg/auth-service -a code-review --follow

# 4. Check CI on the resulting PR
python3 scripts/gh.py pr checks 1 --repo myorg/auth-service

# 5. Approve and merge
python3 scripts/gh.py pr review 1 --action approve --body "LGTM"
python3 scripts/gh.py pr merge  1 --method squash --repo myorg/auth-service
```
