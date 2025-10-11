import argparse, json, pathlib, re
from collections import defaultdict, Counter

FAMILIES = [
  (re.compile(r"^AccountsReceivable.*", re.I), "us-gaap:CurrentAssets"),
  (re.compile(r"^AccountsPayable.*", re.I), "us-gaap:CurrentLiabilities"),
  (re.compile(r"^Inventory.*", re.I), "us-gaap:CurrentAssets"),
  (re.compile(r"^PropertyPlantAndEquipment.*", re.I), "us-gaap:NoncurrentAssets"),
  (re.compile(r"^Goodwill$|^.*IntangibleAssets.*$", re.I), "us-gaap:NoncurrentAssets"),
  (re.compile(r"^OperatingLeaseRightOfUseAsset.*$", re.I), "us-gaap:NoncurrentAssets"),
  (re.compile(r"^OperatingLeaseLiability.*$", re.I), "us-gaap:NoncurrentLiabilities"),
  (re.compile(r"^DeferredRevenue.*$|^ContractWithCustomerLiability.*$", re.I), "us-gaap:CurrentLiabilities"),
  (re.compile(r"^ResearchAndDevelopmentExpense.*$", re.I), "us-gaap:OperatingExpenses"),
  (re.compile(r"^SellingGeneralAndAdministrativeExpense.*$", re.I), "us-gaap:OperatingExpenses"),
  (re.compile(r"^RevenueFromContractWithCustomer.*$|^SalesRevenueNet.*$", re.I), "us-gaap:Revenues"),
  (re.compile(r"^CostOfRevenue.*$|^CostOfGoodsSold.*$", re.I), "us-gaap:CostOfRevenue"),
  (re.compile(r"^IncomeTax.*(Expense|Benefit).*$", re.I), "us-gaap:IncomeTaxExpenseBenefit"),
  (re.compile(r"^InterestExpense.*$", re.I), "us-gaap:InterestExpense"),
  (re.compile(r"^EarningsPerShareDiluted.*$", re.I), "us-gaap:EarningsPerShareDiluted"),
]

def load_short_concepts(facts):
    short2ciks=defaultdict(set)
    with open(facts,"r",encoding="utf-8") as f:
        for ln in f:
            if not ln.strip(): continue
            r=json.loads(ln)
            ns=(r.get("ns") or "").strip()
            c =(r.get("concept") or "").strip()
            cik=(r.get("cik") or "").strip()
            if not c: continue
            short = c if ":" not in c else c.split(":",1)[1]
            short2ciks[short].add(cik)
    return {s: len(cs) for s,cs in short2ciks.items()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--facts", required=True)
    ap.add_argument("--out",   required=True)
    ap.add_argument("--min_cik_support", type=int, default=3)
    ap.add_argument("--max_edges_per_child", type=int, default=1)
    args=ap.parse_args()

    support = load_short_concepts(args.facts)
    rows=[]
    for short, cnt in support.items():
        if cnt < args.min_cik_support: continue
        added=0
        for rx,parent in FAMILIES:
            if rx.match(short):
                child_full = f"us-gaap:{short}"
                rows.append((child_full, parent))
                added+=1
                if added >= args.max_edges_per_child: break

    outp=pathlib.Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w",encoding="utf-8") as w:
        w.write("child,parent,source\n")
        for c,p in sorted(set(rows)):
            w.write(f"{c},{p},auto-freq\n")
    print(f"[freq_booster] wrote {outp} edges={len(set(rows))} (min_cik_support={args.min_cik_support})")

if __name__=="__main__":
    main()
