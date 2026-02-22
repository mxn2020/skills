---
name: call-quality-monitor
id: OC-0114
version: 1.0.0
description: "Call Quality Monitor - Detect jitter, latency, and packet loss in audio streams"
env: []
commands:
  - analyze-audio
  - measure-latency
  - detect-jitter
  - generate-report
---

# Call Quality Monitor

Analyze audio files and network captures to measure call quality metrics including MOS score, jitter, and packet loss.

## Prerequisites

- Python: `pip install soundfile numpy`
- Optional: `ffmpeg` for format conversion

## Commands

| Command | Description |
|---------|-------------|
| `analyze-audio` | Estimate MOS score from an audio file |
| `measure-latency` | Measure perceived latency/gaps in audio |
| `detect-jitter` | Detect jitter patterns in audio |
| `generate-report` | Full quality report for an audio file |

## Usage

```bash
python3 scripts/call_quality_monitor.py analyze-audio --file call.wav
python3 scripts/call_quality_monitor.py measure-latency --file call.wav
python3 scripts/call_quality_monitor.py detect-jitter --file call.wav --threshold 30
python3 scripts/call_quality_monitor.py generate-report --file call.wav --output report.json
```
