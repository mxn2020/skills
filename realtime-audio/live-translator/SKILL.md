---
name: live-translator
id: OC-0107
version: 1.0.0
description: "Live Translator - Translate audio streams and text in real time"
env:
  - OPENAI_API_KEY
  - DEEPL_API_KEY
commands:
  - translate-audio
  - translate-text
  - list-languages
  - detect-language
---

# Live Translator

Translate audio files and text in real time using Whisper (transcription) and DeepL or OpenAI (translation).

## Prerequisites

- `OPENAI_API_KEY` — for audio transcription via Whisper
- `DEEPL_API_KEY` — for high-quality translation (optional; falls back to OpenAI)

## Commands

| Command | Description |
|---------|-------------|
| `translate-audio` | Transcribe and translate an audio file |
| `translate-text` | Translate plain text to a target language |
| `list-languages` | List supported DeepL language codes |
| `detect-language` | Detect the language of a text snippet |

## Usage

```bash
export OPENAI_API_KEY="sk-..."
export DEEPL_API_KEY="..."

python3 scripts/live_translator.py translate-audio --file speech.mp3 --target-lang ES
python3 scripts/live_translator.py translate-text --text "Hello world" --target-lang FR
python3 scripts/live_translator.py list-languages
python3 scripts/live_translator.py detect-language --text "Bonjour le monde"
```
