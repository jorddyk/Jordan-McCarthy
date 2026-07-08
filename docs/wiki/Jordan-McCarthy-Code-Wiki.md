# Jordan McCarthy Code Wiki

_Last updated: 2026-07-08 Europe/Zurich_

## Repository purpose

This private repository is the canonical code vault for Jordan McCarthy's useful code, analysis scripts, figure-rendering workflows, web apps, prompts, and reproducibility support.

Canonical repository: `jorddyk/Jordan-McCarthy`

## Primary organization principle

The repo is organized by **project and purpose**, not by daily code handoff date.

A file belongs where a human would look for it later.

## Human-facing repository map

```text
README.md
projects/
  README.md
  jm105-intronsaurus/
    README.md
    analysis/
    figures/
    docs/
    transformation-protocol-rnaseq/
    jm134-starvation-switch/
    jm133-weak-5ss-mud1/
    figure2-candidate-gate/
    intronsaurus-browser/
  figure-rendering/
    README.md
    docs/
    nature-aging-mockups/
    panel-renderers/
    templates/
    prompts/
  imagej-fiji-aging-chips/
    README.md
    macros/
    groovy/
  language-learning/
    README.md
    active-recall-apps/
  personal-intelligence-agency/
    README.md
    docs/
    prompts/
    rubrics/
    reports/
docs/
  legacy-code-backfill.md
  wiki/
    Jordan-McCarthy-Code-Wiki.md
  handoffs/
    YYYY-MM-DD-code-handoff.md
```

## What belongs where

| Code type | Human project path | Example human file name |
|---|---|---|
| JM105 RNA-seq / intron retention analysis | `projects/jm105-intronsaurus/analysis/` | `calculate-nmd-hidden-intron-retention.py` |
| JM105 manuscript figures | `projects/jm105-intronsaurus/figures/` | `render-figure-2-total-rna-intron-module.py` |
| JM105 transformation protocol RNA-seq | `projects/jm105-intronsaurus/transformation-protocol-rnaseq/` | `build-relative-transcript-abundance-excel.py` |
| JM134 starvation-switch comparison | `projects/jm105-intronsaurus/jm134-starvation-switch/` | `jm134-matched-splicing-index.py` |
| Intronsaurus browser helpers | `projects/jm105-intronsaurus/intronsaurus-browser/` | `upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` |
| Figure mockups / Nature Aging layouts | `projects/figure-rendering/nature-aging-mockups/` | `render-main-figure-layouts.py` |
| Figure prompt/spec artifacts | `projects/figure-rendering/prompts/` | `render-jm105-figure5-powershell-euler.md` |
| ImageJ/Fiji aging-chip macros | `projects/imagej-fiji-aging-chips/macros/` | `jm128-split-nd2-positions-bioformats.ijm` |
| TELC/German study apps | `projects/language-learning/active-recall-apps/` | `telc-c1-essay-skeleton-active-recall.html` |
| Personal intelligence automations | `projects/personal-intelligence-agency/prompts/` | `strategic-alert-triage.md` |
| Signal scoring models | `projects/personal-intelligence-agency/rubrics/` | `strategic-signal-score-0-to-21.md` |
| Daily audit trail | `docs/handoffs/` | `2026-07-08-code-handoff.md` |

## Operating rules

1. Preserve only clean, useful, most-current code.
2. Do not preserve intermediate attempts, duplicate scratch scripts, or one-off failed variants.
3. Prefer updating existing canonical files over creating new files.
4. Never generate fake biological data.
5. If an experiment has not been done, outputs must clearly say `NO DATA`.
6. Distinguish real data, simulated toy data, and `NO DATA` placeholders.
7. Do not commit raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, archives, SLURM logs, scratch folders, cache folders, temporary renders, or Euler output clutter.
8. Do not commit duplicate files named like `final.py`, `final_final.py`, `test.py`, `newplot.py`, or `v2_fixed.py`.
9. Do not commit truncated code. A code file is canonical only when the complete source is available and runnable.
10. Prompt/spec artifacts may be saved when they are exact reusable workflow assets, but must be marked as non-runnable.

## Current project areas

### JM105 / Intronsaurus

Status: active project context. Canonical JM105 analysis and transformation helper scripts have been imported in prior backfill work; Intronsaurus browser helpers for the vNext3I/vNext3Y operational workflows have been imported in the 2026-07-08 pass.

Known constraints:

- Figure 2 should be redesigned around total/rRNA-depleted data only unless Jordan explicitly changes this.
- Poly-A data should not be used or shown for Figure 2 unless explicitly restored by Jordan.
- Figure panels or experiments not yet done must be marked `NO DATA`.
- Distinguish NMD-off/upf1D raw retained signal from NMD-hidden off-minus-on signal.
- Avoid unsupported claims that caloric restriction equals starvation.
- For gene stories, distinguish RNA/host transcript abundance from protein abundance.

