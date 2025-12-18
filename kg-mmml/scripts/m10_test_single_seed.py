#!/usr/bin/env python3
"""
M10 Quick Test: Single Seed Validation

Quick test script to verify the M10 pipeline works before running all 5 seeds.
Runs experiments for seed=42 only.

Usage:
    python scripts/m10_test_single_seed.py

This is useful for:
- Verifying paths are correct
- Testing experiment runtime
- Debugging before full 5-seed run
"""
import subprocess
import sys
import pathlib
import json
import os
from datetime import datetime


def main():
    # Set PYTHONPATH to include kg-mmml/src for imports
    env = os.environ.copy()
    kg_mmml_root = pathlib.Path(__file__).parent.parent.absolute()
    env['PYTHONPATH'] = str(kg_mmml_root / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    print("="*70)
    print("M10 QUICK TEST: Single Seed (seed=42)")
    print("="*70)

    start_time = datetime.now()

    # Test baseline experiment
    print("\n[1/2] Testing baseline (text-only) experiment...")
    baseline_cmd = [
        sys.executable, "kg-mmml/src/cli/baseline_tfidf.py",
        "--facts", "kg-mmml/data/processed/sec_edgar/facts.jsonl",
        "--taxonomy", "kg-mmml/datasets/sec_edgar/taxonomy/usgaap_combined.csv",
        "--out", "kg-mmml/reports/tables/m10_test_seed42_baseline.json",
        "--random_state", "42",
        "--test_size", "0.25",
    ]

    print(f"Command: {' '.join(baseline_cmd)}")
    result = subprocess.run(baseline_cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        print("FAILED: Baseline experiment")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    baseline_metrics = json.loads(pathlib.Path("kg-mmml/reports/tables/m10_test_seed42_baseline.json").read_text())
    print(f"PASS: Baseline: micro_f1={baseline_metrics['micro_f1']:.4f}, macro_f1={baseline_metrics['macro_f1']:.4f}")

    # Test text+concept experiment
    print("\n[2/2] Testing text+concept experiment...")
    text_concept_cmd = [
        sys.executable, "kg-mmml/src/cli/baseline_tfidf.py",
        "--facts", "kg-mmml/data/processed/sec_edgar/facts.jsonl",
        "--taxonomy", "kg-mmml/datasets/sec_edgar/taxonomy/usgaap_combined.csv",
        "--concept_features_npz", "kg-mmml/data/processed/sec_edgar/features/concept_features_filing.npz",
        "--concept_features_index", "kg-mmml/data/processed/sec_edgar/features/concept_features_index.csv",
        "--out", "kg-mmml/reports/tables/m10_test_seed42_text_concept.json",
        "--random_state", "42",
        "--test_size", "0.25",
    ]

    print(f"Command: {' '.join(text_concept_cmd)}")
    result = subprocess.run(text_concept_cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        print("FAILED: Text+concept experiment")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    text_concept_metrics = json.loads(pathlib.Path("kg-mmml/reports/tables/m10_test_seed42_text_concept.json").read_text())
    print(f"PASS: Text+concept: micro_f1={text_concept_metrics['micro_f1']:.4f}, macro_f1={text_concept_metrics['macro_f1']:.4f}")

    # Compute improvement
    micro_improvement = (text_concept_metrics['micro_f1'] - baseline_metrics['micro_f1']) * 100
    macro_improvement = (text_concept_metrics['macro_f1'] - baseline_metrics['macro_f1']) * 100

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*70)
    print("M10 QUICK TEST: PASSED")
    print("="*70)
    print(f"Duration: {duration:.1f}s")
    print(f"\nResults (seed=42):")
    print(f"  Micro-F1 improvement: {micro_improvement:+.2f}pp")
    print(f"  Macro-F1 improvement: {macro_improvement:+.2f}pp")
    print(f"\nEstimated time for 5 seeds: ~{duration * 2 * 5 / 60:.1f} minutes")
    print("\nNext step: Run full validation with:")
    print("  python scripts/run_m10_all.py")
    print("="*70)


if __name__ == "__main__":
    main()
