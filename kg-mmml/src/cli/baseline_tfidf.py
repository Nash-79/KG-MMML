# src/cli/baseline_tfidf.py
import argparse, json, pathlib, random
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score, classification_report
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

def load_taxonomy_parents(tax_path):
    tax = pd.read_csv(tax_path)
    # map child -> parent (many-to-one ok for this baseline)
    child_to_parents = defaultdict(set)
    for _, row in tax.iterrows():
        child = str(row["child"]).strip()
        parent = str(row["parent"]).strip()
        if child and parent:
            child_to_parents[child].add(parent)
    return child_to_parents

def build_corpus_from_facts(facts_path, child_to_parents):
    """
    Returns:
      docs: list of doc_ids
      texts: list of "documents" (space-joined concept tokens)
      labels: list of sets of parent labels (us-gaap:* parents)
    """
    doc_tokens = defaultdict(list)
    doc_labels = defaultdict(set)

    with open(facts_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rec = json.loads(line)
            did = doc_id_from_fact(rec)
            if not did: continue
            c = normalise_concept(rec.get("ns"), rec.get("concept"))
            if not c: continue
            # tokenise by using concept surface minus prefix
            base = c.split(":", 1)[1] if ":" in c else c
            token = base.lower()
            doc_tokens[did].append(token)
            # add parent labels if known
            for p in child_to_parents.get(c, []):
                doc_labels[did].add(p)

    docs = sorted(doc_tokens.keys())
    texts = [" ".join(doc_tokens[d]) for d in docs]
    labels = [sorted(doc_labels[d]) for d in docs]
    return docs, texts, labels

def align_and_concat(X_text, tfidf_docs, concept_npz, concept_index_csv, tfidf_docs_list):
    """Align concept-feature rows to TF-IDF rows and hstack."""
    from scipy.sparse import csr_matrix, load_npz
    Xc = sparse.load_npz(concept_npz)
    idx = pd.read_csv(concept_index_csv)["doc_id"].tolist()
    row_of = {d:i for i,d in enumerate(idx)}
    # build aligned rows for concept features
    rows = []
    for d in tfidf_docs_list:
        i = row_of.get(d, None)
        rows.append(i)
    # select rows, using empty row if missing
    sel = []
    for r in rows:
        if r is None:
            sel.append(sparse.csr_matrix((1, Xc.shape[1]), dtype=Xc.dtype))
        else:
            sel.append(Xc[r])
    Xc_aligned = sparse.vstack(sel)
    return sparse.hstack([X_text, Xc_aligned], format="csr")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default="data/processed/sec_edgar/facts.jsonl")
    ap.add_argument("--taxonomy", default="datasets/sec_edgar/taxonomy/usgaap_combined.csv")
    ap.add_argument("--out", default="reports/tables/baseline_text_metrics.json")

    ap.add_argument("--test_size", type=float, default=0.25)
    ap.add_argument("--random_state", type=int, default=42)
    ap.add_argument("--max_features", type=int, default=20000)
    ap.add_argument("--min_df", type=int, default=2)

    # Optional KG-as-features concatenation
    ap.add_argument("--concept_features_npz", default="", help="Path to concept_features_filing.npz")
    ap.add_argument("--concept_features_index", default="", help="Path to concept_features_index.csv")
    args = ap.parse_args()

    tax_path = pathlib.Path(args.taxonomy)
    if not tax_path.exists():
        # Fallback to minimal taxonomy
        tax_path = pathlib.Path("datasets/sec_edgar/taxonomy/usgaap_min.csv")

    child_to_parents = load_taxonomy_parents(tax_path)
    docs, texts, labels = build_corpus_from_facts(args.facts, child_to_parents)

    # Filter docs with no labels (cannot supervise without at least 1 parent)
    keep = [i for i,l in enumerate(labels) if len(l) > 0]
    docs = [docs[i] for i in keep]
    texts = [texts[i] for i in keep]
    labels = [labels[i] for i in keep]

    if len(docs) < 20:
        raise RuntimeError("Not enough labelled docs inferred from taxonomy. Add more taxonomy pairs or facts.")

    # Multi-label binarisation
    mlb = MultiLabelBinarizer(sparse_output=False)
    Y = mlb.fit_transform(labels)
    label_names = list(mlb.classes_)  # us-gaap:* parents

    # TF-IDF text features
    vec = TfidfVectorizer(max_features=args.max_features, min_df=args.min_df)
    X_text = vec.fit_transform(texts)

    # Optional: add concept features (KG-as-features)
    if args.concept_features_npz and args.concept_features_index:
        X = align_and_concat(X_text, docs, args.concept_features_npz, args.concept_features_index, docs)
        mode = "text+concept"
    else:
        X = X_text
        mode = "text"

    # Train/test split (simple random split on documents)
    rng = np.random.RandomState(args.random_state)
    n = len(docs)
    idx = np.arange(n)
    rng.shuffle(idx)
    split = int(n * (1.0 - args.test_size))
    train_idx, test_idx = idx[:split], idx[split:]

    Xtr, Xte = X[train_idx], X[test_idx]
    Ytr, Yte = Y[train_idx], Y[test_idx]
    docs_te = [docs[i] for i in test_idx]

    # Classifier
    clf = OneVsRestClassifier(
        LogisticRegression(max_iter=200, n_jobs=None, solver="liblinear")
    )
    clf.fit(Xtr, Ytr)
    Yhat = clf.predict(Xte)

    metrics = {
        "mode": mode,
        "n_docs_total": n,
        "n_docs_train": int(Xtr.shape[0]),
        "n_docs_test": int(Xte.shape[0]),
        "micro_f1": float(f1_score(Yte, Yhat, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(Yte, Yhat, average="macro", zero_division=0)),
        "labels": label_names,
    }

    # Per-label report
    report = classification_report(Yte, Yhat, target_names=label_names, output_dict=True, zero_division=0)
    metrics["per_label"] = report

    outp = pathlib.Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(metrics, indent=2))
    print(f"[baseline] wrote {args.out}")
    print(json.dumps({k: metrics[k] for k in ["mode","micro_f1","macro_f1"]}, indent=2))

if __name__ == "__main__":
    main()
