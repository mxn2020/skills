---
name: imgix-builder
id: OC-0067
version: 1.0.0
description: "Imgix URL Builder - Generate on-demand image transformation URLs"
env:
  - IMGIX_API_KEY
  - IMGIX_DOMAIN
commands:
  - build-url
  - list-sources
  - purge
  - get-source
---

# Imgix URL Builder

Generate on-demand image transformation URLs and manage Imgix sources.

## Prerequisites

- `IMGIX_API_KEY` – Imgix management API key.
- `IMGIX_DOMAIN` – Default Imgix source domain (e.g. `my-site.imgix.net`).

## Commands

| Command        | Description                                |
|----------------|--------------------------------------------|
| `build-url`    | Build a transformation URL for an image    |
| `list-sources` | List configured Imgix sources              |
| `purge`        | Purge a cached image from the CDN          |
| `get-source`   | Get details for a specific source          |

## Usage

```bash
export IMGIX_API_KEY="your-key"
export IMGIX_DOMAIN="my-site.imgix.net"
python3 scripts/imgix_builder.py build-url --path "/photos/hero.jpg" --width 800 --height 600 --auto compress,format
python3 scripts/imgix_builder.py list-sources
python3 scripts/imgix_builder.py purge --url "https://my-site.imgix.net/photos/hero.jpg"
python3 scripts/imgix_builder.py get-source --source-id "abc123"
```
