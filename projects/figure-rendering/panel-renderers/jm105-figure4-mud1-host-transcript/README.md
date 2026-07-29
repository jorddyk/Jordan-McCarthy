# JM105 Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response (v11.2)

## Recovery metadata

- Source: recovered verbatim from a Claude response in Jordan's NMD-analysis chat, uploaded 2026-07-29, together with a companion lifespan data-prep script from the same chat.
- Filenames as authored: `JM105_figure4_render_v11_2_20260729.py` and `JM100_lifespan_to_csv_20260728.py`.
- Schema tag embedded in the renderer: `JM105-FIG4-v11.2-20260729`.
- Status: **RECOVERED** — complete, unmodified, compiling Python source committed byte-for-byte (verified with `diff` and `python3 -m py_compile`), not a description or hash.
- Not yet performed: real-data Euler execution, cross-font collision audit under the target font, Windows/local output retrieval, and Jordan's visual acceptance.

## Relationship to PR #12

Draft PR #12 ("Reset JM105 Figure 4 authority and record deprecated renderer provenance") recorded the same figure title — **Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response** — as the current authoritative Figure 4 claim, and stated that the six-panel CR-selectivity-as-Figure-4 lineage before it is deprecated. PR #12 also stated that recovering "the exact renderer, style dependency, launcher, environment, hashes, ... successful Euler proof and reproduction command" was still outstanding.

This v11.2 script's title matches PR #12's stated current authority exactly, and it is self-contained (it defines its own style/typography inline rather than importing an external `paper_style.py`, so there is no separate style-dependency file to recover). It therefore looks like it may satisfy the exact-renderer half of that outstanding recovery target. It does **not** by itself satisfy the rest: a successful real-data Euler run, its hashes, and Jordan's visual acceptance are still needed. PR #12 lives on a different branch (`handoff/figure4-authority-reset-2026-07-28`) that this recovery pass did not touch; reconciling the two is a follow-up step, not done here.

## What `jm105-figure4-render-v11-2-mud1-coupling.py` does

Eight-panel figure asking whether Mud1 is required for both the intron-retention and host-transcript-abundance responses to caloric restriction (CR), in old cells:

- **a** — Mud1 is required for the full lifespan response to CR (Kaplan-Meier survival facets; requires `--lifespan` or panels a/b are explicitly rendered `NOT COMPUTED`, never fabricated).
- **b** — the lifespan extension is smaller in `mud1Δ` (bootstrap estimation plot with a permutation-test interaction P-value).
- **c** — Mud1 is required for full retained-intron suppression (`+MUD1` vs `mud1Δ` CR-suppression scatter with paired Wilcoxon test).
- **d** — candidates differ in how much they need Mud1 (ranked forest plot, bootstrap CIs over libraries).
- **e** — host-transcript abundance responds in `+MUD1`, less in `mud1Δ` (same visual grammar as panel c, applied to spliced-junction abundance).
- **f** — Mud1 couples the two responses (matched regression facets; arrows from `+MUD1` to `mud1Δ` per candidate gene).
- **g** — the interaction is not just a host-abundance artefact (adjustment dumbbells; regresses out the host-abundance genotype difference and shows the residual Mud1-dependence).
- **h** — the coordinated response in raw candidate data (paired heatmaps: retained-intron RNA and spliced-junction RNA, both genotypes × both glucose levels).

Core metrics: `IR = mean(EI,IE) / [mean(EI,IE) + EE]`; `NMD-revealed = IR(upf1Δ) − IR(UPF1+)` within a MUD1 status and condition; `CR suppression = NMD-revealed(old 2%) − NMD-revealed(old 0.1%)`; `Mud1 dependence = CR suppression(+MUD1) − CR suppression(mud1Δ)`; `host response = log2 spliced-junction abundance(0.1%) − log2(2%)`, old cells only. Host response is explicitly RNA (spliced-junction abundance), never protein abundance.

