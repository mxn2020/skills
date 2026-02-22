#!/usr/bin/env python3
"""Embedding Drift Detector – OC-0125"""
import argparse, json, math, os, sys, requests

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"
BASE="https://api.openai.com/v1"
CFG_FILE=os.path.expanduser("~/.openclaw/drift_config.json")

def _key():
    k=os.environ.get("OPENAI_API_KEY")
    if not k: print(f"{RED}Error: OPENAI_API_KEY not set{RESET}"); sys.exit(1)
    return k

def _embed(texts):
    resp=requests.post(f"{BASE}/embeddings",
        headers={"Authorization":f"Bearer {_key()}","Content-Type":"application/json"},
        json={"model":"text-embedding-3-small","input":texts})
    if not resp.ok: print(f"{RED}Embedding error: {resp.text}{RESET}"); sys.exit(1)
    return [d["embedding"] for d in resp.json()["data"]]

def _cos(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    return dot/(math.sqrt(sum(x*x for x in a))*math.sqrt(sum(x*x for x in b))+1e-10)

def compute_drift(args):
    with open(args.collection_file) as f: chunks=json.load(f)
    q_emb=_embed([args.query])[0]
    chunk_texts=[c["text"] if isinstance(c,dict) else c for c in chunks[:20]]
    embs=_embed(chunk_texts)
    scores=[_cos(q_emb,e) for e in embs]
    avg=sum(scores)/len(scores); mn=min(scores); mx=max(scores)
    drift=1-avg
    color=GREEN if drift<0.3 else YELLOW if drift<0.5 else RED
    print(f"{GREEN}Drift Analysis{RESET}")
    print(f"  Query      : {args.query[:60]}")
    print(f"  Avg sim    : {avg:.4f}"); print(f"  Min/Max    : {mn:.4f}/{mx:.4f}")
    print(f"  Drift score: {color}{drift:.4f}{RESET}  ({'OK' if drift<0.3 else 'Warning' if drift<0.5 else 'HIGH DRIFT'})")

def monitor_collection(args):
    with open(args.collection_file) as f: chunks=json.load(f)
    with open(args.query_file) as f: queries=[l.strip() for l in f if l.strip()]
    chunk_texts=[c["text"] if isinstance(c,dict) else c for c in chunks[:10]]
    chunk_embs=_embed(chunk_texts)
    alerts=[]
    for q in queries:
        q_emb=_embed([q])[0]
        avg=sum(_cos(q_emb,e) for e in chunk_embs)/len(chunk_embs)
        drift=1-avg
        if drift>args.threshold: alerts.append((q,drift))
        color=RED if drift>args.threshold else GREEN
        print(f"  {color}drift={drift:.3f}{RESET}  {q[:60]}")
    if alerts: print(f"\n{RED}{len(alerts)} query(s) exceed threshold {args.threshold}{RESET}")
    else: print(f"\n{GREEN}All queries within threshold{RESET}")

def set_threshold(args):
    cfg={}
    if os.path.exists(CFG_FILE):
        with open(CFG_FILE) as f: cfg=json.load(f)
    cfg[args.collection]={"threshold":args.value}
    os.makedirs(os.path.dirname(CFG_FILE),exist_ok=True)
    with open(CFG_FILE,"w") as f: json.dump(cfg,f,indent=2)
    print(f"{GREEN}Threshold for '{args.collection}' set to {args.value}{RESET}")

def generate_alert(args):
    color=RED if args.drift_score>0.5 else YELLOW
    print(f"{color}DRIFT ALERT{RESET}")
    print(f"  Collection  : {args.collection}")
    print(f"  Drift score : {args.drift_score:.4f}")
    print(f"  Severity    : {'HIGH' if args.drift_score>0.5 else 'MEDIUM'}")
    print(f"  Action      : Re-embed collection or refine retrieval strategy")

def main():
    p=argparse.ArgumentParser(description="Embedding Drift Detector")
    s=p.add_subparsers(dest="command",required=True)
    pcd=s.add_parser("compute-drift"); pcd.add_argument("--query",required=True); pcd.add_argument("--collection-file",required=True); pcd.add_argument("--top-k",type=int,default=5)
    pm=s.add_parser("monitor-collection"); pm.add_argument("--collection-file",required=True); pm.add_argument("--query-file",required=True); pm.add_argument("--threshold",type=float,default=0.3)
    ps=s.add_parser("set-threshold"); ps.add_argument("--value",type=float,required=True); ps.add_argument("--collection",required=True)
    pa=s.add_parser("generate-alert"); pa.add_argument("--drift-score",type=float,required=True); pa.add_argument("--collection",required=True)
    args=p.parse_args()
    {"compute-drift":compute_drift,"monitor-collection":monitor_collection,"set-threshold":set_threshold,"generate-alert":generate_alert}[args.command](args)

if __name__=="__main__": main()
