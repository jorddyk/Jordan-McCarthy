# Jordan McCarthy Code Wiki

_Last updated: 2026-07-12 Europe/Zurich_

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
    docs/legacy-code-backfill.md
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
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves vNext3I output. | PowerShell/SSH. | Generated archive; do not commit. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks vNext3I status/logs. | Bash/Euler. | Console status. |
| `projects/jm105-intronsaurus/intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | Runs vNext3Y matched JM105 RNA/Sun protein Gene Stories. | Unrecovered Python builder, archive, workbook. | Generated site/tables/archive; excluded. |
| `projects/jm105-intronsaurus/intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | Uploads/submits vNext3Y. | PowerShell/SSH. | Remote submission. |
| `projects/jm105-intronsaurus/intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | Retrieves vNext3Y outputs. | PowerShell/SSH. | Generated outputs; excluded. |
| `projects/jm105-intronsaurus/intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh` | Checks vNext3Y status/logs. | Bash/Euler. | Console status. |
| `projects/jm105-intronsaurus/intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | Deduplicates Gene Stories labels and adds source/provenance UI. | Existing Intronsaurus DOM/data. | UI patch only; no biological values generated. |

### Verified JM101 provenance clue

`JM101_RNAseq_Protocol_and_Provenance.docx` in File Library verifies the `Y:/Jordan/JM101` project root, historical QuasR BAM path, metadata and annotation files, intron/exon counting, DESeq2 exon-derived size factors, `IRratio = (intron + 1)/(exon + 1)`, Rsubread/featureCounts expression analysis, and named output folders. This is provenance, not exact runnable source; no code was reconstructed from it.

### Highest-priority exact-source queue

1. `110_JM101_JM105_integrate_intronsaurus.py` → `analysis/jm101-jm105-integrate-intronsaurus.py`.
2. `111_JM101_STAR_align_array.sbatch` → `alignment/jm101-star-align-array.sbatch`.
3. `112_JM101_integrate_after_STAR.sbatch` → `analysis/jm101-integrate-after-star.sbatch`.
4. Rsubread Step 2 hard-resume/turbo scripts.
5. Step 3 DESeq2 and IRFinder drafts.
6. Full Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y builders/readers.
7. JM133/JM134 label-audit/rerender and Figure 2 candidate-gate code.

Status for unrecovered items: `exact full source not yet recovered in an accessible source`.

## Figure rendering

### Canonical runnable source

| Path | Purpose | Data status |
|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Renders JM105 Figure 1E/F print panels through PowerShell + embedded Python. | Real total/rRNA-depleted JM105 inputs; SVG/PNG/TSV/JSON audit outputs. |

Reusable prompt/spec assets live under `projects/figure-rendering/prompts/`. Current renderer queue includes main-figure layouts, story-architecture scoring, `NO DATA` placeholders, Figure 5, overlap audits, and JM133/JM134 rerender utilities. Preserve panel aspect ratio and lane geometry; unsupported panels say `NO DATA`.

## ImageJ / Fiji aging chips

### Canonical runnable source

No complete JM076/JM128/JM129 macro or Groovy source is currently canonical.

### Recovery ledger

`projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md` is the single source of truth for unrecovered microscopy scripts.

Priority targets:

- `macros/jm128-split-nd2-positions-bioformats.ijm`
- `macros/jm128-extract-mitosox-c2-every6-zpositions.ijm`
- `macros/jm128-stitch-image-and-image001-brightfield-rls.ijm`
- `macros/jm128-merge-ros-bf-fl.ijm`
- `groovy/jm129-mitosox-virtual-hyperstack-background-subtraction.groovy`
- JM076 Step 1/2/3/4/6 macros named in the historical lab protocol

Known clues include `Image001.nd2`, `Image001_Pos0_Hyperstack.tif`, `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`, `rollingBallRadius=100`, `C=2`, `Z=60`, `T=107/139/145`, and the RLS/ROS output filenames.

### Quantitative constraints

- No silent 8-bit conversion.
- No silent auto-contrast.
- Background subtraction must be explicit and documented.
- Display-only contrast must be labeled as display-only.
- Raw ND2/TIFF stacks and generated outputs stay out of GitHub.

## Language learning

| Path | Purpose | Runtime/status |
|---|---|---|
| `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html` | English→German Kartoffel-text vocabulary trainer. | Complete single-file browser app. |
| `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html` | TELC C1 essay-skeleton oral recall drill. | Complete single-file browser app; Web Speech API optional. |

Full-source gate: only import apps complete from `<!DOCTYPE html>` through `</html>`.

## Personal intelligence agency

Canonical prompt/spec assets include the legacy code backfill, daily code handoff, strategic alert triage, science preemption watch, Swiss leverage radar, and weekly strategic brief/red-team prompts.

# Code-focused execution risks and containment

- **Risk:** inaccessible ephemeral-sandbox claims can be mistaken for recovered source.
  - **Containment:** require a complete currently accessible source body before canonical import.
- **Risk:** detailed microscopy metadata can tempt plausible reconstruction with wrong indexing, channel order, bit depth, Bio-Formats calls, or saving behavior.
  - **Containment:** use the ImageJ backfill ledger as the single source of truth and import only verified complete source.
- **Risk:** daily handoffs can replace project organization.
  - **Containment:** code and current status stay under `projects/`; handoffs remain audit-only.
- **Risk:** JM105 figure logic can drift into poly-A/P-versus-T framing or confuse RNA abundance with protein abundance.
  - **Containment:** project README/wiki remain the source of truth for scientific constraints.

# Last-known canonical decisions

## 2026-07-12

- Repository verified private and writable on `main` with admin/push permissions.
- File Library searched for exact JM128/JM129 microscopy source using filenames, paths, dimensions, time ranges, rolling-ball setting, and output names.
- No complete Fiji macro or Groovy source was recovered; no runnable microscopy code was imported or reconstructed.
- Created `projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md` and updated the project README.
- Containment action: the backfill ledger is now the single source of truth for microscopy recovery state.
- No raw images, generated outputs, archives, logs, or temporary files were committed.

## 2026-07-11

- No complete new runnable source was recovered.
- Recorded `JM101_RNAseq_Protocol_and_Provenance.docx` as a verified recovery clue, not source code.
- Corrected recovery-state language for prior ephemeral-sandbox notes.

## 2026-07-10

- Imported `telc-c1-essay-skeleton-active-recall.html` from a complete HTML source.

## 2026-07-09

- Imported `kartoffel-vocabulary-active-recall.html` from complete File Library source.

## 2026-07-08

- Imported initial JM105 analysis/helpers, Intronsaurus helpers/patch, figure renderer/specs, and automation prompts.
