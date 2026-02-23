---
name: sound-effect-foley
id: OC-0103
version: 1.0.0
description: "Generate sound effects using ElevenLabs sound generation API"
env:
  - ELEVENLABS_API_KEY
commands:
  - generate
  - list-examples
---

# Sound Effect Foley

Generate realistic sound effects from text descriptions using ElevenLabs' sound generation API.

## Prerequisites
- A valid `ELEVENLABS_API_KEY` environment variable.

## Commands
| Command          | Description                                   |
|------------------|-----------------------------------------------|
| `generate`       | Generate a sound effect from a text prompt    |
| `list-examples`  | Show example prompts for various SFX types    |

## Usage
```bash
export ELEVENLABS_API_KEY="your_key"
python3 scripts/sound_effect_foley.py generate --text "Heavy rain on a tin roof with distant thunder" --output rain.mp3
python3 scripts/sound_effect_foley.py generate --text "Gunshot in a large empty warehouse" --duration 2.0 --output shot.mp3
python3 scripts/sound_effect_foley.py list-examples
```
