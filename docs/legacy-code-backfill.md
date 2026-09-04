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
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Figure rendering | Recovered PowerShell + embedded-Python renderer for JM105 Figure 1E/F content-only print panels. Produces transparent SVG/PNG/3x PNG, white-preview PNG, TSV panel data, and JSON audit/provenance. | Uses real local JM105 total/rRNA-depleted source tables if present. No fake biological data. No poly-A. Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR; Panel F uses an audited raw NMD-off set definition and does not claim off-minus-on NMD-hidden IR. |
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
projects/figure-rendering/
```

Imported runnable source:

```text
projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1
```

Imported prompt/spec artifacts:

```text
projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md
projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md
```

Source clues: Figure 5 renderer prompts, PowerPoint/docx panel assets, Nature Aging/Yves-compatible figure-layout mockup code, no-data placeholder renderers, fixed-canvas panel scripts.

Status: first runnable panel-rendering source imported. Exact runnable source for broader mockup rendering, no-data placeholders, and label-overlap auditing is still not recovered. Do not reconstruct from mockup descriptions; mark missing panels as `NO DATA` when code is recovered.

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

## Current continuation pass — 2026-07-08 figure-rendering renderer recovery

- Verified `jorddyk/Jordan-McCarthy` is private and writable with admin/push permissions.
- Searched current project context and File Library for Figure 1E/F, Figure 5, Figure 2–5 mockup, and Nature Aging rendering source clues.
- Recovered and imported the newest useful complete PowerShell/Python renderer for JM105 Figure 1E/F content-only print panels.
- Updated `projects/figure-rendering/README.md`, `projects/figure-rendering/panel-renderers/README.md`, `projects/figure-rendering/docs/legacy-code-backfill.md`, and `docs/wiki/Jordan-McCarthy-Code-Wiki.md`.
- Deliberately did not commit generated Figure 2–5 mockup PNGs because they are visual artifacts with schematic/mock values, not source code.
- Deliberately did not reconstruct missing renderers such as `render-no-data-placeholder.py` or `render-main-figure-layouts.py`; they remain recovery targets until exact source is found.

## Current continuation pass — 2026-08-16 scheduled backfill sweep

- Verified `jorddyk/Jordan-McCarthy` is reachable and current project structure/READMEs were fetched before making changes.
- Searched Google Drive (recent files plus targeted `fullText`/`title` queries for JM134, JM133, Fiji/ImageJ/MitoSOX, `.py`/`.ijm`/`.ps1`/`.sbatch`/`.groovy`/`.html`, `kartoffel`, `render-no-data-placeholder`, `render-main-figure-layouts`) for code not yet in the repo.
- Gmail connector in this session exposes only send/reply/forward/spam/trash actions; no message-search or read tool was available, so Gmail could not be searched for code attachments this pass.
- Found `paper_style.py` (JM105 aging/CR/Mud1 manuscript visual-style module) in Drive. Compared byte-for-byte against `projects/figure-rendering/jm105-figure-bible/paper_style.py`: already canonical in the repo (only difference is an unused `Iterable` import already cleaned up on the committed version). Nothing to import.
- Re-checked "Lab Notebook complete copy and paste text dump" for JM-076 ImageJ/Fiji macro bodies referenced in this file's earlier entries; still only macro names/workflow are present, no macro source. Status unchanged: `exact full source not yet recovered`.
- Found two Drive items that are explicitly out of scope and were **not** imported:
  - A large set of recently modified "HEARTH" documents (operation briefs, memoranda, network/relationship profiles with named individuals, forecast ledgers, WhatsApp-sourced intake notes, negotiation prep). These are exactly the "daily private intelligence products" / "message transcripts" / raw sensitive source material that `projects/personal-intelligence-agency/README.md` says must never be committed. Left untouched.
  - Two Python files unrelated to any declared project (`01_REPRODUCE_TOURNAMENT.py` / OMEGA-SWARM reproducibility script, and `RR_HRFA__VALIDATOR...py`) concerning a glyph/text "decipherment" analysis (Rapa Nui-style corpus, sealed-identity run bundles). They do not map to JM105/Intronsaurus, figure-rendering, ImageJ/Fiji, language-learning, or personal-intelligence-agency, and their provenance/purpose is unclear from the file content alone. Not imported pending Jordan's confirmation of project scope; flagged in the handoff email.
- No newly recovered full source code was committed in this pass; only this continuation-pass note was added.

## Current continuation pass — 2026-08-19 scheduled backfill sweep

- `origin/main` had moved to `a0b1b80` (a Jordan-authored, non-Claude, direct-to-main commit adding a temporary `.github/workflows/chatgpt-whisper-model-fetch.yml` CI workflow, tracked by draft PR #17 "Temporary Whisper model fetch") since the last sweep. This session's designated branch (`claude/dazzling-turing-jc3qks`) did not exist on the remote yet, so it was created fresh from current `main` per this repo's restart rule.
- Searched Google Drive: full recent-files listing (two pages, newest-first) plus targeted `title`/`fullText` queries for `.py`/`.ipynb`/`.sh`/`.sbatch`/`.ijm`/`.groovy`/`.ps1`/`.html`, `kartoffel`, JM134, JM133, JM128, JM129, `Intronsaurus`. All recent Drive activity (2026-08-16 through 2026-08-19) is personal/HEARTH material (genealogy-interview project, decision/forecast ledgers, operation briefs, SAT-prep docs) or a non-code project one-pager (`Ennis project — nuclear basket in senescence.svg`); none of it is new canonical code for a declared project.
- Searched Gmail: `has:attachment` for common code extensions in the last 30 days returned no results; a broader recent-mail sweep found only this repo's own prior daily-handoff self-mails and unrelated marketing/personal mail.
- **Reconciliation**: the 2026-08-16 entry above lists `01_REPRODUCE_TOURNAMENT.py` / `RR_HRFA__VALIDATOR...py` as an unresolved open item pending Jordan's scope decision. That characterization is now known to be stale: draft PR #14, "Recover Rongorongo OMEGA-SWARM/PROMETHEUS reproduction code" (opened 2026-08-03, still open/unmerged), already created `projects/rongorongo/` and imported this exact code (four OMEGA-SWARM reproduction scripts, the PROMETHEUS null compiler, and the HRFA validator/anonymizer), each verified `py_compile`-clean and hash-matched against the Drive source. The 2026-08-16 pass evidently did not check open PRs before re-flagging this as unresolved. No new decipherment code was found in Drive this pass beyond what PR #14 already covers.
- Checked draft PR #16, "JM-136: preserve and organize aging-chip analysis pipeline" (opened 2026-08-14, still open/unmerged, fills the long-outstanding "ImageJ/Fiji aging-chip" recovery target with a Python pipeline under `projects/jm136-aging-chip-analysis/`). Its own body lists 11 named files still missing to call the historical JM-136 source complete (`human_classifier_ui_old.py`, `hungarian.py`, `main.py`, `util_cell_annotation.py`, `pre_hungarian_human_classifier_ui.txt`, `pre_hungarian_train_classifier.txt`, `extract_traps.py`, `audit_annotations.py`, `eval_smoothing_sweep.py`, `merge_annotation_sources.py`, `classification.py`). Searched Drive by exact filename for all of them plus the small runtime/config files it asks about (`aging_chip.yml`, `class_labels.json`, `hmm_transitions.json`, `lifespan_oracle_meta.json`, `model_input_meta.json`): none found this pass.
- Also open and unmerged: draft PR #13, "Add and classify JM105 Figure 3–6 analysis sources" (opened 2026-07-30), which fills part of the "JM105 current RNA-seq poster scripts" / Figure-rendering backfill targets noted earlier in this file.
- No newly recovered full source code was committed in this pass. Three prior recovery passes (PRs #13, #14, #16) remain correctly recovered-but-unmerged and are Jordan's to review/merge; this pass's only contribution is the reconciliation note above and this continuation-pass record.
- **Process note**: this pass's doc corrections were pushed only to `claude/dazzling-turing-jc3qks`; per the "nothing new, no PR" convention no PR was opened, so this branch was never merged and the correction above did not reach `main`. See the 2026-08-20 entry below for the fix.

## Current continuation pass — 2026-08-20 scheduled backfill sweep

- `origin/main` was still at `a7c3bae` (tip after the Whisper workflow add/remove pair; no further main-branch movement since 2026-08-19). The 2026-08-19 sweep's corrected version of this file never reached `main` — it was pushed to `claude/dazzling-turing-jc3qks` (and the 2026-08-18 pass's file similarly sits unmerged on `claude/dazzling-turing-dn1hb6`), and per the repo's "nothing new → no PR" convention neither branch was ever opened for merge. This pass carries that correction forward into this file directly and opens a PR so it actually lands on `main` instead of stranding again — see the process note below.
- Searched Google Drive: `search_files` for everything modified since 2026-08-16, plus a second targeted pass for `.py`/`.ijm`/`.groovy`/`.sh`/`.sbatch`/`.ps1`/`.ipynb`/`.html`/`.R` filenames via Gmail attachments. All Drive activity since the 2026-08-19 sweep is personal/HEARTH/genealogy material: the "Nana — Kathleen LaSpina Parolisi" oral-history project (interview audio, a machine-transcript doc, and a doc titled "LEGACY PocketSphinx Scaffold (Not Verified)"), HEARTH/RELAY operation briefs and ledgers, Mark's SAT-prep docs, and the "Ennis project — nuclear basket in senescence" one-pager/SVG. Read the "PocketSphinx Scaffold" doc in full since its title suggested code: it is raw, heavily garbled ASR output text (one-minute-window transcript chunks), not a code scaffold — no computational artifact there.
- Searched Gmail: `has:attachment` filtered to common code extensions over the last 14 days returned no results; a `decipherment`/`OMEGA-SWARM`/`rongorongo` sweep surfaced only this repo's own prior daily-handoff self-mails and a separate, already-known OMEGA/Rongorongo Direct-Run-Intake automation (`noreply@tm.openai.com`) that manages its own Drive-based archive outside this repo's scope.
- No new code, scripts, or notebooks were found this pass. Confirmed no change in the standing recovery-target list (JM134 scripts 78/83, JM133 canonicalization, Figure 2 stage-1 audit source, JM105 poster scripts 26/28, Intronsaurus vNext3AH archive, ImageJ/Fiji JM128/JM129/JM076 macro bodies, figure-rendering mockup/no-data-placeholder renderers) and no change in the three parked recovery PRs (#13, #14, #16), which remain open/unmerged and are Jordan's to review.
- **Process note**: opened a documentation-only PR from this pass's branch instead of leaving it unmerged like the 2026-08-18 and 2026-08-19 passes, specifically so this reconciliation reaches `main`. This produced draft PR #18, which as of the next entry below is still open/unmerged — so `main` itself has *still* not picked up the reconciliation; only PR #18's branch has it. Recommend merging PR #18 (or an equivalent) so future passes stop reading a stale `main` copy of this file.

## Current continuation pass — 2026-08-21 scheduled backfill sweep

- `origin/main` was still at `a7c3bae`, unchanged since 2026-08-19 (the Whisper workflow add/remove pair). PR #18, which carries the 2026-08-19 reconciliation forward, is still open/draft/unmerged, so `main`'s copy of this file is still the stale 2026-08-16 version. This pass's designated session branch (`claude/dazzling-turing-5r2mce`) cannot push to PR #18's branch (`claude/dazzling-turing-3rc0d7`) under this session's branch policy, so the reconciliation text is carried forward again here (identical content to PR #18) rather than left stale. This creates a second, redundant doc-only PR — see the process note below.
- Searched Google Drive for gmail attachments and everything modified since the 2026-08-20 sweep (`modifiedTime > 2026-08-20T07:15:00Z`, paginated), plus a targeted `title`-based search for the 11 filenames PR #16 lists as still-missing JM-136 source (`hungarian.py`, `util_cell_annotation.py`, `extract_traps.py`, `audit_annotations.py`, `eval_smoothing_sweep.py`, `merge_annotation_sources.py`, `human_classifier_ui*`, etc.): none found. Two new documents appeared under the aging-chip project folder since the last sweep — "Aging Chip Protocol — Longitudinal Yeast RLS — SOP v0.11" and "— v1.0-rc" — but both are wet-lab bench SOP documents (reagent lists, day-by-day handling steps, a materials/equipment table, a CC-BY-4.0 protocol-sharing header), not code or a computational artifact, and contain no reference to the 11 missing JM-136 files. Not imported. Everything else modified since the last sweep is HEARTH/personal material (an "ANCHOR"/Zürich-permanence operation brief, a residence-permit memo, meeting/email-draft notes) explicitly out of scope per `projects/personal-intelligence-agency/README.md`.
- Searched Gmail directly this pass (a working `search_threads`/`get_thread` tool pair was available, unlike several earlier sweeps that only had send/reply/forward tools): `has:attachment newer_than:2d` and `newer_than:14d`, a code-extension filename sweep (`filename:py OR filename:ijm OR filename:sbatch OR filename:groovy OR filename:ps1 OR filename:sh OR filename:ipynb`, zero results), and a keyword sweep for JM134/JM133/JM128/JM129/JM076/Intronsaurus/kartoffel/Figure 2 (201 threads, reviewed by subject/sender — all either this repo's own prior daily-handoff self-mails, unrelated `noreply@tm.openai.com` strategic-brief automation, or personal mail: a TELC C1 certificate notice, a ZVV travelcard receipt, an ILS Zürich open-house invite, a residence-permit appointment confirmation). No code attachments found.
- Confirmed via `list_pull_requests` that the parked recovery PRs are unchanged: #13 (JM105 Figure 3–6 sources, opened 2026-07-30), #14 (Rongorongo/OMEGA-SWARM decipherment code, opened 2026-08-03), #16 (JM-136 aging-chip pipeline, opened 2026-08-14, still missing the same 11 named files), and #18 (this file's 2026-08-19/20 doc reconciliation, opened 2026-08-20) all remain open, draft, and unmerged — no new PRs and no state changes since the 2026-08-20 sweep.
- No new code, scripts, or notebooks were found this pass. No change in the standing recovery-target list.
- **Process note**: this pass's branch-isolation constraint means it cannot land its doc update on PR #18's branch, so it opens a second doc-only PR carrying the same reconciliation text plus this entry. Recommend merging PR #18 first (it is the more complete/older record) and then closing this pass's PR as redundant once its 2026-08-21 entry is manually folded in, or vice versa — either resolves the underlying duplication. The root fix is merging *some* pending doc PR promptly so `main` stops resetting.

## Current continuation pass — 2026-08-25 scheduled backfill sweep

- `origin/main` was still at `a7c3bae`, unchanged since 2026-08-19. Draft PRs #18 (2026-08-20) and #19 (2026-08-21) both carry this same 2026-08-19/20/21 reconciliation text forward on their own branches and remain open/unmerged, so `main`'s copy of this file was still the stale 2026-08-16 version going into this pass. Rather than open a third near-duplicate reconciliation PR, this pass folds the full #18/#19 text into this file (verbatim, as the three entries above) plus this new entry, and the PR opened from this pass explicitly asks Jordan to merge it in place of #18 and #19 (which can then be closed as superseded) rather than merging all three.
- Searched Google Drive: `list_recent_files` (30 newest, all dated 2026-08-22 through 2026-08-25) plus targeted `search_files` queries — `modifiedTime > 2026-08-16` combined with code-extension/keyword terms (`.py`, `.ijm`, `.ps1`, `.sbatch`, `.groovy`, `def `, `import numpy`, `import pandas`), title terms (JM105/JM133/JM134/Intronsaurus/Figure/kartoffel/Fiji/ImageJ), and `modifiedTime > 2026-08-21T07:16:00Z` (everything Drive-modified since the 2026-08-21 sweep, two full pages). Also re-ran the exact-filename search for the 11 files PR #16 lists as still-missing JM-136 source (`hungarian.py`, `util_cell_annotation.py`, `extract_traps.py`, `audit_annotations.py`, `merge_annotation_sources.py`, `human_classifier_ui*`, etc.) and for `kartoffel`: zero matches, same as every prior pass.
- Every file touched since 2026-08-21 is personal/HEARTH/relationship-intelligence material (Wenshuo/Enis meeting records and HEARTH adjudications, Operation Briefs FOUNDRY/LANTERN, the JM105 Forensic Provenance & Ownership Audit, the JM105 Science Preemption Watchlist, Network Profiles, Master Interaction Record, Jordan Canonical Current State Ledger, Jordan Weekly Operating Board, Jordan Forecast & Wrong Ledger, Connection Tracking, Clément WhatsApp/decision records, KINSHIP records, the Direct Decipherment Run Intake Register for the separate out-of-repo OMEGA-SWARM automation) or non-code source documents (two Wenshuo protocol `.docx` files, a meeting screenshot). None of it is code, and the HEARTH/relationship material is explicitly out of scope per `projects/personal-intelligence-agency/README.md`. Nothing new to import.
- Gmail: this session's Gmail connector again exposes only send/reply/forward/spam/trash actions, with no search or read tool, so Gmail could not be searched for code attachments this pass (same limitation as the 2026-08-16 and 2026-08-20 sessions).
- Confirmed via `list_pull_requests` that the parked recovery PRs are unchanged and the backlog has grown: #13 (JM105 Figure 3–6 sources, opened 2026-07-30), #14 (Rongorongo/OMEGA-SWARM decipherment code, opened 2026-08-03), #16 (JM-136 aging-chip pipeline, opened 2026-08-14, still missing the same 11 named files), #18 (doc reconciliation, opened 2026-08-20), and #19 (doc reconciliation, opened 2026-08-21) are all still open, draft, and unmerged. #17 ("Temporary Whisper model fetch") is closed/resolved and needs no action.
- No new code, scripts, or notebooks were found this pass. No change in the standing recovery-target list.

## Current continuation pass — 2026-08-30 scheduled backfill sweep

- Verified `jorddyk/Jordan-McCarthy` is reachable; fetched current repo structure/READMEs before making changes.
- Searched Google Drive for everything modified since the 2026-08-27 aging-chip RLS import (`modifiedTime > 2026-08-27T12:23:00Z`, two full pages, ~25 files): every result was a personal/"HEARTH" intelligence-agency document (operating boards, memoranda, forecast/decision ledgers, relationship/network profiles, a WhatsApp-source dump, a gift/card record, a grocery list) or a Rongorongo decipherment run-intake register. None were code, scripts, or notebooks. `projects/personal-intelligence-agency/README.md` explicitly excludes this class of content from the repo, so nothing was imported.
- Re-ran targeted Drive searches for every outstanding recovery target listed in this file (JM134 scripts 78/83, Figure 2 stage-1 audit files, JM128/JM129 Fiji/bioformats macros, `render-no-data-placeholder`/`render-main-figure-layouts`, Intronsaurus vNext3AH archive): all returned zero results. Status on all of them is unchanged: exact full source not yet recovered.
- Read Drive memo "MEMO 2026-012 — RLS Automation Integration Across JM105 & Intronsaurus" (28 Aug addendum): confirms the 2026-08-27 aging-chip RLS import (commits `337e8f1`, `cfaddd9`) is the current authoritative state; introduces no new code.
- Gmail connector in this session again exposes only send/reply/forward/spam/trash/label actions, no search or read tool, so Gmail could not be searched for code attachments this pass (same limitation noted in the 2026-08-16 and 2026-08-28 passes).
- Process note (not a code-recovery finding): the open PR backlog on GitHub is unchanged at 14 (`#1,#4,#6,#7,#9,#10,#12,#13,#14,#15,#16,#18,#19,#20`), and there are roughly 16 unmerged `claude/dazzling-turing-*` session branches, including at least one (`claude/dazzling-turing-mlt4h0`, commit `4a45cd6`) whose only content is a prior "no new artifacts" backfill note that never reached `main` because no PR was opened for it. Flagged for Jordan in this pass's handoff email; not resolved here (reconciling 14 historical PRs is out of scope for a single incremental sweep).
- No newly recovered full source code was committed in this pass; only this continuation-pass note was added.

