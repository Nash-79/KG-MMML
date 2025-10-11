import argparse, json, random, time, pathlib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from scipy import sparse

def build_corpus_from_facts(facts_path):
    import json
    from collections import defaultdict
    def doc_id(rec):
        cik = (rec.get("cik") or "").strip()
        accn = (rec.get("accn") or "").replace("-", "").strip()
        if cik and accn: return f"filing_{cik}_{accn}"
        return None
    def norm_c(ns, c):
        return f"{ns}:{c}" if ns and not c.startswith(ns + ":") else c

    tokens = defaultdict(list)
    with open(facts_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            rec = json.loads(line)
            did = doc_id(rec)
            if not did: continue
            ns, c = rec.get("ns"), rec.get("concept")
            cc = norm_c(ns, c)
            if not cc: continue
            t = cc.split(":",1)[1].lower() if ":" in cc else cc.lower()
            tokens[did].append(t)
    docs = sorted(tokens.keys())
    texts = [" ".join(tokens[d]) for d in docs]
    return docs, texts

def percentiles(ms):
    return {
        "p50_ms": float(np.percentile(ms, 50)),
        "p95_ms": float(np.percentile(ms, 95)),
        "p99_ms": float(np.percentile(ms, 99)),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default="data/processed/sec_edgar/facts.jsonl")
    ap.add_argument("--out",   default="reports/tables/latency_baseline.csv")
    ap.add_argument("--sizes", nargs="+", default=["1000","10000"])
    ap.add_argument("--svd_dim", type=int, default=256, help="Dimensionality for ANN (Annoy)")
    ap.add_argument("--queries", type=int, default=200)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed)
    docs, texts = build_corpus_from_facts(args.facts)

    vec = TfidfVectorizer(min_df=2, max_features=50000)
    X = vec.fit_transform(texts)
    sizes = [min(int(s), X.shape[0]) for s in args.sizes]
    rows = []

    # Optional: ANN via Annoy on SVD-reduced vectors
    try:
        from annoy import AnnoyIndex
        has_annoy = True
    except Exception:
        has_annoy = False

    for N in sizes:
        XN = X[:N]
        # Warmup TF-IDF cosine exact
        q_idx = np.random.choice(N, size=min(args.queries, N), replace=False)
        q = XN[q_idx]

        # Exact mode (cosine via normalised dot-product on sparse)
        tms = []
        XNn = normalize(XN, norm="l2", copy=True)
        qn  = normalize(q,  norm="l2", copy=True)
        # Warm-up
        _ = qn.dot(XNn.T).max(axis=1).toarray().ravel()
        for i in range(qn.shape[0]):
            t0 = time.perf_counter()
            _ = qn[i].dot(XNn.T).toarray().ravel().argpartition(-args.k)[-args.k:]
            tms.append((time.perf_counter() - t0) * 1000.0)
        p = percentiles(tms)
        rows.append({"N":N,"dim":"tfidf","method":"exact-cosine", **p, "q":len(tms), "notes":"sparse dot"})

        # ANN mode (Annoy on dense SVD)
        if has_annoy:
            svd = TruncatedSVD(n_components=args.svd_dim, random_state=args.seed)
            Xd  = svd.fit_transform(XN)  # (N, d)
            Xd  = normalize(Xd, axis=1)
            from annoy import AnnoyIndex
            ann = AnnoyIndex(args.svd_dim, metric='angular')
            for i in range(N):
                ann.add_item(i, Xd[i].astype(np.float32).tolist())
            ann.build(20)  # trees
            # warm-up
            _ = ann.get_nns_by_vector(Xd[q_idx[0]].astype(np.float32).tolist(), args.k)
            tms = []
            for i in q_idx:
                t0 = time.perf_counter()
                _ = ann.get_nns_by_vector(Xd[i].astype(np.float32).tolist(), args.k)
                tms.append((time.perf_counter() - t0) * 1000.0)
            p = percentiles(tms)
            rows.append({"N":N,"dim":args.svd_dim,"method":"annoy-hnsw-ish", **p, "q":len(tms), "notes":"20 trees"})
        else:
            rows.append({"N":N,"dim":"-", "method":"ANN-missing", "p50_ms":None,"p95_ms":None,"p99_ms":None,"q":0,"notes":"pip install annoy"})

    outp = pathlib.Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(outp, index=False)
    print(f"[latency] wrote {outp}")

if __name__ == "__main__":
    main()
