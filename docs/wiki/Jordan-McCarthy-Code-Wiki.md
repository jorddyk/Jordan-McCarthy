# Jordan McCarthy Code Wiki

_Last updated: 2026-07-13 Europe/Zurich_

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

### Priority exact-source queue

`110_JM101_JM105_integrate_intronsaurus.py`, `111_JM101_STAR_align_array.sbatch`, `112_JM101_integrate_after_STAR.sbatch`, Rsubread Step 2 hard-resume/turbo, Step 3 DESeq2, IRFinder drafts, complete vNext3/vNext3AE builders/readers, and JM133/JM134 analysis utilities. Status: exact full source not yet recovered unless already listed canonical.

## Figure rendering

### Canonical code and infrastructure

- `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1`
- `projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py`
- Figure 4E Euler/retrieval wrappers.
- `projects/figure-rendering/panel-renderers/jm105-rendering-harness/`
- `projects/figure-rendering/panel-renderers/jm105-fig4bc-sequence-architecture/`
- Partial Figure 3 Mud1/CR package: runner/README canonical; complete Python source still pending.

Prompt/spec assets under `projects/figure-rendering/prompts/` define Figure 5, manuscript-sequence, lane/collision, and artifact-package contracts. They are not runnable substitutes.

### Recovery source of truth

`projects/figure-rendering/docs/legacy-code-backfill.md`

Highest-priority missing source:

1. JM134 label-audit/rerender workflow; Euler jobs `3101802`, `3104275`, `3106256`, `3109225`.
2. JM133 weak-5′SS/Mud1 LOESS + marginal-violin renderer.
3. Nature Aging/Yves-compatible main-figure layout renderer.
4. Figure-story scoring model.
5. Figure 5 renderer and reusable `NO DATA` renderer.
6. Figure 2F final renderer and synopsis-aligned RNA-seq renderer.

The 2026-07-13 File Library search used exact filenames, job IDs, output concepts, LOESS/marginal-violin terms, Figure 5, Nature Aging, and `NO DATA`. No complete runnable source was recovered; no reconstruction was committed.

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

Canonical prompt/spec assets cover legacy backfill, daily code handoff, strategic alert triage, science preemption, Swiss leverage, and weekly strategic briefing/red-team tasks.

# Code-focused execution risks and containment

- **Risk:** legacy code remains trapped in old chats while remembered filenames/job IDs create false confidence.
  - **Containment:** project-local backfill ledgers are the source of truth; complete currently accessible source is required before canonical import.
- **Risk:** daily handoffs replace project organization.
  - **Containment:** code/status live under `projects/`; handoffs remain audit-only.
- **Risk:** figure patch sequences create one-off sprawl and violate original geometry.
  - **Containment:** canonicalize only complete final renderers and enforce the rendering operating standard.
- **Risk:** real/simulated/`NO DATA` status drifts.
  - **Containment:** declare data status in project README, renderer outputs, and handoff.

# Last-known canonical decisions

## 2026-07-13

- Repository verified private and writable on `main` with admin/push permissions.
- Figure-rendering legacy search completed; no complete JM133/JM134, Figure 5, main-layout, scoring, or `NO DATA` renderer source recovered.
- Updated the figure-rendering README and project-local backfill ledger.
- No runnable code, biological data, generated renders, or binary outputs were committed.
- Containment: figure-rendering recovery ledger is the single source of truth for missing renderer status.

## 2026-07-12

- No complete Fiji macro/Groovy source recovered; microscopy backfill ledger established.

## 2026-07-11

- JM101 provenance document recorded as a clue, not source code.

## 2026-07-10

- Imported complete TELC C1 essay-skeleton active-recall app.

## 2026-07-09

- Imported complete Kartoffel vocabulary active-recall app.
