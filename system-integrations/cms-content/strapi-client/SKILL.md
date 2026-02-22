---
name: Strapi API Client
id: OC-0045
version: 1.0.0
description: Manage dynamic content types via the Strapi REST API.
---

# Strapi API Client

Interact with your Strapi instance to list content types, create, update, and delete entries.

## Capabilities

- List available content types
- CRUD operations on collection entries
- Filter and paginate entry lists

## Quick Start

```bash
export STRAPI_URL="https://your-strapi.example.com"
export STRAPI_API_TOKEN="your-api-token"
python3 scripts/strapi_client.py list-content-types
python3 scripts/strapi_client.py create --type articles --data '{"title":"Hello","body":"World"}'
```

## Commands & Parameters

| Command              | Parameters                                    | Description                     |
| -------------------- | --------------------------------------------- | ------------------------------- |
| `list-content-types` | —                                             | List registered content types   |
| `list-entries`       | `--type`                                      | List entries for a content type |
| `get-entry`          | `--type`, `--id`                              | Get a single entry by ID        |
| `create`             | `--type`, `--data` (JSON)                     | Create a new entry              |
| `update`             | `--type`, `--id`, `--data` (JSON)             | Update an existing entry        |
| `delete`             | `--type`, `--id`                              | Delete an entry                 |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `STRAPI_URL`, `STRAPI_API_TOKEN`
