# Legacy Code Backfill

Status date: 2026-07-08

This file tracks code recovered from old ChatGPT/project history, uploaded artifacts, and Jordan-authorized sources. It is not a daily handoff. Daily handoffs are audit logs only.

## Repository rules applied

- Organize code by project and purpose, not by date.
- Keep the newest useful canonical version rather than every scratch attempt.
- Do not invent missing source code from summaries.
- Do not commit raw FASTQ/BAM/ND2/TIFF or generated figure images unless explicitly needed as small examples.
- For JM105/Intronsaurus, preserve the current scientific constraints: Figure 2 is total/rRNA-depleted only; no poly-A for Figure 2 unless explicitly restored; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal; distinguish RNA abundance from protein abundance; do not equate CR with starvation.

## Imported in the 2026-07-08 legacy backfill pass

| Canonical path | Project | Purpose | Scientific/data status |
|---|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py` | JM105 / Intronsaurus | Classifies old-selective NMD-revealed introns and tests module + splice-architecture determinants including 5′SS, branchpoint, 3′SS, and PPT features. | Uses real JM105 Euler tables as inputs. No fake biological data. |
| `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md` | Figure rendering | Exact prompt/spec for rendering Figure 5 from PowerShell + Euler with NO DATA placeholders, lane-map/collision/provenance workflow, and fixed-canvas export rules. | Prompt/spec only; no biological data; not runnable code. |
| `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md` | Figure rendering | Exact prompt/spec for Nature Aging / Yves-compatible JM105 figure-sequence redesign. | Prompt/spec only; no biological data; not runnable code. |
| `projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md` | Personal intelligence agency | Exact reusable prompt for code-backfill/search/commit workflow into `jorddyk/Jordan-McCarthy`. | Prompt/workflow artifact only; no biological data; not runnable code. |

## Recovered exact source files identified in current project context

### JM105 transformation-protocol RNA-seq deliverable

Likely canonical path:

```text
projects/jm105-intronsaurus/transformation-protocol-rnaseq/
```

Exact uploaded source folder found in current session:

```text
/mnt/data/JM105_Transformation_Protocol_Pipeline/
```

Files present in the recovered folder:

```text
01_JM105_Upload_And_Submit.ps1
02_JM105_Download_Results.ps1
03_JM105_Check_Job.ps1
JM105_resolve_fastqs.py
JM105_run_transformation_expression.sh
JM105_transformation_expression.sbatch
JM105_build_relative_abundance_excel.py
JM105_transformation_protocol_samples.tsv
README_JM105_Transformation_Protocol.txt
```

Scientific/data status: real JM105 transformation-protocol RNA-seq support workflow; no fake biological data. Binary Excel template and generated output workbook were deliberately not committed in this initial pass.

Status: exact full source recovered locally in an earlier run; small scripts/config should be imported first; larger builder script is queued for source-preserving import.

### JM-134 matched splicing-index / Parenteau starvation-switch analysis

Likely canonical path:

```text
projects/jm105-intronsaurus/jm134-starvation-switch/
```

Exact uploaded source files found:

```text
/mnt/data/JM134_matched_splicing_index.py
/mnt/data/JM134_submit_matched_SI.sh
/mnt/data/JM134_rerender_no_overlap.py
/mnt/data/JM134_run_on_Euler.sh
/mnt/data/81_JM134_symlog_clarity_and_notebook.py
```

Additional exact source appears in current chat history, but needs import as text before being called fully recovered:

```text
scripts/79_JM134_audit_and_beta_binomial.py
scripts/80_JM134_apply_beta_binomial_and_rerender.py
scripts/83_JM134_final_guide_repair.py
```

Scientific/data status: real JM105 total RNA-seq compared with Parenteau/gkaf525 supplementary tables. The beta-binomial update recovered 24 JM105 intron-contrast hits at FDR < 0.10 after the first unweighted ratio-model significance layer produced only 1 hit. No fake biological data.

Known dependency/status notes:

- `81_JM134_symlog_clarity_and_notebook.py` imports Euler-side `scripts/78_JM134_rerender_for_immediate_meaning.py`; the exact full source for script 78 must be preserved before 81 is standalone from the repo.
- `83_JM134_final_guide_repair.py` was the newest layout-repair wrapper at the time of backfill but was blocked from validation by Euler partition downtime/reduced capacity.
- `JM134_run_on_Euler.sh` is an older exploratory S3/S5 overlap workflow and should not be promoted over the matched SI / beta-binomial pipeline unless needed for provenance.

Status: exact local files identified; canonical subset still being imported.

### JM-133 weak 5′ splice-site / Mud1-dependence analysis

Likely canonical path:

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/
```

