# CODE HANDOFF — 2026-07-08 Figure Rendering Lane Contract Backfill

## Repo

`jorddyk/Jordan-McCarthy`

## Project area

Figure rendering / Nature Aging mockups.

## Human purpose

Recover the reusable lessons from the JM105 Figure 2 Panel F failure/repair sequence and the Figure 4 artifact-package workflow into the repo so future figure-rendering chats generate complete downloadable packages, preserve data integrity, and avoid layout whack-a-mole.

## Files created

- `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md`
- `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md`
- `docs/handoffs/2026-07-08-figure-rendering-lane-contract-backfill.md`

## Files updated

- `projects/figure-rendering/README.md`
- `projects/figure-rendering/docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Files deliberately not committed

- Generated Figure 2 Panel F SVG/PDF/PNG/preview files.
- The Figure 2F v7/v8/v9 patch scripts as canonical runnable code, because this pass recovered the prompt/spec and patch sequence but not the complete final standalone renderer source.
- Mockup PNGs, docx/pptx artifacts, biological input tables, Euler logs, tarballs, and generated outputs.

## Scientific/data status

No biological data were changed or imported in this pass. The committed files are prompt/spec artifacts only and are explicitly marked non-runnable.

The new lane/audit prompt preserves current JM105 Figure 2 constraints:

- Figure 2 is total/rRNA-depleted only unless Jordan explicitly reverses this.
- Do not use poly-A, P-versus-T, mRNA-like, or P−T logic for Figure 2.
- NMD-hidden means `IR(upf1Δ) − IR(UPF1+)` matched by intron/condition/genotype/capture.
- Candidate score means `min(aging_effect, CR_suppression)`.
- Panel F Mud1-dependence requires computed +MUD1 versus mud1Δ CR-suppression contrast and data-driven y-limits.

## Implementation notes

The repo now contains a reusable instruction contract that forces future figure-generation runs to:

- state the biological purpose and data transformation before code;
- create a lane map before writing or patching code;
- enumerate exact colliding objects before patching;
- use fixed transparent SVG/PDF/PNG plus white-preview PNG;
- preserve editable SVG text and avoid `bbox_inches="tight"`;
- keep x ticks, genotype labels, right stats, and footnotes in separate lanes;
- use a one-ZIP-plus-one-PowerShell-runner workflow for downloadable artifacts;
- hard-stop on missing required data/provenance unless Jordan explicitly asks for draft mode.

## Final code paths

```text
projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md
projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md
projects/figure-rendering/README.md
projects/figure-rendering/docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
docs/handoffs/2026-07-08-figure-rendering-lane-contract-backfill.md
```

## Legacy-backfill progress

This pass imported two exact reusable prompt/spec artifacts from the current project conversation. No new complete runnable source code was imported.

## Remaining source-recovery targets

- `projects/figure-rendering/panel-renderers/render-figure2-panel-f-mud1-dependence.py` — exact final complete source still needed; current pass only recovered the final layout requirements and patch sequence.
- `projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py`
- `projects/figure-rendering/panel-renderers/render-no-data-placeholder.py`
- `projects/figure-rendering/panel-renderers/avoid-label-overlap-audit.py`
- Figure 4/5 generated artifact-package scripts if complete standalone source is produced in future chats.
