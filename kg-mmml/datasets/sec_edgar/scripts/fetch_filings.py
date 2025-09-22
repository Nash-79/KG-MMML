"""Fetch SEC filings index and filings (free endpoints).
This is a scaffold. Replace TODOs with requests to data.sec.gov respecting rate limits and user-agent header.
"""
import argparse, os, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ciks', nargs='+', required=True, help='List of CIKs (zero-padded)')
    ap.add_argument('--out', default='downloads')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    # TODO: Implement fetch from SEC submissions endpoint (free). Save JSON.
    index = {cik: {'status': 'stub'} for cik in args.ciks}
    with open(os.path.join(args.out, 'index.json'),'w') as f:
        json.dump(index, f, indent=2)
    print('Saved', os.path.join(args.out, 'index.json'))

if __name__ == '__main__':
    main()

