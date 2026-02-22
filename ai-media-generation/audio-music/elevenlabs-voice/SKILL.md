---
name: elevenlabs-voice
id: OC-0102
version: 1.0.0
description: "ElevenLabs TTS with voice cloning – generate speech in any voice"
env:
  - ELEVENLABS_API_KEY
commands:
  - speak
  - list-voices
  - clone-voice
  - get-voice
  - delete-voice
  - list-models
---

# ElevenLabs Voice

Generate ultra-realistic speech and clone voices using ElevenLabs' TTS platform.

## Prerequisites
- A valid `ELEVENLABS_API_KEY` environment variable.

## Commands
| Command        | Description                              |
|----------------|------------------------------------------|
| `speak`        | Convert text to speech                   |
| `list-voices`  | List all available voices with IDs       |
| `clone-voice`  | Create a voice clone from audio samples  |
| `get-voice`    | Get details of a specific voice          |
| `delete-voice` | Delete a cloned voice                    |
| `list-models`  | List available TTS models                |

## Usage
```bash
export ELEVENLABS_API_KEY="your_key"
python3 scripts/elevenlabs_voice.py speak --text "Hello, welcome to our platform!" --output greeting.mp3
python3 scripts/elevenlabs_voice.py speak --text "Narration text here" --voice-id "voice_id" --model eleven_multilingual_v2 --output narration.mp3
python3 scripts/elevenlabs_voice.py list-voices
python3 scripts/elevenlabs_voice.py clone-voice --name "My Voice" --files sample1.mp3 sample2.mp3 --description "Custom voice clone"
python3 scripts/elevenlabs_voice.py get-voice --voice-id "voice_id"
python3 scripts/elevenlabs_voice.py delete-voice --voice-id "voice_id"
python3 scripts/elevenlabs_voice.py list-models
```
