#!/usr/bin/env python3
"""Agent Chain Debugger – OC-0124"""
import argparse, json, os, sys

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"

def _load_trace(file):
    with open(file) as f:
        content=f.read().strip()
    try: return json.loads(content)
    except:
        return [json.loads(line) for line in content.splitlines() if line.strip()]

def parse_trace(args):
    trace=_load_trace(args.file)
    if isinstance(trace,dict): trace=[trace]
    steps=[s for s in trace if s.get("type") in ("tool_call","tool_result","message")]
    print(f"{GREEN}Trace: {len(steps)} steps{RESET}")
    for i,s in enumerate(steps):
        t=s.get("type","?"); name=s.get("name") or s.get("tool","")
        print(f"  [{i:02d}] {YELLOW}{t}{RESET}  {name}")

def visualize(args):
    trace=_load_trace(args.file)
    if isinstance(trace,dict): trace=[trace]
    print(f"{GREEN}Agent Chain Visualization{RESET}")
    indent=0
    for s in trace:
        t=s.get("type","?")
        if t=="tool_call":
            name=s.get("name") or s.get("tool","unknown")
            args_preview=json.dumps(s.get("arguments",s.get("input",{})))[:60]
            print(f"{'  '*indent}├─ {YELLOW}[tool] {name}{RESET}  {args_preview}")
            indent+=1
        elif t=="tool_result":
            indent=max(0,indent-1)
            result=str(s.get("content",s.get("output","")))[:60]
            print(f"{'  '*indent}│  {GREEN}← {result}{RESET}")
        elif t=="message":
            content=str(s.get("content",""))[:80]
            print(f"{'  '*indent}● {content}")

def replay_step(args):
    trace=_load_trace(args.file)
    if isinstance(trace,dict): trace=[trace]
    if args.step_id >= len(trace):
        print(f"{RED}Step {args.step_id} not found (trace has {len(trace)} steps){RESET}"); sys.exit(1)
    step=trace[args.step_id]
    print(f"{GREEN}Step {args.step_id}:{RESET}")
    print(json.dumps(step,indent=2))

def export_report(args):
    trace=_load_trace(args.file)
    if isinstance(trace,dict): trace=[trace]
    fmt=args.format
    if fmt=="md":
        lines=["# Agent Chain Report\n",f"**Steps:** {len(trace)}\n"]
        for i,s in enumerate(trace):
            lines.append(f"## Step {i}: {s.get('type','?')} — {s.get('name',s.get('tool',''))}")
            lines.append(f"```json\n{json.dumps(s,indent=2)[:500]}\n```\n")
        content="\n".join(lines)
    else:
        content=json.dumps(trace,indent=2)
    out=args.output or f"agent_chain.{fmt}"
    with open(out,"w") as f: f.write(content)
    print(f"{GREEN}Report saved to {out}{RESET}")

def main():
    p=argparse.ArgumentParser(description="Agent Chain Debugger")
    s=p.add_subparsers(dest="command",required=True)
    for cmd in ["parse-trace","visualize"]: s.add_parser(cmd).add_argument("--file",required=True)
    pr=s.add_parser("replay-step"); pr.add_argument("--file",required=True); pr.add_argument("--step-id",type=int,required=True)
    pe=s.add_parser("export-report"); pe.add_argument("--file",required=True); pe.add_argument("--output",default=None); pe.add_argument("--format",choices=["md","json","html"],default="md")
    args=p.parse_args()
    {"parse-trace":parse_trace,"visualize":visualize,"replay-step":replay_step,"export-report":export_report}[args.command](args)

if __name__=="__main__": main()
