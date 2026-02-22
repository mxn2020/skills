---
name: Qdrant Collection Manager
id: OC-0041
version: 1.0.0
description: Manage Qdrant collections and run similarity queries.
---

# Qdrant Collection Manager

Create, manage, and query Qdrant vector collections for similarity search.

## Capabilities

- List, create, and delete collections
- Get detailed collection info and statistics
- Upsert points with vectors and payloads
- Run similarity search queries

## Quick Start

```bash
export QDRANT_URL="http://localhost:6333"
export QDRANT_API_KEY="your-api-key"
python3 scripts/qdrant_manager.py list-collections
python3 scripts/qdrant_manager.py create-collection --name docs --size 1536 --distance cosine
python3 scripts/qdrant_manager.py search --name docs --vector '[0.1, 0.2, ...]' --limit 5
```

## Commands & Parameters

| Command              | Parameters                                      | Description                     |
| -------------------- | ----------------------------------------------- | ------------------------------- |
| `list-collections`   | —                                               | List all collections            |
| `create-collection`  | `--name`, `--size`, `--distance`                | Create a collection             |
| `delete-collection`  | `--name`                                        | Delete a collection             |
| `upsert`             | `--name`, `--points` (JSON)                     | Upsert points with vectors      |
| `search`             | `--name`, `--vector` (JSON), `--limit`          | Similarity search               |
| `get-info`           | `--name`                                        | Get collection details          |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `QDRANT_URL`, `QDRANT_API_KEY`
