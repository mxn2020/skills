#!/usr/bin/env python3
"""
Stock Price Fetcher — OC-0159
Get real-time quotes, charts, and earnings data via Alpha Vantage.
"""

import os
import sys
import json
import argparse
from datetime import datetime
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL      = "https://www.alphavantage.co/query"
WATCHLIST_FILE = os.path.expanduser("~/.stock_watchlist.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _api_key() -> str:
    key = os.environ.get("ALPHA_VANTAGE_KEY", "")
    if not key:
        _die("ALPHA_VANTAGE_KEY is not set. Get a free key at alphavantage.co")
    return key


def _request(params: dict) -> dict:
    params["apikey"] = _api_key()
    resp = requests.get(BASE_URL, params=params, timeout=30)
    if not resp.ok:
        _die(f"API {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    if "Note" in data:
        print(f"{YELLOW}API rate limit reached. Try again in a minute.{RESET}")
    if "Error Message" in data:
        _die(f"API Error: {data['Error Message']}")
    return data


def _load_watchlist() -> list:
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_watchlist(data: list):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f)


def quote(ticker: str):
    data = _request({"function": "GLOBAL_QUOTE", "symbol": ticker})
    q = data.get("Global Quote", {})
    if not q or not q.get("01. symbol"):
        _die(f"No data found for ticker '{ticker}'.")

    price  = float(q.get("05. price", 0))
    change = float(q.get("09. change", 0))
    pct    = q.get("10. change percent", "0%")
    open_p = float(q.get("02. open", 0))
    high   = float(q.get("03. high", 0))
    low    = float(q.get("04. low", 0))
    vol    = int(q.get("06. volume", 0))
    prev   = float(q.get("08. previous close", 0))

    color = GREEN if change >= 0 else RED
    arrow = "▲" if change >= 0 else "▼"

    print(f"\n  {BOLD}{CYAN}{ticker.upper()}{RESET}")
    print(f"  Price:   {BOLD}${price:.2f}{RESET}  {color}{arrow} {change:+.2f} ({pct}){RESET}")
    print(f"  Open:    ${open_p:.2f}  |  High: ${high:.2f}  |  Low: ${low:.2f}")
    print(f"  Prev:    ${prev:.2f}  |  Volume: {vol:,}")
    print(f"  As of:   {q.get('07. latest trading day', '')}")
    print()


def chart(ticker: str, days: int = 30):
    data = _request({"function": "TIME_SERIES_DAILY", "symbol": ticker, "outputsize": "compact"})
    ts = data.get("Time Series (Daily)", {})
    if not ts:
        _die(f"No chart data for '{ticker}'.")

    # Get last N days sorted
    dates = sorted(ts.keys(), reverse=True)[:days]
    dates.reverse()
    prices = [float(ts[d]["4. close"]) for d in dates]

    if not prices:
        _die("No price data available.")

    min_p = min(prices)
    max_p = max(prices)
    rng   = max_p - min_p if max_p != min_p else 1

    print(f"\n{BOLD}{ticker.upper()} — Last {len(prices)} Days{RESET}")
    print(f"  High: ${max_p:.2f}  |  Low: ${min_p:.2f}\n")

    height = 10
    for row in range(height, -1, -1):
        threshold = min_p + (rng * row / height)
        line = ""
        for price in prices:
            if price >= threshold:
                line += "█"
            else:
                line += " "
        label = f"${threshold:8.2f} |" if row % 2 == 0 else "          |"
        print(f"  {label}{line}")

    # Date axis
    print(f"  {'─'*12}{'─'*len(prices)}")
    print(f"  {dates[0][:7]}{'':>{len(prices)-7}}{dates[-1][:7]}")
    print()


def earnings(ticker: str):
    data = _request({"function": "EARNINGS", "symbol": ticker})
    quarterly = data.get("quarterlyEarnings", [])[:8]

    if not quarterly:
        _die(f"No earnings data for '{ticker}'.")

    print(f"\n{BOLD}{ticker.upper()} — Quarterly Earnings:{RESET}\n")
    print(f"  {'Fiscal Date':<14} {'EPS Est.':<12} {'EPS Actual':<12} {'Surprise %'}")
    print(f"  {'─'*52}")

    for q in quarterly:
        date     = q.get("fiscalDateEnding", "")[:7]
        est      = q.get("estimatedEPS", "N/A")
        actual   = q.get("reportedEPS", "N/A")
        surprise = q.get("surprisePercentage", "N/A")

        try:
            s = float(surprise)
            color = GREEN if s > 0 else RED
            surp_str = f"{color}{s:+.2f}%{RESET}"
        except (ValueError, TypeError):
            surp_str = "N/A"

        print(f"  {date:<14} {str(est):<12} {str(actual):<12} {surp_str}")
    print()


def search(keywords: str):
    data = _request({"function": "SYMBOL_SEARCH", "keywords": keywords})
    matches = data.get("bestMatches", [])

    if not matches:
        print(f"{YELLOW}No results for '{keywords}'.{RESET}")
        return

    print(f"\n{GREEN}Search results for '{keywords}':{RESET}\n")
    for m in matches[:10]:
        sym   = m.get("1. symbol", "")
        name  = m.get("2. name", "")
        mtype = m.get("3. type", "")
        region = m.get("4. region", "")
        print(f"  {CYAN}{sym:<8}{RESET} {BOLD}{name:<35}{RESET} {mtype}  ({region})")
    print()


def watchlist_cmd(add: str = None, remove: str = None):
    wl = _load_watchlist()

    if add:
        ticker = add.upper()
        if ticker not in wl:
            wl.append(ticker)
            _save_watchlist(wl)
            print(f"{GREEN}Added {ticker} to watchlist.{RESET}")
        else:
            print(f"{YELLOW}{ticker} already in watchlist.{RESET}")
        return

    if remove:
        ticker = remove.upper()
        if ticker in wl:
            wl.remove(ticker)
            _save_watchlist(wl)
            print(f"{GREEN}Removed {ticker} from watchlist.{RESET}")
        else:
            print(f"{YELLOW}{ticker} not in watchlist.{RESET}")
        return

    if not wl:
        print(f"{YELLOW}Watchlist is empty.{RESET}")
        return

    print(f"\n{BOLD}Watchlist ({len(wl)} ticker(s)):{RESET}\n")
    for ticker in wl:
        try:
            data = _request({"function": "GLOBAL_QUOTE", "symbol": ticker})
            q = data.get("Global Quote", {})
            price  = float(q.get("05. price", 0))
            change = float(q.get("09. change", 0))
            pct    = q.get("10. change percent", "0%")
            color  = GREEN if change >= 0 else RED
            print(f"  {CYAN}{ticker:<8}{RESET}  ${price:.2f}  {color}{change:+.2f} ({pct}){RESET}")
        except SystemExit:
            print(f"  {CYAN}{ticker:<8}{RESET}  {RED}error{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="stock_price_fetcher.py",
        description="Stock Price Fetcher — OC-0159"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("quote", help="Get real-time stock quote")
    p.add_argument("--ticker", required=True)

    p = sub.add_parser("chart", help="Show price history chart")
    p.add_argument("--ticker", required=True)
    p.add_argument("--days", type=int, default=30)

    p = sub.add_parser("earnings", help="Get earnings history")
    p.add_argument("--ticker", required=True)

    p = sub.add_parser("search", help="Search for ticker symbol")
    p.add_argument("--keywords", required=True)

    p = sub.add_parser("watchlist", help="Manage stock watchlist")
    p.add_argument("--add", default=None, metavar="TICKER")
    p.add_argument("--remove", default=None, metavar="TICKER")

    args = parser.parse_args()
    dispatch = {
        "quote":     lambda: quote(args.ticker),
        "chart":     lambda: chart(args.ticker, args.days),
        "earnings":  lambda: earnings(args.ticker),
        "search":    lambda: search(args.keywords),
        "watchlist": lambda: watchlist_cmd(
            getattr(args, "add", None),
            getattr(args, "remove", None)
        ),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
