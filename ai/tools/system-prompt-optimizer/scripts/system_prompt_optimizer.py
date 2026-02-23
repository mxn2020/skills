#!/usr/bin/env python3
"""System Prompt Optimizer – OC-0121"""
import argparse, json, os, sys, requests

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"
BASE="https://api.openai.com/v1"

def _key():
    k=os.environ.get("OPENAI_API_KEY")
    if not k: print(f"{RED}Error: OPENAI_API_KEY not set{RESET}"); sys.exit(1)
    return k

def _chat(messages,model="gpt-4o"):
    resp=requests.post(f"{BASE}/chat/completions",
        headers={"Authorization":f"Bearer {_key()}","Content-Type":"application/json"},
        json={"model":model,"messages":messages})
    if not resp.ok: print(f"{RED}API error: {resp.text}{RESET}"); sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]

def optimize(args):
    with open(args.prompt_file) as f: prompt=f.read()
    print(f"{YELLOW}Optimizing prompt ({args.iterations} iterations) ...{RESET}")
    current=prompt
    for i in range(args.iterations):
        feedback=_chat([{"role":"user","content":
            f"You are a prompt engineering expert. Improve this system prompt to better achieve this goal: {args.goal}\n\nCurrent prompt:\n{current}\n\nReturn ONLY the improved prompt text."}])
        current=feedback
        print(f"  {GREEN}Iteration {i+1} complete{RESET}")
    print(f"\n{GREEN}Optimized prompt:{RESET}\n{current}")
    out=args.output or args.prompt_file.replace(".txt","_optimized.txt")
    with open(out,"w") as f: f.write(current)
    print(f"{GREEN}Saved to {out}{RESET}")

def evaluate(args):
    with open(args.prompt_file) as f: prompt=f.read()
    with open(args.test_cases_file) as f: cases=json.load(f)
    print(f"{YELLOW}Evaluating {len(cases)} test cases ...{RESET}")
    scores=[]
    for case in cases[:5]:
        result=_chat([{"role":"system","content":prompt},{"role":"user","content":case["input"]}])
        score_resp=_chat([{"role":"user","content":
            f"Score this response 0-10 for quality. Expected: {case.get('expected','')}\nActual: {result}\nReturn only a number."}])
        try: score=float(score_resp.strip()); scores.append(score)
        except: pass
    avg=sum(scores)/len(scores) if scores else 0
    print(f"{GREEN}Average score: {avg:.1f}/10{RESET}")

def compare_versions(args):
    with open(args.v1_file) as f: v1=f.read()
    with open(args.v2_file) as f: v2=f.read()
    analysis=_chat([{"role":"user","content":
        f"Compare these two system prompts and explain which is better and why:\n\nV1:\n{v1}\n\nV2:\n{v2}"}])
    print(f"{GREEN}Comparison:{RESET}\n{analysis}")

def apply(args):
    with open(args.prompt_file) as f: content=f.read()
    out=args.output or "applied_prompt.txt"
    with open(out,"w") as f: f.write(content)
    print(f"{GREEN}Prompt applied to {out}{RESET}")

def main():
    p=argparse.ArgumentParser(description="System Prompt Optimizer")
    s=p.add_subparsers(dest="command",required=True)
    po=s.add_parser("optimize"); po.add_argument("--prompt-file",required=True); po.add_argument("--goal",required=True); po.add_argument("--iterations",type=int,default=3); po.add_argument("--output",default=None)
    pe=s.add_parser("evaluate"); pe.add_argument("--prompt-file",required=True); pe.add_argument("--test-cases-file",required=True); pe.add_argument("--model",default="gpt-4o-mini")
    pc=s.add_parser("compare-versions"); pc.add_argument("--v1-file",required=True); pc.add_argument("--v2-file",required=True)
    pa=s.add_parser("apply"); pa.add_argument("--prompt-file",required=True); pa.add_argument("--output",default=None)
    args=p.parse_args()
    {"optimize":optimize,"evaluate":evaluate,"compare-versions":compare_versions,"apply":apply}[args.command](args)

if __name__=="__main__": main()
