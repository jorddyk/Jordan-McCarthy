# Jordan McCarthy Code Wiki

_Last updated: 2026-07-08 Europe/Zurich_

## Repository purpose

This private repository is the canonical code vault for Jordan McCarthy's useful code, analysis scripts, figure-rendering workflows, web apps, and reproducibility support.

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
  imagej-fiji-aging-chips/
    README.md
    macros/
    groovy/
  language-learning/
    README.md
    active-recall-apps/
  personal-intelligence-agency/
    README.md
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
| Figure mockups / Nature Aging layouts | `projects/figure-rendering/nature-aging-mockups/` | `render-main-figure-layouts.py` |
| ImageJ/Fiji aging-chip macros | `projects/imagej-fiji-aging-chips/macros/` | `jm128-split-nd2-positions-bioformats.ijm` |
| TELC/German study apps | `projects/language-learning/active-recall-apps/` | `telc-c1-essay-skeleton-active-recall.html` |
| Personal intelligence automations | `projects/personal-intelligence-agency/prompts/` | `strategic-alert-triage.md` |
| Signal scoring models | `projects/personal-intelligence-agency/rubrics/` | `strategic-signal-score-0-to-21.md` |
| Daily audit trail | `docs/handoffs/` | `2026-07-08-code-handoff.md` |

## Operating rules

1. Preserve only clean, useful, most-current code.
2. Do not preserve intermediate attempts, duplicate scratch scripts, or one-off failed variants.
3. Prefer updating canonical files over creating new files.
4. Never generate fake biological data.
5. If an experiment has not been done, outputs must clearly say `NO DATA`.
6. Distinguish real data, simulated toy data, and `NO DATA` placeholders.
7. Do not commit raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, archives, SLURM logs, scratch folders, cache folders, temporary renders, or Euler output clutter.
8. Do not commit duplicate files named like `final.py`, `final_final.py`, `test.py`, `newplot.py`, `v2_fixed.py`, or `chatgpt_version.py`.
9. Do not commit truncated code. A code file is canonical only when the complete source is available and runnable.

## Current project areas

### JM105 / Intronsaurus

Status: active project context. One canonical JM105 analysis script was imported in the legacy backfill pass; many older Intronsaurus/JM101 scripts remain source-recovery targets.

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
```

JM134 chat-history source targets still needing full text import:

```text
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

### Figure rendering / manuscript mockups

Status: active project context; no canonical runnable renderer has yet been imported.

Known constraints:

- Do not fake data.
- Preserve original panel aspect ratios unless Jordan explicitly allows resizing.
- Match Nature Aging-style storytelling while remaining Yves-compatible.
- Use existing figure panels where possible; clearly label newly required panels.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- SVG text remains editable text; fixed canvas exports should not use `bbox_inches="tight"`.

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

Status: active scheduled-task system. Reusable prompts and rubrics should be stored under `projects/personal-intelligence-agency/`, not buried in daily handoff logs.

Current source targets:

- Strategic alert triage prompt.
- Science preemption watch prompt.
- Swiss leverage radar prompt.
- Weekly strategic brief/red-team prompt.
- Daily code handoff prompt.

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
- Imported `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py`.
- Updated `projects/README.md`, `projects/jm105-intronsaurus/README.md`, `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`, `projects/figure-rendering/docs/legacy-code-backfill.md`, and this wiki.
- Binary/generated artifacts deliberately not committed: PNG/PDF/SVG renders, xlsx templates/results, tarballs, docx/pptx manuscript artifacts, raw sequencing/microscopy data.
- Full exact source not yet recovered/imported for ImageJ/Fiji macros, language-learning HTML apps, Intronsaurus reader bundles, and older JM101/Rsubread/STAR scripts.

## Open risks / self-counterintelligence

Current code-focused internal risk: the repo can become a graveyard of daily logs instead of a useful human codebase.

Containment action: daily handoffs must update project folders first and handoff logs second.
