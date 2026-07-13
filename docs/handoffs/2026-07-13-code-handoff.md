# CODE HANDOFF — 2026-07-13

## Repo

`jorddyk/Jordan-McCarthy` — verified private and writable with admin/push permissions.

## Project area

`projects/figure-rendering/`

## Human purpose

Recover or accurately track missing historical figure-rendering code for JM133, JM134, Nature Aging/Yves-compatible manuscript mockups, Figure 5, and `NO DATA` placeholders without inventing scripts from summaries, job IDs, or output artifacts.

## Branch name

`main`

## PR title

None. Documentation-only maintenance was committed directly to `main`.

## Commit message

- `docs(figure-rendering): record 2026-07-13 recovery pass`
- `docs(figure-rendering): link recovery ledger`
- `docs(wiki): record figure-rendering backfill status`
- `docs(handoff): add 2026-07-13 code handoff`

## Project files created/updated

- Updated `projects/figure-rendering/docs/legacy-code-backfill.md`
- Updated `projects/figure-rendering/README.md`
- Updated `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Handoff/audit files created/updated

- Created `docs/handoffs/2026-07-13-code-handoff.md`

## Files not to commit

No raw biological data, generated figure outputs, PNG/PDF/SVG render bundles, archives, SLURM logs, scratch scripts, caches, or partial/truncated code were committed.

## Scientific/data status

No biological data were added or changed. No simulated values were introduced. No unperformed panel was represented as real; unsupported figure content remains governed by explicit `NO DATA` rules.

## Implementation notes

GitHub metadata confirmed the repository exists, is private, uses `main`, and is writable. Repository index files and the figure-rendering project README/wiki were inspected before writing.

File Library searches used exact and combined clues for JM133, JM134, Euler jobs `3101802`, `3104275`, `3106256`, `3109225`, Figure 5, Nature Aging/Yves-compatible layouts, `NO DATA`, LOESS, marginal violin, and likely renderer filenames. No complete Python, R, Bash, Slurm, or PowerShell source body was recovered.

The existing figure-rendering backfill ledger was fetched after a create attempt correctly revealed that the path already existed; it was then updated using its current SHA.

## Final code or candidate imports

Actual canonical code imported this run: **none**.

Candidate imports still pending exact full-source recovery:

- `panel-renderers/jm134-starvation-switch-label-audit.py`
- `panel-renderers/jm133-weak-5ss-mud1-scatter.py`
- `nature-aging-mockups/render-main-figure-layouts.py`
- `nature-aging-mockups/score-figure-story-architecture.py`
- Figure 5 renderer and wrappers
- `panel-renderers/render-no-data-placeholder.py`
- Figure 2F final renderer
- synopsis-aligned RNA-seq renderer

## Legacy-backfill progress

The figure-rendering queue is now more precise: JM133 and JM134 have separate proposed canonical paths and exact historical clues, including the four JM134 Euler job IDs and final panel structure. The search outcome is explicitly recorded as `exact full source not yet recovered` rather than inferred code.

Code-focused internal risk: historical successful jobs and detailed visual descriptions could be mistaken for recoverable source and lead to plausible but noncanonical reconstruction.

Containment action: `projects/figure-rendering/docs/legacy-code-backfill.md` is named as the single source of truth for missing renderer status, and only a complete currently accessible source body may move an item into canonical code.