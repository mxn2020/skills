#!/usr/bin/env python3
"""
Crypto Wallet Watcher — OC-0158
Monitor crypto addresses for incoming/outgoing transactions.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

WATCHLIST_FILE = os.path.expanduser("~/.crypto_watchlist.json")

# Free APIs
ETH_API = "https://api.etherscan.io/api"
BTC_API = "https://api.blockcypher.com/v1/btc/main/addrs"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_watchlist() -> dict:
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"addresses": []}


def _save_watchlist(data: dict):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)


def balance(address: str, chain: str = "eth"):
    chain = chain.lower()
    print(f"{YELLOW}Fetching balance for {chain.upper()} address: {address[:20]}...{RESET}")

    if chain == "eth":
        # Etherscan (no API key needed for basic queries)
        resp = requests.get(ETH_API, params={
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        }, timeout=30)
        if resp.ok:
            data = resp.json()
            if data.get("status") == "1":
                wei = int(data.get("result", 0))
                eth_val = wei / 1e18
                print(f"\n  {GREEN}{eth_val:.6f} ETH{RESET}  ({address[:20]}...)")
            else:
                _die(f"Etherscan error: {data.get('message', 'unknown')}")
        else:
            _die(f"Etherscan API error: {resp.status_code}")

    elif chain == "btc":
        resp = requests.get(
            f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance",
            timeout=30,
        )
        if resp.ok:
            data = resp.json()
            satoshi = data.get("balance", 0)
            btc_val = satoshi / 1e8
            unconf  = data.get("unconfirmed_balance", 0) / 1e8
            print(f"\n  {GREEN}{btc_val:.8f} BTC{RESET}  "
                  f"(unconfirmed: {unconf:.8f})  ({address[:20]}...)")
        else:
            _die(f"BlockCypher API error: {resp.status_code}")

    elif chain in ("sol", "solana"):
        resp = requests.post(
            "https://api.mainnet-beta.solana.com",
            json={"jsonrpc": "2.0", "id": 1, "method": "getBalance",
                  "params": [address]},
            timeout=30,
        )
        if resp.ok:
            lamports = resp.json().get("result", {}).get("value", 0)
            sol_val = lamports / 1e9
            print(f"\n  {GREEN}{sol_val:.6f} SOL{RESET}  ({address[:20]}...)")
        else:
            _die(f"Solana RPC error: {resp.status_code}")
    else:
        _die(f"Unsupported chain: {chain}. Supported: eth, btc, sol")
    print()


def transactions(address: str, chain: str = "eth", limit: int = 10):
    chain = chain.lower()
    print(f"{YELLOW}Fetching {chain.upper()} transactions for {address[:20]}...{RESET}")

    if chain == "eth":
        resp = requests.get(ETH_API, params={
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
        }, timeout=30)
        if not resp.ok:
            _die(f"Etherscan API error: {resp.status_code}")
        data = resp.json()
        txs = data.get("result", [])
        if isinstance(txs, str):
            print(f"{YELLOW}No transactions found or API limit reached.{RESET}")
            return

        print(f"\n{GREEN}Last {min(len(txs), limit)} ETH transaction(s):{RESET}\n")
        for tx in txs[:limit]:
            ts    = datetime.fromtimestamp(int(tx.get("timeStamp", 0)),
                                           tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
            value = int(tx.get("value", 0)) / 1e18
            frm   = tx.get("from", "")[:12]
            to    = tx.get("to", "")[:12]
            txh   = tx.get("hash", "")[:16]
            direction = GREEN if tx.get("to", "").lower() == address.lower() else RED
            arrow = f"{direction}↓ IN{RESET}" if tx.get("to", "").lower() == address.lower() \
                    else f"{direction}↑ OUT{RESET}"
            print(f"  {CYAN}{txh}...{RESET}  {arrow}  {BOLD}{value:.6f} ETH{RESET}  {ts}")
            print(f"    {frm}... → {to}...")

    elif chain == "btc":
        resp = requests.get(
            f"https://api.blockcypher.com/v1/btc/main/addrs/{address}",
            params={"limit": limit},
            timeout=30,
        )
        if not resp.ok:
            _die(f"BlockCypher error: {resp.status_code}")
        data = resp.json()
        txs = data.get("txrefs", [])
        print(f"\n{GREEN}Last {min(len(txs), limit)} BTC transaction(s):{RESET}\n")
        for tx in txs[:limit]:
            sat   = tx.get("value", 0)
            btc   = sat / 1e8
            txh   = tx.get("tx_hash", "")[:16]
            conf  = tx.get("confirmations", 0)
            spent = tx.get("spent", False)
            arrow = f"{RED}↑ OUT{RESET}" if spent else f"{GREEN}↓ IN{RESET}"
            print(f"  {CYAN}{txh}...{RESET}  {arrow}  {BOLD}{btc:.8f} BTC{RESET}  "
                  f"({conf} conf)")
    else:
        _die(f"Unsupported chain for transactions: {chain}")
    print()


def watch_address(add: bool, address: str, label: str = "", chain: str = "eth"):
    wl = _load_watchlist()
    addresses = wl.get("addresses", [])

    if add:
        existing = [a for a in addresses if a.get("address") == address]
        if existing:
            print(f"{YELLOW}Address already in watchlist.{RESET}")
            return
        addresses.append({
            "address": address,
            "label": label or address[:12],
            "chain": chain,
            "added": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "last_tx": None,
        })
        wl["addresses"] = addresses
        _save_watchlist(wl)
        print(f"{GREEN}Added to watchlist: {label or address[:20]} ({chain.upper()}){RESET}")
    else:
        before = len(addresses)
        addresses = [a for a in addresses if a.get("address") != address]
        if len(addresses) == before:
            print(f"{YELLOW}Address not found in watchlist.{RESET}")
            return
        wl["addresses"] = addresses
        _save_watchlist(wl)
        print(f"{GREEN}Removed from watchlist: {address[:20]}{RESET}")

    print(f"  Watchlist size: {len(addresses)} address(es)")
    print()


def alerts():
    wl = _load_watchlist()
    addresses = wl.get("addresses", [])
    if not addresses:
        print(f"{YELLOW}No addresses in watchlist. Add some with: watch --add{RESET}")
        return

    print(f"{YELLOW}Checking {len(addresses)} watched address(es)...{RESET}\n")
    for entry in addresses:
        addr  = entry.get("address", "")
        label = entry.get("label", addr[:12])
        chain = entry.get("chain", "eth")
        print(f"  {CYAN}{label}{RESET}  ({chain.upper()})  {addr[:20]}...")
        try:
            balance(addr, chain)
        except SystemExit:
            print(f"    {RED}Could not check balance.{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="crypto_wallet_watcher.py",
        description="Crypto Wallet Watcher — OC-0158"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("balance", help="Get wallet balance")
    p.add_argument("--address", required=True)
    p.add_argument("--chain", default="eth", choices=["eth", "btc", "sol"])

    p = sub.add_parser("transactions", help="List recent transactions")
    p.add_argument("--address", required=True)
    p.add_argument("--chain", default="eth", choices=["eth", "btc"])
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("watch", help="Manage watchlist")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", action="store_true")
    group.add_argument("--remove", action="store_true")
    p.add_argument("--address", required=True)
    p.add_argument("--label", default="")
    p.add_argument("--chain", default="eth")

    sub.add_parser("alerts", help="Check watched addresses for new activity")

    args = parser.parse_args()

    if args.cmd == "watch":
        watch_address(args.add, args.address, args.label,
                      getattr(args, "chain", "eth"))
    else:
        dispatch = {
            "balance":      lambda: balance(args.address, args.chain),
            "transactions": lambda: transactions(args.address, args.chain, args.limit),
            "alerts":       lambda: alerts(),
        }
        dispatch[args.cmd]()


if __name__ == "__main__":
    main()