Source clues:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/scripts/71_JM133_weak_5SS_need_Mud1.py
/cluster/scratch/jmccarthy/JM105_RNAseq/71_JM133_DO_WEAK_5SS_NEED_MUD1/
Y:\Jordan\JM133 Do weak 5′ splice sites need Mud1
```

Known outputs included primary Q1 figures, named-candidate tables, hard checks, and tarball `JM133_Do_weak_5SS_need_Mud1.tar.gz`. Result: genome-wide correlation between U1 strength and Mud1-dependence was not supported, while six of eight named candidates were Mud1-dependent by the recovered table.

Status: exact full source was canonicalized on open branch/PR `legacy-code-backfill-2026-07-08`; not yet merged to `main` as of this continuation pass.

### JM105 Figure 2 stage-1 audit / candidate gate

Likely canonical path:

```text
projects/jm105-intronsaurus/figure2-candidate-gate/
```

Source clues:

```text
Figure2_stage1_audit_YYYYMMDD_HHMMSS/figure2_stage1_audit.py
Figure_2_input_SHA256SUMS.tsv
Figure_2_candidate_gate_summary.tsv
Figure_2_candidate_ranking.tsv
Figure_2_panel_provenance.json
```

Definitions from project memory:

```text
NMD-hidden IR = IR(upf1Δ) − IR(UPF1+)
aging effect = old 2% − young 2%
CR suppression = old 2% − old 0.1% CR
joint_score = min(aging_effect, CR_suppression)
```

Status: exact full source not yet recovered; source clue retained.

### JM105 current RNA-seq poster scripts

Likely canonical paths:

```text
projects/jm105-intronsaurus/analysis/jm105-paired-gene-body-normalized-leakage-test.py
projects/jm105-intronsaurus/figures/jm105-synopsis-aligned-all-intron-rnaseq-plots.py
projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py
```

Source clues:

```text
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
scripts/29_old_cell_leaky_intron_determinants.py
```

Status:

- `analysis/jm105-old-cell-leaky-intron-determinants.py` imported.
- Scripts 26 and 28 are next import targets; exact full source was visible in project chat but was not imported during this pass.

### Intronsaurus vNext3AH fix10 archive

Likely canonical path:

```text
projects/jm105-intronsaurus/intronsaurus-browser/
```

Source clue:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/code/intronsaurus_vnext3AH_fix10_mrna_like_premrna_model/148_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX10.tar.gz
interactive/Intronsaurus_Explore_Restored_vNext3AH_fix10.html
```

Status: exact archive exists on Euler per project memory, but full source not recovered into GitHub in this pass.

### ImageJ/Fiji aging-chip macros

Likely canonical path:

```text
projects/imagej-fiji-aging-chips/
```

High-priority JM128/JM129 source clues:

```text
jm128-split-nd2-positions-bioformats.ijm
jm128-extract-mitosox-c2-every6-zpositions.ijm
jm129-mitosox-virtual-hyperstack-background-subtraction.groovy
```

Additional Google Drive lab-notebook source clues recovered in this continuation pass:

```text
Y:\Jordan\JM076\Macros\Step1_DetectAdjustConvertResize.ijm
Y:\Jordan\JM076\Macros\Step2_BriightfieldExtractor.ijm
Y:\Jordan\JM076\Macros\Step_3ConvertResize.ijm
Y:\Jordan\JM076\Macros\Step4_RemovebrightfieldSlicesFromStack.ijm
Y:\Jordan\JM076\Macros\Step6_RedChannelMacro.ijm
```

The JM-076 clues come from `Lab Notebook complete copy and paste text dump`, under an aging-chip protocol for intronless nuclear-encoded mitochondrial genes tagged with Tom70-yemScarlet3. The document gives macro names and workflow but not macro bodies, so these remain recovery targets rather than imported code.

Microscopy rules to preserve when importing:

- Do not commit raw ND2/TIFF stacks.
- Do not silently convert quantitative data to 8-bit.
- Do not silently apply auto-contrast to quantitative data.
- Document channel, Z, T, frame sampling, background subtraction, and output naming.

Status: exact full source not yet recovered; source clue retained.

### Figure rendering / Nature Aging mockups

Likely canonical path:

```text
projects/figure-rendering/nature-aging-mockups/
```

Source clues: Figure 5 renderer prompts, PowerPoint/docx panel assets, Nature Aging/Yves-compatible figure-layout mockup code, no-data placeholder renderers, fixed-canvas panel scripts.

Imported prompt/spec artifacts:

```text
projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md
projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md
```

Status: prompt/spec artifacts imported. Exact runnable figure-rendering source not yet recovered. Do not reconstruct from mockup descriptions; mark missing panels as `NO DATA` when code is recovered.

### German/TELC/language-learning apps

Likely canonical path:

```text
projects/language-learning/
```

Source clue:

```text
projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html
```

Status: exact full source not yet recovered.

### Personal intelligence agency prompts/rubrics

Likely canonical path:

```text
projects/personal-intelligence-agency/
```

Imported prompt/workflow artifact:

```text
projects/personal-intelligence-agency/prompts/legacy-code-backfill-github-import.md
```

Recovered conceptual structure:

- Code handoff task remains persistent.
- Four other scheduled tasks were consolidated around strategic alert triage, science preemption watch, Swiss leverage radar, and weekly strategic brief/red-team.

Status: legacy-code-backfill prompt imported. Other exact scheduled-task prompt texts should be imported from scheduled-task records or old chats; not reconstructed here.

## Current continuation pass — 2026-07-08 11:51 Europe/Zurich

- Verified `jorddyk/Jordan-McCarthy` is private and writable with admin/push permissions.
- Searched Google Drive for JM105/Intronsaurus/JM134/Fiji/MitoSOX/source-clue terms.
- Searched Gmail for prior code-handoff records and code-like attachment queries.
- Found the open PR `legacy-code-backfill-2026-07-08` containing JM-133 code; because it is open and not mergeable from the connector context, this pass did not duplicate or overwrite that runnable code on `main`.
- Updated ImageJ/Fiji recovery documentation with exact JM-076 historical macro paths from the lab notebook.
- No newly recovered full source code was committed in this continuation pass; only source-clue documentation was updated.
