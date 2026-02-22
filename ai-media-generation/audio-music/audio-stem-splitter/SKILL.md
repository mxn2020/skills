---
name: audio-stem-splitter
id: OC-0105
version: 1.0.0
description: "Split audio into stems using Demucs via Replicate – separate vocals, bass, drums, other"
env:
  - REPLICATE_API_TOKEN
commands:
  - split
  - split-four-stems
  - list-models
---

# Audio Stem Splitter

Separate audio tracks into individual stems (vocals, bass, drums, other) using Demucs on Replicate.

## Prerequisites
- A valid `REPLICATE_API_TOKEN` environment variable.

## Commands
| Command             | Description                                        |
|---------------------|----------------------------------------------------|
| `split`             | Split audio into selected stems                    |
| `split-four-stems`  | Split audio into all four stems at once            |
| `list-models`       | List available stem separation models              |

## Usage
```bash
export REPLICATE_API_TOKEN="r8_..."
python3 scripts/audio_stem_splitter.py split --input song.mp3 --stems vocals --output-dir ./stems
python3 scripts/audio_stem_splitter.py split --input song.mp3 --stems all --output-dir ./stems
python3 scripts/audio_stem_splitter.py split-four-stems --input song.mp3 --output-dir ./stems
python3 scripts/audio_stem_splitter.py list-models
```
