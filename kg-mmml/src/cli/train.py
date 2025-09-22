import argparse, yaml, time, json, os, random, numpy as np, torch

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    run_id = f"{cfg['experiment']['name']}_{int(time.time())}"
    os.makedirs("reports/tables", exist_ok=True)

    for s in cfg["experiment"].get("seeds",[13]):
        set_seed(s)
        # TODO: load data/model, train/eval; write metrics
    metrics = {"map": 0.00, "f1_zero_shot": 0.00, "seed_count": len(cfg["experiment"].get("seeds",[13]))}
    json.dump(metrics, open(f"reports/tables/{run_id}_metrics.json","w"))
    print("Saved:", f"reports/tables/{run_id}_metrics.json")

if __name__ == "__main__":
    main()
