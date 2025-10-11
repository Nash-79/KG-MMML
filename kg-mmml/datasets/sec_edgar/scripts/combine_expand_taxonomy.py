import pandas as pd, pathlib, argparse, collections

def load_edges(path):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    # Detect schema and normalise to child,parent
    if "child" in cols and "parent" in cols:
        child = df[cols["child"]].astype(str).str.strip()
        parent = df[cols["parent"]].astype(str).str.strip()
    elif "parent" in cols and "child" not in cols:
        # assume two-column parent,child
        child = df.iloc[:,1].astype(str).str.strip()
        parent = df.iloc[:,0].astype(str).str.strip()
    else:
        # assume two columns in unknown order, try to detect by patterns
        if df.shape[1] < 2:
            raise SystemExit(f"{path}: needs at least two columns")
        a = df.iloc[:,0].astype(str).str.strip()
        b = df.iloc[:,1].astype(str).str.strip()
        # prefer child = column containing more leaf-like entries (heuristic)
        child, parent = (a, b)
    # Normalise namespaces (ensure exactly one prefix)
    def norm(s):
        s = s.strip()
        if ":" in s:
            ns, name = s.split(":", 1)
            return f"{ns}:{name}"
        return f"us-gaap:{s}"
    child = child.map(norm)
    parent = parent.map(norm)
    edges = pd.DataFrame({"child": child, "parent": parent})
    # Remove self loops and exact dupes
    edges = edges[edges["child"] != edges["parent"]].drop_duplicates()
    return edges

def add_backbone(edges):
    """Ensure mid-tier hierarchy is present (helps depth)."""
    backbone = [
        ("us-gaap:AssetsCurrent", "us-gaap:Assets"),
        ("us-gaap:AssetsNoncurrent", "us-gaap:Assets"),
        ("us-gaap:LiabilitiesCurrent", "us-gaap:Liabilities"),
        ("us-gaap:LiabilitiesNoncurrent", "us-gaap:Liabilities"),
        ("us-gaap:OperatingExpenses", "us-gaap:OperatingIncomeLoss"),
        ("us-gaap:CostOfRevenue", "us-gaap:CostsAndExpenses"),
        ("us-gaap:SalesRevenueNet", "us-gaap:Revenues"),
        ("us-gaap:ContractWithCustomerRevenue", "us-gaap:Revenues"),
        ("us-gaap:AdditionalPaidInCapital", "us-gaap:StockholdersEquity"),
        ("us-gaap:RetainedEarningsAccumulatedDeficit", "us-gaap:StockholdersEquity"),
        ("us-gaap:TreasuryStockValue", "us-gaap:StockholdersEquity"),
        ("us-gaap:PropertyPlantAndEquipmentNet", "us-gaap:Assets"),
        ("us-gaap:InventoryNet", "us-gaap:Assets"),
        ("us-gaap:AccountsReceivableNetCurrent", "us-gaap:Assets"),
        ("us-gaap:AccountsPayableCurrent", "us-gaap:Liabilities"),
        ("us-gaap:DeferredRevenueCurrent", "us-gaap:Liabilities"),
        ("us-gaap:LongTermDebtNoncurrent", "us-gaap:Liabilities"),
    ]
    bb = pd.DataFrame(backbone, columns=["child", "parent"])
    out = pd.concat([edges, bb], ignore_index=True).drop_duplicates()
    return out

def transitive_closure(edges):
    """Materialise child → all ancestors for is-a depth."""
    parents = collections.defaultdict(set)
    for c, p in edges.itertuples(index=False):
        parents[c].add(p)
    memo = {}
    def anc(c):
        if c in memo: return memo[c]
        A = set()
        for p in parents.get(c, ()):
            A.add(p)
            A |= anc(p)
        memo[c] = A
        return A
    rows = set()
    for c in set(edges["child"]):
        for a in anc(c):
            if c != a:
                rows.add((c, a))
    out = pd.DataFrame(sorted(rows), columns=["child", "parent"])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min",  default="datasets/sec_edgar/taxonomy/usgaap_min.csv")
    ap.add_argument("--auto", default="datasets/sec_edgar/taxonomy/usgaap_auto.csv")
    ap.add_argument("--auto_freq", default="datasets/sec_edgar/taxonomy/usgaap_auto_freq.csv")
    ap.add_argument("--out",  default="datasets/sec_edgar/taxonomy/usgaap_combined.csv")
    args = ap.parse_args()

    frames = []
    for p in [args.min, args.auto, args.auto_freq]:
        path = pathlib.Path(p)
        if path.exists():
            frames.append(load_edges(str(path)))

    base = pd.concat(frames, ignore_index=True).drop_duplicates()
    base = add_backbone(base)
    # Remove any remaining self loops
    base = base[base["child"] != base["parent"]].drop_duplicates()

    # Closure
    closed = transitive_closure(base)
    # Union base + closure (keep both direct and ancestor edges)
    out = pd.concat([base, closed], ignore_index=True).drop_duplicates()

    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"wrote {args.out}: edges_base={len(base)} edges_with_closure={len(out)}")

if __name__ == "__main__":
    main()
