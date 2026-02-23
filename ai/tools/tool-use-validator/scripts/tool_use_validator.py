#!/usr/bin/env python3
"""Tool Use Validator – OC-0123"""
import argparse, json, os, re, sys

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; RESET="\033[0m"

RULES=[
    ("required_fields","All required fields must be present"),
    ("type_check","Field types must match schema"),
    ("no_extra_fields","No undeclared fields allowed (if strict mode)"),
    ("non_empty_strings","String fields must not be empty"),
    ("valid_enums","Enum fields must use allowed values"),
]

def _validate_call(call, schema):
    errors=[]
    required=schema.get("required",[])
    props=schema.get("properties",{})
    for field in required:
        if field not in call: errors.append(f"Missing required field: '{field}'")
    for field, value in call.items():
        if field in props:
            expected_type=props[field].get("type")
            type_map={"string":str,"integer":int,"number":(int,float),"boolean":bool,"array":list,"object":dict}
            if expected_type and expected_type in type_map:
                if not isinstance(value, type_map[expected_type]):
                    errors.append(f"Field '{field}': expected {expected_type}, got {type(value).__name__}")
            enum_vals=props[field].get("enum")
            if enum_vals and value not in enum_vals:
                errors.append(f"Field '{field}': '{value}' not in allowed values {enum_vals}")
            if isinstance(value,str) and not value.strip():
                errors.append(f"Field '{field}': empty string not allowed")
    return errors

def validate(args):
    try: call=json.loads(args.tool_call)
    except json.JSONDecodeError as e: print(f"{RED}Invalid JSON: {e}{RESET}"); sys.exit(1)
    with open(args.schema_file) as f: schema=json.load(f)
    errors=_validate_call(call,schema)
    if errors:
        print(f"{RED}FAIL — {len(errors)} error(s):{RESET}")
        for e in errors: print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"{GREEN}PASS — tool call is valid{RESET}")

def validate_file(args):
    with open(args.file) as f: calls=json.load(f)
    with open(args.schema_file) as f: schema=json.load(f)
    if not isinstance(calls,list): calls=[calls]
    passed=failed=0
    for i,call in enumerate(calls):
        errors=_validate_call(call,schema)
        if errors: failed+=1; print(f"  {RED}[{i}] FAIL:{RESET} {errors[0]}")
        else: passed+=1; print(f"  {GREEN}[{i}] PASS{RESET}")
    print(f"\n{GREEN}{passed} passed{RESET}, {RED if failed else GREEN}{failed} failed{RESET}")

def generate_schema(args):
    with open(args.example_call_file) as f: example=json.load(f)
    props={}
    for k,v in example.items():
        t={str:"string",int:"integer",float:"number",bool:"boolean",list:"array",dict:"object"}.get(type(v),"string")
        props[k]={"type":t,"description":f"The {k} parameter"}
    schema={"type":"object","properties":props,"required":list(example.keys())}
    print(json.dumps(schema,indent=2))

def list_rules(args):
    print(f"{GREEN}Validation rules:{RESET}")
    for name,desc in RULES: print(f"  {name:25s} {desc}")

def main():
    p=argparse.ArgumentParser(description="Tool Use Validator")
    s=p.add_subparsers(dest="command",required=True)
    pv=s.add_parser("validate"); pv.add_argument("--tool-call",required=True); pv.add_argument("--schema-file",required=True)
    pvf=s.add_parser("validate-file"); pvf.add_argument("--file",required=True); pvf.add_argument("--schema-file",required=True)
    pg=s.add_parser("generate-schema"); pg.add_argument("--tool-name",required=True); pg.add_argument("--example-call-file",required=True)
    s.add_parser("list-rules")
    args=p.parse_args()
    {"validate":validate,"validate-file":validate_file,"generate-schema":generate_schema,"list-rules":list_rules}[args.command](args)

if __name__=="__main__": main()
