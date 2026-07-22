# Journal cleanup report

## Summary

The repository now follows SRG → adapted APSRG → CA-APSRG, with clean public wrappers, three main configurations, article tables, nine representative cases, focused tests, and an article-facing Streamlit dashboard.

## File handling

- Retained: all required core modules, scripts 00–04 and 07–08, app, requirements, tests, recovery configs, and preserved numeric tables.
- Moved/archive: early morphology configs, method-ablation configs/runner, and two old notebooks.
- Removed from final branch: stale project tree (then regenerated), development outputs, and 3,504 large archived method-ablation outputs after verified external backup.
- New: `srg.py`, `apsrg.py`, main-method configs, results tables/cases, five focused test modules, audit/report, archive note, and regenerated project tree.

## Validation

- Compile: `src`, `scripts`, and `app.py` passed.
- Pytest: 9 passed; one non-fatal pytest-cache warning caused by an inaccessible pre-existing cache path.
- Smoke: SRG, adapted APSRG, and CA-APSRG R04 passed on a synthetic 64×64 image without output writes.
- Streamlit: headless launch returned HTTP 200; no import error.
- Results ignore check: `results/tables/recovery_article_table.csv` is not ignored.

## Repository size and remaining risks

The pre-cleanup Git pack was 3.63 GiB. The working tree removed a further 1,392,441,774 bytes of method-ablation artifacts, but historical Git objects remain until repository-history maintenance is explicitly authorized. Remote push was rejected by the environment safety reviewer because the 3.63-GiB checkpoint may export research contents to a remote with unverified visibility. License selection, remote publication, and any later history rewrite remain owner decisions.
