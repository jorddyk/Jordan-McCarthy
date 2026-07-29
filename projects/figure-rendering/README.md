# Figure Rendering and Manuscript Mockups

Human goal: preserve reusable code for figure-panel rendering, figure-layout mockups, and manuscript visual planning.

This project is separate from JM105-specific analysis. Code belongs here when its main purpose is layout/rendering rather than calculating biological metrics.

## Start here for every new figure chat

Read these files before writing code or rendering:

```text
projects/figure-rendering/START_HERE_FOR_FIGURE_RENDERING.md
projects/figure-rendering/AGENTS.md
projects/figure-rendering/docs/figure-rendering-reliability-standard.md
projects/figure-rendering/templates/jm105-figure-rendering-learning-loop.md
projects/figure-rendering/templates/figure-rendering-new-chat-checklist.md
projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md
```

The reliability standard is cross-figure. It requires panel-identity and full-scope locks, verified source schemas and renderer CLIs, exact target-Euler execution, cross-font collision testing, direct retrieval, local verification, and Drive/GitHub logging. The learning loop requires every material failure to become a regression test or machine-checkable guard before another submission. The complete Figure 2 incident chronology is in `docs/jm105-figure2-2026-07-14-complete-incident-postmortem.md`; the active Figure 3 incident record is in `docs/jm105-figure3-2026-07-28-rendering-incident-and-learning-record.md`.

## Intended structure

```text
projects/figure-rendering/
  nature-aging-mockups/
    Reusable figure-layout and journal-style mockup scripts.
  panel-renderers/
    Standalone panel rendering utilities.
  qa/
    Fail-closed metadata, alias, rendered-object and artifact checks.
  templates/
    Style/layout templates, learning loops and reusable configuration files.
  prompts/
    Reusable prompt/spec artifacts for figure redesign and rendering.
  docs/legacy-code-backfill.md
    Source-of-truth recovery ledger for unrecovered historical renderers.
  docs/jm105-figure2-euler-rendering-runbook.md
    Figure 2 Euler workflow, failure postmortem, and anti-repeat guardrails.
```

## Guardrails

- Do not fake data.
- Preserve original panel aspect ratios unless resizing is explicitly allowed.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- Clearly distinguish existing panels from newly required panels.
- If data are absent, mark the panel as `NO DATA`.
- SVG text should remain editable text.
- Fixed-canvas rendering scripts should not use a tight-crop save option.
- For JM105 Figure 2-related rendering, do not use poly-A / P-versus-T / mRNA-like logic unless Jordan explicitly restores it.
- Before patching a bad panel, name the exact colliding objects and reallocate lanes rather than locally nudging text.
- Final transparent SVG/PDF/PNG outputs must remain transparent unless an opaque background is explicitly requested; white previews are separate review artifacts.
- A complete-figure request means every panel unless Jordan explicitly authorizes a staged subset.
- Current PowerPoint/composite panel identity cannot be changed because a different source or renderer is easier.
- Local preflight is not acceptance; the exact renderer must run in the target Euler environment.
- Record the actually resolved font and run the post-draw collision gate under the target font and an expected fallback.
- A remote render is incomplete until the same delivery includes direct Windows retrieval, local existence checks, and opening the white preview.
- For JM105/Intronsaurus panel rendering, read `templates/chatgpt-jm105-rendering-operating-standard.md` before writing new code.
- For JM105 Figure 2 Euler work, read `docs/jm105-figure2-euler-rendering-runbook.md` and the complete incident postmortem before launching or wrapping any renderer.
- For JM105 Figure 3 work, read the locked Figure 3 prompt/crosswalk and the 2026-07-28 incident record before code.
- Run the exact-table metadata preflight before Slurm submission; opaque sample IDs are never biological metadata.
- Literal `NaN` cells and visible systematic ORF labels are hard publication-QA failures.
- Commit only the Jordan-accepted canonical renderer; failed attempts belong in one incident record.

