# scripts/fix_taxonomy_columns.py
import pandas as pd, pathlib, sys, re

inp = "datasets/sec_edgar/taxonomy/usgaap_combined.csv"
out = "datasets/sec_edgar/taxonomy/usgaap_combined.fixed.csv"

df = pd.read_csv(inp)
cols = {c.lower(): c for c in df.columns}

# Map to lower-case view
def get(col):
    return df[cols[col]]

# Try to detect swapped columns
if "child" in cols and "parent" in cols:
    child = get("child").astype(str)
    parent = get("parent").astype(str)
else:
    # If we mistakenly saved as parent,child order, try to guess
    if "parent" in cols and "child" not in cols:
        # hope second column is child
        raw = df.copy()
        parent = raw.iloc[:,0].astype(str)
        child  = raw.iloc[:,1].astype(str)
    else:
        raise SystemExit("Could not identify child/parent columns. Please ensure headers exist.")

# Normalise to 'us-gaap:' prefix exactly once
def norm(s):
    s = s.strip()
    if ":" in s:
        ns, name = s.split(":",1)
        return f"{ns}:{name}"
    # if it looks like a US GAAP name without ns, add ns
    if re.match(r"^[A-Za-z0-9].*", s) and not s.startswith("us-gaap:"):
        return f"us-gaap:{s}"
    return s

child = child.map(norm)
parent= parent.map(norm)

fixed = pd.DataFrame({"child": child, "parent": parent})
fixed = fixed.dropna().drop_duplicates()
fixed.to_csv(out, index=False)
print(f"Wrote {out} rows={len(fixed)}")
