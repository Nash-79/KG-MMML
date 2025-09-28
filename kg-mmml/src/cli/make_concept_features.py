# src/cli/make_concept_features.py
import argparse, json, pathlib, re
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from scipy import sparse

def normalise_concept(ns, concept):
    ns = (ns or "").strip()
    c  = (concept or "").strip()
    if not c: return None
    if ns and not c.startswith(ns + ":"):
        return f"{ns}:{c}"
    return c

def doc_id_from_fact(rec):
    cik = (rec.get("cik") or "").strip()
    accn = (rec.get("accn") or "").replace("-", "").strip()
    if cik and accn:
        return f"filing_{cik}_{accn}"
    elif cik:
        return f"company_{cik}"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default="data/processed/sec_edgar/facts.jsonl")
    ap.add_argument("--outdir", default="data/processed/sec_edgar/features")
    ap.add_argument("--vocab_size", type=int, default=5000, help="Top-K concepts by document frequency")
    ap.add_argument("--binary", action="store_true", help="Use binary features instead of counts")
    args = ap.parse_args()

    facts_path = pathlib.Path(args.facts)
    outdir = pathlib.Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    # Collect per-document concept sets
    doc_concepts = defaultdict(Counter)
    df_counts = Counter()

    with facts_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rec = json.loads(line)
            did = doc_id_from_fact(rec)
            if not did: continue
            c = normalise_concept(rec.get("ns"), rec.get("concept"))
            if not c: continue
            doc_concepts[did][c] += 1

    # Build vocabulary by document frequency
    for did, bag in doc_concepts.items():
        for c in bag.keys():
            df_counts[c] += 1

    vocab = [c for c, _ in df_counts.most_common(args.vocab_size)]
    vocab_index = {c:i for i,c in enumerate(vocab)}
    docs = sorted(doc_concepts.keys())
    doc_index = {d:i for i,d in enumerate(docs)}

    rows, cols, data = [], [], []
    for d in docs:
        for c, cnt in doc_concepts[d].items():
            j = vocab_index.get(c)
            if j is None: continue
            rows.append(doc_index[d]); cols.append(j); data.append(1 if args.binary else cnt)

    X = sparse.csr_matrix((data, (rows, cols)), shape=(len(docs), len(vocab)), dtype=np.float32)

    # Save outputs
    npz_path = outdir / "concept_features_filing.npz"
    sparse.save_npz(npz_path, X)
    pd.DataFrame({"doc_id": docs}).to_csv(outdir/"concept_features_index.csv", index=False)
    pd.DataFrame({"concept": vocab}).to_csv(outdir/"concept_features_vocab.csv", index=False)

    print(f"[concept-features] docs={len(docs)} vocab={len(vocab)} nnz={X.nnz} -> {npz_path}")

if __name__ == "__main__":
    main()
