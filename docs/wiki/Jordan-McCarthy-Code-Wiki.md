# Jordan McCarthy Code Wiki

_Last updated: 2026-08-05 Europe/Zurich_

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
- `projects/figure-rendering/panel-renderers/jm105-figure4-secondary-structure-accessibility/` — Figure 4G predicted splice-signal accessibility and RNAlib MFE-derived structure control using the locked Figure 4 selected/background data (selected n=49).
- `projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py` — `RECOVERED` exact complete standalone Figure 2F renderer. It reads the verified raw 402-row strict-gate table, derives all seven cumulative counts, hard-fails unless the final mask equals `candidate_passed_strict` with n=49, performs cross-font collision audits, exports transparent/editable figures and can refresh the Euler file inventory.
- Partial Figure 3 Mud1/CR package: runner/README canonical. The historical v21 Python pair is source-located in the verified 2026-07-15 v6 run and Jordan's retrieved local v6 bundle, but exact bytes are not yet canonical.

Prompt/spec assets under `projects/figure-rendering/prompts/` define Figure 5, manuscript-sequence, lane/collision, and artifact-package contracts. They are not runnable substitutes.

### Recovery source of truth

`projects/figure-rendering/docs/legacy-code-backfill.md`

Highest-priority missing or source-located code:

0. Figure 2 v10 lane-locked renderer `JM105_figure2_render_v10_lane_locked_20260728.py` (SHA-256 `fbd47169d0320e04c0eaf41692b9500be4b1cfa8f862e089b891507c497bd00e`) — supersedes `..._v9_FINAL_20260728.py`, which supersedes `..._v5_20260727.py`. Only a Drive register/transcript with metadata and hash is accessible; no `.py` bytes recovered as of 2026-08-05. `PARTIAL / SOURCE LOCATED`. This is now the preferred Figure 2 target ahead of the older `render_jm105_figure2_public_final.py` lineage.
1. Exact Figure 3 v21 sources `figure3_base_renderer.py` and `Figure_3_render_all_v21.py` — the latest verified source-bearing run is `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`; terminal retrieval records verify complete files of approximately 57 KB and 40 KB, matching `.pyc` companions, and the same files in Jordan's local `JM105_Figure3_Euler_Bundle_v6_EXTRACTED` results. Status: `PARTIAL / SOURCE LOCATED`; the connector exposes only the transcript, not source bytes.
2. Figure 2 public-final renderer — exact complete Python is source-located in File Library and at `/cluster/home/jmccarthy/JM105_Figure2_public_final_20260713_171245/scripts/render_jm105_figure2_public_final.py`; the corrected run succeeded after `threshold_c` → `threshold_cr`. Status: `PARTIAL / SOURCE LOCATED`, not yet imported because full bytes were unavailable to this run.
3. Figure 5 C/D/E public-clean renderer — exact uploaded `rerender_figure5_CDE_public_clean_labeled.py` and complete shell launcher were found in File Library. Status: `PARTIAL / SOURCE LOCATED`; no snippet reconstruction committed.
4. JM134 label-audit/rerender workflow; Euler jobs `3101802`, `3104275`, `3106256`, `3109225`.
5. Nature Aging/Yves-compatible main-figure layout renderer.
6. Figure-story scoring model.
7. Reusable `NO DATA` renderer.
8. Synopsis-aligned RNA-seq renderer.

The 2026-07-16 pass verified the latest Figure 3 v6 retrieval inventory. In addition to the v21 source pair, it contains the current `Figure_3_build_from_v21_and_JM100.py` (~33 KB). The run generated panel source tables and rendered assets before failing only at the composite hard cross-font audit: clipped headings and title/panel-letter overlaps were reported. This is a layout-QC blocker in the newer wrapper, not evidence of missing v21 logic or a biological-data failure. The next recovery must copy the exact `.py` bytes directly from the verified Euler run directory or Jordan's local v6 extraction.

The 2026-07-15 pass verified that the historical Figure 3 v21 source pair exists as complete files and has been retrieved into current build bundles. Two earlier execution failures were source/CLI invocation mismatches: a supplied candidate TSV lacked required `intron_id`, and another wrapper passed an unsupported positional path. Neither failure licenses editing or reconstructing the v21 source.

The 2026-07-14 pass verified that the exact complete Figure 2F seven-gate source is present in the canonical repository, so that item is now `RECOVERED` rather than source-located. The raw table and original generator remain on Euler under `Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/`. No biological code or values were reconstructed.

Rendering constraints: preserve aspect ratio and lane geometry; do not shrink text to solve crowding; editable SVG text; no tight cropping on fixed canvases; transparent final outputs; unsupported panels say `NO DATA`.

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

