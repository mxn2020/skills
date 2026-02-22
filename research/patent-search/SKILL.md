---
name: patent-search
id: OC-0156
version: 1.0.0
description: "Patent Search Tool - Query patent databases for prior art"
env: []
commands:
  - search
  - get-patent
  - prior-art
  - list-by-assignee
---

# Patent Search Tool

Query the USPTO and Google Patents APIs to search for patents, check prior art, and analyze patent landscapes.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)

## Commands

| Command | Description |
|---------|-------------|
| `search` | Search patents by keyword |
| `get-patent` | Get detailed information about a patent |
| `prior-art` | Search for prior art on an invention concept |
| `list-by-assignee` | Find patents by company or inventor |

## Usage

```bash
# Search patents by keyword
python3 scripts/patent_search.py search --query "neural network image recognition" --max-results 10

# Get detailed patent info
python3 scripts/patent_search.py get-patent --patent-id "US10000000"

# Search for prior art
python3 scripts/patent_search.py prior-art --description "A method for compressing video using attention mechanisms"

# Find patents by assignee
python3 scripts/patent_search.py list-by-assignee --assignee "OpenAI" --max-results 20
```
