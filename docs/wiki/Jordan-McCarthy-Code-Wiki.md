# Jordan McCarthy Code Wiki

_Last updated: 2026-07-10 Europe/Zurich_

## Repository purpose

This private repository is the canonical code vault for Jordan McCarthy's useful code, analysis scripts, figure-rendering workflows, web apps, prompts, and reproducibility support.

Canonical repository: `jorddyk/Jordan-McCarthy`

## Primary organization principle

The repo is organized by **project and purpose**, not by daily code handoff date. A file belongs where a human would look for it later.

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

## Operating rules

1. Preserve only clean, useful, most-current code.
2. Do not preserve intermediate attempts, duplicate scratch scripts, or one-off failed variants.
3. Prefer updating existing canonical files over creating new files.
4. Never generate fake biological data.
5. If an experiment has not been done, outputs must clearly say `NO DATA`.
6. Distinguish real data, simulated toy data, and `NO DATA` placeholders.
7. Do not commit raw FASTQ, BAM, SAM, CRAM, BAI, bigWig, archives, SLURM logs, scratch folders, cache folders, temporary renders, Euler output clutter, raw ND2 files, or raw TIFF stacks.
8. Do not commit duplicate files named like `final.py`, `final_final.py`, `test.py`, `newplot.py`, or `v2_fixed.py`.
9. Do not commit truncated code. A code file is canonical only when the complete source is available and runnable.
10. Prompt/spec artifacts may be saved when they are exact reusable workflow assets, but must be marked as non-runnable.

## Current project areas

### JM105 / Intronsaurus

Status: active project context. Canonical JM105 analysis and transformation helper scripts have been imported in prior backfill work; Intronsaurus browser helpers and a Gene Stories provenance patch are represented.

Last-known scientific decisions:

- Figure 2 uses total/rRNA-depleted JM105 only unless Jordan explicitly restores another subset.
- Poly-A, P-versus-T, mRNA-like, and P−T constructs are out of Figure 2 unless explicitly restored.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.
- Do not claim caloric restriction is starvation.
- Unperformed experiments and unsupported panels remain `NO DATA`.

#### Imported canonical code

| Path | Purpose | Required inputs / environment | Outputs / status |
|---|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py` | Classifies old-selective NMD-revealed introns and tests functional module and splice-architecture determinants. | Real JM105 tables on Euler; Python scientific stack. | Analysis tables/figures; real-data workflow, no fake data. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/resolve-fastq-files.py` | Resolves FASTQ files for transformation-protocol samples. | Euler paths and sample manifest. | Resolved file mapping. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/transformation-protocol-samples.tsv` | Sample manifest for JM62-JM73. | None. | Workflow metadata; no raw reads. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/run-transformation-expression.sbatch` | Slurm wrapper for transformation-protocol expression workflow. | Euler/Slurm and referenced scripts. | Submitted workflow outputs/logs; logs stay out of Git. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/check-transformation-job.ps1` | Windows helper for Euler job/log checks. | PowerShell, SSH access. | Console status only. |
| `projects/jm105-intronsaurus/intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | Runs the vNext3I browser workflow. | Euler-side builder and patch-chain dependencies. | Generated browser archive; generated HTML/archive not committed by default. |
| `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | Uploads the vNext3I bundle and submits the build. | PowerShell/SSH. | Remote submission. |
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves and opens the vNext3I archive. | PowerShell/SSH. | Local generated archive; do not commit. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks Slurm status and logs. | Bash/Euler. | Console status. |
| `projects/jm105-intronsaurus/intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | Deduplicates Gene Stories evidence labels and adds source/provenance notes. | Existing Intronsaurus HTML DOM. | UI/provenance patch only; does not generate biological values. |

#### Scientific/context documents

| Path | Purpose | Status |
|---|---|---|
| `projects/jm105-intronsaurus/docs/what-data-shows-summary.md` | Current interpretation guardrail for CR/Mud1/NMD-hidden leakage, Mud1-GFP, intron architecture, RP stratification, and Parenteau comparison logic. | Verified context document; not runnable code. |

#### Current exact-source targets

```text
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
scripts/29_old_cell_leaky_intron_determinants.py original SVG-rich Euler draft
110_JM101_JM105_integrate_intronsaurus.py
111_JM101_STAR_align_array.sbatch
112_JM101_integrate_after_STAR.sbatch
Rsubread Step 2 hard-resume/turbo scripts
Step 3 DESeq2
IRFinder drafts
Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y Python builders and reader bundles
JM133 weak-5SS/Mud1 source
Figure 2 candidate-gate script
```

### Figure rendering / manuscript mockups

Status: one canonical runnable panel renderer plus exact reusable prompt/spec artifacts.

Constraints:

- Preserve original panel aspect ratios unless explicitly changed.
- Use lane geometry and collision inventories; do not solve crowding by silently deleting information.
- Keep SVG text editable and fixed-canvas outputs fixed; avoid `bbox_inches="tight"` for final canvas exports.
- Keep transparent final outputs transparent; white-preview PNGs are separate review assets.
- For JM105 Figure 2, do not introduce poly-A / P-versus-T / mRNA-like logic unless restored.

#### Imported runnable source

| Path | Purpose | Inputs / outputs | Data status |
|---|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Renders JM105 Figure 1E/F content-only print panels through PowerShell + embedded Python. | Reads local total/rRNA-depleted JM105 tables; writes SVG, transparent PNG, 3x PNG, white preview, TSV, and JSON audit. | Real-data workflow; no fake data; no poly-A. Panel definitions are explicitly audited. |

