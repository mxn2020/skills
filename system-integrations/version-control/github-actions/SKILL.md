---
name: github-actions
version: 1.0.0
description: GitHub Actions Trigger. Manually dispatch workflows, monitor runs, and manage CI/CD from agent commands. Use when user asks to trigger, monitor, or cancel GitHub Actions workflows.
---

# GitHub Actions Trigger

Trigger, monitor, and manage GitHub Actions workflows from agent commands.

## Capabilities

1. **List Workflows**: Discover available workflows in a repository.
2. **Trigger Workflows**: Manually dispatch workflow runs.
3. **Run Status**: Check the status of workflow runs.
4. **List Runs**: View recent workflow run history.
5. **Cancel Runs**: Cancel in-progress workflow runs.

## Quick Start

```bash
# List workflows
python3 skills/system-integrations/version-control/github-actions/scripts/actions.py list-workflows --repo owner/repo

# Trigger a workflow
python3 skills/system-integrations/version-control/github-actions/scripts/actions.py trigger-workflow --repo owner/repo --workflow ci.yml --ref main

# Get run status
python3 skills/system-integrations/version-control/github-actions/scripts/actions.py get-run-status --repo owner/repo --run-id 12345

# List recent runs
python3 skills/system-integrations/version-control/github-actions/scripts/actions.py list-runs --repo owner/repo

# Cancel a run
python3 skills/system-integrations/version-control/github-actions/scripts/actions.py cancel-run --repo owner/repo --run-id 12345
```

## Commands & Parameters

### `list-workflows`
Lists available workflows in a repository.
- `--repo`: Repository (owner/name) (required)

### `trigger-workflow`
Manually dispatches a workflow.
- `--repo`: Repository (owner/name) (required)
- `--workflow`: Workflow filename or ID (required)
- `--ref`: Git ref (branch/tag) to run on (default: main)
- `--inputs`: JSON string of workflow inputs

### `get-run-status`
Gets the status of a specific workflow run.
- `--repo`: Repository (owner/name) (required)
- `--run-id`: Workflow run ID (required)

### `list-runs`
Lists recent workflow runs.
- `--repo`: Repository (owner/name) (required)
- `--workflow`: Filter by workflow filename
- `--limit`: Max runs to return (default: 20)
- `--status`: Filter by status (queued, in_progress, completed)

### `cancel-run`
Cancels an in-progress workflow run.
- `--repo`: Repository (owner/name) (required)
- `--run-id`: Workflow run ID (required)

## Dependencies
- `gh` CLI installed and authenticated.
- `GITHUB_TOKEN` environment variable (or `gh auth login`).
