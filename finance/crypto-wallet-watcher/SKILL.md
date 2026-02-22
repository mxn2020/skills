---
name: crypto-wallet-watcher
id: OC-0158
version: 1.0.0
description: "Crypto Wallet Watcher - Monitor addresses for incoming/outgoing transactions"
env: []
commands:
  - watch
  - balance
  - transactions
  - alerts
---

# Crypto Wallet Watcher

Monitor crypto wallet addresses for incoming/outgoing transactions. Supports Bitcoin, Ethereum, and other major chains via public APIs.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)

## Commands

| Command | Description |
|---------|-------------|
| `balance` | Get wallet balance |
| `transactions` | List recent transactions |
| `watch` | Add/remove addresses to watchlist |
| `alerts` | Check for new transactions on watched addresses |

## Usage

```bash
# Check ETH wallet balance
python3 scripts/crypto_wallet_watcher.py balance --address "0x..." --chain eth

# Check BTC wallet balance
python3 scripts/crypto_wallet_watcher.py balance --address "bc1q..." --chain btc

# List recent transactions
python3 scripts/crypto_wallet_watcher.py transactions --address "0x..." --chain eth --limit 10

# Add to watchlist
python3 scripts/crypto_wallet_watcher.py watch --add --address "0x..." --label "My ETH Wallet"

# Check for new activity on watched addresses
python3 scripts/crypto_wallet_watcher.py alerts
```