#### Imported prompt/spec artifacts

```text
projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md
projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md
projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md
projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md
```

These are reusable workflow contracts, not runnable analysis code.

#### Runnable source still needing recovery

```text
projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py
projects/figure-rendering/nature-aging-mockups/score-figure-story-architecture.py
projects/figure-rendering/panel-renderers/render-no-data-placeholder.py
projects/figure-rendering/nature-aging-mockups/figure-5-layout-renderer.py
projects/figure-rendering/panel-renderers/avoid-label-overlap-audit.py
projects/figure-rendering/panel-renderers/render-figure2-panel-f-mud1-dependence.py
```

### ImageJ / Fiji aging-chip macros

Status: source clues recovered; exact full macro source not yet imported.

Priority clues:

```text
jm128-split-nd2-positions-bioformats.ijm
jm128-extract-mitosox-c2-every6-zpositions.ijm
jm129-mitosox-virtual-hyperstack-background-subtraction.groovy
Image001.nd2
Image001_Pos0_Hyperstack.tif
Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions
MitosoxRedInducibleFusionsRepeat.nd2
Continue001.nd2
Continue002.nd2
rollingBallRadius=100
C=2
Z=60
T=107/139/145
Nup60Gcn5MitoSoxRed_RLS_Pos0.tif
Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif
```

Import constraints:

- Do not commit raw ND2 or TIFF stacks.
- Do not silently convert quantitative data to 8-bit.
- Do not silently apply auto-contrast to quantitative data.
- Document channel, Z, T, frame sampling, background subtraction, and output naming.

### Language-learning apps

Status: two complete canonical single-file HTML apps imported.

| Path | Purpose | Runtime / inputs | Outputs / status |
|---|---|---|---|
| `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html` | English-to-German Kartoffel-text vocabulary trainer with aliases, missed pile, shuffle/loop controls, timer ring, typo tolerance, and mobile-friendly UI. | Modern browser; no build step. | Interactive browser app; imported 2026-07-09 from complete File Library source. |
| `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html` | Fourteen-item TELC C1 essay-skeleton oral recall drill with English prompt speech, adjustable silent retrieval gap, German answer speech, progress, restart, and loop controls. | Modern browser; Web Speech API when available, visual fallback otherwise. | Interactive browser app; imported 2026-07-10 from the newer complete `german-drill-6.html` artifact. |

Import rule: a web app is canonical only when complete from `<!DOCTYPE html>` through `</html>`.

### Personal intelligence agency

Status: active automation-support project. Exact reusable prompts belong here, not inside handoff logs.

#### Imported prompt/spec artifacts

```text
projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md
projects/personal-intelligence-agency/prompts/code-handoff.md
projects/personal-intelligence-agency/prompts/strategic-alert-triage.md
projects/personal-intelligence-agency/prompts/science-preemption-watch.md
projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md
projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md
projects/personal-intelligence-agency/docs/legacy-code-backfill.md
```

Current targets:

- Exact 0-to-21 strategic signal scoring rubric.
- Reusable report/email templates if they exist outside prompt bodies.
- Historical task outputs only when they change reusable logic.

Operational note: recovered task metadata has previously shown notifications/email disabled. Delivery settings are runtime configuration, not code, and must not be inferred from prompt files.

## Candidate imports and backfill queue

Priority order remains:

1. Exact JM105 integration/alignment scripts `110`, `111`, and `112`.
2. Rsubread Step 2 hard-resume/turbo, Step 3 DESeq2, and IRFinder drafts.
3. Full Intronsaurus Python builders/readers, especially vNext3 and vNext3AE.
4. Nature Aging/Yves-compatible figure mockup and label-audit renderers.
5. JM128/JM129 Fiji/Groovy microscopy workflows with quantitative integrity preserved.
6. Additional complete language-learning apps only when full source is available.

## Code-focused execution risks and containment

- **Risk:** useful complete apps and scripts remain trapped under generic historical names such as `german-drill-6.html`.
- **Containment:** import only the newest complete source under a human-purpose path and remove the stale candidate entry from project documentation.
- **Risk:** source summaries may be mistaken for code.
- **Containment:** label unrecovered targets `exact full source not yet recovered`; never reconstruct runnable source from summaries.
- **Risk:** daily handoffs could become the primary organization layer.
- **Containment:** canonical code and project status live under `projects/`; `docs/handoffs/` remains audit-only.

## Last-known canonical decisions

### 2026-07-10

- Repository verified private and writable on `main` with admin/push permissions.
- Imported `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html` from the newer File Library `german-drill-6.html` artifact.
- Full-source gate passed: source opened with `<!DOCTYPE html>` and ended with `</html>`.
- Updated the language-learning README and wiki so this app is canonical rather than pending.
- Searches for the priority JM105 `110/111/112` files and JM128/JM129 macro names did not recover exact complete source in this pass; these remain documented targets rather than fabricated code.
- No biological data, raw microscopy, generated figures, archives, or logs were committed.

### 2026-07-09

- Imported `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html` from complete File Library source.
- Updated project-first documentation and the audit trail.

### 2026-07-08

- Imported the first canonical JM105 analysis, transformation helper, Intronsaurus helper/patch, figure-renderer, figure-spec, and automation-prompt batches.
- Preserved current JM105 data/claim constraints and excluded binary/generated/raw data artifacts.