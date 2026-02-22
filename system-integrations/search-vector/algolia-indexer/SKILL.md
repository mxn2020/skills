---
name: Algolia Indexer
id: OC-0039
version: 1.0.0
description: Push content updates and manage search indices with Algolia.
---

# Algolia Indexer

Manage Algolia search indices, push records, and configure settings.

## Capabilities

- List indices and inspect settings
- Add and delete records in an index
- Perform full-text search queries
- Update index settings (searchable attributes, ranking, etc.)

## Quick Start

```bash
export ALGOLIA_APP_ID="your-app-id"
export ALGOLIA_API_KEY="your-admin-api-key"
python3 scripts/algolia_indexer.py list-indices
python3 scripts/algolia_indexer.py add-records --index products --records '[{"objectID":"1","name":"Widget"}]'
python3 scripts/algolia_indexer.py search --index products --query "widget"
```

## Commands & Parameters

| Command         | Parameters                                       | Description                     |
| --------------- | ------------------------------------------------ | ------------------------------- |
| `list-indices`  | —                                                | List all indices                |
| `search`        | `--index`, `--query`                             | Search an index                 |
| `add-records`   | `--index`, `--records` (JSON)                    | Add records to an index         |
| `delete-record` | `--index`, `--object-id`                         | Delete a record by objectID     |
| `get-settings`  | `--index`                                        | Get index settings              |
| `set-settings`  | `--index`, `--settings` (JSON)                   | Update index settings           |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY`
