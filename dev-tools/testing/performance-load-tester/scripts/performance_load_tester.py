#!/usr/bin/env python3
"""
Performance Load Tester — OC-0184
Run skills in parallel to test concurrency and resource usage bounds.
"""

import os
import sys
import json
import time
import shlex
import argparse
import statistics
import subprocess
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _skills_root() -> Path:
    script = Path(__file__).resolve()
    root = script.parent.parent.parent.parent
    if (root / "IDEAS.md").exists():
        return root
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "IDEAS.md").exists():
            return cwd
        cwd = cwd.parent
    return root


def _find_script(skill_name: str) -> Path:
    root = _skills_root()
    matches = list(root.rglob(f"{skill_name}/SKILL.md"))
    if not matches:
        print(f"{RED}Skill '{skill_name}' not found.{RESET}")
        sys.exit(1)
    skill_path = matches[0].parent
    scripts = list((skill_path / "scripts").glob("*.py"))
    if not scripts:
        print(f"{RED}No scripts found in {skill_path}/scripts/{RESET}")
        sys.exit(1)
    return scripts[0]


def _execute_once(script: Path, cmd_args: list, timeout: int = 30) -> dict:
    start = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, str(script)] + cmd_args,
            capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.perf_counter() - start
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "duration": elapsed,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return {"success": False, "exit_code": -1, "duration": elapsed, "timed_out": True}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"success": False, "exit_code": -1, "duration": elapsed, "timed_out": False, "error": str(e)}


def _run_load(script: Path, cmd_args: list, workers: int, iterations: int, timeout: int = 30) -> dict:
    results = []
    wall_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_execute_once, script, cmd_args, timeout) for _ in range(iterations)]
        for future in as_completed(futures):
            results.append(future.result())

    wall_time = time.perf_counter() - wall_start

    durations = [r["duration"] for r in results]
    successes = sum(1 for r in results if r["success"])
    failures  = len(results) - successes
    timeouts  = sum(1 for r in results if r.get("timed_out"))

    return {
        "workers": workers,
        "iterations": iterations,
        "wall_time_s": round(wall_time, 3),
        "throughput_rps": round(iterations / wall_time, 2) if wall_time > 0 else 0,
        "success": successes,
        "failure": failures,
        "timeouts": timeouts,
        "latency": {
            "min_ms":  round(min(durations) * 1000, 1),
            "max_ms":  round(max(durations) * 1000, 1),
            "mean_ms": round(statistics.mean(durations) * 1000, 1),
            "p50_ms":  round(statistics.median(durations) * 1000, 1),
            "p95_ms":  round(_percentile(durations, 95) * 1000, 1),
            "p99_ms":  round(_percentile(durations, 99) * 1000, 1),
        },
    }


