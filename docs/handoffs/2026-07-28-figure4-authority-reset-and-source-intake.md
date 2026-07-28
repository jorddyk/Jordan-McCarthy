# Daily code handoff — 2026-07-28 — Figure 4 authority reset and source intake

## Sources searched

- Current JM105 project conversation and same-day user authority updates.
- File Library code objects and execution transcripts modified 27–28 July 2026.
- Google Drive current-state and renderer-register documents.
- Private GitHub repository, open branches and draft pull requests.
- Local runtime artifacts available to the handoff.
- Gmail attachment search was attempted but the connector was not authenticated; no Gmail result is represented as searched or recovered.

## Material finding

The same-day six-panel CR-selectivity package is exact source-located, but Jordan later superseded it as Figure 4 authority.

Current title:

> Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response

Therefore the CR-selectivity-as-Figure-4 v1/v2 lineage is preserved only as deprecated provenance. It is not imported as current publication code.

## Exact source located but not canonicalized

### Figure 4 CR-selectivity v1 package

The File Library exposes exact source objects and a source SHA-256 manifest for:

```text
94c389a97e15e6c4e4be3d80c9516591eb5796628c7c00acbdee06d950a657e1  JM105_figure4_cr_selectivity_panels_v1_20260728.py
c32c3d05818455af985331dfd82ec4af251d5c6a4b4e5aad90b85b0aaaf01299  paper_style.py
9f0a9fb2ff1c6718e15f147c60628806bc5a6cc94327aca18fe1a6d7e1695798  JM105_Figure4_CR_selectivity_v1.sbatch
6f9dbeba23ff55037d30dfe7e168f4e1ca3dfe61bb783694b4750aa15a61ecb6  run_JM105_Figure4_CR_selectivity_v1_from_PowerShell.ps1
815ce45ff0109796db279db73a23e945b0986041d82b879307217d0d1bc03103  README_JM105_Figure4_CR_selectivity_v1.md
a6c2501bd5a7439b6aceb6c1c39853b335e66ae335ee51b4aa24587276b50a6f  Figure4_panel_contract.tsv
8e97f37c072d1c6e8a388dcb8dc8d587e9cd56181301d0f81034ca7b69e892a4  Figure4_meeting_grounding.md
```

The current connector did not provide a byte-complete transfer mechanism for the large exact source bodies. No snippet-based reconstruction was committed.

Classification: `DEPRECATED / EXACT SOURCE LOCATED`.

### Figure 4 CR-selectivity v2

Execution proof identifies:

```text
JM105_figure4_cr_selectivity_panels_v2_20260728.py
paper_style.py
JM105_Figure4_CR_selectivity_v2.sbatch
job 8888031
```

The real-GFF label preflight passed, but the job failed closed on a measured Panel D fallback-font collision between the `0.1% suppression` gate name and its retained-count statistic. Exact v2 bytes and hashes were not exposed.

Classification: `PARTIAL / FAILED SOURCE LOCATED`.

### Described v3 patch

A later report describes a Panel D lane-only geometry patch and two preflight markers, but no complete exact v3 source package or fully successful output proof was recovered.

Classification: `UNRECOVERED / DIAGNOSTIC DESCRIPTION ONLY`.

## Other exact source objects located

The File Library also contains complete current or near-current Figure 2 and CR-selectivity renderer objects, including:

```text
JM105_figure2_render_v3_NMDoff_20260727.py
JM105_figure2_render_v1_2_20260727.py
JM105_figure2_render_v9_FINAL_20260728.py
JM105_figure2_render_v10_lane_locked_20260728.py
JM105_figure2_render_v12_FINAL_20260728.py
JM105_figure3_render_v3_GFF_20260728.py
JM105_figure3_render_v5_PROVENANCE_SAFE_20260728.py
JM105_figure3_render_v7_INTUITIVE_SEABORN_20260728.py
JM105_figure3_render_v8_PARSER_LOCKED_20260728.py
JM105_figure3_render_v9_NMD_PARSER_LOCKED_20260728.py
```

They were not imported today because the current handoff could not transfer their exact complete bytes into GitHub and because filenames alone do not establish the publication-canonical winner. Failed/superseded variants were not promoted.

## Drive authority check

Current Drive records confirm:

- the 22 July Figure Acceptance Matrix/Figure Bible are obsolete as governing authorities;
- Figure 2 work is currently denominator/source validity, no-exclusion length audit and age × NMD adjudication;
- total/rRNA-depleted JM105, aging first, CR second, Mud1 as genetic handle and NMD primarily as detector remain governing constraints;
- the Figure 2 v10 register records successful private layout validation but does not claim a successful real-data Euler render.

## Repository changes

Created:

```text
projects/figure-rendering/panel-renderers/jm105-figure4-mud1-host-transcript/README.md
docs/handoffs/2026-07-28-figure4-authority-reset-and-source-intake.md
```

Updated in this branch:

```text
projects/jm105-intronsaurus/README.md
projects/jm105-intronsaurus/docs/legacy-code-backfill.md
projects/figure-rendering/docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
```

## Scientific constraints preserved

- Figure 2 remains total/rRNA-depleted JM105 only.
- Raw NMD-off/upf1Δ signal is not relabelled as NMD-hidden off-minus-on signal.
- Caloric restriction is not labelled starvation.
- Host-transcript abundance is not protein abundance.
- No missing biological values, gene names, pairings or causal effects were invented.
- Failed and superseded renderer variants remain provenance, not canonical paper code.
- No raw sequencing data, generated figure binaries, Slurm logs, caches, secrets or scratch outputs were committed.

## Next exact source targets

1. Current Figure 4 notebook/Drive panel authority defining Mud1, intron retention and host-transcript abundance.
2. Complete exact current Figure 4 renderer and style dependency.
3. Exact raw/source-table lineage and hashes for retention and host-transcript abundance.
4. Exact launcher, environment, source-hash manifest and successful Euler validation proof.
5. Exact Novogene denominator files and the JM105 sample manifest needed for Figure 2 measurement validity.
6. Byte-complete transfer of the current Figure 2 renderer package after the real-data winner is adjudicated.
