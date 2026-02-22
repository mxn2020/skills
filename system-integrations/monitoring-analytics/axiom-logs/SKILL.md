---
name: axiom-logs
id: OC-0056
version: 1.0.0
description: "Axiom Log Query - Run structured log queries"
env:
  - AXIOM_TOKEN
  - AXIOM_ORG_ID
commands:
  - query
  - list-datasets
  - ingest
  - get-dataset
  - stream
---

# Axiom Log Query

Run structured log queries, manage datasets, and ingest data via the Axiom API.

## Prerequisites

- `AXIOM_TOKEN` – Axiom API token.
- `AXIOM_ORG_ID` – Axiom organization ID.

## Commands

| Command         | Description                              |
|-----------------|------------------------------------------|
| `query`         | Run an APL query against a dataset       |
| `list-datasets` | List available datasets                  |
| `ingest`        | Ingest JSON data into a dataset          |
| `get-dataset`   | Get metadata for a dataset               |
| `stream`        | Stream recent log entries                |

## Usage

```bash
export AXIOM_TOKEN="your-token"
export AXIOM_ORG_ID="your-org-id"
python3 scripts/axiom_logs.py list-datasets
python3 scripts/axiom_logs.py query --dataset logs --apl "['logs'] | where severity == 'error' | limit 10"
python3 scripts/axiom_logs.py ingest --dataset logs --file data.json
python3 scripts/axiom_logs.py get-dataset --dataset logs
python3 scripts/axiom_logs.py stream --dataset logs --limit 20
```
