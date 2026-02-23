---
name: stock-photo-search
id: OC-0068
version: 1.0.0
description: "Pexels/Pixabay Search - Source free stock photos and videos"
env:
  - PEXELS_API_KEY
  - PIXABAY_API_KEY
commands:
  - search-pexels
  - search-pixabay
  - download
  - curated
  - popular
---

# Pexels / Pixabay Search

Source free stock photos and videos from Pexels and Pixabay.

## Prerequisites

- `PEXELS_API_KEY` – Pexels API key.
- `PIXABAY_API_KEY` – Pixabay API key.

## Commands

| Command          | Description                              |
|------------------|------------------------------------------|
| `search-pexels`  | Search photos on Pexels                  |
| `search-pixabay` | Search photos on Pixabay                 |
| `download`       | Download a photo by URL                  |
| `curated`        | Fetch curated photos from Pexels         |
| `popular`        | Fetch popular images from Pixabay        |

## Usage

```bash
export PEXELS_API_KEY="your-pexels-key"
export PIXABAY_API_KEY="your-pixabay-key"
python3 scripts/stock_photo_search.py search-pexels --query "sunset" --per-page 10
python3 scripts/stock_photo_search.py search-pixabay --query "ocean" --per-page 10
python3 scripts/stock_photo_search.py download --url "https://images.pexels.com/photos/123/example.jpeg" --output photo.jpg
python3 scripts/stock_photo_search.py curated --per-page 5
python3 scripts/stock_photo_search.py popular --per-page 5
```
