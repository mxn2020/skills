---
name: whisper-transcriber
id: OC-0104
version: 1.0.0
description: "OpenAI Whisper transcription – transcribe, translate, and detect language in audio"
env:
  - OPENAI_API_KEY
commands:
  - transcribe
  - translate
  - detect-language
---

# Whisper Transcriber

Transcribe, translate, and detect language in audio files using OpenAI's Whisper API.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command           | Description                                    |
|-------------------|------------------------------------------------|
| `transcribe`      | Transcribe audio to text                       |
| `translate`       | Transcribe and translate audio to English      |
| `detect-language` | Detect the language spoken in an audio file    |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/whisper_transcriber.py transcribe --input audio.mp3 --format srt --output captions.srt
python3 scripts/whisper_transcriber.py transcribe --input lecture.mp3 --language fr --format text --output transcript.txt
python3 scripts/whisper_transcriber.py translate --input spanish_audio.mp3 --output english_transcript.txt
python3 scripts/whisper_transcriber.py detect-language --input audio.mp3
```
