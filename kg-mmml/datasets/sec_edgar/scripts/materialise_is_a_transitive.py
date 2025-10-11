# scripts/materialise_is_a_transitive.py
import pandas as pd, collections, sys

inp = sys.argv[1]  # datasets/sec_edgar/taxonomy/usgaap_combined.csv
out = sys.argv[2]  # datasets/sec_edgar/taxonomy/usgaap_combined_closed.csv

df = pd.read_csv(inp)
df.columns = [c.lower() for c in df.columns]
df = df[['child','parent']].dropna()
df = df[df['child'] != df['parent']].drop_duplicates()

parents = collections.defaultdict(set)
for c,p in df.itertuples(index=False):
    parents[c].add(p)

memo = {}
def anc(c):
    if c in memo: return memo[c]
    A = set()
    for p in parents.get(c,()):
        A.add(p)
        A |= anc(p)
    memo[c] = A
    return A

rows = set()
for c in set(df['child']):
    for a in anc(c):
        if c != a:
            rows.add((c,a))

outdf = pd.DataFrame(sorted(rows), columns=['child','parent'])
# union direct + closure
final = pd.concat([df, outdf], ignore_index=True).drop_duplicates()
final.to_csv(out, index=False)
print(f"wrote {out}: direct={len(df)} with_closure={len(final)}")
