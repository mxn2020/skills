---
name: Weaviate Schema Manager
id: OC-0038
version: 1.0.0
description: Update and manage Weaviate class definitions and objects.
---

# Weaviate Schema Manager

Manage Weaviate schemas, classes, and objects for vector search applications.

## Capabilities

- Retrieve and inspect the full schema
- Create and delete classes with custom properties
- List objects and run semantic queries

## Quick Start

```bash
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="your-api-key"
python3 scripts/weaviate_manager.py get-schema
python3 scripts/weaviate_manager.py create-class --name Article --properties '[{"name":"title","dataType":["text"]}]'
python3 scripts/weaviate_manager.py query --class-name Article --query "machine learning" --limit 5
```

## Commands & Parameters

| Command         | Parameters                                       | Description                  |
| --------------- | ------------------------------------------------ | ---------------------------- |
| `get-schema`    | —                                                | Get the full schema          |
| `create-class`  | `--name`, `--properties` (JSON)                  | Create a new class           |
| `delete-class`  | `--name`                                         | Delete a class               |
| `list-objects`  | `--class-name`, `--limit`                        | List objects in a class      |
| `query`         | `--class-name`, `--query`, `--limit`             | Semantic search              |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `WEAVIATE_URL`, `WEAVIATE_API_KEY`
