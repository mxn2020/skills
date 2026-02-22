---
name: arxiv-summarizer
id: OC-0151
version: 1.0.0
description: "arXiv Summarizer - Search, fetch, and summarize academic papers from arXiv"
env:
  - OPENAI_API_KEY
commands:
  - search
  - fetch-paper
  - summarize
  - list-recent
  - export
---

# arXiv Summarizer

Search and retrieve academic papers from arXiv, generate AI-powered summaries, and export paper details in multiple formats.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `openai` library (`pip install openai`)
- Environment variable: `OPENAI_API_KEY` (required for summarize command)

## Commands

| Command        | Parameters                                                                 | Description                                  |
| -------------- | -------------------------------------------------------------------------- | -------------------------------------------- |
| `search`       | `--query`, `--max-results` (default: 5), `--category` (e.g. cs.AI)        | Search arXiv papers                          |
| `fetch-paper`  | `--arxiv-id`                                                               | Fetch abstract and metadata for a paper      |
| `summarize`    | `--arxiv-id`, `--length` (brief/detailed/bullet-points)                    | Generate AI summary of a paper               |
| `list-recent`  | `--category`, `--days` (default: 7), `--max-results` (default: 5)         | List recently submitted papers               |
| `export`       | `--arxiv-id`, `--output`, `--format` (md/txt)                              | Export paper details to file                 |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

# Search for papers
python3 scripts/arxiv_summarizer.py search --query "transformer attention mechanism" --max-results 5 --category cs.AI

# Fetch paper details
python3 scripts/arxiv_summarizer.py fetch-paper --arxiv-id 2303.08774

# Summarize a paper
python3 scripts/arxiv_summarizer.py summarize --arxiv-id 2303.08774 --length bullet-points

# List recent papers in a category
python3 scripts/arxiv_summarizer.py list-recent --category cs.LG --days 7 --max-results 5

# Export paper to markdown
python3 scripts/arxiv_summarizer.py export --arxiv-id 2303.08774 --output paper.md --format md
```
