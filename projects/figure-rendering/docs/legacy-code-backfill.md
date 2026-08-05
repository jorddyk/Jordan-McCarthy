# Figure Rendering Legacy Code Backfill

This file tracks historical figure-rendering and manuscript-mockup code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue and import audit.

## Imported exact runnable source

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Recovered from the 2026-06-30 JM105 Figure 1E/F panel-rendering chat; latest useful V9 PRINT PowerShell/Python workflow after the layout/text-size repair sequence | Windows PowerShell orchestration that writes and runs a Python renderer for JM105 Figure 1E/F content-only print panels. Produces transparent SVG/PNG/3x PNG, white-preview PNG, TSV panel data, and JSON audit/provenance. | Imported runnable source. Uses real local JM105 total/rRNA-depleted tables if present. No fake data. No poly-A. Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR. Panel F is explicitly a raw NMD-off candidate/category set, not off-minus-on NMD-hidden IR. |

## Imported prompt/spec artifacts

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md` | `Pasted text (3).txt`, 2026-07-07 JM105 Figure 5 render prompt | Reusable exact contract for rendering Figure 5 from PowerShell + Euler without fake data and with lane/collision/provenance audits | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md` | `Pasted text.txt`, 2026-07-07 manuscript figure-redesign prompt | Reusable exact contract for redesigning the main/supplemental figure sequence around Yves/Nature Aging claim architecture | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md` | 2026-07-01/02 Figure 2 Panel F repair and postmortem conversation | Reusable lane-first figure-generation contract: define biological purpose, data transformation, forbidden claims, lane map, collision inventory, transparent outputs, editable SVG text, footer/descriptor axes, and semantic visual QA before code/patching | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md` | 2026-07-02 Figure 4 artifact-package discussion | Reusable artifact workflow contract: one downloadable ZIP package plus one PowerShell runner that uploads/runs on Euler and retrieves outputs, with strict data-integrity hard-stop behavior by default | Imported as prompt/spec; not runnable code |

