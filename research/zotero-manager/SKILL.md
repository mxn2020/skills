---
name: zotero-manager
id: OC-0153
version: 1.0.0
description: "Zotero Manager - Manage Zotero library collections, items, and bibliographies"
env:
  - ZOTERO_API_KEY
  - ZOTERO_USER_ID
commands:
  - list-collections
  - add-item
  - search-items
  - export-bibliography
  - get-item
---

# Zotero Manager

Manage your Zotero reference library: list collections, add new items, search references, export bibliographies in multiple formats, and retrieve item details.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- Environment variables: `ZOTERO_API_KEY`, `ZOTERO_USER_ID`

## Commands

| Command                | Parameters                                                                                              | Description                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `list-collections`     | —                                                                                                       | List all Zotero collections             |
| `add-item`             | `--title`, `--url`, `--authors`, `--year`, `--item-type` (webpage/journalArticle/book), `--collection-key` | Add a new item to library           |
| `search-items`         | `--query`, `--collection-key`                                                                           | Search items in library or collection  |
| `export-bibliography`  | `--collection-key`, `--format` (bibtex/ris/chicago/apa)                                                 | Export bibliography for a collection   |
| `get-item`             | `--item-key`                                                                                            | Retrieve details of a specific item    |

## Usage

```bash
export ZOTERO_API_KEY="your-api-key"
export ZOTERO_USER_ID="your-user-id"

# List all collections
python3 scripts/zotero_manager.py list-collections

# Add a webpage item
python3 scripts/zotero_manager.py add-item --title "My Article" --url "https://example.com" \
  --authors "Smith, John" --year 2024 --item-type webpage --collection-key ABC123

# Search items
python3 scripts/zotero_manager.py search-items --query "machine learning"

# Export bibliography in BibTeX format
python3 scripts/zotero_manager.py export-bibliography --collection-key ABC123 --format bibtex

# Get item details
python3 scripts/zotero_manager.py get-item --item-key XYZ789
```
