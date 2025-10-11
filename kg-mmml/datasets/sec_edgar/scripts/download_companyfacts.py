import argparse, json, pathlib, time, requests

UA = "NareshMepani-MScProject/1.0 (your.email@example.com)"
FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

def zfill10(x): return "".join(ch for ch in x if ch.isdigit()).zfill(10)

def fetch_json(url, sleep=0.2):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    time.sleep(sleep)
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selected", default="data/raw/sec_edgar/selected.json")
    ap.add_argument("--outdir", default="data/processed/sec_edgar/companyfacts")
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args()

    sel = json.loads(pathlib.Path(args.selected).read_text())
    outdir = pathlib.Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    index = {"ok": {}, "missing": []}
    for cik in sel.keys():
        cik10 = zfill10(cik)
        url = FACTS.format(cik=cik10)
        data = fetch_json(url, sleep=args.sleep)
        if data is None:
            index["missing"].append(cik10); continue
        p = outdir / f"companyfacts_{cik10}.json"
        p.write_text(json.dumps(data, indent=2))
        index["ok"][cik10] = str(p)

    (outdir/"index.json").write_text(json.dumps(index, indent=2))
    print(f"Saved facts for {len(index['ok'])} CIKs -> {outdir/'index.json'}")

if __name__ == "__main__":
    main()
