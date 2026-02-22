---
name: Chroma DB Manager
id: OC-0042
version: 1.0.0
description: Manage Chroma vector stores for RAG pipelines.
---

# Chroma DB Manager

Manage ChromaDB collections and documents for retrieval-augmented generation pipelines.

## Capabilities

- List, create, and delete collections
- Add documents with embeddings and metadata
- Query collections by vector similarity
- Get document counts per collection

## Quick Start

```bash
export CHROMA_URL="http://localhost:8000"
python3 scripts/chroma_manager.py list-collections
python3 scripts/chroma_manager.py create-collection --name docs
python3 scripts/chroma_manager.py add --name docs --documents '["hello world"]' --ids '["doc1"]'
python3 scripts/chroma_manager.py query --name docs --texts '["hello"]' --n-results 5
```

## Commands & Parameters

| Command              | Parameters                                                 | Description                  |
| -------------------- | ---------------------------------------------------------- | ---------------------------- |
| `list-collections`   | —                                                          | List all collections         |
| `create-collection`  | `--name`                                                   | Create a collection          |
| `delete-collection`  | `--name`                                                   | Delete a collection          |
| `add`                | `--name`, `--documents` (JSON), `--ids` (JSON)             | Add documents                |
| `query`              | `--name`, `--texts` (JSON), `--n-results`                  | Query by text similarity     |
| `count`              | `--name`                                                   | Get document count           |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variable: `CHROMA_URL` (defaults to `http://localhost:8000`)
