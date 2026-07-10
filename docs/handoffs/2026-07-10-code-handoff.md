# CODE HANDOFF — 2026-07-10

## Repo

`jorddyk/Jordan-McCarthy` — verified private and writable with admin/push permissions. Default branch: `main`.

## Project area

`projects/language-learning/`

## Human purpose

Recover a complete historical TELC C1 active-recall web app from File Library and promote it into the project-first canonical code structure under a human-readable filename. Continue checking the high-priority JM105 and ImageJ/Fiji legacy queues without inventing source when only clues are available.

## Branch name

`main`

## PR title

Not applicable. This was a bounded, exact-source single-file import plus Markdown documentation updates, committed directly to `main`.

## Commit message

- `Import canonical TELC C1 essay-skeleton recall app`
- `Document canonical TELC C1 recall app`
- `Update code wiki for TELC app legacy import`
- `Add 2026-07-10 code handoff`

## Project files created/updated

### Created

- `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`
  - Recovered from the newer File Library artifact `german-drill-6.html` dated 2026-06-18 14:02:32Z.
  - Full-source gate passed: starts with `<!DOCTYPE html>` and ends with `</html>`.
  - Fourteen TELC C1 essay-skeleton prompts.
  - English speech prompt, adjustable silent retrieval interval, German answer speech, progress bar, restart, loop, keyboard control, and visual fallback when speech synthesis is unavailable.

### Updated

- `projects/language-learning/README.md`
  - Promoted the TELC C1 app from pending candidate to canonical runnable app.
  - Added runtime requirements and source provenance.
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
  - Updated date and canonical language-learning inventory.
  - Preserved project organization, JM105 scientific guardrails, figure-rendering constraints, ImageJ/Fiji integrity constraints, candidate imports, and backfill priorities.
  - Recorded this run's containment action and unresolved exact-source queues.

## Handoff/audit files created/updated

- Created `docs/handoffs/2026-07-10-code-handoff.md`.
- The handoff remains an audit record only; canonical code lives under `projects/language-learning/`.

## Files not to commit

- Original generic File Library artifact name `german-drill-6.html` as a duplicate.
- The older duplicate artifact timestamped 2026-06-18 13:59:14Z.
- Raw PDFs, PPTX poster files, personal network HTML dashboards, raw sequencing or microscopy files, ND2/TIFF stacks, archives, generated outputs, caches, logs, and scratch files.
- No partial JM105 scripts or microscopy macros were committed because exact complete source was not recovered in this pass.

## Scientific/data status

- The imported file is a language-learning app and contains no biological data.
- No real, simulated, or placeholder biological datasets were added.
- No JM105 claims or figures were changed.
- Current JM105 guardrails remain: Figure 2 total/rRNA-depleted only unless explicitly changed; distinguish raw NMD-off from NMD-hidden off-minus-on; do not equate CR with starvation; mark unperformed experiments `NO DATA`.

## Implementation notes

- Source selection used the newest of two same-named File Library artifacts.
- The complete artifact was opened multimodally/textually rather than inferred from snippets.
- The app is intentionally dependency-light: one HTML file with embedded CSS and JavaScript; Google Fonts and browser Web Speech API are optional external runtime services.
- Direct commits to `main` were appropriate because the source was exact, complete, self-contained, and non-scientific.

## Final code or candidate imports

### Final canonical import

- `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`

### Candidate imports still pending exact complete source

- `110_JM101_JM105_integrate_intronsaurus.py`
- `111_JM101_STAR_align_array.sbatch`
- `112_JM101_integrate_after_STAR.sbatch`
- Rsubread Step 2 hard-resume/turbo scripts
- Step 3 DESeq2
- IRFinder drafts
- Intronsaurus vNext3/vNext3AE Python builders and reader bundles
- Nature Aging/Yves-compatible main-figure layout and scoring renderers
- Figure 5 renderer, `NO DATA` placeholder renderer, and JM133/JM134 label-audit utilities
- `jm128-split-nd2-positions-bioformats.ijm`
- `jm128-extract-mitosox-c2-every6-zpositions.ijm`
- `jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`

## Legacy-backfill progress

- One additional complete historical app is now represented canonically in GitHub.
- Exact filename searches for the priority JM105 `110/111/112` scripts and JM128/JM129 macro clues returned no complete source in File Library during this pass.
- Those results were treated as `exact full source not yet recovered`, not as permission to reconstruct code.
- Code-focused internal risk found: complete code was trapped under a generic historical name with a duplicate version. Containment action: selected the newest complete source, assigned one human-purpose canonical path, documented provenance, and did not commit the older duplicate.