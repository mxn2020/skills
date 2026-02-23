#!/usr/bin/env python3
"""Bias & Safety Checker – OC-0120"""
import argparse, glob, json, os, sys, requests

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"
OPENAI_BASE="https://api.openai.com/v1"

def _key():
    k=os.environ.get("OPENAI_API_KEY")
    if not k: print(f"{RED}Error: OPENAI_API_KEY not set{RESET}"); sys.exit(1)
    return k

def _check(text):
    prompt=(f"Analyze the following text for: bias (gender, racial, cultural), toxicity, "
            f"PII exposure, and potential hallucinations. Return JSON with keys: "
            f"bias_detected(bool), toxicity_score(0-10), pii_found(list), "
            f"hallucination_risk(low/medium/high), issues(list of strings), "
            f"overall_risk(low/medium/high). Text:\n{text[:3000]}")
    resp=requests.post(f"{OPENAI_BASE}/chat/completions",
        headers={"Authorization":f"Bearer {_key()}","Content-Type":"application/json"},
        json={"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],
              "response_format":{"type":"json_object"}})
    if not resp.ok: print(f"{RED}API error: {resp.text}{RESET}"); sys.exit(1)
    return json.loads(resp.json()["choices"][0]["message"]["content"])

def _print_result(r, label=""):
    if label: print(f"\n{YELLOW}{label}{RESET}")
    risk=r.get("overall_risk","?")
    color=GREEN if risk=="low" else YELLOW if risk=="medium" else RED
    print(f"  Overall risk   : {color}{risk}{RESET}")
    print(f"  Bias detected  : {r.get('bias_detected','?')}")
    print(f"  Toxicity score : {r.get('toxicity_score','?')}/10")
    print(f"  PII found      : {', '.join(r.get('pii_found',[]) or ['none'])}")
    print(f"  Hallucination  : {r.get('hallucination_risk','?')}")
    for issue in r.get("issues",[]):
        print(f"  ⚠ {issue}")

def check_text(args): _print_result(_check(args.text))
def check_file(args):
    with open(args.file) as f: _print_result(_check(f.read()), args.file)
def batch_check(args):
    files=glob.glob(os.path.join(args.dir,"*.txt"))+glob.glob(os.path.join(args.dir,"*.md"))
    results={}
    for f in files:
        with open(f) as fh: r=_check(fh.read())
        results[os.path.basename(f)]=r; _print_result(r,os.path.basename(f))
    if args.output:
        with open(args.output,"w") as fh: json.dump(results,fh,indent=2)
        print(f"\n{GREEN}Report saved to {args.output}{RESET}")
def generate_report(args):
    with open(args.results_file) as f: data=json.load(f)
    output=args.output or "safety_report.md"
    lines=["# Safety & Bias Report\n"]
    for name,r in data.items():
        lines.append(f"## {name}\n- Risk: {r.get('overall_risk')}\n- Issues: {', '.join(r.get('issues',[]) or ['none'])}\n")
    with open(output,"w") as f: f.write("\n".join(lines))
    print(f"{GREEN}Report: {output}{RESET}")

def main():
    p=argparse.ArgumentParser(description="Bias & Safety Checker")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("check-text").add_argument("--text",required=True)
    s.add_parser("check-file").add_argument("--file",required=True)
    pb=s.add_parser("batch-check"); pb.add_argument("--dir",required=True); pb.add_argument("--output",default=None)
    pr=s.add_parser("generate-report"); pr.add_argument("--results-file",required=True); pr.add_argument("--output",default=None)
    args=p.parse_args()
    {"check-text":check_text,"check-file":check_file,"batch-check":batch_check,"generate-report":generate_report}[args.command](args)

if __name__=="__main__": main()
