# CODE HANDOFF — 2026-07-08

## Repo

`jorddyk/Jordan-McCarthy`

## Branch name

`main`

## PR title

No PR opened. Safe Markdown updates, exact prompt/spec artifacts, interpretation summary, and small canonical helper scripts were committed directly to `main`.

## Project area

Primary current pass: Personal intelligence agency prompt/spec backfill.

Earlier 2026-07-08 passes: JM105 / Intronsaurus, figure rendering / Nature Aging mockups, global code wiki.

## Human purpose

Continue the one-time legacy code backfill by importing exact reusable project assets where full text was available and documenting source-recovery targets where only summaries, filenames, partial snippets, or large builders still need a safer text-source import.

This current pass specifically moved active scheduled-task prompt logic out of daily/automation-only state and into the project-organized repo under `projects/personal-intelligence-agency/`.

## Files created/updated

Created in earlier passes:

- `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py`
- `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md`
- `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md`
- `projects/jm105-intronsaurus/docs/what-data-shows-summary.md`
- `projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md`
- `projects/jm105-intronsaurus/intronsaurus-browser/README.md`
- `projects/jm105-intronsaurus/intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch`
- `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh`

Created in this pass:

- `projects/personal-intelligence-agency/prompts/code-handoff.md`
- `projects/personal-intelligence-agency/prompts/strategic-alert-triage.md`
- `projects/personal-intelligence-agency/prompts/science-preemption-watch.md`
- `projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md`
- `projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md`
- `projects/personal-intelligence-agency/docs/legacy-code-backfill.md`

Updated across the 2026-07-08 passes:

- `projects/README.md`
- `projects/jm105-intronsaurus/README.md`
- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`
- `projects/figure-rendering/README.md`
- `projects/figure-rendering/docs/legacy-code-backfill.md`
- `projects/personal-intelligence-agency/README.md`
- `docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
- `docs/handoffs/2026-07-08-code-handoff.md`

Continuation cleanup audit:

- Verified repo remains private and writable on `main` with admin/push permission.
- Verified active personal-intelligence scheduled-task prompts are already canonicalized at the five paths listed above.
- Verified project-level personal-intelligence backfill tracking exists at `projects/personal-intelligence-agency/docs/legacy-code-backfill.md`.
- Removed two duplicate prompt files that were accidentally created during a continuation audit, preserving the canonical filenames:
  - `projects/personal-intelligence-agency/prompts/code-handoff-scheduled-task.md`
  - `projects/personal-intelligence-agency/prompts/strategic-brief-redteam.md`

## Files deliberately not committed

- Raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, ND2, TIFF, archives, SLURM logs, scratch folders, generated plots, Excel workbooks, PowerPoint/Word manuscript artifacts, and output tarballs.
- Sun workbook `11357_2021_412_MOESM3_ESM.xlsx`; it is an input data workbook, not repo code.
- Intronsaurus generated HTML and tar.gz outputs.
- Intermediate Intronsaurus Sun integration versions v3P-v3X; v3Y is the current canonical target.
- The large Python builder `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py` was recovered exactly in the active sandbox in an earlier pass but still needs a full text-source import. It was not reconstructed or partially committed.
- ImageJ/Fiji/Groovy macros whose exact complete source was not recovered.
- Language-learning HTML apps whose full `<!DOCTYPE html>` to `</html>` source was not recovered.
- Reconstructed versions of older Rsubread/STAR/IRFinder scripts where only provenance summaries were found.
- Runnable Figure 5 renderer code, because the available source was an exact prompt/spec, not the generated PowerShell/Bash/Python itself.
- Raw Gmail/calendar contents and transient personal-intelligence task outputs. Only reusable prompt/spec logic was imported.
- During the continuation audit, no additional runnable source was imported because searches returned already-imported prompt/spec artifacts, scientific documents, source clues, or incomplete summaries rather than complete runnable code.

## Scientific/data status

The imported JM105 determinant script uses real JM105 Euler-side tables as inputs. It does not generate fake biological data. It preserves the working interpretation that RNA-seq currently supports selective NMD-revealed intron leakage, not a global all-intron burden claim.

The Intronsaurus vNext3Y helpers support a real-data build from JM105 total/rRNA-depleted Intronsaurus inputs and Sun et al. 2021 processed proteomics. The workflow keeps RNA/host transcript abundance distinct from protein abundance, maps Sun systematic ORF IDs to common gene names, and does not call caloric restriction starvation.

