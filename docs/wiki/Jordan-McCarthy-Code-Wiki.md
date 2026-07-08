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
      jm133-weak-5ss-need-mud1.py
      jm133-weak-5ss-need-mud1.sbatch
    figures/
    metadata/
    docs/
      legacy-code-backfill.md
  figure-rendering/
    README.md
    nature-aging-mockups/
    panel-renderers/
    templates/
    docs/
      legacy-code-backfill.md
  imagej-fiji-aging-chips/
    README.md
    macros/
    groovy/
    docs/
  language-learning/
    README.md
    active-recall-apps/
      README.md
  personal-intelligence-agency/
    README.md
    prompts/
      legacy-code-backfill-to-github.md
    rubrics/
    reports/
docs/
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
| Figure mockups / Nature Aging layouts | `projects/figure-rendering/nature-aging-mockups/` | `render-main-figure-layouts.py` |
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

## Canonical code index

### JM105 / Intronsaurus

| Path | Purpose | Data status | Status |
|---|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py` | JM-133 analysis: 5′SS:U1 strength vs Mud1-dependence in the NMD-off background. Produces the Q1 scatter/marginal violin and QC tables. | Uses real total/rRNA-depleted RNA-seq and feature tables discovered under `/cluster/scratch/jmccarthy/JM105_RNAseq`; no fake data. | Added on branch `legacy-code-backfill-2026-07-08`; current conversation canonicalization, not older hidden disk source. |
| `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch` | Euler launcher for the JM-133 analysis. | Real data only; expects script copied to Euler project scripts folder. | Added on branch `legacy-code-backfill-2026-07-08`. |

Known constraints:

- Figure 2 should be redesigned around total/rRNA-depleted data only unless Jordan explicitly changes this.
- Poly-A data should not be used or shown for Figure 2 unless explicitly restored by Jordan.
- Figure panels or experiments not yet done must be marked `NO DATA`.
- Distinguish NMD-off/upf1D raw retained signal from NMD-hidden off-minus-on signal.
- Avoid unsupported claims that caloric restriction equals starvation.
- For gene stories, distinguish RNA/host transcript abundance from protein abundance.

### Figure rendering / manuscript mockups

Status: active project context; no canonical runnable renderer was imported in the current backfill because only prompt/spec text was recovered, not exact full source.

Known constraints:

- Do not fake data.
- Preserve original panel aspect ratios unless Jordan explicitly allows resizing.
- Match Nature Aging-style storytelling while remaining Yves-compatible.
- Use existing figure panels where possible; clearly label newly required panels.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- SVG text should remain editable; canvas dimensions should be explicit; avoid `bbox_inches="tight"`.

### ImageJ / Fiji aging chips

Status: recovery targets documented in `projects/imagej-fiji-aging-chips/README.md`; exact full macro/Groovy sources have not yet been recovered.

Priority targets include:

- `jm128-split-nd2-positions-bioformats.ijm`
- `jm128-extract-mitosox-c2-every6-zpositions.ijm`
- `jm128-stitch-image-and-image001-brightfield-rls.ijm`
- `jm128-merge-ros-bf-fl.ijm`
- `jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`

Quantification guardrails:

- Do not commit raw ND2 or TIFF stacks.
- Do not silently convert quantitative data to 8-bit.
- Do not silently apply auto-contrast to quantitative data.
- Preserve channel/Z/T/frame-sampling/background-subtraction/output conventions.

### Language-learning apps

Status: candidate source files detected, but full source import still required.

Candidates:

- `kartoffel_vocabulary_active_recall_WORKING.html` -> proposed canonical path `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`
- `german-drill-6.html` -> proposed canonical path `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`

Import rule: do not commit partial/truncated HTML. A web app is canonical only when the complete file from `<!DOCTYPE html>` through `</html>` is available.

### Personal intelligence agency

| Path | Purpose | Status |
|---|---|---|
| `projects/personal-intelligence-agency/prompts/legacy-code-backfill-to-github.md` | Reusable prompt/rubric for one-time legacy code backfill into GitHub. | Added on branch `legacy-code-backfill-2026-07-08`. |

## Daily handoff role

Daily handoffs are audit trails, not the repo's main structure.

A good daily handoff should say:

- What project files changed.
- Why they changed.
- Whether canonical code was imported, updated, or not found.
- What was deliberately not committed.

## Last-known canonical decisions

### 2026-07-08

- Repository confirmed: `jorddyk/Jordan-McCarthy`
- Repository visibility: private
- GitHub permissions: admin/push available through connector
- Initial bootstrap created `docs/wiki/` and `docs/handoffs/`
- Repo was reorganized around `projects/` as the human-facing layer
- Current backfill branch: `legacy-code-backfill-2026-07-08`
- Imported/currently canonicalized code: JM-133 5′SS:U1 strength vs Mud1-dependence analysis and sbatch launcher
- Deliberately not imported: failed/diagnostic Fig2C rebuild attempts 68/69/70; older JM101/JM105 scripts; ImageJ/Fiji macros; language apps; exact full sources not yet recovered from available context in this run

## Open risks / self-counterintelligence

Current code-focused internal risk: the repo can become a graveyard of daily logs instead of a useful human codebase.

Containment action: daily handoffs must update project folders first and handoff logs second.
