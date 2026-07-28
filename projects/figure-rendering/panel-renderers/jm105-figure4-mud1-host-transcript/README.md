# JM105 Figure 4 — Mud1/host-transcript coupling

**Status:** `PARTIAL / AUTHORITY LOCKED; CURRENT RENDERER UNRECOVERED`

**Current manuscript title:**

> Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response

This directory is the canonical destination for the next source-grounded Figure 4 renderer. No current publication renderer is committed here yet because the exact complete code implementing the current authority has not been recovered.

## Authority reset — 2026-07-28

Jordan explicitly superseded the same-day six-panel CR-selectivity-as-Figure-4 lineage. That lineage must not be described as the current Figure 4 architecture or publication renderer.

The obsolete lineage used the title:

> Caloric restriction selectively suppresses an age-associated retained-intron program

That scientific analysis may remain useful elsewhere in the manuscript, but its renderers and failed runs do not govern current Figure 4 numbering, title, panel identities or claim architecture.

## Deprecated exact-source lineage

The following v1 package files are exact source objects in Jordan's File Library and are preserved here only by provenance and hash, not as canonical Figure 4 code:

```text
94c389a97e15e6c4e4be3d80c9516591eb5796628c7c00acbdee06d950a657e1  JM105_figure4_cr_selectivity_panels_v1_20260728.py
c32c3d05818455af985331dfd82ec4af251d5c6a4b4e5aad90b85b0aaaf01299  paper_style.py
9f0a9fb2ff1c6718e15f147c60628806bc5a6cc94327aca18fe1a6d7e1695798  JM105_Figure4_CR_selectivity_v1.sbatch
6f9dbeba23ff55037d30dfe7e168f4e1ca3dfe61bb783694b4750aa15a61ecb6  run_JM105_Figure4_CR_selectivity_v1_from_PowerShell.ps1
815ce45ff0109796db279db73a23e945b0986041d82b879307217d0d1bc03103  README_JM105_Figure4_CR_selectivity_v1.md
a6c2501bd5a7439b6aceb6c1c39853b335e66ae335ee51b4aa24587276b50a6f  Figure4_panel_contract.tsv
8e97f37c072d1c6e8a388dcb8dc8d587e9cd56181301d0f81034ca7b69e892a4  Figure4_meeting_grounding.md
```

The exact file bodies were not transferred through the current connector, so they are not imported from snippets or reconstructed.

## Failed-run provenance

### v1 / job 8886490

- Real counts and SGD GFF paths were reached.
- Rendering stopped because candidate common-name resolution left `YDL012C` visible as a systematic identifier.
- The workflow then emitted misleading post-failure success text and failed retrieval verification.
- Classification: `DEPRECATED DIAGNOSTIC FAILURE`.

### v2 / job 8888031

- Uploaded source names:
  - `JM105_figure4_cr_selectivity_panels_v2_20260728.py`
  - `paper_style.py`
  - `JM105_Figure4_CR_selectivity_v2.sbatch`
- Real-GFF label preflight passed.
- Euler rendering failed closed because Panel D had a measured DejaVu Sans overlap:
  - `gate_name_0.1% suppression`
  - `gate_count_0.1% suppression`
- The exact v2 file bodies and hashes are not available through the current source connector.
- Classification: `PARTIAL / FAILED SOURCE LOCATED`, not canonical.

A later described v3 geometry patch is not complete recoverable source and has no verified full successful run. It remains `UNRECOVERED / DIAGNOSTIC ONLY`.

## Scientific contract for the replacement renderer

The current Figure 4 renderer must be derived from the exact current notebook/Drive authority and declared raw or source tables. It must preserve these boundaries:

- use real JM105 total/rRNA-depleted RNA-seq where JM105 RNA data are used;
- distinguish raw NMD-off/upf1Δ retained signal from `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`;
- distinguish intron retention from host-transcript abundance;
- distinguish host-transcript abundance from protein abundance;
- do not equate caloric restriction with starvation;
- do not infer biological pairing from opaque sample identifiers;
- do not invent missing measurements, gene names, panel values or causal effects;
- unsupported evidence remains `NO DATA`.

## Required exact-source intake

Before this directory can be marked `RECOVERED`, obtain and commit a complete self-contained package containing:

1. the current Figure 4 renderer implementing the Mud1/intron-retention/host-transcript claim;
2. its exact `paper_style.py` or equivalent style dependency;
3. exact Slurm and PowerShell/Bash launchers actually used;
4. the current panel specification or notebook-derived source register;
5. source-table lineage and hashes for intron retention and host-transcript abundance;
6. dependency/environment record;
7. source SHA-256 manifest;
8. successful Euler job ID, stdout marker, output directory and validation/audit files;
9. a concise reproduction command.

## Render contract

Every accepted panel renderer must:

- declare fixed canvas dimensions;
- export transparent editable-text SVG, transparent PDF, transparent PNG and a separate white preview PNG;
- request Arial while auditing installed fallback fonts;
- avoid `bbox_inches="tight"`;
- emit lane map and exact collision inventory;
- fail closed on clipping, registered text collisions, invalid labels and missing required objects;
- identify whether it regenerates panel internals from raw/source tables or merely assembles existing assets.

Composite-only and PowerPoint-asset-only scripts are assembly utilities and cannot be publication-canonical panel renderers.
