# Jordan McCarthy Code Wiki

_Last updated: 2026-08-27 Europe/Zurich_

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

## Aging-chip RLS pipeline

### Scientific state

- Purpose: convert longitudinal yeast aging-chip trap stacks into per-trap division counts, death calls and escape/censoring calls (survival-ready RLS) with bounded human QC.
- Canonical event semantics: division = Late Bud -> Mother/Early Bud bridging No Cell / Blurry gaps; confirmed death = living state -> Dead Cell; "Mother Escaped (Ignore Rest)" right-censors the trap (divisions and death at/after the escape frame do not count).
- 2026-08-27 revision: escape is a trainable 7th state class with a dedicated detector head and a calibrated sustained-run censor decoder; evaluation includes full post-escape frame tails; deployment gate = test MAE <= 1.00, within-1 >= 85%, death agreement >= 90%, escape agreement >= 90%.
- Current model status: deployment gate FAIL (automation withheld); promoted 2026-08-27 as the assistive instrument on dominance over the escape-blind incumbent. Untouched test (n=42 traps, seed-42 trap-level split 207/42/42 from 116,657 annotation rows across three chips): RLS MAE 3.07 overall, 1.12 on escape-clean traps; bias +0.17; death and escape agreement 85.7%. Six-condition interaction arms show no material signed bias in this sample (small n; re-audit as annotation grows).
- Trained `.keras` models, `master_human_annotations.xlsx`, TIFF stacks and per-run reports are deliberately excluded from this repo (hard rule 5); they live in the deployment folder with timestamped `pre_escape_*` backups.

### Canonical code

- `projects/aging-chip-rls-pipeline/human_classifier_ui.py` — trap annotator UI (single source of truth for human RLS and frame labels) with live AI overlay and calibrated detector HUD (division / death / escape-censoring calls).
- `projects/aging-chip-rls-pipeline/train_classifier.py` — endpoint-trained multitask trainer (7-class state + division/dead/escape heads), decoder calibration on held-out traps, deployment gate, candidate_* export on gate failure.
- `projects/aging-chip-rls-pipeline/diagnose_classifier.py` — frame- and trap-level audit of a deployed or candidate model against the master annotations.
- Decode functions are ported verbatim between trainer and UI; do not edit one without the other.
- Handoff record: `docs/handoffs/2026-08-27-aging-chip-rls-escape-retrofit-handoff.md`. Corresponding intelligence memo filed in Drive 2026-08-27 ("HEARTH UPDATE — RLS Tracker escape-censoring retrofit and assistive promotion").


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

Per the personal-intelligence-agency README's own canonicality rules, this project preserves only reusable architecture/prompts/schemas, never daily private intelligence products (Master Interaction Record, Canonical Ledger, Weekly Operating Board, Connection Tracking, Network Profiles, Forecast/Wrong Ledger, and similar Tier-1/Tier-2 live-state Drive documents are explicitly out of scope for this repository and were not touched by the 2026-08-03 pass).

## Rongorongo decipherment

### Scientific state

Statistical/computational cryptanalysis of the Rongorongo script. Every adjudication run recovered so far concludes `NO SYSTEM SURVIVED` / `NO AUTHENTIC BRIDGE SURVIVED`: no candidate decipherment system has cleared the preregistered promotion gates (external bridge, stable phonetic/grammatical value, fresh prediction, re-encoding rate, family-blocked significance, continuous passage). Five specific sign readings (`003=rongo`, `006=a/ki/particle`, `076=person/name marker`, `078=ure/lineage`, `200=ko/particle`) are explicitly rejected, not merely unconfirmed.

### Canonical code

- `projects/rongorongo/omega-swarm-reproduction/` — four `RECOVERED` reproduction scripts (`reproduce_structural_tests.py`, `01_reproduce_tournament.py`, `omega_reproduce.py`, `reproduce_adjudication_omega_swarm_f303e582.py`) for the 2026-07-16/17 OMEGA-SWARM adjudication runs over the frozen 141-passage corpus. Code is complete and `py_compile`-clean; each requires companion data files (`horley_encoding.py`, `horley_parallels.csv`, `frozen_passages.json`, `passage_atlas_frozen.csv`, an `RR_SEALED_IDENTITY...` workbook, an input manifest/systems CSV) that were not located in Drive — status `PARTIAL / CODE RECOVERED, INPUTS NOT LOCATED`.
- `projects/rongorongo/prometheus-null-compiler/rr_prometheus_compiler.py` — `RECOVERED`, self-contained, no external data dependency. Actually executed (`self-test`) during import and its output matched the source-recorded result exactly.
- `projects/rongorongo/hrfa-validator/rr_hrfa_validator.py` — `RECOVERED` (native `.py` file, not a doc mirror). Requires `formula_atlas.jsonl`, not located in Drive — status `PARTIAL / CODE RECOVERED, INPUT NOT LOCATED`.

Prior sealed blind-test branches (`rr/f6r1-jm-a1-sealed`, `rongorongo-y20f-sealed`, `rongorongo-phase19-temp`) remain intentionally unmerged per that project's own convention: they exist only to execute one preregistered test in a clean CI environment, with durable results transferred to the Rongorongo Drive ledger rather than kept in git history.

### Recovery source of truth

Two Drive folders were not deep-searched during the 2026-08-03 pass and are the most likely location of the missing companion data files above: "Rongorongo Decipherment" (id `1kcOu4vkaudFu7mWBS3efGT_HWfI1ngs2`) and "TAU_RONGORONGO_REPLICATION_PREP_2" (id `1PNj62Q3schlCmgigaJlpNJi0YGoSx4EY`).

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

## 2026-08-03

- Searched Google Drive and Gmail for new code/computational artifacts across all projects.
- JM105 figure-rendering: no new artifacts. The Figure 2 v10 lane-locked renderer register remains descriptive-only (confirms the 2026-07-30 finding); no `.py` bytes for v5/v9/v10 exist in Drive.
- Personal intelligence agency: no artifacts imported. Live Tier-1/Tier-2 state documents (Master Interaction Record, Canonical Ledger, Weekly Operating Board, Connection Tracking, Network Profiles, Forecast/Wrong Ledger, HEARTH operations memos) are out of scope per that project's own canonicality rules and were left untouched.
- Rongorongo decipherment: new project directory created at `projects/rongorongo/`. Recovered six complete, `py_compile`-clean Python files plus one JSON manifest from Drive documents (four OMEGA-SWARM reproduction scripts, one self-contained PROMETHEUS null compiler, one HRFA formula-atlas validator). One script (`rr_prometheus_compiler.py`) was independently executed and its self-test output verified against the source record; the shared Ba6 exact-probability constant was independently recomputed and verified. The other five scripts require companion data files not located in Drive (only referenced by name/SHA-256) and are therefore not independently runnable in this repository; each is labeled `PARTIAL / CODE RECOVERED, INPUT(S) NOT LOCATED`.
- No raw data, generated figures, credentials, or fabricated biological/linguistic values were committed.

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