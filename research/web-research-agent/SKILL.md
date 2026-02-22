---
name: web-research-agent
id: OC-0150
version: 1.0.0
description: "Web Research Agent - Search, scrape, and synthesize web content using Serper and OpenAI"
env:
  - OPENAI_API_KEY
  - SERPER_API_KEY
commands:
  - search
  - scrape
  - synthesize
  - export-report
---

# Web Research Agent

An automated web research assistant that searches the web via Serper, scrapes page content, synthesizes findings with OpenAI, and exports structured reports.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `openai` library (`pip install openai`)
- `beautifulsoup4` library (`pip install beautifulsoup4`)
- Environment variables: `OPENAI_API_KEY`, `SERPER_API_KEY`

## Commands

| Command         | Parameters                                                          | Description                                |
| --------------- | ------------------------------------------------------------------- | ------------------------------------------ |
| `search`        | `--query`, `--num-results` (default: 5)                             | Search the web via Serper API              |
| `scrape`        | `--url`, `--extract` (text/links/headings)                          | Scrape content from a URL                  |
| `synthesize`    | `--query`, `--num-sources` (default: 3)                             | Search, scrape, and generate AI summary    |
| `export-report` | `--synthesis-file`, `--output`, `--format` (md/txt)                 | Export a synthesis result to file          |

## Usage

```bash
export OPENAI_API_KEY="sk-..."
export SERPER_API_KEY="your-serper-key"

# Search the web
python3 scripts/web_research_agent.py search --query "quantum computing breakthroughs 2024" --num-results 5

# Scrape a URL
python3 scripts/web_research_agent.py scrape --url "https://example.com" --extract text

# Synthesize research on a topic
python3 scripts/web_research_agent.py synthesize --query "climate change solutions" --num-sources 3

# Export a report
python3 scripts/web_research_agent.py export-report --synthesis-file synthesis.json --output report.md --format md
```
