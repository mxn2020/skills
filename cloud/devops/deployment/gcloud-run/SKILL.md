---
name: gcloud-run
id: OC-0016
version: 1.0.0
description: "Google Cloud Run Deployer - Deploy containerized apps"
env:
  - GOOGLE_CLOUD_PROJECT
commands:
  - list-services
  - deploy
  - describe
  - set-env
  - get-logs
---

# Google Cloud Run Deployer

Deploy, manage, and monitor Cloud Run services.

## Prerequisites

- `gcloud` CLI authenticated and `GOOGLE_CLOUD_PROJECT` set.

## Commands

| Command         | Description                          |
|-----------------|--------------------------------------|
| `list-services` | List all Cloud Run services          |
| `deploy`        | Deploy a container image             |
| `describe`      | Describe a specific service          |
| `set-env`       | Update environment variables         |
| `get-logs`      | Fetch service logs                   |

## Usage

```bash
export GOOGLE_CLOUD_PROJECT="my-project"
python3 scripts/gcloud_run.py list-services --region us-central1
python3 scripts/gcloud_run.py deploy --service my-svc --image gcr.io/proj/img:latest --region us-central1
```
