# scripts/normalise_taxonomy.py
import pandas as pd, re
inp="datasets/sec_edgar/taxonomy/usgaap_combined.csv"
out="datasets/sec_edgar/taxonomy/usgaap_combined.normalised.csv"
df=pd.read_csv(inp)
df.columns=[c.lower() for c in df.columns]
def norm(s):
    s=str(s).strip()
    if not s: return s
    if ":" in s:
        ns,name=s.split(":",1)
        return f"{ns}:{name}"
    return f"us-gaap:{s}"
df['child']=df['child'].map(norm)
df['parent']=df['parent'].map(norm)
df=df.drop_duplicates(subset=['child','parent'])
df.to_csv(out,index=False)
print("wrote",out,"rows",len(df))
