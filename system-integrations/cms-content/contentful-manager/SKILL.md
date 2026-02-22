---
name: Contentful Entry Manager
id: OC-0043
version: 1.0.0
description: Publish or archive content entries in Contentful CMS.
---

# Contentful Entry Manager

Manage content entries in your Contentful space — list, create, publish, unpublish, and archive.

## Capabilities

- List and inspect content entries in a space
- Create new entries with custom field data
- Publish and unpublish entries
- Archive entries to remove them from delivery

## Quick Start

```bash
export CONTENTFUL_SPACE_ID="your-space-id"
export CONTENTFUL_MANAGEMENT_TOKEN="your-cma-token"
python3 scripts/contentful_manager.py list-entries --content-type blogPost
python3 scripts/contentful_manager.py publish --entry-id abc123
```

## Commands & Parameters

| Command         | Parameters                                       | Description                     |
| --------------- | ------------------------------------------------ | ------------------------------- |
| `list-entries`  | `--content-type` (optional)                      | List entries, optionally by type|
| `get-entry`     | `--entry-id`                                     | Get a single entry by ID        |
| `publish`       | `--entry-id`                                     | Publish an entry                |
| `unpublish`     | `--entry-id`                                     | Unpublish an entry              |
| `archive`       | `--entry-id`                                     | Archive an entry                |
| `create-entry`  | `--content-type`, `--fields` (JSON)              | Create a new entry              |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `CONTENTFUL_SPACE_ID`, `CONTENTFUL_MANAGEMENT_TOKEN`
