---
name: mux-uploader
id: OC-0066
version: 1.0.0
description: "Mux Video Uploader - Create video assets and retrieve playback IDs"
env:
  - MUX_TOKEN_ID
  - MUX_TOKEN_SECRET
commands:
  - create-asset
  - list-assets
  - get-asset
  - delete-asset
  - create-upload
  - get-playback
---

# Mux Video Uploader

Create video assets, manage uploads, and retrieve playback IDs from Mux.

## Prerequisites

- `MUX_TOKEN_ID` – Mux API token ID.
- `MUX_TOKEN_SECRET` – Mux API token secret.

## Commands

| Command         | Description                              |
|-----------------|------------------------------------------|
| `create-asset`  | Create a new asset from a video URL      |
| `list-assets`   | List video assets                        |
| `get-asset`     | Get details for a specific asset         |
| `delete-asset`  | Delete a video asset                     |
| `create-upload` | Create a direct upload URL               |
| `get-playback`  | Get playback info for an asset           |

## Usage

```bash
export MUX_TOKEN_ID="your-token-id"
export MUX_TOKEN_SECRET="your-token-secret"
python3 scripts/mux_uploader.py create-asset --url "https://example.com/video.mp4"
python3 scripts/mux_uploader.py list-assets --limit 10
python3 scripts/mux_uploader.py get-asset --asset-id "abc123"
python3 scripts/mux_uploader.py delete-asset --asset-id "abc123"
python3 scripts/mux_uploader.py create-upload --cors-origin "https://example.com"
python3 scripts/mux_uploader.py get-playback --asset-id "abc123"
```
