# JM105 Figure 2 v4.1

Status: user-confirmed successful end-to-end execution on 2026-07-14.

This folder records the accepted execution pattern that finally rendered and retrieved all six Figure 2 panels without clipping or overlap under the Euler font environment.

## Exact renderer source is now in GitHub

The exact accepted Python renderer bytes are stored under:

```text
exact_renderer_parts/render_JM105_Figure2_v4_1_no_overlap.py.part00
...
exact_renderer_parts/render_JM105_Figure2_v4_1_no_overlap.py.part05
```

Run:

```bash
python3 materialize_exact_renderer.py
```

This reconstructs:

```text
render_JM105_Figure2_v4_1_no_overlap.py
```

and refuses to continue unless its SHA256 is exactly:

```text
167ac8ffd306ce5e6fb234a4ed3c35eea5b8f2be7205b0df46c1b4f5b28ec593
```

The parts were created from the exact package that succeeded, and the materializer was independently tested to produce byte-identical output.

The source inputs remain in the immutable accepted Drive package documented in `CANONICAL_PACKAGE_LOCATION.md`; this avoids duplicating biological source tables while preserving the exact runnable code and hashes in GitHub.

## Panel identities

- A: JM104 replicative-lifespan curves.
- B: aging-effect versus old-cell CR-suppression scatter.
- C: full four-quadrant interpretation panel.
- D: ranked named candidates.
- E: accepted raw NMD-on/off profile panel source restored from vector content.
- F: selection-gate hierarchy in the accepted checklist visual language.

## Proven workflow

1. Validate the exact sources and schemas.
2. Upload the renderer, Euler runner, and source inputs.
3. Load `fast_python_workshop_cpu/2025.0.0` and initialize the CPU environment.
4. Compile the exact Python renderer.
5. Render A-F with fixed canvases and the hard post-draw collision gate.
6. Verify every panel's transparent SVG/PDF/PNG and white preview.
7. Retrieve the complete output with direct `scp -r`.
8. Verify the hard audit pass locally and open the white contact sheet.

## How this helps later figures

Use this renderer as an engineering scaffold, not as a biological or visual template to copy blindly.

Reusable components:

- fixed millimetre canvas constants;
- separate panel and composite rendering;
- transparent SVG/PDF/PNG plus white previews;
- editable SVG text settings;
- explicit font resolution and cross-font testing;
- post-draw text clipping and pairwise overlap audit;
- point-versus-direct-label collision testing;
- legend-versus-data collision testing;
- visible systematic-ORF rejection;
- lane-map and collision-inventory exports;
- fail-closed output verification;
- PowerShell → Euler → direct `scp -r` delivery pattern;
- local verification and preview opening before success.

Do not reuse Figure 2 panel identities, source paths, axes, candidate selection, labels, dimensions, colors, or layout for another figure without deriving them from that figure's own PowerPoint, acceptance matrix, source data, and biological claim.

## Cross-font validation

The complete renderer was tested under both Liberation Sans and DejaVu Sans. The v4 failure occurred because a local Liberation Sans pass did not predict DejaVu Sans legend width. v4.1 fixed this using manual two-row legend lanes and fixed label slots.

## Accepted package hashes

```text
JM105_Figure2_v4_1_RENDER_PACKAGE.zip
05bc27f9d0523c9bd6da14bd03e2acc01d8f3790ee927addf121f045f76b5ba5

render_JM105_Figure2_v4_1_no_overlap.py
167ac8ffd306ce5e6fb234a4ed3c35eea5b8f2be7205b0df46c1b4f5b28ec593

run_JM105_Figure2_v4_1_on_euler.sh
11bf4e9bd8f9ea99059503401aebec873792687573db5df85cd25ca563159103

run_JM105_Figure2_v4_1_from_PowerShell.ps1
6c5e990ef4610440803e854b29f6358d072d4844fcb2ed488557e68523dbc2e9

Panel2A_JM104_RLS_source_CLEAN_v3_1.tsv
12005940f6b3366cc52c9f5d28ac188fc5c6703cfd92947f5cc9d2a4767c7c6e

Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv
5ef46cfcbca9663e4ad4369ca3eeb83844098fef2302a9c547089444f7a78e9a

Figure2E_existing.svg
2aef76c99062e1c58f1829821ca5df1cd8af4de5a88c822d55841ed9e28f6b0f
```

The complete incident chronology and all anti-repeat rules are in:

- `../../docs/jm105-figure2-2026-07-14-complete-incident-postmortem.md`
- `../../docs/figure-rendering-reliability-standard.md`

Only the accepted canonical version belongs here. Failed v2/v3/v4 intermediates are documented in the incident record rather than retained as competing renderers.