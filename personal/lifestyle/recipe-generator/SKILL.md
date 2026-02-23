---
name: recipe-generator
id: OC-0170
version: 1.0.0
description: "Recipe Generator & Shopper - Create meal plans and export shopping lists"
env:
  - OPENAI_API_KEY
commands:
  - generate-recipe
  - meal-plan
  - shopping-list
  - substitute
---

# Recipe Generator & Shopper

Generate recipes from available ingredients, create weekly meal plans, and export shopping lists.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI recipe generation

## Commands

| Command | Description |
|---------|-------------|
| `generate-recipe` | Generate a recipe from ingredients or cuisine |
| `meal-plan` | Create a weekly meal plan |
| `shopping-list` | Generate a shopping list from recipes |
| `substitute` | Find ingredient substitutes |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Generate a recipe from available ingredients
python3 scripts/recipe_generator.py generate-recipe --ingredients "chicken,garlic,lemon,olive oil" --cuisine italian

# Create a 5-day meal plan
python3 scripts/recipe_generator.py meal-plan --days 5 --dietary vegetarian

# Generate shopping list for a recipe
python3 scripts/recipe_generator.py shopping-list --recipe "Spaghetti Carbonara" --servings 4

# Find substitute for an ingredient
python3 scripts/recipe_generator.py substitute --ingredient "buttermilk" --recipe "pancakes"
```
