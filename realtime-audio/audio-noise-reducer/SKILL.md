---
name: audio-noise-reducer
id: OC-0112
version: 1.0.0
description: "Audio Noise Reducer - Clean up microphone input and audio files in software"
env: []
commands:
  - reduce-noise
  - batch-reduce
  - measure-snr
  - list-profiles
---

# Audio Noise Reducer

Remove background noise from audio files using the `noisereduce` library (or ffmpeg as fallback).

## Prerequisites

- Python: `pip install noisereduce soundfile numpy`
- Or: `ffmpeg` installed (fallback mode)

## Commands

| Command | Description |
|---------|-------------|
| `reduce-noise` | Remove noise from a single audio file |
| `batch-reduce` | Process all audio files in a directory |
| `measure-snr` | Estimate the signal-to-noise ratio of a file |
| `list-profiles` | List available noise reduction profiles |

## Usage

```bash
python3 scripts/audio_noise_reducer.py reduce-noise --input noisy.wav --output clean.wav
python3 scripts/audio_noise_reducer.py reduce-noise --input call.mp3 --strength high
python3 scripts/audio_noise_reducer.py batch-reduce --dir ./recordings --output-dir ./cleaned
python3 scripts/audio_noise_reducer.py measure-snr --file audio.wav
python3 scripts/audio_noise_reducer.py list-profiles
```
