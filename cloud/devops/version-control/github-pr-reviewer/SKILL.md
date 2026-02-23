---
name: github-pr-reviewer
version: 1.0.0
description: GitHub PR Automated Reviewer. Verify diffs against style guides and flag violations. Use when user asks to review PRs, check code style, or summarize diffs.
---

# GitHub PR Automated Reviewer

Automatically review pull requests, check diffs against style conventions, and generate summaries.

## Capabilities

1. **PR Review**: Analyze PR diffs and post review comments.
2. **PR Listing**: List open pull requests in a repository.
3. **Style Checking**: Flag common style violations in diffs.
4. **Diff Summarization**: Generate human-readable summaries of PR changes.

## Quick Start

```bash
# List open PRs
python3 skills/system-integrations/version-control/github-pr-reviewer/scripts/reviewer.py list-prs --repo owner/repo

# Review a specific PR
python3 skills/system-integrations/version-control/github-pr-reviewer/scripts/reviewer.py review-pr --repo owner/repo --pr 42

# Check style violations in a PR
python3 skills/system-integrations/version-control/github-pr-reviewer/scripts/reviewer.py check-style --repo owner/repo --pr 42

# Summarize a PR diff
python3 skills/system-integrations/version-control/github-pr-reviewer/scripts/reviewer.py summarize-diff --repo owner/repo --pr 42
```

## Commands & Parameters

### `list-prs`
Lists open pull requests.
- `--repo`: Repository (owner/name) (required)
- `--state`: Filter by state: open, closed, merged, all (default: open)
- `--limit`: Max PRs to return (default: 30)

### `review-pr`
Analyzes a PR diff and posts a review.
- `--repo`: Repository (owner/name) (required)
- `--pr`: Pull request number (required)
- `--post-comment`: Post findings as a PR comment (flag)

### `check-style`
Checks for common style violations in a PR diff.
- `--repo`: Repository (owner/name) (required)
- `--pr`: Pull request number (required)
- `--max-line-length`: Max line length to enforce (default: 120)

### `summarize-diff`
Generates a human-readable summary of PR changes.
- `--repo`: Repository (owner/name) (required)
- `--pr`: Pull request number (required)

## Dependencies
- `gh` CLI installed and authenticated.
- `GITHUB_TOKEN` environment variable (or `gh auth login`).