#### Imported canonical code

| Path | Purpose | Status |
|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py` | Classifies old-selective NMD-revealed introns and tests functional module / splice-architecture determinants. | Imported; uses real JM105 tables on Euler; no fake biological data. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/resolve-fastq-files.py` | Resolves FASTQ files for transformation-protocol samples. | Imported; real workflow metadata. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/transformation-protocol-samples.tsv` | Sample manifest for JM62-JM73. | Imported; no raw reads. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/run-transformation-expression.sbatch` | Slurm wrapper for transformation-protocol expression workflow. | Imported; real workflow. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/check-transformation-job.ps1` | Windows helper for Euler job/log checks. | Imported; administrative helper. |
| `projects/jm105-intronsaurus/intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | Slurm wrapper for vNext3I, which restores original total/rRNA-depleted Explore graphs and adds poly-A views. | Imported exact helper source; requires full Python builder and patch-chain dependencies on Euler. |
| `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | Uploads vNext3I bundle and submits the Euler build job. | Imported exact helper source. |
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves and opens the vNext3I HTML archive from Euler. | Imported exact helper source. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks Slurm status and logs for vNext3I. | Imported exact helper source. |

#### Imported JM105 scientific/context documents

| Path | Purpose | Status |
|---|---|---|
| `projects/jm105-intronsaurus/docs/what-data-shows-summary.md` | Preserves the current user-provided interpretation of CR/Mud1/NMD-hidden leakage, Mud1-GFP, intron architecture, RP/non-RP stratification, and Parenteau comparison logic. | Imported exact summary; not runnable code. |

#### Recovered source targets

```text
projects/jm105-intronsaurus/transformation-protocol-rnaseq/
projects/jm105-intronsaurus/jm134-starvation-switch/
```

Transformation-protocol source clue:

```text
/mnt/data/JM105_Transformation_Protocol_Pipeline/
```

JM134 source clues:

```text
/mnt/data/JM134_matched_splicing_index.py
/mnt/data/JM134_submit_matched_SI.sh
/mnt/data/JM134_rerender_no_overlap.py
/mnt/data/81_JM134_symlog_clarity_and_notebook.py
scripts/79_JM134_audit_and_beta_binomial.py
scripts/80_JM134_apply_beta_binomial_and_rerender.py
scripts/83_JM134_final_guide_repair.py
```

Current JM105 exact-source targets still needing import:

```text
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
scripts/29_old_cell_leaky_intron_determinants.py original SVG-rich Euler draft
```

Other JM105 source-recovery targets retained in `docs/legacy-code-backfill.md`: JM133 weak-5SS/Mud1 source, Figure 2 candidate-gate script, Intronsaurus vNext3I/vNext3Y Python builders and patch chain, JM101/JM105 integration, STAR/sbatch, Rsubread step 2/3, IRFinder drafts, and Intronsaurus reader bundles.

### Figure rendering / manuscript mockups

Status: active project context. No canonical runnable renderer has yet been imported. Exact reusable prompt/spec artifacts have been imported.

Known constraints:

- Do not fake data.
- Preserve original panel aspect ratios unless Jordan explicitly allows resizing.
- Match Nature Aging-style storytelling while remaining Yves-compatible.
- Use existing figure panels where possible; clearly label newly required panels.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- SVG text remains editable text; fixed canvas exports should not use `bbox_inches="tight"`.

#### Imported prompt/spec artifacts

| Path | Purpose | Status |
|---|---|---|
| `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md` | Exact Figure 5 rendering contract: PowerShell + Euler, lane map, collision inventory, provenance manifest, fixed-canvas SVG/PDF/PNG/white-preview PNG, and `NO DATA — experiment pending` rules. | Imported exact prompt/spec; not runnable code. |
| `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md` | Exact Nature Aging / Yves-compatible figure-sequence redesign prompt with input gate, confidence tags, panel inventory, claim architecture, and execution checklist. | Imported exact prompt/spec; not runnable code. |

#### Runnable source still needing recovery

```text
projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py
projects/figure-rendering/nature-aging-mockups/score-figure-story-architecture.py
projects/figure-rendering/panel-renderers/render-no-data-placeholder.py
projects/figure-rendering/nature-aging-mockups/figure-5-layout-renderer.py
projects/figure-rendering/panel-renderers/avoid-label-overlap-audit.py
```

### ImageJ/Fiji aging-chip macros

Status: source clues recovered, exact full macro source not yet imported.

Source clues:

```text
jm128-split-nd2-positions-bioformats.ijm
jm128-extract-mitosox-c2-every6-zpositions.ijm
jm129-mitosox-virtual-hyperstack-background-subtraction.groovy
```

Import constraints:

- Do not commit raw ND2/TIFF stacks.
- Do not silently convert quantitative data to 8-bit.
- Do not silently apply auto-contrast to quantitative data.
- Document channel, Z, T, frame sampling, background subtraction, and output naming.

### Language-learning apps

Status: candidate source files detected, but full source import still required.

Candidates:

- `kartoffel_vocabulary_active_recall_WORKING.html` -> proposed canonical path `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`
- `german-drill-6.html` -> proposed canonical path `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`

Import rule: do not commit partial/truncated HTML. A web app is canonical only when the complete file from `<!DOCTYPE html>` through `</html>` is available.

### Personal intelligence agency

Status: active scheduled-task system. Exact active scheduled-task prompts were imported on 2026-07-08. Reusable prompts and rubrics should be stored under `projects/personal-intelligence-agency/`, not buried in daily handoff logs.

#### Imported prompt/spec artifacts

| Path | Purpose | Status |
|---|---|---|
| `projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md` | Exact prompt for recovering old useful code from project history and committing it into `jorddyk/Jordan-McCarthy`. | Imported exact prompt/spec; not runnable code. |
| `projects/personal-intelligence-agency/prompts/code-handoff.md` | Exact active scheduled-task prompt for daily code handoff and ongoing legacy-source recovery. | Imported exact prompt/spec from active automation; not runnable code. |
| `projects/personal-intelligence-agency/prompts/strategic-alert-triage.md` | Exact active scheduled-task prompt for urgent strategic signal triage. | Imported exact prompt/spec from active automation; not runnable code. |
| `projects/personal-intelligence-agency/prompts/science-preemption-watch.md` | Exact active scheduled-task prompt for science/preemption monitoring around JM105/Intronsaurus. | Imported exact prompt/spec from active automation; not runnable code. |
| `projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md` | Exact active scheduled-task prompt for Swiss/ETH/startup/funding/career leverage monitoring. | Imported exact prompt/spec from active automation; not runnable code. |
| `projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md` | Exact active scheduled-task prompt for weekly strategic brief and monthly red-team review. | Imported exact prompt/spec from active automation; not runnable code. |
| `projects/personal-intelligence-agency/docs/legacy-code-backfill.md` | Project-local recovery record for imported automation prompts and remaining rubric/template targets. | Imported; documentation only. |

#### Current source targets

- Exact 0-to-21 strategic signal scoring rubric.
- Reusable report/email templates if they exist outside the prompt bodies.
- Historical task outputs only if they change reusable logic; otherwise do not import daily output spam.

Caution: automation prompt files preserve task logic, but recovered task metadata showed `notifications_enabled: false` and `email_enabled: false`; operational delivery settings must be verified in ChatGPT automation settings.

## Daily handoff role

Daily handoffs are audit trails, not the repo's main structure.

A good daily handoff should say:

- What project files changed.
- Why they changed.
- Whether canonical code was imported, updated, or not found.
- What was deliberately not committed.

## Last-known canonical decisions

### 2026-07-08

- Repository confirmed: `jorddyk/Jordan-McCarthy`.
- Repository visibility: private.
- GitHub permissions: admin/push available through connector.
- Imported `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py` in an earlier backfill pass.
- Imported transformation-protocol helper files in an earlier backfill pass: `resolve-fastq-files.py`, `transformation-protocol-samples.tsv`, `run-transformation-expression.sbatch`, and `check-transformation-job.ps1`.
- Imported exact prompt/spec artifacts for Figure 5 rendering, manuscript figure-sequence redesign, legacy-code backfill workflow, and all five active personal-intelligence scheduled tasks.
- Imported `projects/jm105-intronsaurus/docs/what-data-shows-summary.md` as a scientific interpretation guardrail, not code.
- Imported Intronsaurus vNext3I helper scripts for upload/submit, Slurm run, retrieval, and status checking; full large Python builder remains a documented recovery/import target.
- Updated `projects/README.md`, `projects/jm105-intronsaurus/README.md`, `projects/jm105-intronsaurus/intronsaurus-browser/README.md`, `projects/figure-rendering/README.md`, `projects/personal-intelligence-agency/README.md`, figure-rendering legacy docs, personal-intelligence legacy docs, and this wiki across the 2026-07-08 backfill passes.
- Binary/generated artifacts deliberately not committed: PNG/PDF/SVG renders, xlsx templates/results, tarballs, docx/pptx manuscript artifacts, raw sequencing/microscopy data.
- Full exact source not yet imported for ImageJ/Fiji macros, language-learning HTML apps, some Intronsaurus reader bundles/builders, and older JM101/Rsubread/STAR scripts.

## Open risks / self-counterintelligence

Current code-focused internal risk: the repo can become a graveyard of daily logs and prompt artifacts instead of a useful human codebase.

Containment action: daily handoffs must update project folders first and handoff logs second; prompt/spec artifacts must be clearly marked non-runnable; missing exact source must stay in recovery docs rather than being reconstructed.