## Canonical code status

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `panel-renderers/jm105-figure2-v4_1/` | canonical accepted execution reference | Complete Figure 2 A-F cross-font-safe renderer and Windows/Euler workflow | Real JM104 Panel A source; enriched strict Figure 2 source; accepted Panel E vector source; user-confirmed end-to-end success. |
| `panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py` | RECOVERED canonical source | Standalone Figure 2F seven-gate renderer from the raw 402-row strict-gate table, with cumulative gate counts, collision audits, transparent exports and Euler file inventory | Real total/rRNA-depleted JM105 gate table only; hard-fails unless the final mask equals `candidate_passed_strict` and n=49; NMD-hidden definition preserved. |
| `panel-renderers/render-figure1ef-total-rrna-print.ps1` | canonical | JM105 Figure 1E/F print panel workflow | Real total/rRNA-depleted inputs; no fake data or poly-A. |
| `panel-renderers/jm105-figure3-mud1-cr-panels/` | partial exact-source import | Recovered runner/README; the historical v21 Python source pair is source-located in the verified 2026-07-15 Euler v6 build and Jordan's retrieved local v6 bundle, but exact source bytes are not yet transferred into GitHub | Real JM105 summary tables; no source-schema substitution is allowed. |
| `qa/jm105_metadata_preflight.py` | canonical infrastructure | Fail-closed normalization and exact-table metadata-cell inventory before JM105 rendering | Reads metadata only; no biological metric calculation or simulated data. |
| `qa/test_jm105_metadata_preflight.py` | canonical regression suite | Locks Unicode delta, plain UPF1, MUD1, age and glucose label behavior | Infrastructure-only test cases. |
| `templates/jm105-figure-rendering-learning-loop.md` | canonical operating infrastructure | Converts every material failure into a regression test and defines promotion states | No biological data. |
| `panel-renderers/render-figure4-panel-e-external-context.py` | canonical | Corrected Figure 4E external-context renderer | Uses audited source values; layout repair only. |
| `panel-renderers/run-figure4-panel-e-external-context-euler.sh` | canonical | Euler wrapper for Figure 4E | Administrative wrapper. |
| `panel-renderers/retrieve-figure4-panel-e-external-context.ps1` | canonical | Retrieval helper for Figure 4E outputs | No biological values generated. |
| `panel-renderers/jm105-rendering-harness/` | canonical infrastructure | Source-discovery and fail-fast rendering harness | Infrastructure only. |
| `panel-renderers/jm105-fig4bc-sequence-architecture/` | canonical | Figure 4B/C selected-vs-background sequence architecture | Real selected/background data; no fake data. |
| `panel-renderers/jm105-figure4-secondary-structure-accessibility/` | canonical exploratory/control renderer | Figure 4G predicted splice-signal accessibility and RNAlib MFE-derived structure proxy | Real locked Figure 4 selected/background data; selected n=49; sequence extraction and method caveats audited. |
| `panel-renderers/jm105-figure3-cr-selectivity-v2-1/jm105-figure3-render-v2-1-cr-selectivity.py` | RECOVERED exact source (not yet Euler-run or Jordan-accepted) | Six-panel Figure 3: CR selectively suppresses an age-associated NMD-revealed retained-intron program, `+MUD1` only | Real total/rRNA-depleted JM105 schema required; fail-closed on missing columns, unnamed genes, or synthetic-looking paths; no fake data. |
| `panel-renderers/jm105-figure4-mud1-host-transcript/jm105-figure4-render-v11-2-mud1-coupling.py` | RECOVERED exact source (not yet Euler-run or Jordan-accepted) | Eight-panel Figure 4: Mud1 couples intron-retention and host-transcript-abundance responses to CR; candidates frozen on ageing effect to avoid circularity | Real total/rRNA-depleted JM105 schema required; lifespan panels a/b render `NOT COMPUTED` without real `--lifespan` data; no fake data. |
| `panel-renderers/jm105-figure4-mud1-host-transcript/jm100-lifespan-to-csv.py` | RECOVERED exact source | Converts real `JM100.xlsx` replicative-lifespan data to the CSV Figure 4 panels a/b consume; flags the workbook's transposed `Graphs` summary sheet and the CR-intensity mismatch (JM100 0.5% vs JM105 RNA-seq 0.1%) | Real JM100 lifespan data only; fail-closed on unrecognised strain/glucose labels. |

## Backfilled prompt/spec artifacts

The `prompts/` directory contains exact rendering contracts for Figure 5, manuscript-figure redesign, lane/collision auditing, and artifact packaging. These are specifications, not substitutes for missing runnable source.

