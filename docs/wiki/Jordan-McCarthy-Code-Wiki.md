# Jordan McCarthy Code Wiki

_Last updated: 2026-07-11 Europe/Zurich_

Canonical private repository: `jorddyk/Jordan-McCarthy`

## Repository purpose

This repository is Jordan's project-organized code vault. Canonical code lives under the project where a human would look for it; daily handoffs are audit logs only.

## Repository map

```text
README.md
projects/
  README.md
  jm105-intronsaurus/
    README.md
    analysis/
    alignment/
    figures/
    transformation-protocol-rnaseq/
    jm134-starvation-switch/
    jm133-weak-5ss-mud1/
    figure2-candidate-gate/
    intronsaurus-browser/
    docs/
  figure-rendering/
    README.md
    nature-aging-mockups/
    panel-renderers/
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
    prompts/
    rubrics/
    docs/
docs/
  wiki/Jordan-McCarthy-Code-Wiki.md
  handoffs/YYYY-MM-DD-code-handoff.md
```

## Operating rules

1. Preserve only complete, clean, most-current source.
2. Prefer updating one canonical file over accumulating variants.
3. Never generate fake biological data.
4. Mark unperformed experiments or unsupported panels `NO DATA`.
5. Distinguish real data, simulated toy data, and placeholders.
6. Do not commit FASTQ, BAM, SAM, CRAM, BAI, bigWig, ND2, TIFF stacks, archives, logs, caches, scratch folders, or temporary renders.
7. A filename, summary, output list, provenance document, or prior ephemeral-sandbox note is not recovered source code.
8. For quantitative microscopy, never silently convert to 8-bit or apply auto-contrast; document channel, Z, T, frame sampling, background subtraction, and display-only contrast.

# Project areas

## JM105 / Intronsaurus

### Scientific state

- Figure 2 uses total/rRNA-depleted JM105 only unless Jordan explicitly changes this.
- Poly-A / P-versus-T / mRNA-like constructs remain excluded from Figure 2.
- NMD is primarily the detector; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Current safe claim: CR suppresses part of an age-linked NMD-revealed retained-intron/leakage state in a Mud1-dependent way.
- Mud1 is a genetic handle/permissive requirement, not automatically the sole cause of every candidate intron.
- Distinguish host RNA abundance from protein abundance.
- Do not call caloric restriction starvation.

### Canonical runnable/helper code

| Path | Purpose | Inputs/environment | Outputs/data status |
|---|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py` | Classifies old-selective NMD-revealed introns and tests module/splice-architecture determinants. | Real JM105 tables; Python scientific stack on Euler. | Real-data tables/figures; no fake data. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/resolve-fastq-files.py` | Resolves transformation-protocol FASTQ aliases. | Sample manifest and Euler paths. | File map only. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/transformation-protocol-samples.tsv` | JM62-JM73 sample metadata. | None. | Human-readable metadata; no reads. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/run-transformation-expression.sbatch` | Launches transformation-protocol expression workflow. | Slurm/Euler and referenced scripts. | Workflow outputs; logs excluded. |
| `projects/jm105-intronsaurus/transformation-protocol-rnaseq/check-transformation-job.ps1` | Checks Euler job/log status. | PowerShell/SSH. | Console only. |
| `projects/jm105-intronsaurus/intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | Runs vNext3I Explore restoration. | Unrecovered Python builder and patch dependencies on Euler. | Generated HTML/archive; excluded by default. |
| `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | Uploads/submits vNext3I. | PowerShell/SSH. | Remote submission. |
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves vNext3I output. | PowerShell/SSH. | Local generated archive; do not commit. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks vNext3I status/logs. | Bash/Euler. | Console status. |
| `projects/jm105-intronsaurus/intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | Runs vNext3Y matched JM105 RNA/Sun protein Gene Stories. | Unrecovered Python builder, archive, workbook. | Generated site/tables/archive; excluded. |
| `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | Uploads/submits vNext3Y. | PowerShell/SSH. | Remote submission. |
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | Retrieves vNext3Y outputs. | PowerShell/SSH. | Local generated outputs; excluded. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh` | Checks vNext3Y status/logs. | Bash/Euler. | Console status. |
| `projects/jm105-intronsaurus/intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | Deduplicates Gene Stories labels and adds source/provenance UI. | Existing Intronsaurus DOM/data. | UI patch only; no biological values generated. |

### Scientific/context documents

| Path | Purpose | Status |
|---|---|---|
| `projects/jm105-intronsaurus/docs/what-data-shows-summary.md` | Current JM105 interpretation guardrails. | Verified context; not runnable. |
| `projects/jm105-intronsaurus/docs/legacy-code-backfill.md` | Exact-source recovery queue and clues. | Active documentation; not code. |

### Verified JM101 provenance clue

`JM101_RNAseq_Protocol_and_Provenance.docx` in File Library verifies:

- `Y:/Jordan/JM101` project root.
- `C:/rna_seq/quasr_bam` historical QuasR-compatible BAM path.
- `metadata_clean.csv`, `yeast_introns_sacCer3.rds`, `SGD_features.tab`.
- QuasR intron/exon counting; DESeq2 exon-derived size factors.
- `IRratio = (intron + 1)/(exon + 1)` and intron fraction outputs.
- Rsubread/featureCounts gene-level counts, CPM, genotype×age model, and explicit ratio-of-ratios cross-check.
- Output folders `ir_outputs/` and `expression_outputs/` with named CSV/XLSX/volcano/sanity outputs.

This is provenance, not exact runnable source. No code was reconstructed from it.

### Highest-priority exact-source queue

