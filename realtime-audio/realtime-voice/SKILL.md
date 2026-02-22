---
name: realtime-voice
id: OC-0106
version: 1.0.0
description: "Realtime Voice Interface - STT + LLM + TTS pipeline with low-latency optimization"
env:
  - OPENAI_API_KEY
  - ELEVENLABS_API_KEY
commands:
  - transcribe-audio
  - synthesize-speech
  - start-session
  - get-session-info
---

# Realtime Voice Interface

Low-latency voice pipeline combining Whisper (STT), an LLM, and ElevenLabs (TTS) for real-time conversational AI.

## Prerequisites

- `OPENAI_API_KEY` — OpenAI API key (Whisper + GPT)
- `ELEVENLABS_API_KEY` — ElevenLabs TTS API key

## Commands

| Command | Description |
|---------|-------------|
| `transcribe-audio` | Transcribe an audio file to text via Whisper |
| `synthesize-speech` | Convert text to speech via ElevenLabs |
| `start-session` | Print session configuration info |
| `get-session-info` | Show latency targets and model config |

## Usage

```bash
export OPENAI_API_KEY="sk-..."
export ELEVENLABS_API_KEY="xi-..."

python3 scripts/realtime_voice.py transcribe-audio --file meeting.wav
python3 scripts/realtime_voice.py synthesize-speech --text "Hello world" --output reply.mp3
python3 scripts/realtime_voice.py start-session --model gpt-4o --voice-id 21m00Tcm4TlvDq8ikWAM
python3 scripts/realtime_voice.py get-session-info
```
