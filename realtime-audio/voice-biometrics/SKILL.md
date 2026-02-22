---
name: voice-biometrics
id: OC-0111
version: 1.0.0
description: "Voice Biometrics - Identify and verify speakers by voice print"
env:
  - AZURE_SPEECH_KEY
  - AZURE_SPEECH_REGION
commands:
  - enroll-speaker
  - identify-speaker
  - verify-speaker
  - list-speakers
---

# Voice Biometrics

Enroll speakers by voice print and identify or verify them in future recordings using Azure Speaker Recognition.

## Prerequisites

- `AZURE_SPEECH_KEY` — Azure Cognitive Services key
- `AZURE_SPEECH_REGION` — Azure region (e.g. `eastus`)

## Commands

| Command | Description |
|---------|-------------|
| `enroll-speaker` | Enroll a new speaker with a voice sample |
| `identify-speaker` | Identify the speaker in an audio file |
| `verify-speaker` | Verify if audio matches a known speaker |
| `list-speakers` | List all enrolled speaker profiles |

## Usage

```bash
export AZURE_SPEECH_KEY="..."
export AZURE_SPEECH_REGION="eastus"

python3 scripts/voice_biometrics.py enroll-speaker --name "Alice" --file alice_sample.wav
python3 scripts/voice_biometrics.py identify-speaker --file unknown.wav
python3 scripts/voice_biometrics.py verify-speaker --name "Alice" --file candidate.wav
python3 scripts/voice_biometrics.py list-speakers
```
