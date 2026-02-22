#!/usr/bin/env python3
"""
Recipe Generator & Shopper — OC-0170
Create meal plans and export shopping lists.
"""

import os
import sys
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str, system: str = "You are an expert chef and nutritionist.") -> str:
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1000,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_recipe(ingredients: str, cuisine: str = "", dietary: str = "",
                    servings: int = 2):
    constraints = []
    if cuisine:
        constraints.append(f"cuisine: {cuisine}")
    if dietary:
        constraints.append(f"dietary: {dietary}")

    prompt = (
        f"Create a delicious recipe using these ingredients: {ingredients}.\n"
        f"Servings: {servings}\n"
        + (f"Constraints: {', '.join(constraints)}\n" if constraints else "")
        + "\nFormat:\n"
        "**Recipe Name**\n\n"
        "**Description** (1-2 sentences)\n\n"
        "**Ingredients** (with quantities)\n\n"
        "**Instructions** (step-by-step)\n\n"
        "**Nutritional Info** (approx per serving)\n\n"
        "**Time:** Prep XX min | Cook XX min"
    )
    print(f"{YELLOW}Generating recipe...{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def meal_plan(days: int = 7, dietary: str = "", calories: int = 0):
    constraints = []
    if dietary:
        constraints.append(dietary)
    if calories:
        constraints.append(f"~{calories} calories per day")

    prompt = (
        f"Create a {days}-day meal plan with breakfast, lunch, and dinner.\n"
        + (f"Dietary requirements: {', '.join(constraints)}\n" if constraints else "")
        + "For each day, list:\n"
        "- Breakfast (with prep time)\n"
        "- Lunch (with prep time)\n"
        "- Dinner (with prep time)\n"
        "- Approximate total calories\n\n"
        "Keep meals varied, nutritious, and practical."
    )
    print(f"{YELLOW}Generating {days}-day meal plan...{RESET}\n")
    print(f"{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}{days}-Day Meal Plan{RESET}")
    print(f"{BOLD}{'='*55}{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def shopping_list(recipe_name: str, servings: int = 4):
    prompt = (
        f"Generate a complete shopping list for '{recipe_name}' ({servings} servings).\n\n"
        "Organize by store section:\n"
        "- Produce\n"
        "- Meat/Seafood\n"
        "- Dairy\n"
        "- Pantry/Dry Goods\n"
        "- Frozen\n"
        "- Other\n\n"
        "Include exact quantities. Add estimated cost per item in USD."
    )
    print(f"{YELLOW}Generating shopping list for '{recipe_name}' ({servings} servings)...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Shopping List — {recipe_name}{RESET}\n")
    print(result)
    print()


def substitute(ingredient: str, recipe: str = "", dietary: str = ""):
    context = f"in the recipe '{recipe}'" if recipe else "in cooking"
    constraints = f"Must be {dietary}." if dietary else ""

    prompt = (
        f"Suggest 3 substitutes for '{ingredient}' {context}. {constraints}\n\n"
        "For each substitute provide:\n"
        "1. Name and quantity adjustment\n"
        "2. How it changes the dish\n"
        "3. When to use it"
    )
    print(f"{YELLOW}Finding substitutes for '{ingredient}'...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Substitutes for {ingredient}:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="recipe_generator.py",
        description="Recipe Generator & Shopper — OC-0170"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("generate-recipe", help="Generate a recipe")
    p.add_argument("--ingredients", required=True, help="Comma-separated ingredients")
    p.add_argument("--cuisine", default="")
    p.add_argument("--dietary", default="", help="e.g. vegetarian, gluten-free, vegan")
    p.add_argument("--servings", type=int, default=2)

    p = sub.add_parser("meal-plan", help="Create a meal plan")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--dietary", default="")
    p.add_argument("--calories", type=int, default=0)

    p = sub.add_parser("shopping-list", help="Generate shopping list")
    p.add_argument("--recipe", required=True)
    p.add_argument("--servings", type=int, default=4)

    p = sub.add_parser("substitute", help="Find ingredient substitutes")
    p.add_argument("--ingredient", required=True)
    p.add_argument("--recipe", default="")
    p.add_argument("--dietary", default="")

    args = parser.parse_args()
    dispatch = {
        "generate-recipe": lambda: generate_recipe(args.ingredients, args.cuisine,
                                                     args.dietary, args.servings),
        "meal-plan":       lambda: meal_plan(args.days, args.dietary, args.calories),
        "shopping-list":   lambda: shopping_list(args.recipe, args.servings),
        "substitute":      lambda: substitute(args.ingredient, args.recipe, args.dietary),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
