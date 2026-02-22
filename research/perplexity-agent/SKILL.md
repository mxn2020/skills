---
name: perplexity-agent
id: OC-0155
version: 1.0.0
description: "Perplexity Query Agent - Use Perplexity's API for grounded, citation-backed answers"
env:
  - PERPLEXITY_API_KEY
commands:
  - search
  - deep-research
  - summarize-topic
---

# Perplexity Query Agent

Query Perplexity's AI API for grounded, citation-backed answers with real-time web access.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `PERPLEXITY_API_KEY` — from Perplexity developer settings

## Commands

| Command | Description |
|---------|-------------|
| `search` | Ask a question and get a cited answer |
| `deep-research` | Detailed research with expanded citations |
| `summarize-topic` | Generate a structured topic summary |

## Usage

```bash
export PERPLEXITY_API_KEY="your_key"

# Quick search with citations
python3 scripts/perplexity_agent.py search --query "latest advances in quantum computing 2024"

# Deep research with full citations
python3 scripts/perplexity_agent.py deep-research --query "transformer architecture improvements"

# Structured topic summary
python3 scripts/perplexity_agent.py summarize-topic --topic "Large Language Models" --depth brief
```
