---
name: gitlab-pipeline
version: 1.0.0
description: GitLab Pipeline Monitor. Watch CI/CD pipeline status and report failures. Use when user asks to monitor GitLab pipelines, check job status, or retry failed jobs.
---

# GitLab Pipeline Monitor

Monitor GitLab CI/CD pipelines, check job statuses, and manage pipeline execution.

## Capabilities

1. **List Pipelines**: View recent pipelines for a project.
2. **Pipeline Details**: Get detailed status of a specific pipeline.
3. **Job Inspection**: List and inspect individual jobs within a pipeline.
4. **Retry Jobs**: Retry failed jobs.
5. **Cancel Pipelines**: Cancel running pipelines.

## Quick Start

```bash
# List recent pipelines
python3 skills/cloud/devops/version-control/gitlab-pipeline/scripts/pipeline.py list-pipelines --project my-group/my-project

# Get pipeline details
python3 skills/cloud/devops/version-control/gitlab-pipeline/scripts/pipeline.py get-pipeline --project my-group/my-project --pipeline-id 12345

# List jobs in a pipeline
python3 skills/cloud/devops/version-control/gitlab-pipeline/scripts/pipeline.py get-jobs --project my-group/my-project --pipeline-id 12345

# Retry a failed job
python3 skills/cloud/devops/version-control/gitlab-pipeline/scripts/pipeline.py retry-job --project my-group/my-project --job-id 67890

# Cancel a pipeline
python3 skills/cloud/devops/version-control/gitlab-pipeline/scripts/pipeline.py cancel-pipeline --project my-group/my-project --pipeline-id 12345
```

## Commands & Parameters

### `list-pipelines`
Lists recent pipelines for a project.
- `--project`: GitLab project path (group/project) (required)
- `--status`: Filter by status (running, pending, success, failed, canceled)
- `--limit`: Max pipelines to return (default: 20)
- `--ref`: Filter by branch/tag

### `get-pipeline`
Gets details of a specific pipeline.
- `--project`: GitLab project path (required)
- `--pipeline-id`: Pipeline ID (required)

### `get-jobs`
Lists jobs in a pipeline.
- `--project`: GitLab project path (required)
- `--pipeline-id`: Pipeline ID (required)

### `retry-job`
Retries a failed job.
- `--project`: GitLab project path (required)
- `--job-id`: Job ID (required)

### `cancel-pipeline`
Cancels a running pipeline.
- `--project`: GitLab project path (required)
- `--pipeline-id`: Pipeline ID (required)

## Dependencies
- `GITLAB_TOKEN` environment variable (GitLab personal access token).
- `GITLAB_URL` environment variable (default: https://gitlab.com).
- Python `requests` library (`pip install requests`).
