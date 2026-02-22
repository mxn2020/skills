#!/usr/bin/env python3
"""
Budget Tracker — OC-0160
Parse transactions and categorize spending automatically.
"""

import os
import sys
import csv
import json
import uuid
import argparse
from datetime import datetime, timezone

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

DATA_FILE    = os.path.expanduser("~/.budget_tracker.json")
BUDGETS_FILE = os.path.expanduser("~/.budget_limits.json")

AUTO_CATEGORIES = {
    "food": ["grocery", "restaurant", "cafe", "food", "eat", "lunch", "dinner",
             "breakfast", "pizza", "burger", "coffee"],
    "transport": ["uber", "lyft", "taxi", "gas", "fuel", "parking", "transit",
                  "bus", "train", "flight", "airline"],
    "utilities": ["electric", "water", "internet", "phone", "utility", "bill"],
    "entertainment": ["netflix", "spotify", "cinema", "movie", "concert", "game",
                      "subscription", "streaming"],
    "shopping": ["amazon", "shop", "mall", "clothing", "shoes", "retail"],
    "health": ["pharmacy", "gym", "doctor", "hospital", "medicine", "dental"],
    "rent": ["rent", "mortgage", "housing", "lease"],
    "salary": ["salary", "paycheck", "wage", "income", "payroll"],
    "freelance": ["freelance", "consulting", "contract", "invoice"],
}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_data() -> list:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_data(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _load_budgets() -> dict:
    if os.path.exists(BUDGETS_FILE):
        try:
            with open(BUDGETS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_budgets(data: dict):
    with open(BUDGETS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _auto_categorize(description: str) -> str:
    desc_lower = description.lower()
    for cat, keywords in AUTO_CATEGORIES.items():
        if any(kw in desc_lower for kw in keywords):
            return cat
    return "other"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def add_transaction(amount: float, tx_type: str, category: str, description: str):
    if tx_type not in ("income", "expense"):
        _die("Type must be 'income' or 'expense'.")

    if not category:
        category = _auto_categorize(description)

    record = {
        "id": str(uuid.uuid4())[:8],
        "date": _today(),
        "type": tx_type,
        "amount": round(amount, 2),
        "category": category.lower(),
        "description": description,
    }
    data = _load_data()
    data.append(record)
    _save_data(data)

    color = GREEN if tx_type == "income" else RED
    sign  = "+" if tx_type == "income" else "-"
    print(f"{color}{sign}${amount:.2f}{RESET}  {BOLD}{description}{RESET}  "
          f"[{CYAN}{category}{RESET}]")
    print(f"  ID: {record['id']}  |  Date: {record['date']}")
    print()


def list_transactions(limit: int = 20, tx_type: str = None, category: str = None):
    data = _load_data()
    if tx_type:
        data = [t for t in data if t.get("type") == tx_type]
    if category:
        data = [t for t in data if t.get("category") == category.lower()]

    recent = sorted(data, key=lambda t: t.get("date", ""), reverse=True)[:limit]
    if not recent:
        print(f"{YELLOW}No transactions found.{RESET}")
        return

    print(f"\n{BOLD}Transactions ({len(recent)}):{RESET}\n")
    for t in recent:
        color = GREEN if t.get("type") == "income" else RED
        sign  = "+" if t.get("type") == "income" else "-"
        amt   = t.get("amount", 0)
        desc  = t.get("description", "")
        cat   = t.get("category", "")
        date  = t.get("date", "")
        print(f"  {CYAN}{date}{RESET}  {color}{sign}${amt:.2f}{RESET}  "
              f"{BOLD}{desc[:40]}{RESET}  [{cat}]")
    print()


def summary(month: str = None):
    if not month:
        month = _current_month()
    data = _load_data()
    budgets = _load_budgets()

    month_data = [t for t in data if t.get("date", "").startswith(month)]

    if not month_data:
        print(f"{YELLOW}No transactions for {month}.{RESET}")
        return

    income = sum(t["amount"] for t in month_data if t.get("type") == "income")
    expenses = sum(t["amount"] for t in month_data if t.get("type") == "expense")
    net = income - expenses

    # Group expenses by category
    by_cat: dict = {}
    for t in month_data:
        if t.get("type") == "expense":
            cat = t.get("category", "other")
            by_cat[cat] = by_cat.get(cat, 0) + t["amount"]

    print(f"\n{BOLD}Budget Summary — {month}:{RESET}\n")
    print(f"  {GREEN}Income:    ${income:>10.2f}{RESET}")
    print(f"  {RED}Expenses:  ${expenses:>10.2f}{RESET}")
    color = GREEN if net >= 0 else RED
    print(f"  {color}Net:       ${net:>10.2f}{RESET}\n")

    if by_cat:
        print(f"  {BOLD}By Category:{RESET}")
        for cat, total in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
            budget = budgets.get(cat, 0)
            if budget:
                pct = total / budget * 100
                status_color = RED if pct > 100 else (YELLOW if pct > 80 else GREEN)
                bar = f"  [{status_color}{int(pct)}%{RESET} of ${budget:.0f}]"
            else:
                bar = ""
            print(f"    {CYAN}{cat:<15}{RESET} ${total:>8.2f}{bar}")
    print()


def set_budget(category: str, amount: float):
    budgets = _load_budgets()
    budgets[category.lower()] = amount
    _save_budgets(budgets)
    print(f"{GREEN}Budget set: {category} → ${amount:.2f}/month{RESET}")


def import_csv(filepath: str):
    if not os.path.exists(filepath):
        _die(f"File not found: {filepath}")

    data = _load_data()
    imported = 0
    errors = 0

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Support common CSV formats
                amount = float(row.get("amount") or row.get("Amount") or
                               row.get("Debit") or row.get("debit") or 0)
                desc = (row.get("description") or row.get("Description") or
                        row.get("Memo") or "").strip()
                date = (row.get("date") or row.get("Date") or _today()).strip()[:10]
                tx_type = "expense" if amount > 0 else "income"
                amount = abs(amount)
                cat = _auto_categorize(desc)

                data.append({
                    "id": str(uuid.uuid4())[:8],
                    "date": date,
                    "type": tx_type,
                    "amount": round(amount, 2),
                    "category": cat,
                    "description": desc,
                })
                imported += 1
            except (ValueError, KeyError):
                errors += 1

    _save_data(data)
    print(f"{GREEN}Imported {imported} transaction(s).{RESET}")
    if errors:
        print(f"{YELLOW}Skipped {errors} row(s) due to parse errors.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="budget_tracker.py",
        description="Budget Tracker — OC-0160"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-transaction", help="Add a transaction")
    p.add_argument("--amount", type=float, required=True)
    p.add_argument("--type", required=True, choices=["income", "expense"])
    p.add_argument("--category", default="")
    p.add_argument("--description", required=True)

    p = sub.add_parser("list", help="List recent transactions")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--type", default=None, choices=["income", "expense"])
    p.add_argument("--category", default=None)

    p = sub.add_parser("summary", help="Show monthly summary")
    p.add_argument("--month", default=None, help="YYYY-MM format (default: current)")

    p = sub.add_parser("set-budget", help="Set monthly budget for a category")
    p.add_argument("--category", required=True)
    p.add_argument("--amount", type=float, required=True)

    p = sub.add_parser("import-csv", help="Import from CSV file")
    p.add_argument("--file", required=True)

    args = parser.parse_args()
    dispatch = {
        "add-transaction": lambda: add_transaction(
            args.amount, args.type, args.category, args.description),
        "list":            lambda: list_transactions(
            args.limit, getattr(args, "type", None), getattr(args, "category", None)),
        "summary":         lambda: summary(args.month),
        "set-budget":      lambda: set_budget(args.category, args.amount),
        "import-csv":      lambda: import_csv(args.file),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
