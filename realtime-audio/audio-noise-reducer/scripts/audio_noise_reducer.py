#!/usr/bin/env python3
"""Audio Noise Reducer – OC-0112"""

import argparse
import os
import sys
import glob
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PROFILES = {
    "low":    {"prop_decrease": 0.5,  "stationary": True},
    "medium": {"prop_decrease": 0.75, "stationary": True},
    "high":   {"prop_decrease": 1.0,  "stationary": False},
}


def _reduce_with_noisereduce(input_path, output_path, strength):
    try:
        import noisereduce as nr
        import soundfile as sf
        import numpy as np
    except ImportError:
        return False
    data, rate = sf.read(input_path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    profile = PROFILES[strength]
    reduced = nr.reduce_noise(y=data, sr=rate, **profile)
    sf.write(output_path, reduced, rate)
    return True


def _reduce_with_ffmpeg(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", "afftdn=nf=-25",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def reduce_noise(args):
    print(f"{YELLOW}Reducing noise: {args.input} -> {args.output} (strength={args.strength}){RESET}")
    if _reduce_with_noisereduce(args.input, args.output, args.strength):
        print(f"{GREEN}Done (noisereduce): {args.output}{RESET}")
    elif _reduce_with_ffmpeg(args.input, args.output):
        print(f"{GREEN}Done (ffmpeg fallback): {args.output}{RESET}")
    else:
        print(f"{RED}Error: neither noisereduce nor ffmpeg is available. "
              f"Install with: pip install noisereduce soundfile numpy{RESET}")
        sys.exit(1)


def batch_reduce(args):
    patterns = ["*.wav", "*.mp3", "*.m4a", "*.ogg"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(args.dir, p)))
    if not files:
        print(f"{YELLOW}No audio files found in {args.dir}{RESET}")
        return
    os.makedirs(args.output_dir, exist_ok=True)
    for f in files:
        name = os.path.basename(f)
        out = os.path.join(args.output_dir, name)
        print(f"{YELLOW}Processing {name} ...{RESET}")
        if _reduce_with_noisereduce(f, out, args.strength) or _reduce_with_ffmpeg(f, out):
            print(f"  {GREEN}OK{RESET} -> {out}")
        else:
            print(f"  {RED}FAILED{RESET}")


def measure_snr(args):
    try:
        import soundfile as sf
        import numpy as np
    except ImportError:
        print(f"{RED}Error: pip install soundfile numpy{RESET}")
        sys.exit(1)
    data, rate = sf.read(args.file)
    if data.ndim > 1:
        data = data.mean(axis=1)
    # Estimate noise from first 0.5s, signal from rest
    noise_samples = int(0.5 * rate)
    noise_power = np.mean(data[:noise_samples] ** 2) + 1e-10
    signal_power = np.mean(data[noise_samples:] ** 2) + 1e-10
    snr_db = 10 * np.log10(signal_power / noise_power)
    color = GREEN if snr_db > 20 else YELLOW if snr_db > 10 else RED
    print(f"SNR estimate: {color}{snr_db:.1f} dB{RESET}")
    if snr_db < 10:
        print(f"{YELLOW}Low SNR — noise reduction recommended{RESET}")


def list_profiles(args):
    print(f"{GREEN}Available noise reduction profiles:{RESET}")
    for name, params in PROFILES.items():
        print(f"  {name:8s}  prop_decrease={params['prop_decrease']}  stationary={params['stationary']}")


def main():
    parser = argparse.ArgumentParser(description="Audio Noise Reducer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("reduce-noise")
    p_r.add_argument("--input", required=True)
    p_r.add_argument("--output", required=True)
    p_r.add_argument("--strength", choices=["low", "medium", "high"], default="medium")

    p_b = sub.add_parser("batch-reduce")
    p_b.add_argument("--dir", required=True)
    p_b.add_argument("--output-dir", required=True)
    p_b.add_argument("--strength", choices=["low", "medium", "high"], default="medium")

    p_s = sub.add_parser("measure-snr")
    p_s.add_argument("--file", required=True)

    sub.add_parser("list-profiles")

    args = parser.parse_args()
    dispatch = {
        "reduce-noise": reduce_noise,
        "batch-reduce": batch_reduce,
        "measure-snr": measure_snr,
        "list-profiles": list_profiles,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
