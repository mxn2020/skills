---
name: copilot
version: 1.0.0
description: >
  GitHub Copilot CLI skill. Use when you need an AI agent to perform LOCAL
  coding work: edit files, run shell commands, and iterate on code in a
  working directory. This is completely separate from `gh agent-task`.
---

# Copilot CLI Skill

## What this is

The **GitHub Copilot CLI** (`copilot` binary, installed via npm) is a local,
interactive, agentic terminal tool. It:

- Runs **on the host machine** in a working directory you specify.
- Reads and **edits local files** directly.
- Runs **shell commands** on the host.
- Streams its progress to stdout.
- Exits when the task is done.

## What this is NOT

| NOT this | Use instead |
|----------|-------------|
| `gh copilot` extension | Deprecated Oct 25, 2025 — do not use |
| `gh agent-task` | Remote task that opens a PR. Use the `gh` skill. |
| GitHub Copilot Chat | Browser/IDE feature, not scriptable |

## Installation
```bash
npm install -g @github/copilot
# verify
copilot --version
```

## Authentication

Either:
- Set `GH_TOKEN` (or `GITHUB_TOKEN`) to a fine-grained PAT with the
  **"Copilot Requests"** permission, or
- Run `copilot` once interactively and follow the `/login` device-code flow.

## Key concept: tool approval

By default `copilot` pauses and asks for approval before every file write or
shell command. For non-interactive / AI agent use you **must** pass an
approval flag, otherwise it will block indefinitely.

| Flag | Effect |
|------|--------|
| `--allow-all-tools` | Approve everything (full access, same as current user) |
| `--allow-tool shell` | Approve all shell commands without prompt |
| `--allow-tool write` | Approve all file writes without prompt |
| `--allow-tool shell(rm)` | Approve only `rm` commands |
| `--deny-tool shell(rm)` | Block `rm` entirely |

You can combine `--allow-tool` and `--deny-tool` freely. `--deny-tool` takes
precedence over `--allow-tool`.

---

## Commands

### `run` — execute a Copilot CLI task
```bash
python3 scripts/gh-copilot.py run "<prompt>" [options]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--cwd <path>` | Working directory (default: current dir) |
| `--allow-all-tools` | Approve all tools without prompting |
| `--allow-tool <spec>` | Approve a specific tool (repeatable) |
| `--deny-tool <spec>` | Block a specific tool (repeatable) |
| `--model <name>` | Override AI model (default: Claude Sonnet 4.5) |
| `--experimental` | Enable preview features |
| `--trust-all-repos` | Skip directory trust prompt |
| `--token <pat>` | PAT to use (overrides GH_TOKEN) |

---

## Usage examples
```bash
# Explain code in a local repo (read-only, no tools needed)
python3 scripts/gh-copilot.py run "Explain the auth middleware in src/auth.py" \
  --cwd /path/to/my-project

# Fix a bug — allow file writes only
python3 scripts/gh-copilot.py run "Fix the null pointer bug in UserService.java" \
  --cwd /path/to/project \
  --allow-tool write

# Full autonomous task: edit files + run tests
python3 scripts/gh-copilot.py run \
  "Add input validation to all API endpoints. Run pytest after each change." \
  --cwd /path/to/api-project \
  --allow-all-tools

# Same but block destructive shell commands
python3 scripts/gh-copilot.py run \
  "Refactor the database layer to use SQLAlchemy 2.0." \
  --cwd /path/to/project \
  --allow-tool write \
  --allow-tool shell \
  --deny-tool "shell(rm)" \
  --deny-tool "shell(git push)"

# Use a specific model
python3 scripts/gh-copilot.py run "Review and improve test coverage" \
  --cwd /path/to/project \
  --allow-tool write \
  --model "claude-sonnet-4"
```

---

## Typical pattern: local work → then push via `gh`

The Copilot CLI works locally. Once it's done editing, you use normal git and
the `gh` skill to push and open a PR:
```bash
# 1. Run Copilot CLI to do the local coding work
python3 scripts/gh-copilot.py run \
  "Implement the feature described in TASK.md" \
  --cwd /repos/my-project \
  --allow-tool write \
  --allow-tool shell \
  --deny-tool "shell(git push)"

# 2. Push and open a PR with the gh skill
cd /repos/my-project
python3 ../gh/scripts/gh_skill.py pr create \
  --title "feat: implement feature X" \
  --body "Implemented by Copilot CLI" \
  --base main \
  --repo myorg/my-project
```
