---
name: active-listener
id: OC-0109
version: 1.0.0
description: "Active Listener - Detect pauses, extract speaker turns, summarize dialogue"
env:
  - OPENAI_API_KEY
commands:
  - detect-pauses
  - extract-turns
  - summarize-turns
  - analyze-dialogue
---

# Active Listener

Analyze audio conversations to detect pauses, extract speaker turns, and summarize dialogue segments.

## Prerequisites

- `OPENAI_API_KEY` — OpenAI API key (Whisper + GPT)

## Commands

| Command | Description |
|---------|-------------|
| `detect-pauses` | Find silence gaps above a threshold in a transcript |
| `extract-turns` | Split a transcript into speaker turns |
| `summarize-turns` | Summarize each speaker turn |
| `analyze-dialogue` | Full analysis: turns + pauses + summary |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/active_listener.py detect-pauses --file call.mp3 --threshold 1.5
python3 scripts/active_listener.py extract-turns --transcript-file transcript.txt
python3 scripts/active_listener.py summarize-turns --transcript-file transcript.txt
python3 scripts/active_listener.py analyze-dialogue --file meeting.mp3
```
