---
name: MeiliSearch Settings
id: OC-0040
version: 1.0.0
description: Configure MeiliSearch ranking rules, stop words, and index settings.
---

# MeiliSearch Settings

Configure and manage MeiliSearch indexes, documents, and search settings.

## Capabilities

- List, create, and inspect indexes
- Add documents and perform full-text search
- Get and update settings (ranking rules, stop words, synonyms, etc.)

## Quick Start

```bash
export MEILISEARCH_URL="http://localhost:7700"
export MEILISEARCH_API_KEY="your-master-key"
python3 scripts/meilisearch_settings.py list-indexes
python3 scripts/meilisearch_settings.py create-index --uid movies --primary-key id
python3 scripts/meilisearch_settings.py update-settings --uid movies --settings '{"rankingRules":["words","typo","proximity"]}'
```

## Commands & Parameters

| Command            | Parameters                                    | Description                    |
| ------------------ | --------------------------------------------- | ------------------------------ |
| `list-indexes`     | —                                             | List all indexes               |
| `create-index`     | `--uid`, `--primary-key`                      | Create a new index             |
| `search`           | `--uid`, `--query`                            | Search an index                |
| `get-settings`     | `--uid`                                       | Get index settings             |
| `update-settings`  | `--uid`, `--settings` (JSON)                  | Update index settings          |
| `add-documents`    | `--uid`, `--documents` (JSON)                 | Add documents to an index      |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `MEILISEARCH_URL`, `MEILISEARCH_API_KEY`
