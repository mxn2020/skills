#!/usr/bin/env python3
"""Twilio SMS & WhatsApp – OC-0076"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.twilio.com/2010-04-01"


def _account_sid():
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    if not sid:
        print(f"{RED}Error: TWILIO_ACCOUNT_SID is not set{RESET}")
        sys.exit(1)
    return sid


def _auth():
    sid = _account_sid()
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not token:
        print(f"{RED}Error: TWILIO_AUTH_TOKEN is not set{RESET}")
        sys.exit(1)
    return (sid, token)


def _from_number():
    number = os.environ.get("TWILIO_PHONE_NUMBER")
    if not number:
        print(f"{RED}Error: TWILIO_PHONE_NUMBER is not set{RESET}")
        sys.exit(1)
    return number


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", auth=_auth(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def send_sms(args):
    sid = _account_sid()
    payload = {"To": args.to, "From": args.from_number or _from_number(), "Body": args.body}
    data = _request("post", f"/Accounts/{sid}/Messages.json", data=payload)
    print(f"{GREEN}SMS sent{RESET}  sid={data['sid']}  to={data['to']}  status={data['status']}")


def send_whatsapp(args):
    sid = _account_sid()
    to_number = f"whatsapp:{args.to}" if not args.to.startswith("whatsapp:") else args.to
    from_number = args.from_number or _from_number()
    from_number = f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
    payload = {"To": to_number, "From": from_number, "Body": args.body}
    data = _request("post", f"/Accounts/{sid}/Messages.json", data=payload)
    print(f"{GREEN}WhatsApp message sent{RESET}  sid={data['sid']}  to={data['to']}  status={data['status']}")


def list_messages(args):
    sid = _account_sid()
    params = {"PageSize": args.limit}
    data = _request("get", f"/Accounts/{sid}/Messages.json", params=params)
    for msg in data.get("messages", []):
        direction = msg.get("direction", "unknown")
        color = GREEN if direction.startswith("outbound") else YELLOW
        print(
            f"{color}[{direction}]{RESET}  {msg['sid']}  "
            f"from={msg['from']}  to={msg['to']}  "
            f"status={msg['status']}  date={msg.get('date_sent', 'n/a')}"
        )


def get_message(args):
    sid = _account_sid()
    data = _request("get", f"/Accounts/{sid}/Messages/{args.message_sid}.json")
    print(f"{GREEN}Message {data['sid']}{RESET}")
    print(f"  From:      {data.get('from', 'n/a')}")
    print(f"  To:        {data.get('to', 'n/a')}")
    print(f"  Status:    {data.get('status', 'n/a')}")
    print(f"  Direction: {data.get('direction', 'n/a')}")
    print(f"  Body:      {data.get('body', '')}")
    print(f"  Sent:      {data.get('date_sent', 'n/a')}")
    print(f"  Price:     {data.get('price', 'n/a')} {data.get('price_unit', '')}")


def list_phone_numbers(args):
    sid = _account_sid()
    data = _request("get", f"/Accounts/{sid}/IncomingPhoneNumbers.json")
    for num in data.get("incoming_phone_numbers", []):
        capabilities = num.get("capabilities", {})
        caps = ", ".join(k for k, v in capabilities.items() if v)
        print(
            f"{GREEN}{num['phone_number']}{RESET}  "
            f"friendly={num.get('friendly_name', 'n/a')}  "
            f"capabilities=[{caps}]"
        )


def main():
    parser = argparse.ArgumentParser(description="Twilio SMS & WhatsApp")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sms = sub.add_parser("send-sms", help="Send an SMS message")
    p_sms.add_argument("--to", required=True, help="Recipient phone number (E.164)")
    p_sms.add_argument("--body", required=True, help="Message body")
    p_sms.add_argument("--from-number", default=None, help="Override sender number")

    p_wa = sub.add_parser("send-whatsapp", help="Send a WhatsApp message")
    p_wa.add_argument("--to", required=True, help="Recipient phone number (E.164)")
    p_wa.add_argument("--body", required=True, help="Message body")
    p_wa.add_argument("--from-number", default=None, help="Override sender number")

    p_list = sub.add_parser("list-messages", help="List recent messages")
    p_list.add_argument("--limit", type=int, default=20, help="Number of messages")

    p_get = sub.add_parser("get-message", help="Get message details")
    p_get.add_argument("--message-sid", required=True, help="Message SID")

    sub.add_parser("list-phone-numbers", help="List account phone numbers")

    args = parser.parse_args()
    commands = {
        "send-sms": send_sms,
        "send-whatsapp": send_whatsapp,
        "list-messages": list_messages,
        "get-message": get_message,
        "list-phone-numbers": list_phone_numbers,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
