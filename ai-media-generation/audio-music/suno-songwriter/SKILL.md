---
name: suno-songwriter
id: OC-0100
version: 1.0.0
description: "Suno AI music generation – create full songs with vocals from text prompts"
env:
  - SUNO_COOKIE
commands:
  - generate
  - get-song
  - list-songs
  - download
---

# Suno Songwriter

Generate full AI-composed songs with vocals using Suno AI from text descriptions.

## Prerequisites
- A valid `SUNO_COOKIE` environment variable (session cookie from studio.suno.ai).

## Commands
| Command      | Description                                |
|--------------|--------------------------------------------|
| `generate`   | Generate a new song from a prompt          |
| `get-song`   | Get details and status of a song           |
| `list-songs` | List recently generated songs              |
| `download`   | Download a song to an MP3 file             |

## Usage
```bash
export SUNO_COOKIE="your_session_cookie"
python3 scripts/suno_songwriter.py generate --prompt "Upbeat pop song about summer adventures" --wait --output-dir ./music
python3 scripts/suno_songwriter.py generate --prompt "Sad blues piano ballad" --make-instrumental --wait --output-dir ./music
python3 scripts/suno_songwriter.py get-song --song-id "song_abc123"
python3 scripts/suno_songwriter.py list-songs --limit 10
python3 scripts/suno_songwriter.py download --song-id "song_abc123" --output song.mp3
```
