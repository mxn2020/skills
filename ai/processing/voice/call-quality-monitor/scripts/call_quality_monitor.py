#!/usr/bin/env python3
"""Call Quality Monitor – OC-0114"""

import argparse
import json
import os
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _load_audio(file_path):
    try:
        import soundfile as sf
        import numpy as np
        data, rate = sf.read(file_path)
        if data.ndim > 1:
            data = data.mean(axis=1)
        return data, rate, np
    except ImportError:
        print(f"{RED}Error: pip install soundfile numpy{RESET}")
        sys.exit(1)


def _estimate_mos(snr_db, packet_loss_pct=0.0):
    # ITU-T G.107 simplified R-factor → MOS
    r = 93.2 - max(0, 15 - snr_db) - (30 * packet_loss_pct / 100)
    r = max(0, min(100, r))
    if r >= 90: mos = 4.5
    elif r >= 80: mos = 4.0
    elif r >= 70: mos = 3.5
    elif r >= 60: mos = 3.0
    else: mos = max(1.0, r / 20)
    return round(mos, 2)


def analyze_audio(args):
    data, rate, np = _load_audio(args.file)
    noise_samples = min(int(0.5 * rate), len(data) // 4)
    noise_power = np.mean(data[:noise_samples] ** 2) + 1e-10
    signal_power = np.mean(data ** 2) + 1e-10
    snr = 10 * np.log10(signal_power / noise_power)
    mos = _estimate_mos(snr)
    color = GREEN if mos >= 4.0 else YELLOW if mos >= 3.0 else RED
    print(f"{GREEN}Audio Quality Analysis{RESET}")
    print(f"  File      : {args.file}")
    print(f"  Duration  : {len(data)/rate:.1f}s")
    print(f"  Sample rate: {rate} Hz")
    print(f"  Est. SNR  : {snr:.1f} dB")
    print(f"  Est. MOS  : {color}{mos:.2f} / 5.0{RESET}  ({'Excellent' if mos>=4.3 else 'Good' if mos>=4.0 else 'Fair' if mos>=3.0 else 'Poor'})")


def measure_latency(args):
    data, rate, np = _load_audio(args.file)
    frame_size = int(0.02 * rate)  # 20ms frames
    energies = []
    for i in range(0, len(data) - frame_size, frame_size):
        frame = data[i:i + frame_size]
        energies.append(np.sqrt(np.mean(frame ** 2)))
    threshold = np.percentile(energies, 20)
    silent_frames = sum(1 for e in energies if e < threshold)
    silence_pct = 100 * silent_frames / len(energies)
    print(f"{GREEN}Latency / Gap Analysis{RESET}")
    print(f"  Total frames : {len(energies)}")
    print(f"  Silent frames: {silent_frames} ({silence_pct:.1f}%)")
    if silence_pct > 30:
        print(f"  {YELLOW}High silence ratio — possible network gaps or hold time{RESET}")
    else:
        print(f"  {GREEN}Silence ratio within normal range{RESET}")


def detect_jitter(args):
    data, rate, np = _load_audio(args.file)
    frame_size = int(0.02 * rate)
    energies = [np.sqrt(np.mean(data[i:i+frame_size]**2))
                for i in range(0, len(data)-frame_size, frame_size)]
    diffs = np.abs(np.diff(energies))
    mean_jitter_ms = np.mean(diffs) * 1000
    max_jitter_ms = np.max(diffs) * 1000
    threshold = args.threshold
    color = GREEN if mean_jitter_ms < threshold else YELLOW if mean_jitter_ms < threshold * 2 else RED
    print(f"{GREEN}Jitter Analysis{RESET}")
    print(f"  Mean jitter : {color}{mean_jitter_ms:.1f} ms{RESET}")
    print(f"  Max jitter  : {max_jitter_ms:.1f} ms")
    print(f"  Threshold   : {threshold} ms")
    if mean_jitter_ms > threshold:
        print(f"  {RED}Jitter exceeds threshold — audio quality may be affected{RESET}")


def generate_report(args):
    data, rate, np = _load_audio(args.file)
    noise_power = np.mean(data[:int(0.5*rate)]**2) + 1e-10
    snr = 10 * np.log10(np.mean(data**2) / noise_power)
    mos = _estimate_mos(snr)
    frame_size = int(0.02 * rate)
    energies = [np.sqrt(np.mean(data[i:i+frame_size]**2))
                for i in range(0, len(data)-frame_size, frame_size)]
    silence_pct = 100 * sum(1 for e in energies if e < np.percentile(energies, 20)) / len(energies)
    report = {
        "file": args.file,
        "duration_s": round(len(data)/rate, 2),
        "sample_rate_hz": rate,
        "snr_db": round(snr, 2),
        "mos_estimate": mos,
        "silence_pct": round(silence_pct, 1),
        "quality": "Excellent" if mos >= 4.3 else "Good" if mos >= 4.0 else "Fair" if mos >= 3.0 else "Poor",
    }
    print(json.dumps(report, indent=2))
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"{GREEN}Report saved to {args.output}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Call Quality Monitor")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd in ["analyze-audio", "measure-latency"]:
        p = sub.add_parser(cmd)
        p.add_argument("--file", required=True)

    p_j = sub.add_parser("detect-jitter")
    p_j.add_argument("--file", required=True)
    p_j.add_argument("--threshold", type=float, default=30.0, help="ms")

    p_r = sub.add_parser("generate-report")
    p_r.add_argument("--file", required=True)
    p_r.add_argument("--output", default=None)

    args = parser.parse_args()
    dispatch = {
        "analyze-audio": analyze_audio,
        "measure-latency": measure_latency,
        "detect-jitter": detect_jitter,
        "generate-report": generate_report,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
