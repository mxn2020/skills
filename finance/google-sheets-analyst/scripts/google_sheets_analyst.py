#!/usr/bin/env python3
"""
Google Sheets Analyst — OC-0163
Read, write, and analyze data in Google Spreadsheets.
"""

import os
import sys
import json
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("GOOGLE_SHEETS_TOKEN", "")
    if not token:
        _die("GOOGLE_SHEETS_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if not resp.ok:
        _die(f"Sheets API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def read(spreadsheet_id: str, cell_range: str):
    data = _request("GET", f"{spreadsheet_id}/values/{cell_range}")
    rows = data.get("values", [])

    if not rows:
        print(f"{YELLOW}No data in range {cell_range}.{RESET}")
        return

    # Print as table
    col_widths = []
    for row in rows:
        for i, cell in enumerate(row):
            if i >= len(col_widths):
                col_widths.append(0)
            col_widths[i] = max(col_widths[i], len(str(cell)))

    print(f"\n{BOLD}Data from {cell_range} ({len(rows)} row(s)):{RESET}\n")
    for ri, row in enumerate(rows):
        line = ""
        for i, cell in enumerate(row):
            width = col_widths[i] if i < len(col_widths) else 10
            color = CYAN if ri == 0 else ""
            line += f"{color}{str(cell):<{width+2}}{RESET}"
        print(f"  {line}")
    print()


def write(spreadsheet_id: str, cell_range: str, values_str: str):
    # Parse values: "v1,v2,v3" or "r1c1,r1c2;r2c1,r2c2"
    rows = []
    for row_str in values_str.split(";"):
        rows.append([v.strip() for v in row_str.split(",")])

    body = {"values": rows, "majorDimension": "ROWS"}
    data = _request("PUT",
        f"{spreadsheet_id}/values/{cell_range}",
        params={"valueInputOption": "USER_ENTERED"},
        json=body,
    )
    updated = data.get("updatedCells", 0)
    print(f"{GREEN}Updated {updated} cell(s) in {cell_range}.{RESET}")


def append(spreadsheet_id: str, sheet: str, values_str: str):
    rows = [[v.strip() for v in values_str.split(",")]]
    data = _request("POST",
        f"{spreadsheet_id}/values/{sheet}!A1:append",
        params={"valueInputOption": "USER_ENTERED", "insertDataOption": "INSERT_ROWS"},
        json={"values": rows, "majorDimension": "ROWS"},
    )
    updated = data.get("updates", {}).get("updatedCells", 0)
    print(f"{GREEN}Appended {updated} cell(s) to {sheet}.{RESET}")


def stats(spreadsheet_id: str, cell_range: str):
    data = _request("GET", f"{spreadsheet_id}/values/{cell_range}")
    rows = data.get("values", [])

    nums = []
    non_nums = 0
    for row in rows:
        for cell in row:
            try:
                nums.append(float(str(cell).replace(",", "").replace("$", "")))
            except ValueError:
                non_nums += 1

    if not nums:
        print(f"{YELLOW}No numeric values found in {cell_range}.{RESET}")
        return

    total   = sum(nums)
    count   = len(nums)
    mean    = total / count
    minimum = min(nums)
    maximum = max(nums)
    sorted_nums = sorted(nums)
    median  = sorted_nums[count // 2] if count % 2 else \
              (sorted_nums[count // 2 - 1] + sorted_nums[count // 2]) / 2
    variance = sum((x - mean) ** 2 for x in nums) / count
    std_dev  = variance ** 0.5

    print(f"\n{BOLD}Stats for {cell_range} ({count} values):{RESET}\n")
    print(f"  Sum:     {GREEN}{total:,.2f}{RESET}")
    print(f"  Mean:    {mean:,.2f}")
    print(f"  Median:  {median:,.2f}")
    print(f"  Min:     {minimum:,.2f}")
    print(f"  Max:     {maximum:,.2f}")
    print(f"  Std Dev: {std_dev:,.2f}")
    if non_nums:
        print(f"  {YELLOW}Skipped {non_nums} non-numeric cell(s).{RESET}")
    print()


def list_sheets(spreadsheet_id: str):
    data = _request("GET", spreadsheet_id, params={"fields": "sheets.properties"})
    sheets = data.get("sheets", [])

    if not sheets:
        print(f"{YELLOW}No sheets found.{RESET}")
        return

    print(f"\n{GREEN}Sheets in spreadsheet:{RESET}\n")
    for sheet in sheets:
        props = sheet.get("properties", {})
        title  = props.get("title", "")
        index  = props.get("index", 0)
        rows   = props.get("gridProperties", {}).get("rowCount", 0)
        cols   = props.get("gridProperties", {}).get("columnCount", 0)
        print(f"  {CYAN}[{index}]{RESET} {BOLD}{title}{RESET}  ({rows} rows × {cols} cols)")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="google_sheets_analyst.py",
        description="Google Sheets Analyst — OC-0163"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("read", help="Read data from a range")
    p.add_argument("--spreadsheet-id", required=True)
    p.add_argument("--range", required=True, dest="cell_range")

    p = sub.add_parser("write", help="Write data to a range")
    p.add_argument("--spreadsheet-id", required=True)
    p.add_argument("--range", required=True, dest="cell_range")
    p.add_argument("--values", required=True, help="Comma/semicolon separated values")

    p = sub.add_parser("append", help="Append rows to a sheet")
    p.add_argument("--spreadsheet-id", required=True)
    p.add_argument("--sheet", required=True)
    p.add_argument("--values", required=True, help="Comma-separated row values")

    p = sub.add_parser("stats", help="Calculate stats on a range")
    p.add_argument("--spreadsheet-id", required=True)
    p.add_argument("--range", required=True, dest="cell_range")

    p = sub.add_parser("list-sheets", help="List sheets in a spreadsheet")
    p.add_argument("--spreadsheet-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "read":        lambda: read(args.spreadsheet_id, args.cell_range),
        "write":       lambda: write(args.spreadsheet_id, args.cell_range, args.values),
        "append":      lambda: append(args.spreadsheet_id, args.sheet, args.values),
        "stats":       lambda: stats(args.spreadsheet_id, args.cell_range),
        "list-sheets": lambda: list_sheets(args.spreadsheet_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
