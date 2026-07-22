# Repository cleanup audit

## Retained

Core code under `src/data`, `src/evaluation`, `src/pipeline`, `src/preprocessing`, `src/segmentation`, `src/ui`, and `src/utils`; the required scripts; `app.py`; main/recovery configurations; tests; article tables; and nine representative cases.

## Archived

Early morphology configurations, method-ablation configurations and runner, and two superseded notebooks. Large method-ablation outputs are externally backed up and documented in `archive/README.md`.

## Removed from the article branch

Development output trees, stale project tree, and 3,504 large method-ablation artifacts. They remain recoverable from the checkpoint/tag and verified external backup.

## Dependencies and risks

`app.py`, pipeline, and scripts depend on `apsrg_baseline.py` and `ca_apsrg.py`; the clean `srg.py` and `apsrg.py` wrappers reuse those actual APIs. `ca_apsrg.py` owns refinement while seed selection/growing remain in their specialized modules. Remaining risks: adapted APSRG is not IUWT-exact; output backup paths are workstation-local; remote push is pending; license is undecided.
