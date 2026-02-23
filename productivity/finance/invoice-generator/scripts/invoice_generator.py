#!/usr/bin/env python3
"""
Invoice Generator — OC-0161
Create and send professional invoices from structured data.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

DATA_FILE = os.path.expanduser("~/.invoices.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_invoices() -> list:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_invoices(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _next_invoice_number(invoices: list) -> str:
    if not invoices:
        return "INV-001"
    nums = []
    for inv in invoices:
        iid = inv.get("id", "")
        try:
            nums.append(int(iid.split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"INV-{(max(nums) + 1):03d}" if nums else "INV-001"


def _parse_items(items_str: str) -> list:
    """Parse 'Description:Qty:UnitPrice,...'"""
    items = []
    for part in items_str.split(","):
        part = part.strip()
        if not part:
            continue
        segments = part.rsplit(":", 2)
        if len(segments) == 3:
            desc, qty_s, price_s = segments
            try:
                qty   = float(qty_s.strip())
                price = float(price_s.strip())
                items.append({"description": desc.strip(), "qty": qty,
                               "unit_price": price, "total": round(qty * price, 2)})
            except ValueError:
                _die(f"Invalid item format: '{part}'. Use 'Description:Qty:UnitPrice'")
        else:
            _die(f"Invalid item format: '{part}'. Use 'Description:Qty:UnitPrice'")
    return items


def _format_invoice_text(inv: dict) -> str:
    lines = []
    sep = "─" * 55
    lines.append(sep)
    lines.append(f"  INVOICE  {inv['id']}")
    lines.append(sep)
    lines.append(f"  Date:     {inv['date']}")
    lines.append(f"  Due:      {inv['due_date']}")
    lines.append(f"  Status:   {inv['status'].upper()}")
    lines.append("")
    lines.append(f"  Bill To:  {inv['client']}")
    if inv.get("client_email"):
        lines.append(f"  Email:    {inv['client_email']}")
    lines.append("")
    lines.append(f"  {'Description':<30} {'Qty':>6} {'Unit':>10} {'Total':>10}")
    lines.append(f"  {'─'*30} {'─'*6} {'─'*10} {'─'*10}")
    for item in inv.get("items", []):
        desc  = item["description"][:30]
        qty   = item["qty"]
        price = item["unit_price"]
        total = item["total"]
        lines.append(f"  {desc:<30} {qty:>6.1f} ${price:>9.2f} ${total:>9.2f}")
    lines.append(f"  {'─'*58}")
    sub = inv.get("subtotal", 0)
    tax = inv.get("tax", 0)
    tot = inv.get("total", 0)
    lines.append(f"  {'Subtotal':>50} ${sub:>9.2f}")
    if tax:
        lines.append(f"  {'Tax':>50} ${tax:>9.2f}")
    lines.append(f"  {BOLD}{'TOTAL':>50} ${tot:>9.2f}{RESET}")
    lines.append(sep)
    if inv.get("notes"):
        lines.append(f"  Notes: {inv['notes']}")
    return "\n".join(lines)


def create(client: str, client_email: str, items_str: str,
           due_days: int = 30, tax_pct: float = 0, notes: str = ""):
    items = _parse_items(items_str)
    if not items:
        _die("No valid items provided.")

    subtotal = sum(i["total"] for i in items)
    tax = round(subtotal * tax_pct / 100, 2)
    total = round(subtotal + tax, 2)

    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    due_date = (datetime.now(timezone.utc) + timedelta(days=due_days)).strftime("%Y-%m-%d")

    invoices = _load_invoices()
    inv_id   = _next_invoice_number(invoices)

    invoice = {
        "id": inv_id,
        "date": today,
        "due_date": due_date,
        "status": "unpaid",
        "client": client,
        "client_email": client_email,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "notes": notes,
    }
    invoices.append(invoice)
    _save_invoices(invoices)

    print(f"\n{GREEN}Invoice created: {BOLD}{inv_id}{RESET}\n")
    print(_format_invoice_text(invoice))
    print()


def list_invoices():
    invoices = _load_invoices()
    if not invoices:
        print(f"{YELLOW}No invoices yet.{RESET}")
        return

    print(f"\n{BOLD}Invoices ({len(invoices)}):{RESET}\n")
    for inv in sorted(invoices, key=lambda i: i.get("date", ""), reverse=True):
        status = inv.get("status", "unpaid")
        color  = GREEN if status == "paid" else (RED if status == "overdue" else YELLOW)
        print(f"  {CYAN}{inv['id']}{RESET}  {inv['date']}  "
              f"{BOLD}{inv['client'][:25]}{RESET}  "
              f"${inv.get('total', 0):.2f}  [{color}{status}{RESET}]")
    print()


def send(invoice_id: str, from_email: str = "invoices@yourdomain.com"):
    invoices = _load_invoices()
    inv = next((i for i in invoices if i.get("id") == invoice_id), None)
    if not inv:
        _die(f"Invoice '{invoice_id}' not found.")

    key = os.environ.get("RESEND_API_KEY", "")
    if not key:
        print(f"{YELLOW}RESEND_API_KEY not set. Printing invoice instead:{RESET}\n")
        print(_format_invoice_text(inv))
        return

    html_body = f"<pre>{_format_invoice_text(inv)}</pre>"
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "from": from_email,
            "to": [inv.get("client_email", "")],
            "subject": f"Invoice {invoice_id} — ${inv.get('total', 0):.2f}",
            "html": html_body,
        },
        timeout=30,
    )
    if resp.ok:
        print(f"{GREEN}Invoice {invoice_id} sent to {inv.get('client_email')}.{RESET}")
    else:
        _die(f"Failed to send: {resp.status_code} {resp.text[:200]}")


def mark_paid(invoice_id: str):
    invoices = _load_invoices()
    for inv in invoices:
        if inv.get("id") == invoice_id:
            inv["status"] = "paid"
            inv["paid_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            _save_invoices(invoices)
            print(f"{GREEN}Invoice {invoice_id} marked as paid.{RESET}")
            return
    _die(f"Invoice '{invoice_id}' not found.")


def main():
    parser = argparse.ArgumentParser(
        prog="invoice_generator.py",
        description="Invoice Generator — OC-0161"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="Create a new invoice")
    p.add_argument("--client", required=True, help="Client name")
    p.add_argument("--client-email", required=True, help="Client email")
    p.add_argument("--items", required=True,
                   help="Items as 'Description:Qty:UnitPrice,...'")
    p.add_argument("--due-days", type=int, default=30)
    p.add_argument("--tax-pct", type=float, default=0, help="Tax percentage")
    p.add_argument("--notes", default="")

    sub.add_parser("list", help="List all invoices")

    p = sub.add_parser("send", help="Email an invoice")
    p.add_argument("--invoice-id", required=True)
    p.add_argument("--from", default="invoices@yourdomain.com", dest="from_email")

    p = sub.add_parser("mark-paid", help="Mark invoice as paid")
    p.add_argument("--invoice-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "create":    lambda: create(args.client, args.client_email, args.items,
                                    args.due_days, args.tax_pct, args.notes),
        "list":      lambda: list_invoices(),
        "send":      lambda: send(args.invoice_id, args.from_email),
        "mark-paid": lambda: mark_paid(args.invoice_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
