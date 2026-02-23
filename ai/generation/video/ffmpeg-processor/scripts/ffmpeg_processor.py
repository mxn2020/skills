#!/usr/bin/env python3
"""FFmpeg Processor – OC-0098"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _run(cmd, check=True):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result
    except FileNotFoundError:
        print(f"{RED}Error: command not found: {cmd[0]}. Please install ffmpeg.{RESET}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed:{RESET} {' '.join(cmd)}")
        print(e.stderr)
        sys.exit(1)


def _check_input(path):
    if not os.path.exists(path):
        print(f"{RED}Error: input file '{path}' not found{RESET}")
        sys.exit(1)


def cut(args):
    _check_input(args.input)
    output = args.output or f"cut_{os.path.basename(args.input)}"
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-ss", args.start,
        "-to", args.end,
        "-c", "copy",
        output,
    ]
    _run(cmd)
    print(f"{GREEN}Saved:{RESET} {output}")


def merge(args):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for inp in args.inputs:
            _check_input(inp)
            abs_path = os.path.abspath(inp)
            f.write(f"file '{abs_path}'\n")
        list_file = f.name
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            args.output,
        ]
        _run(cmd)
        print(f"{GREEN}Saved:{RESET} {args.output}")
    finally:
        os.unlink(list_file)


def transcode(args):
    _check_input(args.input)
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-c:v", args.codec,
        "-crf", str(args.crf),
        "-preset", args.preset,
        "-c:a", "copy",
        args.output,
    ]
    _run(cmd)
    print(f"{GREEN}Saved:{RESET} {args.output}")


def watermark(args):
    _check_input(args.input)
    _check_input(args.watermark)
    output = args.output or f"watermarked_{os.path.basename(args.input)}"

    position_map = {
        "top-left": "10:10",
        "top-right": "main_w-overlay_w-10:10",
        "bottom-left": "10:main_h-overlay_h-10",
        "bottom-right": "main_w-overlay_w-10:main_h-overlay_h-10",
        "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
    }
    pos = position_map.get(args.position, "main_w-overlay_w-10:main_h-overlay_h-10")

    filter_str = f"[1:v]format=rgba,colorchannelmixer=aa={args.opacity}[wm];[0:v][wm]overlay={pos}"
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-i", args.watermark,
        "-filter_complex", filter_str,
        "-c:a", "copy",
        output,
    ]
    _run(cmd)
    print(f"{GREEN}Saved:{RESET} {output}")


def extract_audio(args):
    _check_input(args.input)
    output = args.output or "audio.mp3"
    format_codec_map = {
        "mp3": "libmp3lame",
        "aac": "aac",
        "wav": "pcm_s16le",
        "flac": "flac",
    }
    codec = format_codec_map.get(args.format, "libmp3lame")
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-vn",
        "-acodec", codec,
        output,
    ]
    _run(cmd)
    print(f"{GREEN}Saved:{RESET} {output}")


def resize(args):
    _check_input(args.input)
    output = args.output or f"resized_{os.path.basename(args.input)}"

    if args.scale:
        vf = f"scale=iw*{args.scale}:ih*{args.scale}"
    elif args.width and args.height:
        vf = f"scale={args.width}:{args.height}"
    elif args.width:
        vf = f"scale={args.width}:-2"
    elif args.height:
        vf = f"scale=-2:{args.height}"
    else:
        print(f"{RED}Error: specify --width, --height, or --scale{RESET}")
        sys.exit(1)

    cmd = ["ffmpeg", "-y", "-i", args.input, "-vf", vf, "-c:a", "copy", output]
    _run(cmd)
    print(f"{GREEN}Saved:{RESET} {output}")


def info(args):
    _check_input(args.input)
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        args.input,
    ]
    result = _run(cmd)
    data = json.loads(result.stdout)

    fmt = data.get("format", {})
    print(f"{GREEN}Format:{RESET} {fmt.get('format_long_name', 'n/a')}")
    print(f"  Duration: {float(fmt.get('duration', 0)):.2f}s")
    print(f"  Size:     {int(fmt.get('size', 0)) // 1024} KB")
    print(f"  Bitrate:  {int(fmt.get('bit_rate', 0)) // 1000} kbps")

    for stream in data.get("streams", []):
        codec_type = stream.get("codec_type", "unknown")
        codec_name = stream.get("codec_name", "n/a")
        if codec_type == "video":
            w = stream.get("width", "?")
            h = stream.get("height", "?")
            fps = stream.get("r_frame_rate", "?")
            print(f"{GREEN}Video:{RESET} {codec_name} {w}x{h} @ {fps} fps")
        elif codec_type == "audio":
            sr = stream.get("sample_rate", "?")
            ch = stream.get("channels", "?")
            print(f"{GREEN}Audio:{RESET} {codec_name} {sr}Hz {ch}ch")


def main():
    parser = argparse.ArgumentParser(description="FFmpeg Processor – OC-0098")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cut = sub.add_parser("cut", help="Cut a clip from a video")
    p_cut.add_argument("--input", required=True)
    p_cut.add_argument("--start", required=True, help="Start time HH:MM:SS")
    p_cut.add_argument("--end", required=True, help="End time HH:MM:SS")
    p_cut.add_argument("--output", default=None)

    p_merge = sub.add_parser("merge", help="Concatenate multiple videos")
    p_merge.add_argument("--inputs", required=True, nargs="+")
    p_merge.add_argument("--output", required=True)

    p_transcode = sub.add_parser("transcode", help="Re-encode a video with a different codec")
    p_transcode.add_argument("--input", required=True)
    p_transcode.add_argument("--output", required=True)
    p_transcode.add_argument("--codec", default="libx264", choices=["libx264", "libx265", "vp9", "av1"])
    p_transcode.add_argument("--crf", type=int, default=23)
    p_transcode.add_argument("--preset", default="medium", choices=["ultrafast", "fast", "medium", "slow"])

    p_wm = sub.add_parser("watermark", help="Overlay an image watermark onto a video")
    p_wm.add_argument("--input", required=True)
    p_wm.add_argument("--watermark", required=True)
    p_wm.add_argument("--position", default="bottom-right",
                      choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"])
    p_wm.add_argument("--opacity", type=float, default=0.7)
    p_wm.add_argument("--output", default=None)

    p_audio = sub.add_parser("extract-audio", help="Extract audio from a video")
    p_audio.add_argument("--input", required=True)
    p_audio.add_argument("--output", default="audio.mp3")
    p_audio.add_argument("--format", default="mp3", choices=["mp3", "aac", "wav", "flac"])

    p_resize = sub.add_parser("resize", help="Resize video dimensions")
    p_resize.add_argument("--input", required=True)
    p_resize.add_argument("--width", type=int, default=None)
    p_resize.add_argument("--height", type=int, default=None)
    p_resize.add_argument("--scale", type=float, default=None, help="Scale factor e.g. 0.5")
    p_resize.add_argument("--output", default=None)

    p_info = sub.add_parser("info", help="Show video metadata")
    p_info.add_argument("--input", required=True)

    args = parser.parse_args()
    commands = {
        "cut": cut,
        "merge": merge,
        "transcode": transcode,
        "watermark": watermark,
        "extract-audio": extract_audio,
        "resize": resize,
        "info": info,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
