#!/usr/bin/env python3
import argparse, json, pathlib, re, csv, yaml

def normalise(name: str) -> str:
    # Ensure we emit us-gaap:* names
    name = (name or "").strip()
    if not name:
        return ""
    if ":" not in name:
        return f"us-gaap:{name}"
    return name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", required=True, help="facts.jsonl (from companyfacts_to_facts.py)")
    ap.add_argument("--rules", required=True, help="pattern_rules.yaml")
    ap.add_argument("--out", required=True, help="CSV to write (parent,child)")
    args = ap.parse_args()

    # 1) collect observed concept names as us-gaap:* (child candidates)
    concepts = set()
    with open(args.facts, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            j = json.loads(line)
            ns = (j.get("ns") or "").strip()
            c = (j.get("concept") or "").strip()
            if not c: continue
            cname = f"{ns}:{c}" if ns and not c.startswith(ns + ":") else c
            # only target us-gaap concepts for these rules
            if not cname.startswith("us-gaap:"): 
                continue
            concepts.add(cname)

    # 2) load rules
    rules = yaml.safe_load(open(args.rules, "r", encoding="utf-8"))
    compiled = [(normalise(parent), [re.compile(p) for p in pats]) for parent, pats in rules.items()]

    # 3) generate pairs (parent, child) only when regex matches child (without the prefix)
    pairs = set()
    for parent, patterns in compiled:
        parent_base = parent.split(":", 1)[1]
        for child in concepts:
            child_base = child.split(":", 1)[1]
            if child == parent:
                continue
            if any(r.search(child_base) for r in patterns):
                pairs.add((parent, child))

    # 4) write CSV
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["parent", "child"])
        for p, c in sorted(pairs):
            w.writerow([p, c])

    print(f"[autotaxonomy] wrote {len(pairs)} pairs -> {args.out}")

if __name__ == "__main__":
    main()
