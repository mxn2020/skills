---
name: wikipedia-deep-dive
id: OC-0152
version: 1.0.0
description: "Wikipedia Deep Dive - Search, fetch, and summarize Wikipedia articles"
env:
  - OPENAI_API_KEY
commands:
  - search
  - fetch-article
  - summarize
  - extract-links
  - get-sections
---

# Wikipedia Deep Dive

Search Wikipedia, retrieve full article content, generate AI-powered summaries, extract links, and explore article sections across multiple languages.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `openai` library (`pip install openai`) — optional, required for summarize command
- Environment variable: `OPENAI_API_KEY` (optional, for summarize command)

## Commands

| Command          | Parameters                                               | Description                                      |
| ---------------- | -------------------------------------------------------- | ------------------------------------------------ |
| `search`         | `--query`, `--lang` (default: en), `--limit` (default: 5) | Search Wikipedia articles                       |
| `fetch-article`  | `--title`, `--lang` (default: en)                        | Fetch full article content                       |
| `summarize`      | `--title`, `--length` (brief/detailed)                   | Generate AI summary of an article               |
| `extract-links`  | `--title`, `--max` (default: 20)                         | Extract wikilinks from an article               |
| `get-sections`   | `--title`                                                | List all sections of an article                 |

## Usage

```bash
export OPENAI_API_KEY="sk-..."  # optional

# Search Wikipedia
python3 scripts/wikipedia_deep_dive.py search --query "quantum entanglement" --lang en --limit 5

# Fetch a full article
python3 scripts/wikipedia_deep_dive.py fetch-article --title "Quantum entanglement" --lang en

# Summarize an article with AI
python3 scripts/wikipedia_deep_dive.py summarize --title "Quantum entanglement" --length detailed

# Extract links from an article
python3 scripts/wikipedia_deep_dive.py extract-links --title "Quantum entanglement" --max 20

# Get article sections
python3 scripts/wikipedia_deep_dive.py get-sections --title "Quantum entanglement"
```
