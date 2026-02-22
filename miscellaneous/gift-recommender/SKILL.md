---
name: gift-recommender
id: OC-0174
version: 1.0.0
description: "Gift Recommender - Suggest personalized gifts based on recipient interests and budget"
env:
  - OPENAI_API_KEY
commands:
  - recommend
  - budget-gifts
  - occasion
  - wishlist
---

# Gift Recommender

Get personalized gift suggestions based on recipient interests, age, budget, and occasion using AI.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI gift recommendations

## Commands

| Command | Description |
|---------|-------------|
| `recommend` | Get gift recommendations for a person |
| `budget-gifts` | Find gifts within a specific budget range |
| `occasion` | Get occasion-specific gift ideas |
| `wishlist` | Generate a wishlist from interests |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Get recommendations for a friend
python3 scripts/gift_recommender.py recommend --recipient "35-year-old male friend" --interests "hiking,coffee,photography" --budget 100

# Budget-specific gifts
python3 scripts/gift_recommender.py budget-gifts --min 20 --max 50 --interests "cooking,travel"

# Occasion-specific gifts
python3 scripts/gift_recommender.py occasion --occasion "wedding" --couple "adventure-loving couple" --budget 200

# Generate a wishlist
python3 scripts/gift_recommender.py wishlist --interests "gaming,tech,sci-fi" --budget 500
```
