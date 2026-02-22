---
name: rag-manager
id: OC-0118
version: 1.0.0
description: "RAG Manager - Handle document chunking, embedding, and vector storage for RAG pipelines"
env:
  - OPENAI_API_KEY
commands:
  - ingest
  - query
  - list-collections
  - delete-collection
---

# RAG Manager

Ingest documents into a vector store and query them using semantic search. Supports ChromaDB (local) or a JSON-based fallback store.

## Prerequisites

- `OPENAI_API_KEY`
- Optional: `pip install chromadb` for persistent vector storage

## Commands

| Command | Description |
|---------|-------------|
| `ingest` | Chunk and embed a document into a collection |
| `query` | Semantic search over a collection |
| `list-collections` | List all available collections |
| `delete-collection` | Delete a collection and its embeddings |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/rag_manager.py ingest --file docs/guide.md --collection my-docs
python3 scripts/rag_manager.py query --text "How do I reset a password?" --collection my-docs --top-k 3
python3 scripts/rag_manager.py list-collections
python3 scripts/rag_manager.py delete-collection --collection my-docs
```