## Current recovery focus

`docs/legacy-code-backfill.md` is the single source of truth for missing historical figure code. Highest-priority targets are now the exact Figure 3 v21 source pair, Figure 2 public-final renderer, Figure 5 C/D/E public-clean renderer, JM134 label-audit/rerender workflow, JM133 weak-5′SS/Mud1 renderer, main-figure layout renderer, story-scoring model, and reusable `NO DATA` renderer.

A 2026-07-16 File Library pass identified the latest verified Figure 3 source-bearing run at `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_chat_build_20260715_163813/`. Its downloaded inventory includes `figure3_base_renderer.py` (~57 KB), `Figure_3_render_all_v21.py` (~40 KB), matching `.pyc` files, and the newer `Figure_3_build_from_v21_and_JM100.py` (~33 KB). Jordan's local `JM105_Figure3_Euler_Bundle_v6_EXTRACTED` results also contain these files. The run generated panel sources and assets, then failed only at the composite cross-font text audit due to clipped headings and title/panel-letter overlaps. The connector still exposes only the retrieval transcript, not exact source bodies, so the files remain `PARTIAL / SOURCE LOCATED`; no snippet reconstruction is permitted.

A 2026-07-15 File Library pass located definitive terminal records showing that `figure3_base_renderer.py` and `Figure_3_render_all_v21.py` were recovered from the historical v21 Euler area and copied into current Figure 3 build bundles. The observed earlier failures were invocation/schema problems—missing `intron_id` in a supplied candidate TSV and an unsupported extra positional argument—not proof of incomplete renderer source.

A 2026-07-13 evening File Library pass located exact uploaded files for the current Figure 5 C/D/E renderer and its Euler launcher, plus evidence that the corrected Figure 2 public-final renderer ran successfully after the `threshold_c` → `threshold_cr` fix. The complete Python files are present in File Library, but the connector exposed only indexed excerpts rather than retrievable full file bytes, so they remain `PARTIAL / SOURCE LOCATED` and were not reconstructed or committed. The next import must use the exact uploaded `.py` files or the verified Euler paths, not snippet assembly.

On 2026-07-14, the exact complete standalone Figure 2F seven-gate raw-count renderer was recovered and committed at `panel-renderers/jm105-figure2-v4_1/figure2f_seven_gate_counts.py`. Its verified source is the strict 402-row gate table and generator under `/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/`. It preserves the total/rRNA-depleted-only Figure 2 contract, distinguishes NMD-hidden off-minus-on IR, and does not reconstruct biological values.

The 2026-07-14 Figure 2 incident produced the accepted v4.1 execution pattern after failures involving archive layers, execution policy, missing files, raw-text audits, moved scripts, nested SSH, missing CLI arguments, Excel `UsedRange`, PowerShell interpolation, raw/enriched schemas, false visual audits, and cross-font clipping. Future figure chats must use the new reliability standard rather than repeat that discovery process.

The 2026-07-28 Figure 3 incident added permanent guards for clickable artifact delivery, local filename discovery, opaque sample IDs, Unicode genotype symbols, plain `UPF1`, common-name-only visible labels, literal-NaN rejection, exact axis contrasts, scheduler-state interpretation and the prohibition on promoting a non-Mud1 CR-selectivity renderer as canonical Figure 3.

On 2026-07-29, Jordan supplied the exact complete Python source for three files that a Claude response produced in the NMD-analysis chat, recovering: the Figure 3 v2.1 CR-selectivity renderer, the Figure 4 v11.2 Mud1-coupling renderer, and the JM100 lifespan-to-CSV converter that feeds Figure 4 panels a/b. All three compiled and were committed byte-for-byte unmodified under `panel-renderers/jm105-figure3-cr-selectivity-v2-1/` and `panel-renderers/jm105-figure4-mud1-host-transcript/`. This is source recovery only — no Euler execution or Jordan visual acceptance has happened yet, and the Figure 4 title matches the current authority PR #12 recorded, but that PR's outstanding request for a successful Euler run and hashes remains open. See both new folders' READMEs for the full recovery notes, including two flagged discrepancies (a stale version string in each script's header docstring, and an open question about whether the Figure 3/Figure 4 split reconciles with the 2026-07-28 "locked Mud1-dependence Figure 3" framing).
