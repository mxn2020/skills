---
name: bitbucket-integration
version: 1.0.0
description: Bitbucket Integration. Sync Jira tickets with commits and manage repositories. Use when user asks to list Bitbucket repos, PRs, commits, or link Jira tickets.
---

# Bitbucket Integration

Manage Bitbucket repositories, pull requests, and link Jira tickets to commits.

## Capabilities

1. **List Repos**: List repositories in a workspace.
2. **List PRs**: List pull requests in a repository.
3. **Get Commits**: View commit history for a repository.
4. **Link Jira**: Associate Jira ticket IDs with commits.
5. **List Branches**: List branches in a repository.

## Quick Start

```bash
# List repositories
python3 skills/cloud/devops/version-control/bitbucket-integration/scripts/bitbucket.py list-repos --workspace my-workspace

# List pull requests
python3 skills/cloud/devops/version-control/bitbucket-integration/scripts/bitbucket.py list-prs --workspace my-workspace --repo my-repo

# Get commits
python3 skills/cloud/devops/version-control/bitbucket-integration/scripts/bitbucket.py get-commits --workspace my-workspace --repo my-repo

# Link Jira tickets from commits
python3 skills/cloud/devops/version-control/bitbucket-integration/scripts/bitbucket.py link-jira --workspace my-workspace --repo my-repo

# List branches
python3 skills/cloud/devops/version-control/bitbucket-integration/scripts/bitbucket.py list-branches --workspace my-workspace --repo my-repo
```

## Commands & Parameters

### `list-repos`
Lists repositories in a Bitbucket workspace.
- `--workspace`: Bitbucket workspace slug (required)
- `--limit`: Max repos to return (default: 25)

### `list-prs`
Lists pull requests in a repository.
- `--workspace`: Bitbucket workspace slug (required)
- `--repo`: Repository slug (required)
- `--state`: Filter by state: OPEN, MERGED, DECLINED, SUPERSEDED (default: OPEN)

### `get-commits`
Lists recent commits for a repository.
- `--workspace`: Bitbucket workspace slug (required)
- `--repo`: Repository slug (required)
- `--limit`: Max commits to return (default: 20)
- `--branch`: Filter by branch

### `link-jira`
Scans commits for Jira ticket references and reports linkages.
- `--workspace`: Bitbucket workspace slug (required)
- `--repo`: Repository slug (required)
- `--limit`: Max commits to scan (default: 50)

### `list-branches`
Lists branches in a repository.
- `--workspace`: Bitbucket workspace slug (required)
- `--repo`: Repository slug (required)

## Dependencies
- `BITBUCKET_USERNAME` environment variable.
- `BITBUCKET_APP_PASSWORD` environment variable.
- Python `requests` library (`pip install requests`).
