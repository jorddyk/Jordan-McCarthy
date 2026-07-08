# Figure Panel Generation Lane/Audit Contract

Purpose: reusable prompt/spec artifact for JM105/Intronsaurus figure-panel generation after the Figure 2 Panel F layout repair sequence.

Original source clue/conversation context: recovered from the July 2026 JM105 Figure 2 panel-rendering failure/postmortem conversation. Panel F only became acceptable after switching from local nudges to explicit lane allocation: descriptor axis, plot lane, x-tick lane, genotype lane, right-stat lane, and footer axis.

Expected inputs: figure-specific `.docx` source-of-truth document, visual mockup/PPT/screenshot, real data paths on Windows/Euler, and panel-specific biological definitions.

Expected outputs when used to generate code: complete runnable renderer package; transparent SVG/PDF/PNG; white-preview PNG; source TSVs; provenance; layout decisions; text layout audit; text overlap audit; output manifest.

Known assumptions: prompt/spec artifact only; not runnable code. It uses no biological data and must not be treated as analysis output.

Data status: no real data used here; no toy/simulated data generated; no `NO DATA` placeholders rendered.

---

## Non-negotiable behavior

Treat each figure panel as a layout contract, not as a plotting task.

Before writing code:

1. State what the panel must prove biologically in one sentence.
2. State what data transformation is being used, including whether it is raw IR, NMD-hidden IR, CR suppression, aging effect, or Mud1-dependence.
3. State what is forbidden. For current Figure 2: no poly-A logic, no P-versus-T, no mRNA-like wording, no P − T ranking.
4. Inspect the visual target/mockup and define fixed lanes: plot lane, label lane, header/descriptor lane, legend lane, x-label lane, genotype/group lane, right-stat lane, and footnote lane.
5. Do not solve crowding by deleting scientific or aesthetic content unless Jordan explicitly asks. First solve by lane separation, canvas ratio, controlled text size, wrapping, manual legends, or moving labels out of dense data regions.

## Code rules

1. Provide complete runnable code blocks or downloadable artifacts only. No snippets unless explicitly requested.
2. Label every inline code block as EULER, PowerShell, Python, or R.
3. Every figure-rendering script must run a syntax preflight before submission:

```bash
python -m py_compile script.py
```

4. Every figure-rendering job must write:
   - transparent SVG
   - transparent PDF
   - transparent PNG
   - white-preview PNG
   - plot source TSV
   - layout/audit TSV
   - run summary TXT
5. Do not use `bbox_inches="tight"` for final figure assets unless explicitly justified, because it can crop labels unpredictably.
6. Preserve editable SVG text:

```python
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
```

7. Request Arial, but do not pretend Euler truly has Arial unless audited. SVG text should still request Arial so it resolves on Windows/PowerPoint/Illustrator.
8. Preview PNGs may have white backgrounds, but final SVG/PDF/PNG must remain transparent unless explicitly requested.
9. Never add a white panel box, grey border, or rounded card to the final transparent SVG unless explicitly requested.

## Data-audit rules

1. Always write `DATA_CHANGED=False` unless the code intentionally modifies the source data.
2. Always write `POLYA_DATA_USED=False` for current Figure 2.
3. Always write `CAPTURE_USED=total/rRNA-depleted` for current Figure 2.
4. Do not call a value NMD-hidden unless it was computed as:

```text
IR(upf1Δ / NMD-off) − IR(UPF1+ / NMD-on)
```

matched by intron, age, glucose, genotype, and capture.

5. Do not call a contrast Mud1-dependent unless CR suppression was computed in both +MUD1 and mud1Δ:

```text
CR suppression(+MUD1) − CR suppression(mud1Δ)
```

6. For Figure 2 candidate ranking, use:

```text
joint_score = min(aging_effect, CR_suppression)
```

and audit that `joint_score` exactly equals the recomputed minimum.

7. Keep systematic ORF names out of visible labels when a common SGD name exists. Systematic names may appear in audit tables only.
8. Exclude mitochondrial and UTR introns from the main strict nuclear ORF candidate set unless explicitly told otherwise.
9. Always write coverage audits showing which introns have complete condition/genotype/NMD data.

## Visual-audit rules

After rendering, audit text clipping and text overlap using the Matplotlib renderer.

The audit must write:

```text
text_layout_audit.tsv
text_overlap_audit.tsv
```

The audit is necessary but not sufficient. Also inspect the rendered preview logically:

- Are any handles touching labels?
- Are footer lines too close?
- Are labels inside data clouds?
- Are titles/subtitles colliding?
- Are axis labels or tick labels compressed?
- Does the y-axis waste space and compress the data?
- Are transparent outputs actually transparent?

When Jordan points to an overlap, identify the exact colliding objects before patching. For example:

```text
orange legend handle touches black NMD-off text
```

not:

```text
legend is too high
```

Do not guess adjacent causes. Patch the actual visual collision.

## Current Figure 2 panel-specific rules

### Panel A

- Hero map.
- x-axis: aging effect in 2% glucose.
- y-axis: old-cell CR suppression.
- Use strict nuclear mRNA/ORF intron universe.
- Use label column with leader lines for top candidates.
- No internal panel letter/title if the composite figure provides them.

### Panel C

- Ranked reliable candidates.
- Must show common gene/intron label, aging effect, CR suppression, and conservative score.
- Do not use P − T or poly-A ranking.
- Preserve table/bar richness by using separate lanes for each metric.
- Do not put bars, values, and score in the same x-space.

### Panel D

- Representative raw NMD-on/off profiles.
- Must show raw retained-intron IR across young 2%, old 2%, old 0.1% CR.
- Must show NMD-on/UPF1+ and NMD-off/upf1Δ.
- Use large enough points and traces to be readable at final panel size.
- If using a legend, manually space legend handles and text if Matplotlib's default legend touches text.
- Do not let gene labels compete with the legend or data.

### Panel E

- Reliability/gating panel.
- Should show transparent candidate-selection gates and n retained after each gate.
- Must not be decorative only; it should explain why the candidates in C are reliable.

### Panel F

- Set-level Mud1-dependence preview/test.
- Must show selected candidates paired by intron.
- Use old 2% and old 0.1% CR NMD-hidden IR in +MUD1 and mud1Δ.
- Show points as individual introns, grey paired lines, and mean ± 95% CI bars.
- Use data-driven y-limits; do not force symmetric ±0.4 if it wastes space.
- Do not include internal F/title if the composite figure already has panel labels.
- Keep the subtitle/descriptor in a dedicated top axis if used.
- Keep x ticks, genotype labels, and footer in separate vertical lanes.
- Keep right-side set-test text in its own lane with separate rows for label and q value.
- Footer should be in a dedicated footer axis with enough line spacing, not stacked `fig.text` calls.

## Answer-format rules for future chats

1. Start with a concise diagnosis of the actual problem.
2. Say what the final structural fix is.
3. Then provide downloadable artifacts or one complete runnable code block.
4. Include the exact output directory and exact files to inspect/retrieve.
5. Include a short checklist of what the run summary should show.
6. Do not over-apologize.
7. Do not say "this should probably work" without a concrete audit.
8. Do not ask Jordan for a screenshot/log when the next useful step can be a self-contained diagnostic+patch block.
9. If a job fails, first identify whether the failure is code syntax, data coverage, plotting, or post-render serialization. Do not assume a data problem.
10. Keep responses practical and not verbose unless Jordan asks for a postmortem or instruction set.

## Decision rule

If a panel looks bad, do not patch locally first. Reconstruct the lane map, identify which lanes collide, then change the layout so the collision is impossible.
