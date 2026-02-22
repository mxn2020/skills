---
name: podcast-summarizer
id: OC-0113
version: 1.0.0
description: "Podcast Summarizer - Fetch, transcribe, and summarize podcast episodes on demand"
env:
  - OPENAI_API_KEY
commands:
  - summarize-file
  - summarize-url
  - fetch-rss
  - extract-topics
---

# Podcast Summarizer

Download podcast episodes, transcribe them with Whisper, and generate AI summaries.

## Prerequisites

- `OPENAI_API_KEY` — OpenAI API key

## Commands

| Command | Description |
|---------|-------------|
| `summarize-file` | Summarize a local audio file |
| `summarize-url` | Download and summarize an audio URL |
| `fetch-rss` | List recent episodes from an RSS feed |
| `extract-topics` | Extract key topics from an audio file |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/podcast_summarizer.py summarize-file --file episode.mp3 --length medium
python3 scripts/podcast_summarizer.py summarize-url --url https://... --length brief
python3 scripts/podcast_summarizer.py fetch-rss --feed-url https://feeds.example.com/podcast.xml --limit 5
python3 scripts/podcast_summarizer.py extract-topics --file episode.mp3
```
