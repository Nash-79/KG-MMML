# src/cli/train.py
import argparse, yaml, time, json, os, random, pathlib
import numpy as np, torch
from src.utils.data_utils import build_corpus_from_facts

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)

def load_taxonomy(path):
    import pandas as pd
    df = pd.read_csv(path)
    mp = {}
    for _, r in df.iterrows():
        c, p = str(r["child"]).strip(), str(r["parent"]).strip()
        if c and p: mp.setdefault(c, set()).add(p)
    return mp

def run_baseline(cfg, seed):
    """TF-IDF baseline."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import MultiLabelBinarizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    
    set_seed(seed)
    tax = load_taxonomy(cfg["data"]["taxonomy"])
    docs, texts, labels, _ = build_corpus_from_facts(cfg["data"]["facts"], tax)
    
    # Filter docs with labels
    keep = [i for i, l in enumerate(labels) if len(l) > 0]
    texts = [texts[i] for i in keep]
    labels = [labels[i] for i in keep]
    
    # Features
    vec = TfidfVectorizer(min_df=2, max_features=20000)
    X = vec.fit_transform(texts)
    
    # Labels
    mlb = MultiLabelBinarizer(sparse_output=False)
    Y = mlb.fit_transform(labels)
    
    # Split
    Xtr, Xte, Ytr, Yte = train_test_split(X, Y, test_size=0.25, random_state=seed)
    
    # Train
    clf = OneVsRestClassifier(LogisticRegression(max_iter=200, solver="liblinear"))
    clf.fit(Xtr, Ytr)
    Yhat = clf.predict(Xte)
    
    return {
        "micro_f1": float(f1_score(Yte, Yhat, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(Yte, Yhat, average="macro", zero_division=0)),
    }

def run_joint(cfg, seed):
    """Joint model with consistency loss."""
    # Import train_joint logic here or refactor into module
    # Currently not used - use train_joint.py directly instead
    return {"micro_f1": 0.0, "macro_f1": 0.0}  # Placeholder

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    
    cfg = yaml.safe_load(open(args.config))
    model_type = cfg.get("model", {}).get("type", "vl_baseline")
    run_id = f"{cfg['experiment']['name']}_{int(time.time())}"
    os.makedirs("reports/tables", exist_ok=True)
    
    results = []
    for s in cfg["experiment"].get("seeds", [13]):
        if model_type == "vl_baseline":
            metrics = run_baseline(cfg, s)
        elif model_type == "joint_model":
            metrics = run_joint(cfg, s)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        metrics["seed"] = s
        results.append(metrics)
    
    # Aggregate
    agg = {
        "micro_f1_mean": float(np.mean([r["micro_f1"] for r in results])),
        "micro_f1_std": float(np.std([r["micro_f1"] for r in results])),
        "macro_f1_mean": float(np.mean([r["macro_f1"] for r in results])),
        "seeds": cfg["experiment"]["seeds"],
        "per_seed": results,
    }
    
    out_path = pathlib.Path(f"reports/tables/{run_id}_metrics.json")
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"Saved: {out_path}")
    print(json.dumps({k: v for k, v in agg.items() if k != "per_seed"}, indent=2))

if __name__ == "__main__":
    main()