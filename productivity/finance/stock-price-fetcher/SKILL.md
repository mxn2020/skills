---
name: stock-price-fetcher
id: OC-0159
version: 1.0.0
description: "Stock Price Fetcher - Get real-time quotes, charts, and earnings data"
env:
  - ALPHA_VANTAGE_KEY
commands:
  - quote
  - chart
  - earnings
  - search
  - watchlist
---

# Stock Price Fetcher

Get real-time stock quotes, price history, earnings data, and manage a personal watchlist using Alpha Vantage API.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `ALPHA_VANTAGE_KEY` — free API key from alphavantage.co

## Commands

| Command | Description |
|---------|-------------|
| `quote` | Get real-time quote for a ticker |
| `chart` | Show price history as ASCII chart |
| `earnings` | Get earnings history |
| `search` | Search for ticker symbols |
| `watchlist` | Manage and display watchlist |

## Usage

```bash
export ALPHA_VANTAGE_KEY="your_key"

# Get quote
python3 scripts/stock_price_fetcher.py quote --ticker AAPL

# Show price chart (last 30 days)
python3 scripts/stock_price_fetcher.py chart --ticker TSLA --days 30

# Get earnings history
python3 scripts/stock_price_fetcher.py earnings --ticker MSFT

# Search for ticker
python3 scripts/stock_price_fetcher.py search --keywords "Tesla"

# View/manage watchlist
python3 scripts/stock_price_fetcher.py watchlist --add NVDA
python3 scripts/stock_price_fetcher.py watchlist
```
