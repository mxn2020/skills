#!/usr/bin/env python3
"""Eval Suite Runner – OC-0126"""
import argparse, json, os, sys, time, requests

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"
BASE="https://api.openai.com/v1"
SUITES_DIR=os.path.expanduser("~/.openclaw/suites")

def _key():
    k=os.environ.get("OPENAI_API_KEY")
    if not k: print(f"{RED}Error: OPENAI_API_KEY not set{RESET}"); sys.exit(1)
    return k

def _load_suite(suite_file):
    with open(suite_file) as f: return json.load(f)

def _run_model(prompt, model):
    resp=requests.post(f"{BASE}/chat/completions",
        headers={"Authorization":f"Bearer {_key()}","Content-Type":"application/json"},
        json={"model":model,"messages":[{"role":"user","content":prompt}]},timeout=30)
    if not resp.ok: return None
    return resp.json()["choices"][0]["message"]["content"]

def _score(output, expected):
    if not expected: return None
    if expected.lower() in output.lower(): return 1.0
    words=set(expected.lower().split()); out_words=set(output.lower().split())
    return len(words&out_words)/len(words) if words else 0.0

def run(args):
    suite=_load_suite(args.suite_file)
    results={"model":args.model,"suite":args.suite_file,"timestamp":time.time(),"tests":[]}
    passed=failed=0
    for test in suite.get("tests",[]):
        output=_run_model(test["prompt"],args.model)
        score=_score(output or "",test.get("expected",""))
        ok=score is None or score>=0.5
        if ok: passed+=1; color=GREEN
        else: failed+=1; color=RED
        results["tests"].append({"id":test.get("id","?"),"score":score,"passed":ok,"output":(output or "")[:200]})
        print(f"  {color}{'PASS' if ok else 'FAIL'}{RESET}  [{test.get('id','?')}]  score={score:.2f}" if score is not None else f"  {GREEN}PASS{RESET}  [{test.get('id','?')}]")
    print(f"\n{GREEN}{passed} passed{RESET}  {RED if failed else GREEN}{failed} failed{RESET}")
    if args.output_dir:
        os.makedirs(args.output_dir,exist_ok=True)
        out=os.path.join(args.output_dir,f"run_{int(time.time())}.json")
        with open(out,"w") as f: json.dump(results,f,indent=2)
        print(f"{GREEN}Results: {out}{RESET}")

def add_test(args):
    if os.path.exists(args.suite_file):
        with open(args.suite_file) as f: suite=json.load(f)
    else:
        suite={"name":os.path.basename(args.suite_file),"tests":[]}
    suite["tests"].append({"id":args.id or f"test_{len(suite['tests'])+1}","prompt":args.prompt,"expected":args.expected})
    with open(args.suite_file,"w") as f: json.dump(suite,f,indent=2)
    print(f"{GREEN}Test added to {args.suite_file}{RESET}")

def list_tests(args):
    suite=_load_suite(args.suite_file)
    print(f"{GREEN}Tests in {args.suite_file}: {len(suite.get('tests',[]))}{RESET}")
    for t in suite.get("tests",[]): print(f"  [{t.get('id','?')}] {t['prompt'][:60]}")

def compare_runs(args):
    with open(args.run_a) as f: a=json.load(f)
    with open(args.run_b) as f: b=json.load(f)
    a_by_id={t["id"]:t for t in a.get("tests",[])}; b_by_id={t["id"]:t for t in b.get("tests",[])}
    print(f"{GREEN}Comparing {a['model']} vs {b['model']}{RESET}")
    for tid in set(a_by_id)|set(b_by_id):
        ta=a_by_id.get(tid,{}); tb=b_by_id.get(tid,{})
        sa=ta.get("score"); sb=tb.get("score")
        diff=f"{(sb or 0)-(sa or 0):+.2f}" if sa is not None and sb is not None else "N/A"
        color=GREEN if (sb or 0)>=(sa or 0) else RED
        print(f"  [{tid}]  A={sa:.2f}  B={sb:.2f}  {color}Δ={diff}{RESET}")

def main():
    p=argparse.ArgumentParser(description="Eval Suite Runner")
    s=p.add_subparsers(dest="command",required=True)
    pr=s.add_parser("run"); pr.add_argument("--suite-file",required=True); pr.add_argument("--model",default="gpt-4o-mini"); pr.add_argument("--output-dir",default=None)
    pa=s.add_parser("add-test"); pa.add_argument("--suite-file",required=True); pa.add_argument("--prompt",required=True); pa.add_argument("--expected",default=""); pa.add_argument("--id",default=None)
    s.add_parser("list-tests").add_argument("--suite-file",required=True)
    pc=s.add_parser("compare-runs"); pc.add_argument("--run-a",required=True); pc.add_argument("--run-b",required=True)
    args=p.parse_args()
    {"run":run,"add-test":add_test,"list-tests":list_tests,"compare-runs":compare_runs}[args.command](args)

if __name__=="__main__": main()
