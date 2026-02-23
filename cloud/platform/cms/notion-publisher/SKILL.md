---
name: Notion Page Publisher
id: OC-0049
version: 1.0.0
description: Create and update Notion pages and databases.
---

# Notion Page Publisher

Search, create, and update Notion pages and databases via the Notion API.

## Capabilities

- Search across pages and databases
- Create and update pages with rich properties
- Append block children to existing pages
- Query database contents

## Quick Start

```bash
export NOTION_API_KEY="your-integration-token"
python3 scripts/notion_publisher.py search --query "Meeting Notes"
python3 scripts/notion_publisher.py create-page --parent-id abc123 --properties '{"title":[{"text":{"content":"New Page"}}]}'
```

## Commands & Parameters

| Command          | Parameters                                            | Description                        |
| ---------------- | ----------------------------------------------------- | ---------------------------------- |
| `search`         | `--query`                                             | Search pages and databases         |
| `get-page`       | `--page-id`                                           | Get a page by ID                   |
| `create-page`    | `--parent-id`, `--properties` (JSON)                  | Create a new page                  |
| `update-page`    | `--page-id`, `--properties` (JSON)                    | Update page properties             |
| `append-blocks`  | `--page-id`, `--blocks` (JSON)                        | Append block children to a page    |
| `get-database`   | `--database-id`                                       | Query a database                   |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `NOTION_API_KEY`
