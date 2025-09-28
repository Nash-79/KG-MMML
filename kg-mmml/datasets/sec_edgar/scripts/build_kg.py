# datasets/sec_edgar/scripts/build_kg.py
import argparse, json, pathlib, csv

def load_taxonomy(csv_path: str):
    """Load parent,child rows from a CSV (header: parent,child)."""
    pairs = []
    p = pathlib.Path(csv_path)
    if not p.exists():
        return pairs
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parent = (row.get("parent") or "").strip()
            child = (row.get("child") or "").strip()
            if parent and child:
                pairs.append((parent, child))
    return pairs

def write_csv(nodes, edges, outdir: pathlib.Path):
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "kg_nodes.csv").open("w", newline="", encoding="utf-8") as nf:
        nw = csv.writer(nf)
        nw.writerow(["node_id", "type", "attrs_json"])
        for n in nodes:
            nw.writerow([n["id"], n["type"], json.dumps(n.get("attrs", {}))])
    with (outdir / "kg_edges.csv").open("w", newline="", encoding="utf-8") as ef:
        ew = csv.writer(ef)
        ew.writerow(["src_id", "edge_type", "dst_id", "attrs_json"])
        for e in edges:
            ew.writerow([e["src"], e["type"], e["dst"], json.dumps(e.get("attrs", {}))])

def normalise_concept_id(ns: str, concept: str) -> str:
    """
    Ensure concept IDs align with taxonomy (e.g., 'us-gaap:Assets').
    If facts provide ns='us-gaap' and concept='Assets', produce 'us-gaap:Assets'.
    If concept already has a prefix, keep it as-is.
    """
    ns = (ns or "").strip()
    cname = (concept or "").strip()
    if not cname:
        return "UNKNOWN"
    if ns and not cname.startswith(ns + ":"):
        cname = f"{ns}:{cname}"
    return cname

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selected", default="data/raw/sec_edgar/selected.json",
                    help="JSON produced by select_filings.py (CIK -> {10-K/10-Q:[{accession,doc}]})")
    ap.add_argument("--facts", default="data/processed/sec_edgar/facts.jsonl",
                    help="Normalised facts JSONL (ns, concept, unit, value, period_end, accn)")
    ap.add_argument("--taxonomy", default="datasets/sec_edgar/taxonomy/usgaap_min.csv",
                    help="CSV of parent,child concept pairs (us-gaap:* names)")
    ap.add_argument("--snapshot", default="data/kg/sec_edgar_2025-09-22",
                    help="Output folder for kg_nodes.csv and kg_edges.csv")
    args = ap.parse_args()

    sel_path = pathlib.Path(args.selected)
    facts_path = pathlib.Path(args.facts)
    snap_dir = pathlib.Path(args.snapshot)

    if not sel_path.exists():
        raise FileNotFoundError(f"Missing --selected file: {sel_path}")
    selected = json.loads(sel_path.read_text())

    facts = []
    if facts_path.exists():
        with facts_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        facts.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    taxonomy_pairs = load_taxonomy(args.taxonomy)

    # Build graph
    nodes, edges = [], []
    seen_nodes = set()            # (id,type)
    seen_edges = set()            # (src,type,dst)

    def add_node(nid: str, ntype: str, attrs=None):
        key = (nid, ntype)
        if key in seen_nodes:
            return
        nodes.append({"id": nid, "type": ntype, "attrs": attrs or {}})
        seen_nodes.add(key)

    def add_edge(src: str, etype: str, dst: str, attrs=None):
        key = (src, etype, dst)
        if key in seen_edges:
            return
        edges.append({"src": src, "type": etype, "dst": dst, "attrs": attrs or {}})
        seen_edges.add(key)

    # Companies & filings from selected.json
    for cik, forms in selected.items():
        cid = f"cik_{cik}"
        add_node(cid, "Company", {"cik": cik})
        for form, items in (forms or {}).items():
            for it in items:
                accn = (it.get("accession") or "").replace("-", "")
                fid = f"filing_{cik}_{accn}" if accn else f"filing_{cik}_UNKNOWN"
                add_node(fid, "Filing", {"form": form, "accession": it.get("accession", "")})
                add_edge(cid, "reports", fid, {})

    # Facts → Concept, Unit, Period (namespace-aware concept IDs)
    for f in facts:
        ns = (f.get("ns") or "").strip()
        cname = normalise_concept_id(ns, f.get("concept", ""))
        cpt = f"concept_{cname}"
        unit = (f.get("unit") or "").strip()
        period_end = (f.get("period_end") or "").strip()

        unt = f"unit_{unit}" if unit else "unit_UNKNOWN"
        per = f"period_{period_end}" if period_end else "period_UNKNOWN"

        add_node(cpt, "Concept", {"ns": ns})
        add_node(unt, "Unit", {"symbol": unit})
        add_node(per, "Period", {"end": period_end})

        # Directional edges
        add_edge(cpt, "measured-in", unt, {})
        add_edge(cpt, "for-period", per, {})

    # Taxonomy is-a edges (Concept → Concept)
    for parent, child in taxonomy_pairs:
        p_id = f"concept_{parent}"
        c_id = f"concept_{child}"
        add_node(p_id, "Concept", {})
        add_node(c_id, "Concept", {})
        add_edge(c_id, "is-a", p_id, {})

    write_csv(nodes, edges, snap_dir)
    print(f"Snapshot: {snap_dir} | nodes: {len(nodes)} | edges: {len(edges)}")

if __name__ == "__main__":
    main()
