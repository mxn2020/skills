#!/usr/bin/env python3
"""Knowledge Graph Builder – OC-0122"""
import argparse, json, os, sys, requests

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"
BASE="https://api.openai.com/v1"
DEFAULT_GRAPH=os.path.expanduser("~/.openclaw/knowledge.json")

def _key():
    k=os.environ.get("OPENAI_API_KEY")
    if not k: print(f"{RED}Error: OPENAI_API_KEY not set{RESET}"); sys.exit(1)
    return k

def _chat(prompt):
    resp=requests.post(f"{BASE}/chat/completions",
        headers={"Authorization":f"Bearer {_key()}","Content-Type":"application/json"},
        json={"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],
              "response_format":{"type":"json_object"}})
    if not resp.ok: print(f"{RED}API error: {resp.text}{RESET}"); sys.exit(1)
    return json.loads(resp.json()["choices"][0]["message"]["content"])

def _load(graph_file):
    if os.path.exists(graph_file):
        with open(graph_file) as f: return json.load(f)
    return {"nodes":[],"edges":[]}

def _save(graph,graph_file):
    os.makedirs(os.path.dirname(graph_file),exist_ok=True)
    with open(graph_file,"w") as f: json.dump(graph,f,indent=2)

def extract(args):
    result=_chat(f"Extract entities and relationships from this text. Return JSON: {{entities:[{{name,type}}], relationships:[{{from,relation,to}}]}}\n\n{args.text}")
    print(f"{GREEN}Entities:{RESET}"); [print(f"  {e['name']} ({e['type']})") for e in result.get("entities",[])]
    print(f"{GREEN}Relationships:{RESET}"); [print(f"  {r['from']} --[{r['relation']}]--> {r['to']}") for r in result.get("relationships",[])]

def add_document(args):
    with open(args.file) as f: text=f.read()
    result=_chat(f"Extract entities and relationships. Return JSON: {{entities:[{{name,type}}], relationships:[{{from,relation,to}}]}}\n\n{text[:5000]}")
    graph=_load(args.graph_file)
    existing_names={n["name"] for n in graph["nodes"]}
    for e in result.get("entities",[]):
        if e["name"] not in existing_names:
            graph["nodes"].append(e); existing_names.add(e["name"])
    graph["edges"].extend(result.get("relationships",[]))
    _save(graph,args.graph_file)
    print(f"{GREEN}Added {len(result.get('entities',[]))} entities and {len(result.get('relationships',[]))} relationships{RESET}")

def query_graph(args):
    graph=_load(args.graph_file)
    matches=[n for n in graph["nodes"] if args.entity.lower() in n["name"].lower()]
    if not matches: print(f"{YELLOW}No entity matching '{args.entity}' found{RESET}"); return
    entity_name=matches[0]["name"]
    related=[e for e in graph["edges"] if entity_name in (e.get("from",""),e.get("to",""))]
    print(f"{GREEN}Entity: {entity_name}{RESET}")
    for r in related[:10]: print(f"  {r.get('from')} --[{r.get('relation')}]--> {r.get('to')}")

def export_graph(args):
    graph=_load(args.graph_file)
    fmt=args.format
    if fmt=="dot":
        lines=["digraph G {"]+[f'  "{e.get("from")}" -> "{e.get("to")}" [label="{e.get("relation")}"];' for e in graph["edges"]]+["}"]
        content="\n".join(lines)
    elif fmt=="csv":
        content="from,relation,to\n"+"\n".join(f"{e.get('from')},{e.get('relation')},{e.get('to')}" for e in graph["edges"])
    else:
        content=json.dumps(graph,indent=2)
    out=args.output or f"knowledge_graph.{fmt}"
    with open(out,"w") as f: f.write(content)
    print(f"{GREEN}Exported to {out} ({len(graph['nodes'])} nodes, {len(graph['edges'])} edges){RESET}")

def main():
    p=argparse.ArgumentParser(description="Knowledge Graph Builder")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("extract").add_argument("--text",required=True)
    pad=s.add_parser("add-document"); pad.add_argument("--file",required=True); pad.add_argument("--graph-file",default=DEFAULT_GRAPH)
    pq=s.add_parser("query-graph"); pq.add_argument("--entity",required=True); pq.add_argument("--graph-file",default=DEFAULT_GRAPH); pq.add_argument("--depth",type=int,default=2)
    pe=s.add_parser("export-graph"); pe.add_argument("--graph-file",default=DEFAULT_GRAPH); pe.add_argument("--format",choices=["json","dot","csv"],default="json"); pe.add_argument("--output",default=None)
    args=p.parse_args()
    {"extract":extract,"add-document":add_document,"query-graph":query_graph,"export-graph":export_graph}[args.command](args)

if __name__=="__main__": main()
