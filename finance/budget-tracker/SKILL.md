---
name: budget-tracker
id: OC-0160
version: 1.0.0
description: "Budget Tracker - Parse transactions and categorize spending automatically"
env: []
commands:
  - add-transaction
  - list
  - summary
  - set-budget
  - import-csv
---

# Budget Tracker

Track income and expenses, auto-categorize transactions, set budgets, and analyze spending patterns — all from the terminal.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `add-transaction` | Add an income or expense |
| `list` | List recent transactions |
| `summary` | Show spending summary by category |
| `set-budget` | Set a monthly budget for a category |
| `import-csv` | Import transactions from a CSV file |

## Usage

```bash
# Add an expense
python3 scripts/budget_tracker.py add-transaction --amount 45.50 --type expense --category food --description "Grocery run"

# Add income
python3 scripts/budget_tracker.py add-transaction --amount 3500 --type income --category salary --description "Monthly salary"

# List last 20 transactions
python3 scripts/budget_tracker.py list --limit 20

# Show monthly summary
python3 scripts/budget_tracker.py summary --month 2024-12

# Set a monthly budget for food
python3 scripts/budget_tracker.py set-budget --category food --amount 500

# Import CSV
python3 scripts/budget_tracker.py import-csv --file transactions.csv
```
