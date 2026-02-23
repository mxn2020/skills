---
name: news-aggregator
id: OC-0157
version: 1.0.0
description: "News Aggregator - Pull and summarize headlines by topic from RSS/APIs"
env:
  - NEWS_API_KEY
commands:
  - headlines
  - search
  - digest
  - sources
---

# News Aggregator

Pull and summarize news headlines by topic from NewsAPI and RSS feeds. Generate daily digests for your preferred topics.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `NEWS_API_KEY` — from newsapi.org (free tier available)

## Commands

| Command | Description |
|---------|-------------|
| `headlines` | Get top headlines by category or country |
| `search` | Search news by keyword or topic |
| `digest` | Generate a summarized digest for multiple topics |
| `sources` | List available news sources |

## Usage

```bash
export NEWS_API_KEY="your_key"

# Get top tech headlines
python3 scripts/news_aggregator.py headlines --category technology --country us

# Search for specific topics
python3 scripts/news_aggregator.py search --query "artificial intelligence" --max-results 10

# Generate a morning digest
python3 scripts/news_aggregator.py digest --topics "technology,science,business"

# List available sources
python3 scripts/news_aggregator.py sources --category technology
```
