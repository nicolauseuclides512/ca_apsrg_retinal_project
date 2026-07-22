# SRG → adapted APSRG → CA-APSRG

Research repository for retinal-vessel segmentation on DRIVE, STARE, and CHASEDB1. The scientific path is explicit: SRG provides fuzzy seed support and connected-edge, edge-delayed growing; the **adapted APSRG baseline** adds automatic Harris polling; CA-APSRG refines the resulting APSRG mask using context and conservative adaptive morphology.

This APSRG implementation is adapted to the preprocessing and vessel-enhancement pipeline in this repository. It is not claimed as an exact reproduction of the original IUWT-based method.

## Methods

- **SRG:** fuzzy SRG features and seeds, connected-edge processing, and edge-delayed region growing; no Harris and no context refinement. Entry point: `segment_with_srg`.
- **adapted APSRG baseline:** fuzzy support, Harris-based automatic seed polling, and seeded region growing; no context refinement. Entry point: `segment_with_apsrg`.
- **CA-APSRG:** selective fuzzy–Harris seeds, target seed recovery, radius-1 dilation, edge-delayed growing, local-or-region acceptance, process-context extraction, and conservative adaptive morphology. Its CA-specific boundary is `ca_apsrg_refine`: APSRG mask → context extraction → refinement decision → adaptive morphology → CA-APSRG mask.

The principal improvements come from seed recovery, selective fuzzy–Harris polling, and local-or-region acceptance. Adaptive morphology is intentionally conservative. Process-context override is not claimed to improve accuracy: R04 and R06 produced identical masks in the recorded experiment.

## Configurations and results

Article-facing configurations are in `configs/main_methods/`: `srg_baseline.yaml`, `apsrg_baseline.yaml`, and the principal candidate `ca_apsrg_r04.yaml`. `configs/default.yaml` is retained for historical/development use and is not the final article configuration.

Recovery ablation:

| ID | Change |
|---|---|
| R00 | legacy percentile polling + BFS control |
| R01 | selective fuzzy–Harris, 35 seeds, BFS |
| R02 | target recovery to 77 seeds, radius 1, BFS |
| R03 | edge-delayed, region-mean acceptance |
| R04 | edge-delayed, local-or-region acceptance; principal candidate |
| R05 | R04 with hybrid priority |
| R06 | R04 with process-context override; identical to R04 here |

Mean CA-APSRG F1 for R00 → R04 was 0.5573 → 0.6016 on CHASEDB1, 0.6979 → 0.7056 on DRIVE, and 0.6454 → 0.6435 on STARE. Full article tables and process-context diagnostics are versioned in `results/tables/`; nine best/typical/worst examples are in `results/representative_cases/`. These values are preserved experimental results, not recomputed claims.

## Install and data

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/00_convert_all_to_png.py --input-root "data/raw/Retinal Vessel" --output-root data/working_png --copy-png --binarize-masks
python scripts/01_build_manifest.py --working-root data/working_png --output data/manifests/manifest.csv
```

Raw data and working PNGs are ignored by Git. Dataset annotations remain governed by their original dataset terms.

## Run

```powershell
# one image
python scripts/02_run_single_image.py --manifest data/manifests/manifest.csv --dataset DRIVE --image-id 23 --config configs/main_methods/ca_apsrg_r04.yaml

# batch
python scripts/03_run_batch.py --manifest data/manifests/manifest.csv --dataset DRIVE --config configs/main_methods/ca_apsrg_r04.yaml --output-dir outputs/smoke_or_batch

# recovery ablation and diagnostics
python scripts/07_run_recovery_ablation.py --dataset DRIVE --dataset STARE --dataset CHASEDB1
python scripts/08_export_process_context_diagnostics.py

# application
streamlit run app.py
```

Streamlit provides Home, Single Image Demo, Batch Result Viewer, Recovery Ablation R00–R06, Method Explanation, and About Dataset. The recovery viewer includes overview, APSRG versus CA-APSRG, stage/delta analysis, process-context diagnostics, representative cases, image browsing, and CSV tables when artifacts are available.

## Validation

```powershell
python -m compileall src
python -m compileall scripts
python -m py_compile app.py
python -m pytest -q
```

The smoke tests should use only one to three images and a separate output directory so recorded results are never overwritten.

## Limitations and future work

Performance gains vary across datasets and R04 is slightly below R00 on STARE. APSRG preprocessing is adapted rather than an exact IUWT reproduction. Process-context thresholds remain insufficiently calibrated, adaptive morphology changes few pixels, and no clinical validation has been performed. Future work includes dataset-aware context calibration, topology/width-aware growing, broader datasets, deep-learning comparisons, and runtime optimization.

## Citation, license, and clinical disclaimer

Until the article is published, cite this repository and its maintained URL. No `LICENSE` file has been selected; reuse rights therefore require the owner's permission. This software is for research only and **is not a clinical diagnostic tool**.
