# Outputs Directory

Experimental outputs and model artifacts from training runs.

## Purpose

Stores experiment outputs during active development and testing. This directory is git-ignored to avoid committing large model files and intermediate results.

## Structure

Outputs are organized by experiment name matching configs:

```
outputs/
├── <experiment_name>/
│   ├── metrics.json          # Performance metrics
│   ├── model.pkl             # Trained model (if applicable)
│   ├── predictions.csv       # Test set predictions
│   └── logs/                 # Training logs
└── README.md                 # This file
```

## Current Status

All M5 PyTorch joint model experiments archived to archive/outputs/m5_joint_ablations/ as of Week 11-12 M6 consolidation.

Production baseline uses sklearn LogisticRegression (text + concept features). Metrics stored in reports/tables/ (consolidated). No separate output directory needed since sklearn trains quickly and metrics are logged directly.

## Guidelines

Belongs here:
- Active experiment outputs during M7-M9 testing
- Model checkpoints from training runs
- Intermediate predictions for error analysis
- Experiment-specific logs and artifacts

Does not belong here:
- Final consolidated metrics (use reports/tables/)
- Production model configs (use configs/)
- Completed experiments (archive to archive/outputs/<milestone>/)
- Source code or data (use src/ and data/ respectively)

## Archiving

After completing a milestone or experiment series:
1. Move experiment directories to archive/outputs/<milestone_name>/
2. Create a README in the archive explaining the experiments
3. Keep only active/in-progress experiments in outputs/
4. Update this file to reflect current status

## Current Experiments

None. Directory cleaned as of Week 11-12 M6 consolidation.

Future experiments (M7 onwards) will create new subdirectories as needed.

## References

- Experiment configs: configs/
- Consolidated results: reports/tables/
- Archived experiments: archive/outputs/
- Progress tracking: docs/progress/
