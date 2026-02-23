#!/usr/bin/env python3
"""Mux Video Uploader – OC-0066"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.mux.com"


def _auth():
    token_id = os.environ.get("MUX_TOKEN_ID")
    token_secret = os.environ.get("MUX_TOKEN_SECRET")
    if not token_id or not token_secret:
        print(f"{RED}Error: MUX_TOKEN_ID and MUX_TOKEN_SECRET must be set{RESET}")
        sys.exit(1)
    return (token_id, token_secret)


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(
        f"{BASE_URL}{path}", auth=_auth(),
        headers={"Content-Type": "application/json"}, **kwargs,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def create_asset(args):
    payload = {
        "input": [{"url": args.url}],
        "playback_policy": [args.playback_policy],
    }
    data = _request("post", "/video/v1/assets", json=payload)
    asset = data.get("data", {})
    print(f"{GREEN}Created asset {asset.get('id', 'n/a')}{RESET}")
    print(f"  Status:   {asset.get('status', 'n/a')}")
    pbs = asset.get("playback_ids", [])
    if pbs:
        print(f"  Playback: {pbs[0].get('id', 'n/a')} ({pbs[0].get('policy', '')})")


def list_assets(args):
    params = {"limit": args.limit, "page": args.page}
    data = _request("get", "/video/v1/assets", params=params)
    assets = data.get("data", [])
    print(f"{GREEN}Assets (page {args.page}){RESET}")
    for a in assets:
        status = a.get("status", "unknown")
        color = GREEN if status == "ready" else YELLOW
        duration = a.get("duration", 0)
        print(f"  {color}[{status}]{RESET} {a['id']}  duration={duration:.1f}s")


def get_asset(args):
    data = _request("get", f"/video/v1/assets/{args.asset_id}")
    asset = data.get("data", {})
    print(f"{GREEN}Asset {asset.get('id', 'n/a')}{RESET}")
    print(f"  Status:     {asset.get('status', 'n/a')}")
    print(f"  Duration:   {asset.get('duration', 0):.1f}s")
    print(f"  Resolution: {asset.get('resolution_tier', 'n/a')}")
    print(f"  Created:    {asset.get('created_at', 'n/a')}")
    for pb in asset.get("playback_ids", []):
        print(f"  Playback:   {pb.get('id', 'n/a')} ({pb.get('policy', '')})")
    for track in asset.get("tracks", []):
        print(f"  Track:      {track.get('type', '?')} – {track.get('max_width', '')}x{track.get('max_height', '')}")


def delete_asset(args):
    _request("delete", f"/video/v1/assets/{args.asset_id}")
    print(f"{GREEN}Deleted asset {args.asset_id}{RESET}")


def create_upload(args):
    payload = {
        "cors_origin": args.cors_origin,
        "new_asset_settings": {"playback_policy": [args.playback_policy]},
    }
    if args.timeout:
        payload["timeout"] = args.timeout
    data = _request("post", "/video/v1/uploads", json=payload)
    upload = data.get("data", {})
    print(f"{GREEN}Upload created{RESET}")
    print(f"  Upload ID: {upload.get('id', 'n/a')}")
    print(f"  URL:       {upload.get('url', 'n/a')}")
    print(f"  Timeout:   {upload.get('timeout', 'n/a')}s")


def get_playback(args):
    data = _request("get", f"/video/v1/assets/{args.asset_id}")
    asset = data.get("data", {})
    pbs = asset.get("playback_ids", [])
    if not pbs:
        print(f"{YELLOW}No playback IDs for asset {args.asset_id}{RESET}")
        return
    print(f"{GREEN}Playback IDs for asset {args.asset_id}{RESET}")
    for pb in pbs:
        pid = pb.get("id", "n/a")
        policy = pb.get("policy", "n/a")
        print(f"  {YELLOW}{pid}{RESET}  policy={policy}")
        print(f"  HLS: https://stream.mux.com/{pid}.m3u8")


def main():
    parser = argparse.ArgumentParser(description="Mux Video Uploader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create-asset", help="Create asset from video URL")
    p_create.add_argument("--url", required=True, help="Video source URL")
    p_create.add_argument("--playback-policy", default="public", choices=["public", "signed"])

    p_list = sub.add_parser("list-assets", help="List video assets")
    p_list.add_argument("--limit", type=int, default=25)
    p_list.add_argument("--page", type=int, default=1)

    p_get = sub.add_parser("get-asset", help="Get asset details")
    p_get.add_argument("--asset-id", required=True)

    p_del = sub.add_parser("delete-asset", help="Delete a video asset")
    p_del.add_argument("--asset-id", required=True)

    p_upload = sub.add_parser("create-upload", help="Create a direct upload URL")
    p_upload.add_argument("--cors-origin", default="*", help="Allowed CORS origin")
    p_upload.add_argument("--playback-policy", default="public", choices=["public", "signed"])
    p_upload.add_argument("--timeout", type=int, help="Upload timeout in seconds")

    p_pb = sub.add_parser("get-playback", help="Get playback info for an asset")
    p_pb.add_argument("--asset-id", required=True)

    args = parser.parse_args()
    commands = {
        "create-asset": create_asset,
        "list-assets": list_assets,
        "get-asset": get_asset,
        "delete-asset": delete_asset,
        "create-upload": create_upload,
        "get-playback": get_playback,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
