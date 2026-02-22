---
name: voice-sentiment
id: OC-0108
version: 1.0.0
description: "Voice Sentiment Analyzer - Detect emotion and stress in audio input"
env:
  - OPENAI_API_KEY
commands:
  - analyze-file
  - analyze-text
  - batch-analyze
---

# Voice Sentiment Analyzer

Detect emotion, tone, and stress levels in audio recordings by transcribing with Whisper and analyzing sentiment with GPT.

## Prerequisites

- `OPENAI_API_KEY` — OpenAI API key

## Commands

| Command | Description |
|---------|-------------|
| `analyze-file` | Transcribe audio and analyze sentiment |
| `analyze-text` | Analyze sentiment of plain text |
| `batch-analyze` | Analyze all audio files in a directory |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/voice_sentiment.py analyze-file --file call.mp3
python3 scripts/voice_sentiment.py analyze-text --text "I'm really frustrated with this!"
python3 scripts/voice_sentiment.py batch-analyze --dir ./recordings --output report.json
```
