---
name: unsplash-search
id: OC-0064
version: 1.0.0
description: "Unsplash Photo Search - Find and license high-res stock photos"
env:
  - UNSPLASH_ACCESS_KEY
commands:
  - search
  - get-photo
  - download
  - random
  - list-collections
---

# Unsplash Photo Search

Find and license high-resolution stock photos from Unsplash.

## Prerequisites

- `UNSPLASH_ACCESS_KEY` – Unsplash API access key.

## Commands

| Command            | Description                              |
|--------------------|------------------------------------------|
| `search`           | Search photos by keyword                 |
| `get-photo`        | Get details for a specific photo         |
| `download`         | Trigger a download for a photo           |
| `random`           | Fetch random photos                      |
| `list-collections` | List featured collections                |

## Usage

```bash
export UNSPLASH_ACCESS_KEY="your-key"
python3 scripts/unsplash_search.py search --query "mountains" --per-page 10
python3 scripts/unsplash_search.py get-photo --photo-id "abc123"
python3 scripts/unsplash_search.py download --photo-id "abc123"
python3 scripts/unsplash_search.py random --count 3
python3 scripts/unsplash_search.py list-collections --per-page 5
```