Candidate selection is deliberately **not** based on the `+MUD1` vs `mud1Δ` contrast itself (that would be circular — selecting on the effect and then testing for the effect). Candidates are frozen on the ageing effect within `+MUD1` alone (old 2% vs young 2%), which never touches the `mud1Δ` arm; the CR-based selection is retained only as a reported sensitivity check.

## Hard rules enforced in code (fail-closed)

- Common gene names only on every visible label; `--gene-map` (`SGD_features.tab`) is required.
- No `NaN` categories; unparseable rows are dropped and counted, never plotted.
- No panel frames (explicit Yves style rule).
- Typography sizes are fixed and inherited from the accepted Figure 3, not reinvented.
- Lane-locked layout in inches with an explicit geometry validator: it checks tight bounding boxes (not just axes rectangles, since tick labels and axis titles sit outside the axes rectangle) for panel-to-panel overlap and off-canvas text, and reports failures rather than silently rendering over them.
- Panels a and b require `--lifespan`; without it they render as `NOT COMPUTED`, never fabricated survival curves.
- Refuses inputs whose path contains `dryrun`, `synthetic`, `fixture`, `fake`, `mock`, `dummy`, `simulated`, or `example`.

## What `jm100-lifespan-to-csv.py` does

Converts `JM100.xlsx` (replicative lifespan, CR × Mud1) into the three-column CSV (`genotype`, `glucose`, `divisions`) that Figure 4 panels a and b consume, reading only the workbook's `Results` sheet (one row per mother cell, `Buddingcount` = number of divisions).

Two things it explicitly checks or fixes, per its own docstring:

1. The workbook's `Graphs` summary sheet has the glucose labels **transposed** relative to the raw `Results` sheet (its 18.08-division `Mud1` value is actually 0.5% glucose, not 2%). The script never reads `Graphs` for data; it only re-derives the same check from `Results` and reports if the transposition is present, so a stale summary sheet can't silently leak into a figure.
2. JM100's CR arm is 0.5% glucose; the JM105 RNA-seq CR arm is 0.1% glucose. These are different CR intensities, and the script prints this distinction explicitly rather than letting the two get conflated.

Strain naming: in this workbook, `Mud1` denotes the deletion strain (not wild type) — mapped explicitly (`STRAIN` dict) rather than by delta-symbol detection, which would otherwise misread it as wild type.

Fails closed (nonzero exit, message on stderr) if the workbook is missing, missing required columns, or contains unrecognised strain/glucose labels.

## Required inputs

- Renderer: `--counts` (same JM105 intron count schema as the Figure 3 script), `--gene-map` (`SGD_features.tab`), `--outdir`; `--lifespan` optional (CSV from `jm100-lifespan-to-csv.py`).
- Lifespan converter: `--xlsx` (real `JM100.xlsx`), `--out` (CSV path), `--sheet` (defaults to `Results`).

Renderer outputs: transparent SVG/PDF/PNG, a white-background preview PNG, `Figure4_intron_table.tsv`, `Figure4_candidates.tsv`, `Figure4_frozen_candidates.tsv`, `provenance.json` (full source/gene-map/lifespan SHA-256 hashes, candidate-selection basis, all formulas, and an explicit statement that no synthetic-data branch exists), and `figure4_manifest.json` (schema, per-panel statistics, geometry/collision audit results, `panels_not_computed` if `--lifespan` was omitted).

## Scientific/data status

Real total/rRNA-depleted JM105 and real JM100 lifespan data only; no simulated or fabricated values. No raw data, generated figures, spreadsheets, or Euler run outputs are committed alongside this source.

## Known discrepancy to flag for Jordan

The renderer's own top-of-file docstring still names the file `JM105_figure4_render_v1_20260728.py`, several versions behind the `v11.2` schema tag and the filename it was uploaded under — evidently a stale header carried over between iterations. The `SCHEMA` string and code both agree on `v11.2`, and the file was committed unmodified per this repo's rule to import exact recovered source without editing it.
