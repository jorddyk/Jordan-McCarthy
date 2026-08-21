# Jordan McCarthy Code Wiki

_Last updated: 2026-07-20 Europe/Zurich_

Canonical private repository: `jorddyk/Jordan-McCarthy`

## Repository purpose

Project-organized code vault. Canonical code lives under the project where a human would look for it; daily handoffs are audit logs only.

## Operating rules

1. Preserve only complete, clean, most-current source.
2. Prefer one canonical file over accumulating variants.
3. Never generate fake biological data; unsupported experiments or panels are `NO DATA`.
4. Distinguish real data, simulated toy data, and placeholders.
5. Exclude FASTQ/BAM/SAM/CRAM/BAI/bigWig, ND2/TIFF stacks, archives, logs, caches, scratch folders, and temporary renders.
6. Filenames, summaries, output lists, provenance documents, historical job success, prompts, and patch sequences are recovery clues—not recovered runnable source.
7. Quantitative microscopy must not silently convert to 8-bit or apply auto-contrast.
8. The Daily Code Handoff is an operational continuity service: it may search authorized sources, preserve exact complete code, update existing canonical files and this wiki, and commit safe changes to this private repository.
9. For manuscript figures, distinguish raw/source-table panel renderers, assembly-only scripts and deprecated diagnostics. An assembly success is not a panel-rerender success.

# Project areas

## JM105 / Intronsaurus

### Scientific state

- Figure 2 uses total/rRNA-depleted JM105 only unless Jordan explicitly changes this.
- Poly-A/P-versus-T/mRNA-like constructs remain excluded from Figure 2.
- NMD is primarily the detector; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Safe visible claim: CR suppresses part of an age-linked NMD-revealed retained-intron/leakage state in a Mud1-dependent way.
- Mud1 is a genetic handle/permissive requirement, not automatically the sole cause of every candidate intron.
- Distinguish host RNA abundance from protein abundance; CR is not starvation.

### Canonical code

- `projects/jm105-intronsaurus/analysis/jm105-old-cell-leaky-intron-determinants.py`
- Transformation-protocol sample resolver, manifest, Slurm runner, and PowerShell checker under `transformation-protocol-rnaseq/`.
- Intronsaurus vNext3I/vNext3Y launch/retrieval/status helpers and the vNext3AH UI patch under `intronsaurus-browser/`.
- Exact complete JM133 analysis and Euler launcher are preserved on open branch/PR `legacy-code-backfill-2026-07-08` / PR #1 at:
  - `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py`
  - `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch`
  Their source is uploaded to GitHub but not yet canonical on `main` because PR #1 currently requires conflict resolution against newer main history.

### Priority exact-source queue

`110_JM101_JM105_integrate_intronsaurus.py`, `111_JM101_STAR_align_array.sbatch`, `112_JM101_integrate_after_STAR.sbatch`, Rsubread Step 2 hard-resume/turbo, Step 3 DESeq2, IRFinder drafts, complete vNext3/vNext3AE builders/readers, JM134 analysis utilities, `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py`, `26_paired_gene_body_normalized_leakage_test.py`, and `28_make_synopsis_aligned_all_intron_RNAseq_plots.py`. Status: exact full source not yet recovered unless already listed canonical or preserved on the named branch.

## Figure rendering

### Canonical code and infrastructure

- `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1`
- `projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py`
- Figure 4E Euler/retrieval wrappers.
- `projects/figure-rendering/panel-renderers/jm105-rendering-harness/`
- `projects/figure-rendering/panel-renderers/jm105-fig4bc-sequence-architecture/`
- `projects/figure-rendering/panel-renderers/jm105-figure4-secondary-structure-accessibility/` — Figure 4G predicted splice-signal accessibility and RNAlib MFE-derived structure control using the locked Figure 4 selected/background data.
- `projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py` — `RECOVERED` exact complete standalone Figure 2F renderer. It reads the verified raw 402-row strict-gate table, derives all seven cumulative counts, hard-fails unless the final mask equals `candidate_passed_strict` with n=49, performs cross-font collision audits and exports transparent/editable figures.
- `projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/` — complete targeted Figure 3 A/D/G v22 modules, Euler launcher, README and validation record are preserved on draft PR #7. Status: `RECOVERED / DRAFT PR`, with two exact historical v21 dependencies still awaiting byte-for-byte standalone import.

