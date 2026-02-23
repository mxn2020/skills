#!/usr/bin/env python3
"""
API Response Mocker — OC-0180
Intercept outgoing API calls and return fixture data for offline testing.
"""

import os
import sys
import json
import argparse
import threading
import http.server
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

FIXTURES_FILE = os.path.expanduser("~/.api_mock_fixtures.json")
CALLS_LOG     = os.path.expanduser("~/.api_mock_calls.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_fixtures() -> dict:
    if os.path.exists(FIXTURES_FILE):
        try:
            with open(FIXTURES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_fixtures(data: dict):
    with open(FIXTURES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _load_calls() -> list:
    if os.path.exists(CALLS_LOG):
        try:
            with open(CALLS_LOG) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_calls(data: list):
    with open(CALLS_LOG, "w") as f:
        json.dump(data, f, indent=2)


class MockHandler(http.server.BaseHTTPRequestHandler):
    def _handle(self):
        fixtures = _load_fixtures()
        key = f"{self.command}:{self.path}"
        # Also try path without query string
        path_no_qs = self.path.split("?")[0]
        key_noqs = f"{self.command}:{path_no_qs}"

        # Log the call
        calls = _load_calls()
        calls.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
        })
        _save_calls(calls)

        fixture = fixtures.get(key) or fixtures.get(key_noqs)
        if fixture:
            status = fixture.get("status", 200)
            body   = json.dumps(fixture.get("response", {}))
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "No fixture found",
                "path": self.path,
                "method": self.command,
            }).encode())

    def do_GET(self):    self._handle()
    def do_POST(self):   self._handle()
    def do_PUT(self):    self._handle()
    def do_DELETE(self): self._handle()
    def do_PATCH(self):  self._handle()

    def log_message(self, format, *args):
        pass  # Suppress default logging


def start(port: int = 8765):
    print(f"{GREEN}Starting mock API server on port {port}...{RESET}")
    print(f"  Fixtures file: {FIXTURES_FILE}")
    print(f"  Calls log:     {CALLS_LOG}")

    fixtures = _load_fixtures()
    if fixtures:
        print(f"  Loaded {len(fixtures)} fixture(s)")

    print(f"\n{CYAN}Mock server running at http://localhost:{port}{RESET}")
    print(f"  Press Ctrl+C to stop\n")

    server = http.server.HTTPServer(("", port), MockHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server stopped.{RESET}")


def add_fixture(path: str, method: str = "GET", response_str: str = "{}",
                status: int = 200):
    try:
        response = json.loads(response_str)
    except json.JSONDecodeError:
        _die(f"Invalid JSON response: {response_str[:100]}")

    fixtures = _load_fixtures()
    key = f"{method.upper()}:{path}"
    fixtures[key] = {"status": status, "response": response}
    _save_fixtures(fixtures)

    print(f"{GREEN}Fixture added:{RESET}")
    print(f"  {method.upper()} {path} → {status}")
    print(f"  Response: {json.dumps(response)[:80]}")
    print()


def list_fixtures():
    fixtures = _load_fixtures()
    if not fixtures:
        print(f"{YELLOW}No fixtures configured.{RESET}")
        return

    print(f"\n{BOLD}Configured Fixtures ({len(fixtures)}):{RESET}\n")
    for key, fixture in fixtures.items():
        method, _, path = key.partition(":")
        status   = fixture.get("status", 200)
        response = json.dumps(fixture.get("response", {}))[:60]
        color    = GREEN if 200 <= status < 300 else (YELLOW if status < 400 else RED)
        print(f"  {CYAN}{method:<7}{RESET} {path}")
        print(f"    Status: {color}{status}{RESET}  |  Response: {response}")
    print()


def remove_fixture(path: str, method: str = "GET"):
    fixtures = _load_fixtures()
    key = f"{method.upper()}:{path}"
    if key not in fixtures:
        _die(f"Fixture not found: {method.upper()} {path}")
    del fixtures[key]
    _save_fixtures(fixtures)
    print(f"{GREEN}Fixture removed: {method.upper()} {path}{RESET}")


def verify_calls(clear: bool = False):
    calls = _load_calls()
    if not calls:
        print(f"{YELLOW}No API calls logged yet.{RESET}")
        return

    print(f"\n{BOLD}API Calls Log ({len(calls)} total):{RESET}\n")
    for call in calls[-20:]:
        ts     = call.get("timestamp", "")[:19]
        method = call.get("method", "GET")
        path   = call.get("path", "")
        print(f"  {CYAN}{ts}{RESET}  {BOLD}{method:<7}{RESET} {path}")

    if clear:
        _save_calls([])
        print(f"\n{GREEN}Call log cleared.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="api_response_mocker.py",
        description="API Response Mocker — OC-0180"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start", help="Start mock server")
    p.add_argument("--port", type=int, default=8765)

    p = sub.add_parser("add-fixture", help="Add a mock response")
    p.add_argument("--path", required=True)
    p.add_argument("--method", default="GET")
    p.add_argument("--response", required=True, help="JSON response body")
    p.add_argument("--status", type=int, default=200)

    sub.add_parser("list-fixtures", help="List fixtures")

    p = sub.add_parser("remove-fixture", help="Remove a fixture")
    p.add_argument("--path", required=True)
    p.add_argument("--method", default="GET")

    p = sub.add_parser("verify-calls", help="Show logged API calls")
    p.add_argument("--clear", action="store_true", help="Clear log after showing")

    args = parser.parse_args()
    dispatch = {
        "start":          lambda: start(args.port),
        "add-fixture":    lambda: add_fixture(args.path, args.method,
                                               args.response, args.status),
        "list-fixtures":  lambda: list_fixtures(),
        "remove-fixture": lambda: remove_fixture(args.path, args.method),
        "verify-calls":   lambda: verify_calls(args.clear),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
