---
name: Webflow CMS Updater
id: OC-0048
version: 1.0.0
description: Push collection item changes to Webflow CMS.
---

# Webflow CMS Updater

Manage Webflow sites, collections, and items through the Webflow Data API.

## Capabilities

- List sites and their collections
- CRUD operations on collection items
- Publish staged changes to production

## Quick Start

```bash
export WEBFLOW_API_TOKEN="your-api-token"
python3 scripts/webflow_updater.py list-sites
python3 scripts/webflow_updater.py list-items --collection-id abc123
python3 scripts/webflow_updater.py create-item --collection-id abc123 --fields '{"name":"New Item","slug":"new-item"}'
```

## Commands & Parameters

| Command            | Parameters                                        | Description                        |
| ------------------ | ------------------------------------------------- | ---------------------------------- |
| `list-sites`       | —                                                 | List all authorized sites          |
| `list-collections` | `--site-id`                                       | List collections for a site        |
| `list-items`       | `--collection-id`                                 | List items in a collection         |
| `create-item`      | `--collection-id`, `--fields` (JSON)              | Create a new collection item       |
| `update-item`      | `--collection-id`, `--item-id`, `--fields` (JSON) | Update an existing item            |
| `publish`          | `--site-id`, `--domains` (optional, JSON array)   | Publish staged changes             |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `WEBFLOW_API_TOKEN`
