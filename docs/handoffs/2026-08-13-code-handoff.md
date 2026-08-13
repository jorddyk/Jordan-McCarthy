# CODE HANDOFF — 2026-08-13

## Repo

`jorddyk/Jordan-McCarthy` — verified writable on `main`.

## Project area

Repository-wide sweep (Gmail, Google Drive, private GitHub repo).

## Human purpose

Search authorized sources for code or computational artifacts not yet preserved in the repository, and preserve any complete, exact, runnable source found — without reconstructing code from summaries, memos, or transcripts.

## Branch name

`main`

## PR title

None. Documentation-only maintenance was committed directly to `main`.

## Commit message

- `docs(handoff): add 2026-08-13 code handoff`

## Project files created/updated

None. No project code files were touched.

## Handoff/audit files created/updated

- Created `docs/handoffs/2026-08-13-code-handoff.md`

## Files not to commit

No raw biological data, generated figure outputs, render bundles, archives, logs, scratch scripts, or partial/summarized code were committed.

## Scientific/data status

No biological data were added or changed. No simulated values were introduced.

## Search scope and method

- Gmail: searched for code-shaped attachments and recent messages referencing scripts/notebooks/renderers (`newer_than:20d`, `has:attachment` with `.py`/`.ipynb`/`.sbatch`/`.sh`/`.R`/`.ijm`/`.groovy`/`.ps1`/`.zip` filenames). No code attachments were found; recent inbox content is newsletters/receipts plus automated ChatGPT task-status emails from the existing (non-GitHub) Daily Code Handoff process.
- Google Drive: searched recent-modified files for code file types and extensions, for JM105/figure-rendering/Euler-related full text, and inspected the `06 Current Figure Rendering Code` and `07 — Source Archive & Raw Traffic` folders directly.
- Read the three most relevant recently-modified project documents in full:
  - `CURRENT — JM105 Figure 2 v10 lane-locked renderer register` — a register (SHA-256, schema, CLI invocation) describing `JM105_figure2_render_v10_lane_locked_20260728.py`. Does not contain the script body.
  - `MEMO 2026-012 — RLS Automation Integration Across JM105 & Intronsaurus` — strategic memo on the Yeast Cell Replicative Lifespan Tracker & AI Engine. No source code.
  - `SOURCE — RLS Tracker Round 11 Principal-Supplied Technical Record` — a Tier-1 evidentiary description of `train_classifier.py` and `human_classifier_ui.py` (architecture, hyperparameters, dataset state). Explicitly a description reviewed "in the active conversation," not the file bodies.
  - `CURRENT — JM105 denominator, source provenance, and intron-length audit gate` — an analysis/QA rule register, not code.

## Final code or candidate imports

Actual canonical code imported this run: **none**.

No complete, exact, runnable source body (Python, R, Bash, Slurm, PowerShell, Fiji macro, or Groovy) was located in Gmail or Drive that is not already reflected as `PARTIAL / SOURCE LOCATED` or as a recovery target in the existing project backfill ledgers. The clearest lead — the RLS Tracker & AI Engine (`train_classifier.py`, `human_classifier_ui.py`) referenced in `MEMO 2026-012` and the `SOURCE —` record — is documented only as an architecture description, not as retrievable file bytes, so it is recorded here as a recovery target rather than imported.

## Legacy-backfill progress

New recovery target identified: the RLS Tracker & AI Engine (yeast replicative-lifespan aging-chip scoring pipeline: `train_classifier.py`, `human_classifier_ui.py`, plus a prospective-lifespan-oracle module) described in Drive folder `07 — Source Archive & Raw Traffic`. This is adjacent to `projects/imagej-fiji-aging-chips/` but is a Python/TensorFlow-Keras computer-vision pipeline rather than a Fiji macro, so it would need its own canonical path if/when exact source is recovered. No entry was added to `projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md` in this pass since that ledger is scoped to Fiji/ImageJ macros; a future pass should decide the right canonical home before importing.

Code-focused internal risk: an architecture description with real hyperparameters and file names (`train_classifier.py`, `human_classifier_ui.py`) reads very close to source and could be mistaken for recoverable code.

Containment action: this handoff records the finding as a named recovery target only; no code was reconstructed from the description.