## Current continuation pass — 2026-09-01 scheduled backfill sweep

- Verified `jorddyk/Jordan-McCarthy` is reachable; current README, project structure, and this file were read before making changes.
- Searched Google Drive for everything modified since the 2026-08-27 aging-chip RLS import (`main` @ `cfaddd9`), plus targeted `fullText`/`title` queries for JM134 (script 78/83, beta-binomial), JM133, `kartoffel`/TELC, JM076/JM128/JM129 Fiji/ImageJ macro terms, and common code extensions (`.py`, `.ijm`, `.groovy`, `.sbatch`, `.ps1`, `.sh`) modified in the last two weeks.
- Every hit was either a personal/"HEARTH" intelligence-agency document (Socratic-adjudication records, operation briefs, memos, network profiles, forecast/decision ledgers, a Rongorongo run-intake register) or unrelated (a meeting decision sheet). None were code-shaped or in scope for this repo; none imported, consistent with the repo's out-of-scope rule for daily private intelligence products.
- Re-checked every outstanding recovery target below (JM134 scripts 78/83, JM133 PR #1, Figure 2 stage-1 audit, Intronsaurus vNext3AH archive, JM-076/JM128/JM129 Fiji macros, `kartoffel` exact source, figure-rendering placeholder renderers): no change, still unrecovered. `paper_style.py` re-spot-checked as already canonical (no diff from the 2026-08-16 check).
- Gmail connector in this session again exposes only send/reply/forward/spam/trash actions; no search/read tool, so Gmail could not be searched for code attachments this pass (same limitation noted 2026-08-16).
- No newly recovered full source code found or committed this pass; only this documentation update.
- **Process note (unchanged from PR #21):** as of this pass there are still ~20 open pull requests and numerous unmerged `claude/dazzling-turing-*` session branches against this repo, several of which (e.g. PR #16 "JM-136: preserve and organize aging-chip analysis pipeline", still `draft`) contain real recovered/organized code that has not reached `main`. This session did not merge or close any PR (out of scope for an automated sweep without explicit direction) but flags it again in the handoff email — the backlog is now the single biggest gap between "recovered" and "actually preserved in the vault."

## Current continuation pass — 2026-09-02 scheduled backfill sweep

- **Reconciliation**: folded the parallel, unmerged 2026-08-19/20/21/25 reconciliation (PRs #18, #19, #20) and the independently-forked 2026-08-30 (PR #21) and 2026-09-01 (branch `claude/dazzling-turing-waf0ea`, no PR opened) entries into this single file, in chronological order, so one PR carries the full history forward instead of adding a fifth parallel branch. This pass's PR asks Jordan to merge it in place of #18, #19, #20 and #21 (all four can then be closed as superseded).
- Searched Google Drive: `list_recent_files` (25 newest) and targeted `search_files` queries for everything modified since 2026-09-01, for common code extensions (`.py`, `.ipynb`, `.sbatch`, `.ijm`, `.groovy`, `.R`) modified since 2026-08-16, and by exact filename for the priority recovery targets (`figure3_base_renderer`, `Figure_3_render_all_v21`, `render_jm105_figure2_public_final`, `rerender_figure5_CDE_public_clean_labeled`, `110_JM101_JM105_integrate_intronsaurus`, `141_intronsaurus_matched_rna_protein_gene_stories_v3Y`, JM128/JM129/JM076/MitoSOX/rollingBall, and the 6 files PR #16 still lists as missing JM-136 source). All zero matches except the priority-target searches, which (as expected) surface nothing because that source was never uploaded to Drive as a standalone file. The only Drive activity since 2026-09-01 is five more personal/HEARTH documents (rowing log, strategic-state registers, forecast ledger, decipherment run-intake register, Master Interaction Record) — out of scope per `projects/personal-intelligence-agency/README.md`.
- Searched Gmail directly this pass (`search_threads`/`get_thread` worked): `newer_than:7d has:attachment` (4 threads: Swisscare invoices and Anthropic billing receipts, no code), a code-extension `filename:` sweep (0 results), and a JM134/JM133/JM128/JM129/JM076/Intronsaurus/kartoffel/"figure 2"/jm136 keyword sweep over the last 14 days (3 threads, all unrelated personal mail — a 2024 hotel/zoo booking and a 2023 restaurant billing dispute — no code attachments, no new hits since the 2026-08-21 pass's broader keyword sweep).
- Confirmed via `list_pull_requests`/`pull_request_read` that PR #16 ("JM-136: preserve and organize aging-chip analysis pipeline", opened 2026-08-14, draft, 8,949 additions across 17 files) is unchanged: still lists the same files as missing before it can be called complete, still mergeable, still unmerged. #13 (JM105 Figure 3–6 sources) and #14 (Rongorongo/OMEGA-SWARM decipherment code) are likewise unchanged. Repo-wide: 15 open PRs (`#1,#4,#6,#7,#9,#10,#12,#13,#14,#15,#16,#18,#19,#20,#21`) plus the unmerged `waf0ea` branch.
- No new code, scripts, or notebooks were found this pass. No change in the standing recovery-target list.

## Current continuation pass — 2026-09-03 scheduled backfill sweep

- Verified `jorddyk/Jordan-McCarthy` is reachable and current project structure/READMEs were fetched before making changes.
- Google Drive: reviewed the 20 most-recently-modified files, plus targeted `title`/`fullText` queries for JM105/JM134/JM133/Intronsaurus, `.py`/`.ijm`/`.ps1`/`.sbatch`/`.groovy`/`.sh`/`.ipynb` extensions, `kartoffel`, `render-no-data-placeholder`, `render-main-figure-layouts`, `aging-chip`/`rls_detector`/`RLS`, and `vNext3AH`. No runnable source code turned up that is not already canonical in the repo.
- Gmail: this pass had a working search/read connector (`search_threads` / `get_thread`), unlike the 2026-08-16 pass where only send/reply/forward/spam/trash were exposed. Searched for attachment filenames (`.py`, `.ipynb`, `.ijm`, `.groovy`, `.sbatch`, `.ps1`, generic `has:attachment`) and for code/handoff-related subjects, with no date limit. Result: no code or computational-artifact attachments exist anywhere in the account's mail history. All matches were administrative/personal mail (invoices, receipts, a TELC certificate, an appointment confirmation, old verification-code emails). Gmail is confirmed empty of recoverable code for this and future passes unless new mail arrives.
- All of the previously identified "exact full source not yet recovered" items (JM134 scripts 78/83, JM133 canonicalization, Figure 2 stage-1 audit, JM105 poster scripts 26/28, Intronsaurus vNext3AH archive, ImageJ/Fiji JM128/JM129/JM076 macro bodies, figure-rendering mockup/no-data-placeholder renderers, `kartoffel-vocabulary-active-recall.html`) remain outstanding; none were found in Drive this pass.
- Confirmed `projects/jm105-intronsaurus/jm133-weak-5ss-mud1/` already exists on `main` (the JM-133 canonicalization noted as pending-merge in the 2026-07-08 entries above has since landed; the `legacy-code-backfill-2026-07-08` branch referenced there no longer appears in the branch list).
- Confirmed the aging-chip RLS pipeline first-imported on 2026-08-27 (`projects/aging-chip-rls-pipeline/`) has no newer runnable-code revision in Drive; only planning/protocol documents (SOP v0.11, Protocol v1.0-rc, MEMO 2026-012, JM-138 SYNE27 intake plan) were found, and per repo rules these are prose/spec, not source code, so nothing new to import.
- Found, and again did not import, the same two out-of-scope Python "decipherment" files first flagged 2026-08-16 (`RR_HRFA__VALIDATOR__actor-Kaihu-SourceCritic-GPT56T__...py` and the OMEGA-SWARM reproducibility script), plus a related "Direct Decipherment Run Intake Register" spreadsheet (not code). Status unchanged: no declared project in this repo covers this material, and it is not imported pending Jordan's confirmation of scope.
- Found, and did not import, a large and growing set of "HEARTH" personal-intelligence documents (operation briefs, Socratic-adjudication memos, network profiles, forecast/interaction ledgers, a genealogy interview sheet, a third party's unrelated shared PDF). These fall under `projects/personal-intelligence-agency/README.md`'s explicit prohibition on private raw intelligence products, message text, and named-individual profiles. Left untouched.
- No newly recovered full source code was committed in this pass; only this continuation-pass note and the accompanying handoff record were added.

## Current continuation pass — 2026-09-04 scheduled backfill sweep

- **Reconciliation**: PRs #22 (2026-09-02, folds in #18/#19/#20/#21/`waf0ea`) and #23 (2026-09-03) both remain open/draft/unmerged, and `main`'s copy of this file is still the stale 2026-08-16 version (verified: `main` @ `cfaddd9`, this file unchanged there since the 2026-08-16 commit). This pass's designated branch (`claude/dazzling-turing-bvxwgq`) folds #22's full consolidated text plus #23's 2026-09-03 entry into this file, in chronological order, plus this new entry — continuing #22's approach rather than opening a sixth parallel doc-only branch. Per this session's tooling, no PR is opened for this pass (see the handoff record); Jordan will need to either merge this branch directly or have a future pass open a PR from it.
- Searched Google Drive: `list_recent_files` (30 newest) plus targeted `search_files` for everything modified since the 2026-09-03 sweep (`modifiedTime > 2026-09-03T00:00:00Z`) combined with code-extension/title terms (`.py`, `.ijm`, `.groovy`, `.sbatch`, `.ps1`, `.html`, `.ipynb`). All hits since 2026-09-03 are personal/HEARTH material (Direct Decipherment Run Intake Register, HEARTH App Feed, Owner-Facing Operating State, Master Interaction Record, Jordan Weekly Operating Board, a grocery list, Network Profiles) — out of scope per `projects/personal-intelligence-agency/README.md`. No code found.
- Searched Gmail: `has:attachment newer_than:3d` returned zero threads. Consistent with the 2026-09-03 pass's finding that Gmail contains no recoverable code/computational-artifact attachments across the account's mail history.
- Re-checked PR #16 ("JM-136: preserve and organize aging-chip analysis pipeline"): still open, draft, `mergeable_state: clean`, unchanged since 2026-08-14 (8,949 additions, 17 files, 19 commits). Still correctly left unmerged pending Jordan's review — this is domain-sensitive scientific code (classifier training/UI/diagnostics) that an automated sweep should not merge unilaterally.
- No new code, scripts, or notebooks were found this pass. No change in the standing recovery-target list.
- **PR backlog status (escalating)**: repo-wide there are 15 open PRs (`#1,#4,#6,#7,#9,#10,#12,#13,#14,#15,#16,#18,#19,#20,#21,#22,#23` — note: 17 numbers listed because both #22 and #23 are additional to the 15 counted on 2026-09-02) plus this pass's unopened branch. Three of these (#13, #14, #16) hold real, reviewed-enough-to-review recovered code that has been unmerged for 5+ weeks (#16 since 2026-08-14, #14 since 2026-08-03, #13 since 2026-07-30). This is now the single biggest gap between "recovered" and "actually preserved in the vault" — flagged in every pass since 2026-08-30 and unchanged. Separately: Gmail shows every prior daily-handoff self-email in this thread history still marked `UNREAD` in the inbox, suggesting these findings may not be reaching Jordan through that channel.
