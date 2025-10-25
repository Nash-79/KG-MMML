# src/cli/make_concept_features.py
"""
Generate concept feature matrices for KG-as-features baseline.

This script creates binary or count-based concept feature matrices from
SEC EDGAR facts. Concepts are extracted from filings and converted into
sparse feature vectors that can be concatenated with text features (TF-IDF)
for baseline classification.

The script generates:
1. concept_features_filing.npz - Sparse matrix (n_docs × n_concepts)
2. concept_features_index.csv - Document ID to row mapping
3. concept_features_vocab.csv - Concept vocabulary

Week 9 generation stats:
    - 4,502 concepts (top by document frequency)
    - 563,622 non-zero entries (binary indicators)
    - 3,218 documents

Usage:
    python -m src.cli.make_concept_features \\
        --facts data/processed/sec_edgar/facts.jsonl \\
        --outdir data/processed/sec_edgar/features \\
        --vocab_size 5000 --binary

Results:
    Text+concept features improve classification by +2.27pp macro-F1
    and +1.36pp micro-F1 compared to text-only baseline.
"""
import argparse
import pathlib
import numpy as np
import pandas as pd
from collections import Counter
from scipy import sparse

from ..utils.data_utils import build_corpus_from_facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default="data/processed/sec_edgar/facts.jsonl")
    ap.add_argument("--outdir", default="data/processed/sec_edgar/features")
    ap.add_argument("--vocab_size", type=int, default=5000,
                    help="Top-K concepts by document frequency")
    ap.add_argument("--binary", action="store_true",
                    help="Use binary features instead of counts")
    args = ap.parse_args()
    
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Build corpus (no taxonomy needed)
    docs, _, _, concept_lists = build_corpus_from_facts(args.facts)
    
    # Count document frequency for each concept
    df_counts = Counter()
    doc_concept_counts = {}
    
    for i, concepts in enumerate(concept_lists):
        counts = Counter(concepts)
        doc_concept_counts[docs[i]] = counts
        for c in counts.keys():
            df_counts[c] += 1
    
    # Build vocabulary by document frequency
    vocab = [c for c, _ in df_counts.most_common(args.vocab_size)]
    vocab_index = {c: i for i, c in enumerate(vocab)}
    doc_index = {d: i for i, d in enumerate(docs)}
    
    rows, cols, data = [], [], []
    for d in docs:
        for c, cnt in doc_concept_counts[d].items():
            j = vocab_index.get(c)
            if j is None:
                continue
            rows.append(doc_index[d])
            cols.append(j)
            data.append(1 if args.binary else cnt)
    
    X = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(len(docs), len(vocab)),
        dtype=np.float32
    )
    
    # Save outputs
    npz_path = outdir / "concept_features_filing.npz"
    sparse.save_npz(npz_path, X)
    pd.DataFrame({"doc_id": docs}).to_csv(
        outdir / "concept_features_index.csv", index=False
    )
    pd.DataFrame({"concept": vocab}).to_csv(
        outdir / "concept_features_vocab.csv", index=False
    )
    
    print(f"[concept-features] docs={len(docs)} vocab={len(vocab)} "
          f"nnz={X.nnz} -> {npz_path}")


if __name__ == "__main__":
    main()