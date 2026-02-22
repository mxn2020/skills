---
name: vercel-deployer
id: OC-0009
version: 1.0.0
description: "Vercel Deployment Manager - Trigger builds, manage env vars, alias domains"
env:
  - VERCEL_TOKEN
commands:
  - list-projects
  - deploy
  - list-deployments
  - set-env
  - alias-domain
---

# Vercel Deployment Manager

Manage Vercel projects, deployments, environment variables, and domain aliases.

## Prerequisites

- A valid `VERCEL_TOKEN` environment variable.

## Commands

| Command            | Description                        |
|--------------------|------------------------------------|
| `list-projects`    | List all Vercel projects           |
| `deploy`           | Trigger a new deployment           |
| `list-deployments` | List recent deployments            |
| `set-env`          | Set an environment variable        |
| `alias-domain`     | Assign a domain alias to a deploy  |

## Usage

```bash
export VERCEL_TOKEN="your-token"
python3 scripts/vercel_deployer.py list-projects
python3 scripts/vercel_deployer.py deploy --project my-app
python3 scripts/vercel_deployer.py set-env --project my-app --key DB_URL --value "postgres://..."
python3 scripts/vercel_deployer.py alias-domain --deployment-id dpl_xxx --domain app.example.com
```
