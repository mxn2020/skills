---
name: Pinecone Index Manager
id: OC-0037
version: 1.0.0
description: Create, delete, and manage vector indexes for RAG applications using Pinecone.
---

# Pinecone Index Manager

Manage Pinecone vector indexes for retrieval-augmented generation (RAG) applications.

## Capabilities

- List, create, describe, and delete Pinecone indexes
- Upsert vectors with metadata into an index
- Query indexes with vector similarity search

## Quick Start

```bash
export PINECONE_API_KEY="your-api-key"
python3 scripts/pinecone_manager.py list-indexes
python3 scripts/pinecone_manager.py create-index --name my-index --dimension 1536 --metric cosine
python3 scripts/pinecone_manager.py query --name my-index --vector '[0.1, 0.2, ...]' --top-k 5
```

## Commands & Parameters

| Command          | Parameters                                      | Description                    |
| ---------------- | ----------------------------------------------- | ------------------------------ |
| `list-indexes`   | —                                               | List all indexes               |
| `create-index`   | `--name`, `--dimension`, `--metric`             | Create a new index             |
| `delete-index`   | `--name`                                        | Delete an index                |
| `describe-index` | `--name`                                        | Show index details             |
| `upsert`         | `--name`, `--vectors` (JSON)                    | Upsert vectors into an index   |
| `query`          | `--name`, `--vector` (JSON), `--top-k`          | Query by vector similarity     |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variable: `PINECONE_API_KEY`
