---
name: camera-feed-analyzer
id: OC-0168
version: 1.0.0
description: "Camera Feed Analyzer - Describe or detect objects in a home camera snapshot"
env:
  - OPENAI_API_KEY
  - HOME_ASSISTANT_URL
  - HOME_ASSISTANT_TOKEN
commands:
  - analyze-snapshot
  - detect-motion
  - describe-scene
  - analyze-file
---

# Camera Feed Analyzer

Analyze home camera snapshots using AI vision. Detect objects, describe scenes, and identify unusual activity.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for GPT-4 Vision analysis
- `HOME_ASSISTANT_URL` + `HOME_ASSISTANT_TOKEN` — for camera entity integration

## Commands

| Command | Description |
|---------|-------------|
| `analyze-snapshot` | Fetch and analyze a camera snapshot from HA |
| `detect-motion` | Describe movement or activity in an image |
| `describe-scene` | Provide a detailed scene description |
| `analyze-file` | Analyze a local image file |

## Usage

```bash
export OPENAI_API_KEY="your_key"
export HOME_ASSISTANT_URL="http://homeassistant.local:8123"
export HOME_ASSISTANT_TOKEN="your_ha_token"

# Analyze camera feed from Home Assistant
python3 scripts/camera_feed_analyzer.py analyze-snapshot --entity-id "camera.front_door"

# Describe a local image file
python3 scripts/camera_feed_analyzer.py analyze-file --file /path/to/snapshot.jpg

# Detect motion/activity
python3 scripts/camera_feed_analyzer.py detect-motion --entity-id "camera.backyard"
```
