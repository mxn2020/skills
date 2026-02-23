---
name: cloudflare-workers
id: OC-0018
version: 1.0.0
description: "Cloudflare Worker Manager - Update edge scripts"
env:
  - CLOUDFLARE_API_TOKEN
  - CLOUDFLARE_ACCOUNT_ID
commands:
  - list-workers
  - deploy
  - get-worker
  - delete
  - tail-logs
---

# Cloudflare Worker Manager

Manage Cloudflare Workers – deploy, inspect, delete, and tail logs.

## Prerequisites

- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` environment variables.

## Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `list-workers` | List all Workers scripts             |
| `deploy`       | Upload/update a Worker script        |
| `get-worker`   | Get Worker script metadata           |
| `delete`       | Delete a Worker                      |
| `tail-logs`    | Tail Worker logs in real time        |

## Usage

```bash
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
python3 scripts/cloudflare_workers.py list-workers
python3 scripts/cloudflare_workers.py deploy --name my-worker --script worker.js
python3 scripts/cloudflare_workers.py tail-logs --name my-worker
```
