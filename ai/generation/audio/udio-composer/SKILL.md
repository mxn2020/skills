---
name: udio-composer
id: OC-0101
version: 1.0.0
description: "Udio AI music generation – compose and download original music tracks"
env:
  - UDIO_AUTH_TOKEN
commands:
  - generate
  - get-track
  - list-tracks
  - download
---

# Udio Composer

Generate original AI music tracks in any style using Udio's composition engine.

## Prerequisites
- A valid `UDIO_AUTH_TOKEN` environment variable.

## Commands
| Command       | Description                             |
|---------------|-----------------------------------------|
| `generate`    | Generate a new music track from a prompt|
| `get-track`   | Get details and status of a track       |
| `list-tracks` | List recently generated tracks          |
| `download`    | Download a track to an MP3 file         |

## Usage
```bash
export UDIO_AUTH_TOKEN="your_token"
python3 scripts/udio_composer.py generate --prompt "Cinematic orchestral score, epic battle scene" --wait --output-dir ./music
python3 scripts/udio_composer.py get-track --track-id "track_abc123"
python3 scripts/udio_composer.py list-tracks --limit 10
python3 scripts/udio_composer.py download --track-id "track_abc123" --output track.mp3
```
