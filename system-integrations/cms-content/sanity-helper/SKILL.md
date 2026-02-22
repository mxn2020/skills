---
name: Sanity Studio Helper
id: OC-0044
version: 1.0.0
description: Trigger webhooks or clear datasets in Sanity CMS.
---

# Sanity Studio Helper

Query, create, patch, and delete documents in your Sanity dataset, plus trigger webhooks.

## Capabilities

- List and retrieve documents from a dataset
- Create, patch, and delete documents via mutations
- Trigger deploy webhooks for rebuilds

## Quick Start

```bash
export SANITY_PROJECT_ID="your-project-id"
export SANITY_TOKEN="your-api-token"
export SANITY_DATASET="production"
python3 scripts/sanity_helper.py list-documents --type post
python3 scripts/sanity_helper.py create --doc '{"_type":"post","title":"Hello"}'
```

## Commands & Parameters

| Command            | Parameters                                    | Description                     |
| ------------------ | --------------------------------------------- | ------------------------------- |
| `list-documents`   | `--type` (optional)                           | List documents, filter by type  |
| `get-document`     | `--id`                                        | Get a document by ID            |
| `create`           | `--doc` (JSON)                                | Create a new document           |
| `patch`            | `--id`, `--set` (JSON)                        | Patch fields on a document      |
| `delete`           | `--id`                                        | Delete a document               |
| `trigger-webhook`  | `--url`                                       | POST to a deploy webhook URL    |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `SANITY_PROJECT_ID`, `SANITY_TOKEN`, `SANITY_DATASET`
