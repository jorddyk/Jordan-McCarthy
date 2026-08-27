# JM-136 Source Inventory

**Snapshot date:** 2026-08-14  
**Branch:** `jm136-aging-chip-pipeline`  
**Rule:** a file is not marked preserved merely because it appeared in a screenshot or earlier conversation. Exact source must be available and committed.

## Current uploaded source set

All nine Python files below were supplied directly in the current JM-136 handoff and passed `python -m py_compile` in the ingestion sandbox before repository work began.

| Canonical repository file | Original supplied filename | Original SHA-256 | Expected Git blob after CRLF→LF normalization | Status |
|---|---|---|---|---|
| `P3_tracking.py` | `P3_tracking(1).py` | `495aae0d...` | `a2afed74a2cc6eb6bdecd57b378b7d5b1a112431` | committed; trailing-newline normalization check still open |
| `train_classifier.py` | `train_classifier(3).py` | `cf635c2097e5daf824ec94d357789cdd5ce71ff0c56b07f7317a7a27da77ad78` | `5c56729855bc573d8ac72ec7a653b4bc90266f33` | committed + Git blob verified |
| `train_classifier_v6_long_context.py` | `train_classifier_v6_long_context(2).py` | `d9e6d2d51353f275289e43bbe9504ab3963df87749ff56a1746ddef645cd204a` | `e90325d7841745ae81643638d17be13f7f346965` | pending commit |
| `train_oracle_only.py` | `train_oracle_only(2).py` | `21165b69e3f046e4a15e5a47f9a2137ef68c857feb0b98c8fde3719c22720b0f` | `6bd6f4f2e7f3988ef22f953a6218adbed8de1aea` | committed + Git blob verified |
| `train_rls_sequence_refiner.py` | `train_rls_sequence_refiner(2).py` | `404d1bd73dc6dd32fcde67f490e3f88de3cec0af04d92e6b6d07a36fdc02b03c` | `53749c738a6599dc147f39f7f46c5c4dffb8f777` | committed + Git blob verified |
| `train_rls_supermodel_v7.py` | `train_rls_supermodel_v7(2).py` | `98bd0367288a5d3fcba458a3e891db0bb968a11c6e965db3e654e1e56b489848` | `a8a82034b61bf031c4997ff653041ebccc61bdd0` | pending commit |
| `train_rls_supermodel_v7_1_embedded_gold.py` | `train_rls_supermodel_v7_1_embedded_gold(2).py` | `d1de4c697e187f5ec85d2139dc1c705e6c0d82658dde04d0afd4aa3c6592f451` | `1177e74ec5c09cb74c78f11903fc6a3d1bc5ee26` | pending commit |
| `train_temporal_residual_rls.py` | `train_temporal_residual_rls(2).py` | `670fb41e20059bdd9b8e33721fe2601f0235ac8701ff117177e40b5081aaaf6e` | `aef69fcc1c01f3cdd3adc495ff0927da0751356e` | committed + Git blob verified |
| `human_classifier_ui.py` | `human_classifier_ui(2).py` | `973921cd8cdda7cb21b942e1dff5c33de5d69e10f2d7d0658e0a39430c10ecea` | `75ebf368e82b0cb798cef1c8659158a3ebe458d8` | pending commit |

The abbreviated `495aae0d...` entry should be replaced with the full original SHA-256 when the final inventory verification pass is made.

## Additional exact sources known to exist in prior uploads / File Library

These are part of the pipeline history and should be ingested after their exact source bodies are supplied or otherwise verified without reconstruction:

- `extract_traps.py`
- `audit_annotations.py`
- `eval_smoothing_sweep.py`
- `merge_annotation_sources.py`
- `classification.py`

They are **not** marked committed here simply because earlier ChatGPT sessions contained them.

## Files visible on the Windows project screenshot but not yet supplied as exact current-turn source

These cannot truthfully be called preserved until the originals are uploaded:

- `human_classifier_ui_old.py`
- `hungarian.py`
- `main.py`
- `util_cell_annotation.py`
- `pre_hungarian_human_classifier_ui.txt`
- `pre_hungarian_train_classifier.txt`

If these are still meaningful code/history, upload the originals. If any are obsolete junk, mark them intentionally obsolete rather than silently omitting them.

## Reproducibility-relevant configuration visible locally

The following small text/config artifacts may belong in Git if they contain no sensitive data and correspond to a source/model release:

- `aging_chip.yml`
- `class_labels.json`
- `hmm_transitions.json`
- `lifespan_oracle_meta.json`
- `model_input_meta.json`

They should be version-linked to the code/model that consumed them rather than copied into the repository as unexplained root files.

## Deliberately excluded from source Git by default

- `aging_chip_classifier.keras`
- `lifespan_oracle.keras`
- candidate/fold `.keras` files
- `.h5` / `.weights.h5` checkpoints
- `JM135.xlsx`
- `annotation/master_human_annotations.xlsx`
- recovered/autorecover Excel workbooks
- extracted trap TIFFs
- raw ND2 / TIFF acquisitions
- videos such as `trap_0.avi`
- generated training plots/reports and Slurm logs

These are artifacts/data, not source. Their hashes and approved storage locations should be registered in run manifests when they matter to a scientific result.

## Completeness gate before merge

Before this branch can be described as containing “all JM-136 code,” do all of the following:

1. Commit and blob-verify the four pending current-turn files.
2. Resolve the `P3_tracking.py` trailing-newline blob mismatch.
3. Obtain or explicitly waive the screenshot-only source files.
4. Ingest the five known prior exact pipeline sources or explicitly classify them as out-of-scope/historical.
5. Decide which small configs are canonical source-controlled configuration.
6. Re-run syntax checks from a clean checkout.
7. Create semantic regression fixtures before any package-style refactor.

Until then, the honest description is: **a provenance-structured JM-136 branch containing the verified core source set plus an explicit completeness ledger.**