## Priority code to recover

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `panel-renderers/jm105-figure3-v21/figure3_base_renderer.py` and `panel-renderers/jm105-figure3-v21/Figure_3_render_all_v21.py` | Exact historical v21 sources were found in `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316` and copied into 2026-07-15 Figure 3 chat-build bundles; the latest verified retrieval is `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`, also downloaded into Jordan's local `JM105_Figure3_Euler_Bundle_v6_EXTRACTED` results; terminal records show complete files of about 57 KB and 40 KB, plus matching `.pyc` files | Preserve the last known complete Figure 3 v21 renderer and its shared base module before adapting any parser or panel logic | `PARTIAL / SOURCE LOCATED`: exact complete bytes exist on Euler and in Jordan's retrieved local v6 bundle, but this automation can access only the terminal transcript, not the `.py` file bodies; do not reconstruct from logs |
| 2 | `panel-renderers/jm105-figure2-public-final/render_jm105_figure2_public_final.py` | Exact uploaded Python was copied to `/cluster/home/jmccarthy/JM105_Figure2_public_final_20260713_171245/scripts/render_jm105_figure2_public_final.py`; successful rerun recorded after replacing `threshold_c` with `threshold_cr` | Render Figure 2 public-final panels and provenance/audit exports from the strict total/rRNA-depleted source table | `PARTIAL / SOURCE LOCATED`: exact complete source exists in File Library/Euler, but full bytes were not retrievable in this automation run; do not reconstruct from terminal excerpts |
| 3 | `panel-renderers/jm105-figure5-public-clean/rerender_figure5_CDE_public_clean_labeled.py` | Exact File Library upload `rerender_figure5_CDE_public_clean_labeled.py`, created 2026-07-13 15:57 CEST, with matching exact shell launcher | Render public-facing Figure 5 C/D/E assets, audits, matched tables and contact sheet while leaving 5A/5B unrendered without secure provenance and 5F untouched | `PARTIAL / SOURCE LOCATED`: indexed excerpts and complete launcher verified; full Python bytes were not exposed by the current connector, so no snippet-based reconstruction was committed |
| 4 | `panel-renderers/jm134-starvation-switch-label-audit.py` | JM134 final layout and gene-labelled rerender workflow; Euler jobs `3101802`, `3104275`, `3106256`, `3109225` | Audit and rerender significant-in-both, JM105-only, and same-direction labels without overlap | Exact full source not yet recovered |
| 5 | `panel-renderers/jm133-weak-5ss-mud1-scatter.py` | JM133 weak 5-prime splice-site/Mud1 scatter with LOESS, highlighted leaky set, eight ringed candidates, and marginal violin | Render the final JM133 relationship panel while preserving exact candidate and label logic | Exact full source not yet recovered |
| 6 | `nature-aging-mockups/render-main-figure-layouts.py` | Recent Nature Aging / Yves-compatible figure mockup rendering conversations | Render drag-and-drop main-figure layout mockups for JM105/Intronsaurus while preserving existing panel aspect ratios and avoiding whitespace/text overlap | Exact full source not yet recovered |
| 7 | `nature-aging-mockups/score-figure-story-architecture.py` | Requested scoring model for humanized/Yves-compatible/Nature Aging-likely figures | Score figure layouts across acceptance-likelihood, Yves compatibility, and human/non-AI design | Exact full source not yet recovered |
| 8 | `panel-renderers/render-no-data-placeholder.py` | Figure 5 placeholder/NO DATA renderer | Render placeholders for experiments not yet done without fabricating data | Exact full source not yet recovered |
| 9 | `nature-aging-mockups/figure-5-layout-renderer.py` | Figure 5 rendering from PowerShell/Euler using uploaded Fig5 docs/PPT | Render Figure 5 mockup from existing panels and NO DATA placeholders, matching style of other panels | Exact full source not yet recovered |
| 10 | `nature-aging-mockups/render-synopsis-aligned-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Render normal all-intron/all-gene RNA-seq panels required by the synopsis; may live under JM105 figures rather than generic rendering | Full current source was previously reported visible in project chat but is not currently accessible as a complete source body; exact full source not yet recovered |
| 11 | `panel-renderers/render-figure2-panel-f-mud1-dependence.py` | Euler folders `PanelF_render_v7_TRANSPARENT_NO_BORDER_FOOTER_FIXED`, `PanelF_render_v8_FOOTER_SPACING_BEAUTIFUL`, and `PanelF_render_v9_TOP_DESCRIPTOR_SPACING_FIXED` | Render Figure 2F with computed NMD-hidden IR, data-driven y-limits, transparent outputs, dedicated descriptor/footer axes, and separated label lanes | Exact final complete source not yet recovered; patch sequence is not sufficient |

## 2026-08-05 recovery pass

Google Drive search (title/fullText for `figure2_render`, `figure3_base_renderer`, `JM105`, `figure3`, `figure5`) and Gmail search (attachment/keyword) across Jordan-authorized sources found no new complete runnable source files. Findings:

- `paper_style.py` (Drive file `1u94c0_GQM-C76L9FqINY3DmZ1KmTAuD0`, folder `00_OBSOLETE — superseded by Yves most recent interpretation — 2026-07-27`) was compared byte-for-byte against the canonical `projects/figure-rendering/jm105-figure-bible/paper_style.py`. They match (Drive copy has one extra unused `Iterable` import). No update needed; already canonical.
- A new Drive document "CURRENT — JM105 Figure 2 v10 lane-locked renderer register" (folder `JM105 - Intronsaurus & Nature Aging/06 Current Figure Rendering Code`, doc id `1-YKaFJ5hcravba7pPV8EzbOUdgPl-tvRPjUImR_QyFk`, 2026-07-28) records a further iteration of the Figure 2 renderer beyond the previously tracked `render_jm105_figure2_public_final.py` lineage:
  - `JM105_figure2_render_v10_lane_locked_20260728.py` — SHA-256 `fbd47169d0320e04c0eaf41692b9500be4b1cfa8f862e089b891507c497bd00e`, fixed canvas 7.2×9.6in, schema `JM105-FIG2-LANE-LOCKED-v10-20260728`, Euler destination `/cluster/home/jmccarthy/JM105_NMD_AUDIT/`. Explicitly supersedes `JM105_figure2_render_v9_FINAL_20260728.py` for scientific/rendering use.
  - A separate transcript document ("SOURCE — Claude denominator, Novogene, and intron-length audit transcript — unverified", doc id `1sR2ORMKsI_fAq6-NyKh0Klmu5IKps0zktlA2nTOoQIE`) references an earlier `JM105_figure2_render_v5_20260727.py` (28,031 bytes, sha256 prefix `5b100be26eb4760e`) in the same lineage, with the panel-A CPM/library-size-denominator issue as the open scientific question.
  - Only the register/transcript documents are present in Drive; the actual `.py` bytes for v5, v9, or v10 were not found in any accessible source. Status: `PARTIAL / SOURCE LOCATED` (register/metadata only), same standard as items 1–3 above. This v9/v10 lane-locked lineage is a newer, distinct candidate from the previously tracked `render_jm105_figure2_public_final.py` item and should be treated as the current preferred target once bytes become available.
- No Gmail message or attachment in the authorized mailbox contained figure-rendering, JM105/Intronsaurus, ImageJ/Fiji, or language-learning source code. Gmail content is personal/administrative (travel, lab-meeting forwards, correspondence) and not a source of canonical code this run.

## 2026-07-16 recovery pass

A new File Library pass verified the latest Figure 3 recovery/build location: `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`. Its retrieved output inventory contains the exact historical `figure3_base_renderer.py` (~57 KB) and `Figure_3_render_all_v21.py` (~40 KB), their compiled companions, and the current `Figure_3_build_from_v21_and_JM100.py` (~33 KB). The same complete output set was downloaded into Jordan's local `JM105_Figure3_Euler_Bundle_v6_EXTRACTED` results.

The v6 build progressed far enough to generate panel sources and rendered assets, then failed only at the composite hard cross-font audit. Reported failures included clipped headings (`Host RNA abundance does not explain the intron effect`, `mud1Δ does not cause gross cell-cycle slowing`) and title/panel-letter overlap pairs. This is a layout-QC failure in the newer wrapper, not evidence of missing v21 source or biological-data failure.

The exact source bodies remain inaccessible to this automation because File Library exposes the terminal transcript rather than the downloaded `.py` files. Status therefore remains `PARTIAL / SOURCE LOCATED`. The next recovery action is direct byte transfer from the verified `Figure3_chat_build_20260715_163813` run directory or Jordan's local v6 extraction; commit the v21 pair unchanged before considering the newer wrapper.

## 2026-07-15 recovery pass

The File Library pass found new exact-source evidence for the Figure 3 v21 renderer. Terminal transcripts from the 2026-07-15 recovery/build workflow show that both `figure3_base_renderer.py` and `Figure_3_render_all_v21.py` were retrieved as complete files from the historical v21 area and copied into multiple Figure 3 chat-build run directories. The records show approximately 57 KB and 40 KB source files, matching compiled `.pyc` companions.

The same transcripts also show a concrete execution blocker: one attempted v21 run was supplied a Figure 2 plot-source TSV lacking the required `intron_id` field, and a later wrapper passed an extra positional path that the v21 CLI did not accept. Those are invocation/source-schema failures, not evidence that the recovered v21 source is incomplete.

The current connector exposes only the terminal transcript, not the exact `.py` bytes. Therefore the two files remain `PARTIAL / SOURCE LOCATED`, not `RECOVERED`. The next handoff must transfer the exact source files directly from the verified Euler historical/run directories or Jordan's local `JM105_Figure3_Euler_Bundle_v5` extraction and then commit them without modification before any adaptation.

## 2026-07-13 recovery passes

The first File Library pass searched exact and combined clues for JM133, JM134, the four Euler job IDs, Figure 5, Nature Aging mockups, `NO DATA`, LOESS, marginal violin, and likely renderer filenames. It did not expose complete runnable bodies for the priority targets.

The evening pass found materially better evidence:

- exact uploaded `rerender_figure5_CDE_public_clean_labeled.py` and complete `run_rerender_figure5_CDE_public_clean_labeled.sh`;
- terminal proof that `render_jm105_figure2_public_final.py` was a 48 KB exact file uploaded to Euler;
- a successful Figure 2 rerun after the precise `threshold_c` → `threshold_cr` correction;
- the exact Euler run directory and expected canonical destination.

The connector returned searchable excerpts but failed to open or transfer the full uploaded Python files. Therefore these are classified `PARTIAL / SOURCE LOCATED`, not `RECOVERED`. No biological code was reconstructed from excerpts. The next handoff should retrieve the exact files from File Library or copy them directly from the verified Euler paths.

## Mockup/image-generation artifacts deliberately not committed as code

- Generated Nature Aging-style mockup PNGs are not runnable source.
- Prompt assets may be canonical specifications, but schematic/mock values must never be represented as real manuscript data.

## Figure-rendering guardrails

- Do not fake data.
- Preserve original panel aspect ratios unless resizing is explicitly allowed.
- Do not shrink text as the default crowding solution; crop canvas, reduce nonessential text, move text to captions, or expand plot lanes.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- Clearly distinguish existing panels from newly required panels.
- If data are absent, mark the panel as `NO DATA`.
- Figure 2 must stay total/rRNA-depleted only unless Jordan explicitly changes it.
- SVG text should remain editable text, not outlined/path-converted.
- Do not use `bbox_inches="tight"` in fixed-canvas figure exports.
- Before patching a figure, list exact colliding objects by name and resolve by lane geometry, not by deleting required information.
- Final transparent SVG/PDF/PNG outputs must stay transparent; white previews are separate.

## Backfill method

1. Search old ChatGPT/project context by exact project names, job IDs, filenames, and output folders.
2. Search File Library and authorized sources for associated `.py`, `.R`, `.ps1`, `.sh`, `.sbatch`, and complete generated-script artifacts.
3. Recover the latest complete code only.
4. Commit recovered code under human-purpose names, not chat/date names.
5. Keep obsolete or partial code out of the repo unless explicitly documented as deprecated reference material.

## Containment action

This ledger is the single source of truth for unrecovered figure-rendering code. Historical job success, remembered outputs, prompt specifications, and patch sequences do not qualify as canonical runnable source.