import argparse, pathlib
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual", default="datasets/sec_edgar/taxonomy/usgaap_min.csv")
    ap.add_argument("--auto",   default="datasets/sec_edgar/taxonomy/usgaap_auto.csv")
    ap.add_argument("--out",    default="datasets/sec_edgar/taxonomy/usgaap_combined.csv")
    args = ap.parse_args()

    m = pd.read_csv(args.manual)
    a = pd.read_csv(args.auto)
    m["source"] = m.get("source", "manual")
    a["source"] = a.get("source", "auto")
    df = pd.concat([m[["child","parent","source"]], a[["child","parent","source"]]], ignore_index=True)
    df = df.drop_duplicates().reset_index(drop=True)
    outp = pathlib.Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outp, index=False)
    print(f"[combine] manual={len(m)} auto={len(a)} -> combined={len(df)} -> {outp}")

if __name__ == "__main__":
    main()
