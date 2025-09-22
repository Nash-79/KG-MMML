setup:
\tpython -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e .

run:
\tpython -m src.cli.train --config $(CONFIG)

srs:
\tpython -m src.cli.compute_srs --config $(CONFIG) --out reports/tables/srs.csv

latency:
\tpython -m src.cli.evaluate_latency --config configs/system_hybrid.yaml --out reports/tables/latency.csv
