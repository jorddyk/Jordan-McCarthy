# JM105 Figure 3 | CR selectively suppresses an age-associated retained-intron program (v2.1)

## Recovery metadata

- Source: recovered verbatim from a Claude response in Jordan's NMD-analysis chat, uploaded 2026-07-29.
- Filename as authored: `JM105_figure3_render_v2_1_20260728.py`.
- Schema tag embedded in the source: `JM105-FIG3-v2.1-20260728`.
- Status: **RECOVERED** — the complete, unmodified, compiling Python source is committed here byte-for-byte (verified with `diff` and `python3 -m py_compile` at import time). This is a stronger status than the repo's usual `PARTIAL / SOURCE LOCATED`, because the full file bytes were directly available this time, not just a description or hash.
- Not yet performed: a real-data Euler execution, cross-font collision audit under the target font, Windows/local retrieval of outputs, and Jordan's visual acceptance. Per the figure-rendering reliability standard, source recovery is a precondition for canonical acceptance, not a substitute for it.

## What this script does

Six-panel Figure 3 renderer restricted to wild-type MUD1 (`+MUD1`) libraries only. It tests three linked claims about caloric restriction (CR) and NMD-revealed retained introns:

- **a** — does CR reverse ageing, and only ageing (trajectory plot by response class)?
- **b** — is the coupling per-intron or only an average effect (paired scatter)?
- **c** — how much of the ageing gain does CR remove (reversal-fraction ECDF)?
- **d** — which named transcripts (three-column heatmap, common gene names only)?
- **e** — is suppression specific to age-up introns (class comparison)?
- **f** — does it hold in raw per-replicate data (strip plot, no averaging)?

Core metric, defined once and reused: `IR = mean(EI, IE) / [mean(EI, IE) + EE]`; `NMD-revealed = IR(upf1Δ) − IR(UPF1+)`; `ageing effect = NMD-revealed(old 2%) − NMD-revealed(young 2%)`; `CR suppression = NMD-revealed(old 2%) − NMD-revealed(old 0.1%)`.

## Hard rules enforced in code (fail-closed)

- Common gene names only on every visible label; the script stops if fewer than 90% of plotted genes resolve to a standard name from `SGD_features.tab`.
- No `NaN` categories: unparseable condition/age/genotype rows are dropped and the drop count is printed, never silently plotted.
- Lane-locked layout: every title/subtitle/legend/axis position is a fixed inch offset on a 7.2 × 9.2 in canvas; a post-draw pass measures actual text bounding boxes and reports any collision.
- No undefined jargon on an axis; every axis states the measured quantity in words.
- Refuses inputs whose path contains `dryrun`, `synthetic`, `fixture`, `fake`, `mock`, `dummy`, `simulated`, or `example`.

## Required inputs

- `--counts`: real total/rRNA-depleted JM105 intron EI/IE/EE count table (same schema as other JM105 figure renderers: `sample`, `age`, `glucose`, `mud1_status`, `upf1_status`, `intron_id`, `intron_category`, `parent`, `EI_count`, `IE_count`, `EE_total`, `mean_EI_IE_boundary_count`).
- `--gene-map`: `SGD_features.tab` (required; common names are mandatory, not optional).
- `--outdir`: output directory; a timestamped `FIGURE3_<stamp>/` run folder is created underneath.

Outputs: transparent SVG/PDF/PNG, a white-background preview PNG, `Figure3_intron_table.tsv`, `Figure3_top_candidates.tsv`, and `figure3_manifest.json` recording the source SHA-256, gene-name resolution fraction, per-panel statistics, and any measured text collisions.

## Scientific/data status

Real total/rRNA-depleted JM105 data only; no simulated or fabricated values. No raw data, generated figures, or Euler run outputs are committed alongside this source.

## Known discrepancy to flag for Jordan

The script's own top-of-file docstring still names the file `JM105_figure3_render_v1_20260728.py`, one version behind the `v2.1` schema tag and the filename it was uploaded under. This looks like a stale header comment carried over between iterations rather than a functional issue — the `SCHEMA` string and all computation match `v2.1` — but it was not edited here, consistent with this repo's rule to import exact recovered source unchanged rather than adapt it.

A separate open item for Jordan to reconcile: the 2026-07-28 Figure 3 learning-loop handoff (`docs/handoffs/2026-07-28-jm105-figure3-learning-loop.md`) states "the locked Figure 3 is the Mud1-dependence figure" and that a CR-selectivity renderer must not be promoted as canonical Figure 3. This v2.1 script is a CR-selectivity design restricted to `+MUD1` only, with the Mud1-dependence comparison deferred to the companion Figure 4 script recovered alongside it (`../jm105-figure4-mud1-host-transcript/`). Whether this two-figure split is the new intended architecture, or whether it needs to be reconciled against the earlier "locked" framing, is a Jordan call, not one this recovery pass makes unilaterally.
