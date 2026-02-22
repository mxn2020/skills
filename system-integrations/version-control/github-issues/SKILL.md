---
name: github-issues
version: 1.0.0
description: GitHub Issues Agent. Label, triage, close, and prioritize issues automatically. Use when user asks to manage, triage, or organize GitHub issues.
---

# GitHub Issues Agent

Automate GitHub issue management including labeling, triaging, closing, and prioritizing issues.

## Capabilities

1. **Issue Listing**: List and filter issues in a repository.
2. **Issue Creation**: Create new issues with labels and assignees.
3. **Labeling**: Add or update labels on issues.
4. **Closing**: Close issues with a comment.
5. **Triage**: Auto-label issues based on title and body content.
6. **Prioritization**: Assign priority labels based on keyword analysis.

## Quick Start

```bash
# List open issues
python3 skills/system-integrations/version-control/github-issues/scripts/issues.py list-issues --repo owner/repo

# Create a new issue
python3 skills/system-integrations/version-control/github-issues/scripts/issues.py create-issue --repo owner/repo --title "Bug: login fails" --body "Steps to reproduce..."

# Auto-triage issues
python3 skills/system-integrations/version-control/github-issues/scripts/issues.py triage --repo owner/repo

# Prioritize issues
python3 skills/system-integrations/version-control/github-issues/scripts/issues.py prioritize --repo owner/repo
```

## Commands & Parameters

### `list-issues`
Lists issues in a repository.
- `--repo`: Repository (owner/name) (required)
- `--state`: Filter by state: open, closed, all (default: open)
- `--limit`: Max issues to return (default: 30)
- `--label`: Filter by label

### `create-issue`
Creates a new issue.
- `--repo`: Repository (owner/name) (required)
- `--title`: Issue title (required)
- `--body`: Issue body
- `--labels`: Comma-separated labels
- `--assignee`: Assignee username

### `label-issue`
Adds labels to an issue.
- `--repo`: Repository (owner/name) (required)
- `--issue`: Issue number (required)
- `--labels`: Comma-separated labels to add (required)

### `close-issue`
Closes an issue with an optional comment.
- `--repo`: Repository (owner/name) (required)
- `--issue`: Issue number (required)
- `--comment`: Closing comment

### `triage`
Auto-labels issues based on content analysis.
- `--repo`: Repository (owner/name) (required)
- `--limit`: Number of issues to triage (default: 20)

### `prioritize`
Assigns priority labels based on keyword analysis.
- `--repo`: Repository (owner/name) (required)
- `--limit`: Number of issues to analyze (default: 20)

## Dependencies
- `gh` CLI installed and authenticated.
- `GITHUB_TOKEN` environment variable (or `gh auth login`).