The Figure 3 v22 tracked files include:

- `render_figure3_ADG_v22.py`
- `figure3_adg_v22_common.py`
- `figure3_adg_v22_manifest.py`
- `figure3_adg_v22_panel_a.py`
- `figure3_adg_v22_panel_d.py`
- `figure3_adg_v22_panel_g.py`
- `render_figure3_ADG_v22.sbatch`
- `VALIDATION_ADG_v22.json`

Prompt/spec assets under `projects/figure-rendering/prompts/` define Figure 5, manuscript-sequence, lane/collision, and artifact-package contracts. They are not runnable substitutes.

### Recovery source of truth

`projects/figure-rendering/docs/legacy-code-backfill.md`

Highest-priority missing or source-located code:

1. Exact Figure 3 v21 dependencies `figure3_base_renderer.py` and `Figure_3_render_all_v21.py`. Jordan recovered them from `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316` into `JM105_Figure3_v21_RECOVERY_20260720_154634.tar.gz`; hashes are verified. Status: `PARTIAL / EXACT ARCHIVE RECOVERED`; the files remain absent as standalone GitHub files because the current connector could not transfer their complete large bodies.
2. Figure 2 public-final renderer — exact complete Python is source-located in File Library and at `/cluster/home/jmccarthy/JM105_Figure2_public_final_20260713_171245/scripts/render_jm105_figure2_public_final.py`; corrected run succeeded after `threshold_c` → `threshold_cr`. Status: `PARTIAL / SOURCE LOCATED`.
3. Figure 5 C/D/E public-clean renderer — exact uploaded `rerender_figure5_CDE_public_clean_labeled.py` and complete shell launcher were found in File Library. Status: `PARTIAL / SOURCE LOCATED`.
4. JM134 label-audit/rerender workflow; Euler jobs `3101802`, `3104275`, `3106256`, `3109225`.
5. Nature Aging/Yves-compatible main-figure layout renderer.
6. Figure-story scoring model.
7. Reusable `NO DATA` renderer.
8. Synopsis-aligned RNA-seq renderer.

Rendering constraints: preserve aspect ratio and lane geometry; do not shrink text to solve crowding; editable SVG text; no tight cropping on fixed canvases; transparent final outputs; white previews separate; unsupported panels say `NO DATA`.

## ImageJ / Fiji aging chips

No complete JM076/JM128/JM129 macro or Groovy source is currently canonical. Recovery status is maintained in `projects/imagej-fiji-aging-chips/docs/legacy-code-backfill.md`.

Priority targets include ND2 position splitting, C2 MitoSOX extraction, BF/FL/ROS/RLS merging, virtual hyperstacks, and quantitative rolling-ball background subtraction. Known clues include `Image001.nd2`, `Image001_Pos0_Hyperstack.tif`, `MitosoxRedInducibleFusionsRepeat.nd2`, `Continue001.nd2`, `Continue002.nd2`, `rollingBallRadius=100`, `C=2`, `Z=60`, `T=107/139/145`, and the named RLS/ROS outputs.

## Language learning

Canonical complete single-file apps:

- `projects/language-learning/active-recall-apps/kartoffel-vocabulary-active-recall.html`
- `projects/language-learning/active-recall-apps/telc-c1-essay-skeleton-active-recall.html`

Only import web apps complete from `<!DOCTYPE html>` through `</html>`.

## Personal intelligence agency