def _percentile(data: list, pct: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (pct / 100) * (len(sorted_data) - 1)
    lower = int(index)
    upper = min(lower + 1, len(sorted_data) - 1)
    return sorted_data[lower] + (index - lower) * (sorted_data[upper] - sorted_data[lower])


def _print_result(r: dict):
    ok_color = GREEN if r["failure"] == 0 else YELLOW
    print(f"  Workers:      {r['workers']}")
    print(f"  Iterations:   {r['iterations']}")
    print(f"  Wall time:    {r['wall_time_s']}s")
    print(f"  Throughput:   {r['throughput_rps']} req/s")
    print(f"  {ok_color}Success:{RESET}      {r['success']}")
    if r["failure"]:
        print(f"  {RED}Failures:{RESET}     {r['failure']}  (timeouts: {r['timeouts']})")
    lat = r["latency"]
    print(f"  Latency (ms): min={lat['min_ms']}  p50={lat['p50_ms']}  p95={lat['p95_ms']}  p99={lat['p99_ms']}  max={lat['max_ms']}")


def run(skill_name: str, cmd: str, workers: int, iterations: int, output: str = None):
    script = _find_script(skill_name)
    cmd_args = shlex.split(cmd) if cmd else []
    print(f"\n{BOLD}Load Test — {skill_name}{RESET}")
    print(f"  Script:  {script.name}")
    print(f"  Command: {cmd or '(none)'}")
    print(f"  Workers: {workers}  Iterations: {iterations}\n")
    print(f"{YELLOW}Running...{RESET}")

    result = _run_load(script, cmd_args, workers, iterations)
    print()
    _print_result(result)
    print()

    payload = {
        "skill": skill_name,
        "command": cmd,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "results": [result],
    }
    out_file = output or "perf_report.json"
    Path(out_file).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  Report saved to {out_file}")


def benchmark(skill_name: str, cmd: str, levels: str, iterations_per_level: int = 20, output: str = None):
    script = _find_script(skill_name)
    cmd_args = shlex.split(cmd) if cmd else []
    worker_levels = [int(x.strip()) for x in levels.split(",")]
    results = []

    print(f"\n{BOLD}Benchmark — {skill_name}{RESET}")
    print(f"  Command:    {cmd or '(none)'}")
    print(f"  Levels:     {worker_levels}")
    print(f"  Iterations: {iterations_per_level} per level\n")

    for w in worker_levels:
        print(f"  {CYAN}[workers={w}]{RESET} Running {iterations_per_level} iterations...", end=" ", flush=True)
        r = _run_load(script, cmd_args, w, iterations_per_level)
        results.append(r)
        ok = GREEN if r["failure"] == 0 else YELLOW
        print(f"{ok}{r['throughput_rps']} rps{RESET}  p95={r['latency']['p95_ms']}ms  "
              f"fail={r['failure']}")

    print(f"\n{BOLD}Comparison Table:{RESET}")
    print(f"  {'Workers':>8}  {'RPS':>8}  {'p50 ms':>8}  {'p95 ms':>8}  {'p99 ms':>8}  {'Failures':>8}")
    print(f"  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
    for r in results:
        lat = r["latency"]
        fail_color = RED if r["failure"] else GREEN
        print(f"  {r['workers']:>8}  {r['throughput_rps']:>8}  {lat['p50_ms']:>8}  "
              f"{lat['p95_ms']:>8}  {lat['p99_ms']:>8}  "
              f"{fail_color}{r['failure']:>8}{RESET}")
    print()

    payload = {
        "skill": skill_name,
        "command": cmd,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "results": results,
    }
    out_file = output or "perf_report.json"
    Path(out_file).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  Report saved to {out_file}")


def report(file: str = "perf_report.json"):
    p = Path(file)
    if not p.exists():
        print(f"{RED}Report file not found: {file}{RESET}")
        sys.exit(1)
    data = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{BOLD}Performance Report — {data['skill']}{RESET}")
    print(f"  Timestamp: {data['timestamp']}")
    print(f"  Command:   {data.get('command', 'N/A')}\n")
    for r in data["results"]:
        print(f"  {CYAN}[workers={r['workers']}]{RESET}")
        _print_result(r)
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="performance_load_tester.py",
        description="Performance Load Tester — OC-0184"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="Run a load test")
    p.add_argument("--skill", required=True, help="Skill name")
    p.add_argument("--cmd", default="", help="Arguments to pass to the skill script")
    p.add_argument("--workers", type=int, default=5, help="Parallel worker count (default: 5)")
    p.add_argument("--iterations", type=int, default=20, help="Total iterations (default: 20)")
    p.add_argument("--output", default=None, help="Save report to this file")

    p = sub.add_parser("benchmark", help="Run multiple concurrency levels")
    p.add_argument("--skill", required=True)
    p.add_argument("--cmd", default="")
    p.add_argument("--levels", default="1,5,10,20", help="Comma-separated worker counts (default: 1,5,10,20)")
    p.add_argument("--iterations", type=int, default=20)
    p.add_argument("--output", default=None)

    p = sub.add_parser("report", help="Display a saved report")
    p.add_argument("--file", default="perf_report.json")

    args = parser.parse_args()
    if args.cmd == "run":
        run(args.skill, args.cmd, args.workers, args.iterations, args.output)
    elif args.cmd == "benchmark":
        benchmark(args.skill, args.cmd, args.levels, args.iterations, args.output)
    elif args.cmd == "report":
        report(args.file)


if __name__ == "__main__":
    main()
