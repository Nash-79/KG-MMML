import argparse, json, pathlib, re, sys, yaml
from collections import defaultdict, Counter

def load_concepts(facts_path, min_cik_support=1):
    """
    Scan facts.jsonl and return:
      - concepts_full: set like {'us-gaap:Assets', 'us-gaap:CashAndCashEquivalentsAtCarryingValue', ...}
      - concepts_short: mapping short->support (unique CIK count)
    """
    short2ciks = defaultdict(set)
    full_set = set()
    with open(facts_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            r = json.loads(line)
            ns = (r.get("ns") or "").strip()
            c  = (r.get("concept") or "").strip()
            cik = (str(r.get("cik") or "").strip())
            if not c: continue
            if ns and not c.startswith(ns + ":"):
                full = f"{ns}:{c}"
                short = c
            elif ":" in c:
                full = c
                short = c.split(":", 1)[1]
            else:
                # No namespace; treat as US GAAP short with fallback
                full = f"us-gaap:{c}"
                short = c
            full_set.add(full)
            if cik:
                short2ciks[short].add(cik)
    # keep only shorts with sufficient cik support
    short_supported = {s for s, ciks in short2ciks.items() if len(ciks) >= min_cik_support}
    return full_set, short_supported

def compile_rules(yaml_path):
    y = yaml.safe_load(pathlib.Path(yaml_path).read_text())
    parents_map = y.get("parents", {}) or {}
    compiled = {}
    for parent, patterns in parents_map.items():
        pats = []
        for p in patterns or []:
            # compile case-insensitive, anchored as provided in YAML
            pats.append(re.compile(p, re.IGNORECASE))
        compiled[parent] = pats
    return compiled

def match_rules(concepts_full, concepts_short, rules):
    edges = set()
    rule_hits = Counter()
    # also precompute a short->full mapping (best-effort)
    shorts_full = defaultdict(set)
    for full in concepts_full:
        if ":" in full:
            shorts_full[full.split(":",1)[1]].add(full)
    for parent, pats in rules.items():
        # normalise parent to full namespace once
        if ":" not in parent:
            parent_full = f"us-gaap:{parent}"
        else:
            parent_full = parent
        for rx in pats:
            # 1) match SHORT names first (fast & robust)
            matched_shorts = [s for s in concepts_short if rx.search(s)]
            for s in matched_shorts:
                for full in shorts_full.get(s, []):
                    edges.add((full, parent_full))
                    rule_hits[(parent_full, rx.pattern)] += 1
            # 2) also try FULL names (just in case)
            for full in concepts_full:
                if rx.search(full):
                    edges.add((full, parent_full))
                    rule_hits[(parent_full, rx.pattern)] += 1
    return edges, rule_hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", required=True, help="data/processed/sec_edgar/facts.jsonl")
    ap.add_argument("--rules", required=True, help="datasets/sec_edgar/taxonomy/pattern_rules.yaml")
    ap.add_argument("--out", required=True, help="datasets/sec_edgar/taxonomy/usgaap_auto.csv")
    ap.add_argument("--min_cik_support", type=int, default=1, help="only include concepts seen in >= this many distinct CIKs")
    args = ap.parse_args()

    concepts_full, concepts_short = load_concepts(args.facts, min_cik_support=args.min_cik_support)
    rules = compile_rules(args.rules)
    edges, rule_hits = match_rules(concepts_full, concepts_short, rules)

    outp = pathlib.Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as w:
        w.write("child,parent,source\n")
        for child, parent in sorted(edges):
            w.write(f"{child},{parent},auto\n")
    print(f"[autotaxonomy] wrote {outp} pairs={len(edges)} (min_cik_support={args.min_cik_support})")

    # diagnostics
    by_parent = defaultdict(int)
    for (parent, pat), cnt in rule_hits.items():
        by_parent[parent] += cnt
    print("[autotaxonomy] per-parent hit counts (approx):")
    for p, cnt in sorted(by_parent.items(), key=lambda x: -x[1])[:20]:
        print(f"  {p}: {cnt}")
    if len(edges) == 0:
        print("[autotaxonomy] WARNING: 0 pairs found. Check that your patterns match SHORT names like 'Assets' and not just namespaced 'us-gaap:Assets'.")
        print("[autotaxonomy] Try increasing coverage or lowering anchors, or run with --min_cik_support=1 initially.")

if __name__ == "__main__":
    main()