Canonical prompt/spec assets cover legacy backfill, daily code handoff, strategic alert triage, science preemption, Swiss leverage, and weekly strategic briefing/red-team tasks. Live task configuration, rather than historical README wording, determines current permissions.

# Code-focused execution risks and containment

- **Risk:** legacy code remains trapped in old chats while remembered filenames/job IDs create false confidence.
  - **Containment:** project-local backfill ledgers are the source of truth; complete currently accessible source is required before canonical import.
- **Risk:** daily handoffs replace project organization.
  - **Containment:** code/status live under `projects/`; handoffs remain audit-only.
- **Risk:** figure patch sequences create one-off sprawl and violate original geometry.
  - **Containment:** canonicalize only complete final renderers and enforce the rendering operating standard.
- **Risk:** real/simulated/`NO DATA` status drifts.
  - **Containment:** declare data status in project README, renderer outputs, and handoff.
- **Risk:** code preservation is disabled during agency restructuring.
  - **Containment:** Daily Code Handoff is explicitly exempt from campaign-count reductions and may be disabled only by a direct Jordan instruction.

# Last-known canonical decisions

## 2026-07-20

- Repository re-verified private and writable.
- Exact Figure 3 recovery archive confirmed: `JM105_Figure3_v21_RECOVERY_20260720_154634.tar.gz`.
- Exact v21 source hashes verified:
  - `Figure_3_render_all_v21.py`: `2595f23d89c0b040d861f95d3b26139c1856eb00103625c05e4498d21d4de8a4`
  - `figure3_base_renderer.py`: `9a8e87fdccd5509eb33328a6177350e442078c78be3025721975f504d97ddce1`
- Complete Figure 3 A/D/G v22 source modules, launcher, README and validation record committed to draft PR #7 under `projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/`.
- Panel D corrected encoding is open = old 2% glucose; filled = old 0.1% glucose CR; horizontal position remains quantitative NMD-hidden IR.
- Panel G local source-table preflight: 402 finite pairs, 22 outside the old display limit, zero clipped in v22.
- Figure 3 v22 remains draft pending raw Euler execution and byte-for-byte standalone import of the exact v21 dependency pair.
- No raw sequencing data, generated figures, logs, cluster scratch, secrets, credentials or invented biological values were committed.

## 2026-07-16

- Repository re-verified private and writable on `main`.
- Latest verified Figure 3 source-bearing run: `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`.
- Exact complete source files confirmed in the retrieval inventory and Jordan's local v6 extraction: `figure3_base_renderer.py`, `Figure_3_render_all_v21.py`, and current wrapper `Figure_3_build_from_v21_and_JM100.py`.
- Source bodies remained `PARTIAL / SOURCE LOCATED` at that time because the connector exposed terminal transcripts rather than files.
- The v6 run reached rendered panel/output generation and then failed the composite cross-font audit; this was layout QC, not biological-source failure.

## 2026-07-14

- Exact complete Figure 2F seven-gate renderer is `RECOVERED` at `projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py`.
- The renderer uses the real strict 402-row total/rRNA-depleted JM105 gate table, preserves `NMD_hidden = IR(upf1Δ) - IR(upf1+)`, and hard-fails on schema/count/final-mask disagreement.

## 2026-07-13

- Daily Code Handoff restored as an enabled daily, write-capable operational continuity service.
- Repository verified private and writable with admin/push permissions.
- Exact complete JM133 Python and sbatch sources verified on PR #1; merge remains blocked by branch conflicts.
- Exact Figure 2 public-final and Figure 5 C/D/E Python files were located but remained `PARTIAL / SOURCE LOCATED`.

## 2026-07-12

- No complete Fiji macro/Groovy source recovered; microscopy backfill ledger established.

## 2026-07-10

- Imported complete TELC C1 essay-skeleton active-recall app.

## 2026-07-09

- Imported complete Kartoffel vocabulary active-recall app.
