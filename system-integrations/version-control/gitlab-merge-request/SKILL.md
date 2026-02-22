---
name: gitlab-merge-request
version: 1.0.0
description: GitLab Merge Request Manager. Auto-assign reviewers and manage MR lifecycle. Use when user asks to create, review, approve, or merge GitLab merge requests.
---

# GitLab Merge Request Manager

Manage GitLab merge requests including creation, reviewer assignment, approval, and merging.

## Capabilities

1. **List MRs**: List merge requests in a project.
2. **Create MRs**: Create new merge requests with title, description, and assignees.
3. **Assign Reviewers**: Auto-assign or manually assign reviewers to MRs.
4. **Approve MRs**: Approve merge requests.
5. **Merge MRs**: Merge approved merge requests.

## Quick Start

```bash
# List open MRs
python3 skills/system-integrations/version-control/gitlab-merge-request/scripts/merge_request.py list-mrs --project my-group/my-project

# Create a merge request
python3 skills/system-integrations/version-control/gitlab-merge-request/scripts/merge_request.py create-mr --project my-group/my-project --source feature-branch --target main --title "Add new feature"

# Assign reviewers
python3 skills/system-integrations/version-control/gitlab-merge-request/scripts/merge_request.py assign-reviewers --project my-group/my-project --mr-id 10 --reviewers user1,user2

# Approve a MR
python3 skills/system-integrations/version-control/gitlab-merge-request/scripts/merge_request.py approve-mr --project my-group/my-project --mr-id 10

# Merge a MR
python3 skills/system-integrations/version-control/gitlab-merge-request/scripts/merge_request.py merge-mr --project my-group/my-project --mr-id 10
```

## Commands & Parameters

### `list-mrs`
Lists merge requests in a project.
- `--project`: GitLab project path (group/project) (required)
- `--state`: Filter by state: opened, closed, merged, all (default: opened)
- `--limit`: Max MRs to return (default: 20)

### `create-mr`
Creates a new merge request.
- `--project`: GitLab project path (required)
- `--source`: Source branch (required)
- `--target`: Target branch (default: main)
- `--title`: MR title (required)
- `--description`: MR description

### `assign-reviewers`
Assigns reviewers to a merge request.
- `--project`: GitLab project path (required)
- `--mr-id`: Merge request IID (required)
- `--reviewers`: Comma-separated reviewer usernames (required)

### `approve-mr`
Approves a merge request.
- `--project`: GitLab project path (required)
- `--mr-id`: Merge request IID (required)

### `merge-mr`
Merges a merge request.
- `--project`: GitLab project path (required)
- `--mr-id`: Merge request IID (required)
- `--squash`: Squash commits on merge (flag)
- `--delete-branch`: Delete source branch after merge (flag)

## Dependencies
- `GITLAB_TOKEN` environment variable (GitLab personal access token).
- `GITLAB_URL` environment variable (default: https://gitlab.com).
- Python `requests` library (`pip install requests`).
