---
name: auto-subtitle
id: OC-0099
version: 1.0.0
description: "Auto-generate and burn subtitles using OpenAI Whisper API and FFmpeg"
env:
  - OPENAI_API_KEY
commands:
  - transcribe
  - burn-subtitles
  - generate-srt
---

# Auto Subtitle

Automatically transcribe speech and burn subtitles into videos using Whisper and FFmpeg.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.
- `ffmpeg` must be installed and available in your PATH.

## Commands
| Command           | Description                                        |
|-------------------|----------------------------------------------------|
| `transcribe`      | Transcribe audio/video to a subtitle file          |
| `burn-subtitles`  | Burn a subtitle file permanently into a video      |
| `generate-srt`    | Transcribe and save directly as SRT in one step    |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/auto_subtitle.py transcribe --input video.mp4 --output captions.srt
python3 scripts/auto_subtitle.py burn-subtitles --video video.mp4 --subtitles captions.srt --output captioned.mp4
python3 scripts/auto_subtitle.py generate-srt --input video.mp4 --language en --output captions.srt
```