1. `110_JM101_JM105_integrate_intronsaurus.py` → `analysis/jm101-jm105-integrate-intronsaurus.py`.
2. `111_JM101_STAR_align_array.sbatch` / later load-stack variant → `alignment/jm101-star-align-array.sbatch`.
3. `112_JM101_integrate_after_STAR.sbatch` / later load-stack variant → `analysis/jm101-integrate-after-star.sbatch`.
4. Rsubread Step 2 hard-resume and throughput-turbo scripts.
5. Step 3 DESeq2 and IRFinder drafts.
6. Full Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y builders/readers.
7. `scripts/26_paired_gene_body_normalized_leakage_test.py`.
8. `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`.
9. JM133 weak-5′SS source staged historically in PR #1 but not canonical on `main`.
10. JM134 label-audit/rerender code and Figure 2 candidate-gate code.

Status for all unrecovered items: `exact full source not yet recovered in an accessible source` unless a complete body is explicitly present in GitHub.

## Figure rendering

### Canonical runnable source

| Path | Purpose | Data status |
|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Renders JM105 Figure 1E/F print panels through PowerShell + embedded Python. | Real total/rRNA-depleted JM105 inputs; SVG/PNG/TSV/JSON audit outputs. |

### Reusable prompt/spec assets

- `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md`
- `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md`
- `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md`
- `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md`

These are non-runnable workflow contracts.

### Current renderer queue

- `nature-aging-mockups/render-main-figure-layouts.py`
- `nature-aging-mockups/score-figure-story-architecture.py`
- `panel-renderers/render-no-data-placeholder.py`
- `nature-aging-mockups/figure-5-layout-renderer.py`
- `panel-renderers/avoid-label-overlap-audit.py`
- JM133/JM134 label audit/rerender utilities

Figure constraints: preserve panel aspect ratio and lane geometry; keep SVG text editable; fixed canvases remain fixed; use separate transparent and white-preview outputs; unsupported panels say `NO DATA`.

## ImageJ / Fiji aging chips

Status: exact full JM128/JM129 macro/Groovy source remains unrecovered.

Priority clues:

- `Image001.nd2`
- `Image001_Pos0_Hyperstack.tif`
- `Y:/Laura/JM128 How do superoxide levels change during aging/seperate_positions`
- `MitosoxRedInducibleFusionsRepeat.nd2`
- `Continue001.nd2`, `Continue002.nd2`
- `rollingBallRadius=100`
- `C=2`, `Z=60`, `T=107/139/145`
- `Nup60Gcn5MitoSoxRed_RLS_Pos0.tif`
- `Nup60Gcn5MitoSoxRed_ROS_Pos{outPos}_merged.tif`

Proposed canonical targets:

- `macros/jm128-split-nd2-positions-bioformats.ijm`
- `macros/jm128-extract-mitosox-c2-every6-zpositions.ijm`
- `groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`

## Language learning

| Path | Purpose | Runtime/status |
|---|---|---|
| `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html` | English→German Kartoffel-text vocabulary trainer. | Complete single-file browser app. |
| `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html` | TELC C1 essay-skeleton oral recall drill. | Complete single-file browser app; Web Speech API optional. |

Full-source gate: only import apps complete from `<!DOCTYPE html>` through `</html>`.

## Personal intelligence agency

Canonical prompt/spec assets include:

- `projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md`
- `projects/personal-intelligence-agency/prompts/code-handoff.md`
- `projects/personal-intelligence-agency/prompts/strategic-alert-triage.md`
- `projects/personal-intelligence-agency/prompts/science-preemption-watch.md`
- `projects/personal-intelligence-agency/prompts/swiss-leverage-radar.md`
- `projects/personal-intelligence-agency/prompts/weekly-strategic-brief-redteam.md`

Current target: exact 0-to-21 strategic-signal scoring rubric and reusable report/email templates, if complete source exists.

# Code-focused execution risks and containment

- **Risk:** prior notes can say source was recovered in an ephemeral sandbox even though the body is no longer accessible.
  - **Containment:** treat inaccessible ephemeral-source claims as clues only; require re-verification before canonical import.
- **Risk:** script names and provenance summaries can be mistaken for source code.
  - **Containment:** label them `exact full source not yet recovered` and never reconstruct runnable source from narrative.
- **Risk:** daily handoffs can replace project organization.
  - **Containment:** code and current status stay under `projects/`; handoffs remain audit-only.
- **Risk:** JM105 figure logic can drift into poly-A/P-versus-T framing or confuse RNA abundance with protein abundance.
  - **Containment:** project README/wiki are the source of truth for current scientific constraints.

# Last-known canonical decisions

## 2026-07-11

- Repository verified private and writable on `main` with admin/push permissions.
- No complete new runnable source was recovered.
- File Library searches for `110`, `111`, `112`, STAR, Rsubread hard-resume/turbo, Step 3 DESeq2, and IRFinder returned no exact source body.
- `JM101_RNAseq_Protocol_and_Provenance.docx` was recorded as a verified recovery clue with paths, metrics, outputs, and troubleshooting.
- Corrected recovery-state language: a prior ephemeral-sandbox report is not equivalent to currently accessible canonical source.
- No biological data, raw sequencing/microscopy files, generated sites, archives, logs, or temporary outputs were committed.

## 2026-07-10

- Imported `telc-c1-essay-skeleton-active-recall.html` from a complete HTML source.
- Updated project-first documentation and handoff audit.

## 2026-07-09

- Imported `kartoffel-vocabulary-active-recall.html` from complete File Library source.

## 2026-07-08

- Imported initial JM105 analysis/helpers, Intronsaurus helpers/patch, figure renderer/specs, and automation prompts.