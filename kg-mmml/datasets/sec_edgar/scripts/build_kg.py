"""Build KG CSVs from parsed filings + taxonomy map (stub)."""
import argparse, os, csv, json
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', required=True, help='index.json from fetch step')
    ap.add_argument('--outdir', default='kg')
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    nodes_path = os.path.join(args.outdir, 'kg_nodes.csv')
    edges_path = os.path.join(args.outdir, 'kg_edges.csv')
    with open(nodes_path,'w',newline='') as nf, open(edges_path,'w',newline='') as ef:
        nw, ew = csv.writer(nf), csv.writer(ef)
        nw.writerow(['node_id','type','attrs_json'])
        ew.writerow(['src_id','edge_type','dst_id','attrs_json'])
        nw.writerow(['example_company','Company', json.dumps({'name':'Example Co'})])
        ew.writerow(['example_company','reports','filing_example', json.dumps({})])
    print('Wrote', nodes_path, edges_path)
if __name__ == '__main__':
    main()