The imported Figure 5 prompt/spec and interpretation Markdown files are not biological data and are not runnable code. They preserve exact workflow/scientific constraints, including: no fake data; `NO DATA — experiment pending` for missing experiments; Figure 2 total/rRNA-depleted-only unless explicitly changed; no unsupported poly-A/P-versus-T/mRNA-like/P−T additions; RNA abundance distinguished from protein abundance; CR not called starvation.

The personal intelligence files imported in this pass are exact prompt/spec artifacts from active scheduled tasks. They contain no raw private inbox/calendar dumps and no generated daily intelligence output.

## Implementation notes

The imported JM105 determinant script classifies old-selective leaky introns using the detector logic:

```text
Old detector   = Old upf1Δ - Old WT
Young detector = Young upf1Δ - Young WT
Old-selective leakage = Old detector - Young detector
```

The vNext3Y Intronsaurus helper set points at the recovered large builder and supports a single-entry Gene Stories design with comparison-matched groups:

```text
Aging: old vs young
Old-cell CR: old CR vs old 2%
Young-cell CR: young CR vs young 2%
JM105 regulatory tests
```

The personal-intelligence prompt files were recovered from active automations. The recovered metadata showed `notifications_enabled: false` and `email_enabled: false`; the repo files preserve exact task logic, but operational email delivery settings must be checked in the ChatGPT automation UI when delivery matters.

GitHub connector status:

- Repository resolved: `jorddyk/Jordan-McCarthy`
- Visibility: private
- Permissions: admin/push available
- Default branch: `main`

Continuation audit search status:

- File search found uploaded Figure 5 prompt/spec files and manuscript documents, including `Fig5_McCarthy.docx`, `Fig2_McCarthy.docx`, and `What Data Shows.docx`, but not additional full runnable source code.
- Google Drive search found MitoSOX and lab-notebook source clues, including `Lab Notebook complete copy and paste text dump`, but not complete `.ijm`/Groovy macro bodies.
- GitHub PR audit found open PR #1, `Legacy code backfill: JM133 and recovery docs`, containing JM133 weak-5SS/Mud1 code on branch `legacy-code-backfill-2026-07-08`; it remains open and unmerged in the connector-visible state.

## Final code / prompt paths

```text
projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py
projects/jm105-intronsaurus/intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch
projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1
projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1
projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh
projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md
projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md
projects/jm105-intronsaurus/docs/what-data-shows-summary.md
projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md
projects/personal-intelligence-agency/prompts/code-handoff.md
projects/personal-intelligence-agency/prompts/strategic-alert-triage.md
projects/personal-intelligence-agency/prompts/science-preemption-watch.md
projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md
projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md
projects/personal-intelligence-agency/docs/legacy-code-backfill.md
```

## Legacy-backfill progress

Recovered and committed one canonical JM105 analysis script in an earlier pass. Subsequent passes recovered and committed exact prompt/spec artifacts, a scientific interpretation summary, vNext3Y Intronsaurus operational helpers, and now the exact active personal-intelligence scheduled-task prompts.

Updated the recovery queues with specific next targets:

```text
intronsaurus-browser/integrate-sun-matched-rna-protein-gene-stories.py
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
scripts/29_old_cell_leaky_intron_determinants.py original SVG-rich Euler draft
```

Older high-priority unrecovered targets remain:

```text
110_JM101_JM105_integrate_intronsaurus.py
111/113 JM101 STAR align array sbatch
112/114 JM101 integrate-after-STAR sbatch
JM101 Rsubread Step 2/3 scripts
JM101 IRFinder draft workflow
Intronsaurus vNext3 / vNext3AE reader bundles
JM128/JM129 Fiji/Groovy microscopy scripts
language-learning active-recall HTML apps
runnable Figure 5 PowerShell/Bash/Python renderer source
JM134 beta-binomial / final layout repair scripts
JM133 weak-5SS/Mud1 source from Euler or open PR #1 if it should be merged to main
personal intelligence exact scoring rubric and report templates
```

## Code-focused self-counterintelligence

Detected risk: the repo can become a graveyard of daily logs and prompt artifacts instead of a useful human codebase.

Containment action: prompt/spec artifacts were saved only when exact and reusable, clearly marked non-runnable, and placed under project-purpose folders. Missing source remains in recovery docs rather than being reconstructed.

Continuation audit risk: duplicate prompt files can appear when a continuation run does not first inspect existing canonical filenames.

Containment action: duplicate prompt files created during the continuation audit were deleted, and the handoff now records the canonical filenames to use going forward.
