import json, argparse, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="data/raw/sec_edgar/index.json")
    ap.add_argument("--out", default="data/raw/sec_edgar/selected.json")
    ap.add_argument("--limit", type=int, default=1, help="per form type per company")
    args = ap.parse_args()

    idx = json.loads(pathlib.Path(args.index).read_text())
    selected = {}
    for cik, meta in idx.get("ok", {}).items():
        p = pathlib.Path(meta["submissions_json"])
        if not p.exists():
            print(f"Warning: missing {p}")
            continue
        j = json.loads(p.read_text())
        recent = j.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accns = recent.get("accessionNumber", [])
        primdocs = recent.get("primaryDocument", [])
        out = {"10-K": [], "10-Q": []}
        for form, accn, doc in zip(forms, accns, primdocs):
            if form in ("10-K", "10-Q"):
                out[form].append({"accession": accn, "doc": doc})
        out["10-K"] = out["10-K"][:args.limit]
        out["10-Q"] = out["10-Q"][:args.limit]
        selected[cik] = out

    pathlib.Path(args.out).write_text(json.dumps(selected, indent=2))
    print(f"Saved {args.out}")

if __name__ == "__main__":
    main()