# 2026-07-09 Code Handoff

## Repo

`jorddyk/Jordan-McCarthy`

Repository verification:

- Exists: yes.
- Visibility: private.
- Default branch: `main`.
- Connector permissions observed: admin/maintain/push/pull/triage available.

## Project area

`projects/language-learning/`

## Human purpose

Recover one complete historical language-learning web app from File Library and preserve it in the project-first code vault under a human-readable path. This prevents useful app code from remaining trapped as a File Library artifact or daily-handoff clue.

## Branch name

`main`

Direct commit to `main` was used because this was a small, complete, low-risk single-file app import plus documentation updates.

## PR title

No PR created.

## Commit message

Primary code import:

```text
Import Kartoffel active recall web app
```

Follow-up documentation commits:

```text
Update language learning README after Kartoffel app import
Update code wiki after Kartoffel app import
Add 2026-07-09 code handoff
```

## Project files created/updated

Created:

- `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`

Updated:

- `projects/language-learning/README.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Handoff/audit files created/updated

Created:

- `docs/handoffs/2026-07-09-code-handoff.md`

## Files not to commit

Not committed:

- Raw PDFs and grammar-source documents.
- Incomplete/truncated language-learning snippets.
- Raw microscopy files, ND2 files, TIFF stacks, generated render outputs, archives, cache folders, or SLURM logs.
- Any reconstructed or invented code.

## Scientific/data status

No biological data, figure data, sequencing data, microscopy data, or `NO DATA` scientific panels were changed in this run.

The imported app is a language-learning utility, not scientific analysis. It contains a fixed vocabulary list from the Kartoffel text and client-side study logic.

## Implementation notes

Recovered complete File Library source:

- Source artifact: `kartoffel_vocabulary_active_recall_WORKING.html`.
- Completeness check: source opened with `<!DOCTYPE html>` and ended with `</html>`.
- Imported as a canonical runnable single-file HTML/CSS/JavaScript app.
- Human path chosen: `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`.

App features preserved:

- English-to-German recall prompts.
- German answer aliases.
- Typo-tolerant answer checking with Levenshtein distance.
- Missed pile.
- Reveal / next / restart controls.
- Shuffle and loop toggles.
- Adjustable timer ring.
- Mobile-friendly dark single-page UI.

## Final code or candidate imports

Imported final canonical code:

```text
projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html
```

Remaining candidate imports:

```text
projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html
```

The TELC app should only be imported if the complete exact source is recovered from `<!DOCTYPE html>` through `</html>`.

## Legacy-backfill progress

Completed in this run:

- Recovered and imported one complete language-learning HTML app.
- Updated the language-learning README so the app is no longer listed as merely a candidate.
- Updated the code wiki with the new canonical app and the 2026-07-09 canonical decision.

Still pending from the current legacy queue:

- JM105/Intronsaurus: `110_JM101_JM105_integrate_intronsaurus.py`, `111_JM101_STAR_align_array.sbatch`, `112_JM101_integrate_after_STAR.sbatch`, Rsubread Step 2 hard-resume/turbo scripts, Step 3 DESeq2, IRFinder drafts, Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y builders and reader bundles.
- Figure rendering: Nature Aging/Yves-compatible main figure mockup renderers, scoring-model code, Figure 5 renderer, `NO DATA` placeholder renderer, JM133/JM134 label audit/rerender utilities.
- ImageJ/Fiji aging chips: JM128/JM129 macros and Groovy scripts for Bio-Formats ND2 splitting, MitoSOX C2 extraction, BF/FL merge, virtual hyperstack construction, ROS/RLS processing, and quantitative background-subtraction workflows.
- Language-learning: TELC C1 essay-skeleton app full source.

Code-focused internal execution risk and containment action:

- Risk detected: legacy code sprawl and useful apps trapped in uploaded-file artifacts rather than project paths.
- Containment action: imported the complete recovered Kartoffel app into the project-first language-learning folder and updated the wiki/README as the source of truth.