## 2026-08-05

- Repository re-verified private and writable on `main`; work delivered on branch `claude/dazzling-turing-hdmrkv`.
- Gmail and Google Drive searched as authorized sources; no new complete runnable canonical code found for any project area.
- `paper_style.py` re-verified byte-identical to the Drive copy; already canonical, no change.
- New Figure 2 renderer lineage identified (v5 → v9 → v10 lane-locked) via a Drive register/transcript; only metadata and a SHA-256 hash are accessible, not source bytes. Recorded in `projects/figure-rendering/docs/legacy-code-backfill.md` as the current preferred Figure 2 target.
- Out-of-taxonomy content noted: a Drive folder tree prefixed `RR_...` (e.g. `RR_OMEGA_SWARM_DIRECT_DECIPHERMENT...`, `RR_HRFA__HISTORICAL_RAPA_NUI_FORMULA_ATLAS...`) contains Python scripts unrelated to any current repo project (JM105, figure-rendering, ImageJ/Fiji, language-learning, personal-intelligence-agency); appears to be a separate personal/side workflow. Not imported; no project category exists for it yet.
- No biological data, generated renders, raw sequencing, microscopy stacks, or binary outputs were committed.

## 2026-07-16

- Repository re-verified private and writable on `main`.
- Latest verified Figure 3 source-bearing run: `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`.
- Exact complete source files confirmed in the retrieval inventory and Jordan's local v6 extraction: `figure3_base_renderer.py` (~57 KB), `Figure_3_render_all_v21.py` (~40 KB), and current wrapper `Figure_3_build_from_v21_and_JM100.py` (~33 KB).
- Source bodies remain `PARTIAL / SOURCE LOCATED` because the connector exposes only terminal transcripts, not the downloaded files.
- The v6 run reached rendered panel/output generation and then failed the composite cross-font audit due to clipped headings and title/panel-letter overlaps; this is layout QC, not biological-source failure.
- No source was reconstructed from logs; no raw data, generated renders, binaries, secrets, or invented biological values were committed.

## 2026-07-15

- Repository re-verified private and writable on `main`.
- Exact complete Figure 3 v21 source files are confirmed present on Euler and in retrieved local/build bundles, but remain `PARTIAL / SOURCE LOCATED` because exact `.py` bytes were not exposed to this automation.
- Verified filenames: `figure3_base_renderer.py` (~57 KB) and `Figure_3_render_all_v21.py` (~40 KB), with matching compiled companions.
- Recorded blockers are invocation/schema mismatches, not missing renderer logic: candidate TSV without `intron_id`, and unsupported extra positional CLI argument.
- No code was reconstructed from terminal output; no biological values, raw data, generated renders, logs, or binaries were committed.

## 2026-07-14

- Repository verified private and writable on `main`.
- Exact complete Figure 2F seven-gate renderer is `RECOVERED` at `projects/figure-rendering/panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py` (source commit `e4e64e91210cf0c353785c791cee36e2b8108403`).
- The renderer uses the real strict 402-row total/rRNA-depleted JM105 gate table, preserves `NMD_hidden = IR(upf1Δ) - IR(UPF1+)`, and hard-fails on schema/count/final-mask disagreement.
- No raw data, generated renders, logs, secrets, or reconstructed biological values were committed.

## 2026-07-13

- Daily Code Handoff restored as an enabled daily, write-capable operational continuity service.
- Network Evidence live permissions corrected to append only to the Master Interaction Record.
- Repository verified private and writable on `main` with admin/push permissions.
- Exact complete JM133 Python and sbatch sources verified on PR #1; source is uploaded to GitHub, while merge to `main` remains blocked by branch conflicts with newer main history.
- Exact Figure 2 public-final and Figure 5 C/D/E Python files were located in File Library/Euler evidence; they remain `PARTIAL / SOURCE LOCATED` because complete transferable bytes were unavailable in this run.
- Figure 2 corrected rerun was verified successful after the precise `threshold_c` → `threshold_cr` fix; the source used strict total/rRNA-depleted JM105 inputs and did not justify importing outputs or reconstructing code from logs.
- Figure 4G secondary-structure accessibility renderer remains registered under the canonical figure-rendering path; it uses the locked selected/background data and preserves the audited method caveats.
- No biological data, generated renders, raw sequencing, microscopy stacks, or binary outputs were committed.

## 2026-07-12

- No complete Fiji macro/Groovy source recovered; microscopy backfill ledger established.

## 2026-07-11

- JM101 provenance document recorded as a clue, not source code.

## 2026-07-10

- Imported complete TELC C1 essay-skeleton active-recall app.

## 2026-07-09

- Imported complete Kartoffel vocabulary active-recall app.