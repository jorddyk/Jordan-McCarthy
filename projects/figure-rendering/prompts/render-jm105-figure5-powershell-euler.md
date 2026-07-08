# Render JM105 Figure 5 from PowerShell + Euler

Purpose: reusable exact prompt/spec for rendering JM105 Figure 5 using PowerShell + Euler while protecting scientific integrity and layout quality.

Original source clue/conversation context: uploaded project File Library item `Pasted text (3).txt`, created 2026-07-07, from the JM105 Figure 5 rendering-instructions chat.

Expected inputs: Fig5_McCarthy.docx/pptx, Figures 1–4 docs/ppts, Mud1 Paper Presentation with All Figures.pptx, What Data Shows.docx, and current real data sources when available.

Expected outputs: a prompt for an AI/coder that must produce fixed-dimension transparent SVG/PDF/PNG plus white-preview PNG, logs, provenance manifest, and audit report.

Known assumptions: Euler project root defaults to `/cluster/scratch/jmccarthy/JM105_RNAseq`; missing experiments must be represented as `NO DATA — experiment pending`; no fake data may be generated.

Data status: prompt/spec artifact only. It does not contain biological data and is not runnable code.

---

You are continuing the JM105 RNA Seq Analysis project. Your task is to render Figure 5 from PowerShell + Euler, using the uploaded Figure 5 document and the uploaded Figures 1–4 as style/story references.

READ THESE FILES FIRST:
- Fig5_McCarthy.docx = authoritative Figure 5 panel specification.
- Fig5_McCarthy.pptx = visual mockup only. Treat any gels, bars, curves, scatter, or numeric values inside it as non-authoritative unless independently matched to real data files.
- Fig1_McCarthy.docx / Fig1_McCarthy.pptx
- Fig2_McCarthy.docx / Fig2_McCarthy.pptx
- Fig3_McCarthy.docx / Fig3_McCarthy.pptx
- Fig4_McCarthy.docx / Fig4_McCarthy.pptx
- Mud1 Paper Presentation with All Figures.pptx = style and color reference.
- What Data Shows.docx = current story logic.
- Synopsis_for_Yves_Barral_Jordan_McCarthy_v4.docx = background only; it is out of date and must not override the RNA-seq results.

ABSOLUTE PRIORITY ORDER:
1. Real data provenance beats mockup appearance.
2. Fig5_McCarthy.docx defines what each panel should mean.
3. What Data Shows.docx defines the current biological interpretation.
4. Figures 1–4 define graphic design, color coding, panel typography, and figure style.
5. The old synopsis is historical background only.
6. Fig5_McCarthy.pptx is a design sketch only, not a data source.

DO NOT GENERATE FAKE DATA.
No fake gels.
No fake qPCR bars.
No fake RT-PCR bands.
No fake reporter values.
No fake lifespan curves.
No fake aging-chip scores.
No fake error bars.
No simulated distributions pretending to be experiments.
No made-up n, p-values, fold changes, or confidence intervals.

For any panel requiring an experiment that has not been done or whose real source file cannot be identified, render a polished placeholder that says:
“NO DATA — experiment pending”
Then add one concise line describing the intended assay. Do not include axes, fake points, fake bands, fake curves, or fake measurements in a NO DATA panel.

FIGURE 5 STORY:
Figure 5 should be a coherent final validation/model figure for the JM105 paper:
Aging creates a selected retained-intron / NMD-sensitive leakage state.
CR suppresses this state.
Mud1 is required for full CR suppression.
The RNA-seq supports a Mud1-linked spliceosome/QC state, not global splicing collapse.
The figure should make clear which validations are pending and which conclusions are already supported by RNA-seq and existing lifespan/cell-cycle data.

PANEL CONTENT:
5A. Targeted validation of selected retained introns
- Intended assay: RT-PCR or RT-qPCR for 3–6 candidates from Figures 2–3.
- Conditions: young 2%, old 2%, old 0.1% CR; optionally +MUD1 vs mud1Δ and NMD-on vs NMD-off.
- Readout: spliced isoform vs retained-intron isoform.
- If no real RT-PCR/qPCR data file exists, render NO DATA placeholder only.

5B. NMD sensitivity / leakage validation
- Intended point: selected retained-intron RNAs are stabilized when NMD is off, supporting entry into an NMD-sensitive pool.
- Allowed assays only if real: NMD-on vs NMD-off RT-PCR/qPCR, fractionation + NMD background, RNA FISH/localization.
- RNA-seq-derived NMD-hidden values may be referenced only as already-established context, not as an orthogonal validation panel unless the panel is explicitly relabeled as RNA-seq evidence.
- If no real validation data exists, render NO DATA placeholder only.

5C. Candidate intron perturbation or reporter test
- Intended assay: intron deletion/correction, reporter, splice-site strengthening/weakening, or directly relevant export reporter.
- Purpose: causal bridge from descriptive RNA-seq to mechanism.
- If no real perturbation/reporter data exists, render NO DATA placeholder only.

5D. Lifespan or aging-state consequence
- Intended assay: replicative lifespan, aging-chip survival, interdivision timing, stress/mitochondrial phenotype, or rescue/modification of mud1Δ CR defect by candidate intron correction/removal.
- Use real existing lifespan/cell-cycle data only if source files are found and provenance is explicit.
- Do not render the mock lifespan curves from Fig5_McCarthy.pptx unless they correspond to real data.
- If no candidate-intron consequence data exists, render NO DATA placeholder only.

5E. Integrated final model
- This panel can be conceptual because it is a model.
- It must summarize only supported claims:
  aging increases a selected retained-intron / NMD-sensitive state;
  CR suppresses it;
  Mud1 is required for full CR suppression;
  the best model is a Mud1-linked spliceosome/QC allocation state.
- Do not claim direct spliceosome relocalization unless direct localization data are included elsewhere.
- Do not claim causality for every candidate intron.
- Avoid poly-A / mRNA-like / P-versus-T framing.

5F. Caveats and boundaries
- State clearly what Figure 5 does not claim:
  not global collapse of splicing;
  not every intron;
  not poly-A representation as the main story;
  not host-expression change alone;
  not proof of direct spliceosome relocalization unless directly measured;
  not therapeutic translation;
  not universal conservation.
- This panel should be polished, not apologetic. It should make the figure stronger.

LAYOUT:
- Match the landscape Figure 1–3 / Figure 5 deck format: 13.333333 × 7.5 inches.
- Use a 2 × 3 grid: A–C top row, D–F bottom row.
- Title lane across top.
- Each panel gets a bordered rounded card with a panel letter, concise conclusion-style title, and either real data or a NO DATA placeholder/model/caveat content.
- Do not add panels beyond A–F.
- Do not render irrelevant panels from the outdated synopsis.
- Do not include external comparison panels unless explicitly part of Fig5_McCarthy.docx and backed by real data.
- Do not include poly-A, P-versus-T, mRNA-like, or P−T constructs.

COLOR AND STYLE:
- Extract the palette from Figures 1–4 / Mud1 Paper Presentation with All Figures before drawing.
- Preserve existing color meanings strictly.
- Keep existing blue/orange/green/purple logic consistent with prior figures.
- Use neutral gray for NO DATA placeholders.
- Use Arial throughout.
- SVG text must remain editable text, never converted to paths.
- Nature Aging style: clean, high-density, restrained, publication-ready, no decorative fake science.
- Minimum final rendered font sizes:
  panel letters ≥16 pt;
  panel titles ≥8 pt;
  axis titles if any ≥7 pt;
  tick labels if any ≥6 pt;
  placeholder text ≥10 pt;
  caveat/model text ≥6.5 pt.
- After rendering, parse the emitted SVG and report actual font-size attributes by panel.

MANDATORY WORKFLOW — DO THIS BEFORE WRITING CODE:
Step 1: Emit a lane map.
Make a table assigning every object in Figure 5 to exactly one lane:
descriptor/title, plot, label, legend, x-tick, group label, right-stat, footer.
Include the coordinate/anchor for each object.
For NO DATA panels, include placeholder headline, assay note, and any icon/schematic in the lane map.
If two objects collide, resolve by lane geometry, not by dropping objects.

Step 2: Emit a collision inventory before patching.
List exact object pairs:
[object A] × [object B] → resolution.
Cover:
- text clipping;
- character overlap;
- title spillover;
- panel-letter/title collision;
- placeholder text crowding;
- legend/label collision;
- footer line spacing;
- wasted y-axis range if any real plot exists;
- label–point collision if any real plot exists;
- semantic collision, e.g. data-looking object in a NO DATA panel.
If a lane was checked and clean, say so by lane name.

Step 3: Data provenance manifest.
Before rendering, create and show a table:
panel | render mode | data status | source path | source columns/files | decision.
Allowed render modes:
REAL_DATA,
MODEL_ONLY,
CAVEAT_ONLY,
NO_DATA_PLACEHOLDER.
A-D should default to NO_DATA_PLACEHOLDER unless a real source is found.
E should be MODEL_ONLY.
F should be CAVEAT_ONLY.

Step 4: Code contract.
Deliver complete end-to-end runnable code only.
No snippets.
No placeholders.
No “same as above.”
No undefined variables.
Explicit entry point.
Separate PowerShell and Euler code clearly.
Use one canonical output folder, not scattered iteration folders.

PowerShell requirements:
- Provide one complete PowerShell script that:
  1. defines local and remote paths;
  2. creates the remote Figure 5 render folder on Euler;
  3. uploads the renderer/script and any required small input manifests;
  4. submits or runs the Euler job;
  5. retrieves SVG, PDF, PNG, white-preview PNG, logs, audit files, and manifest.
- Do not use ambiguous manual steps unless absolutely required.

Euler requirements:
- Use /cluster/scratch/jmccarthy/JM105_RNAseq as the project root unless a file inspection proves another root is needed.
- Create a timestamped folder like:
  /cluster/scratch/jmccarthy/JM105_RNAseq/Figure5_render_YYYYMMDD_HHMMSS
- Include a complete bash script and complete Python script.
- The Python script must render fixed-dimension:
  transparent SVG,
  transparent PDF,
  transparent PNG,
  white-background preview PNG.
- Canvas size must be declared as constants.
- Confirm in a code comment that bbox_inches="tight" does not appear.
- Do not use bbox_inches="tight" anywhere.
- Do not infer canvas from content.

Render verification:
- Parse SVG after rendering.
- Report actual font-size values per panel.
- Verify that SVG text is editable text, not paths.
- Verify there are exactly six panels A–F.
- Verify every NO DATA panel contains “NO DATA — experiment pending.”
- Verify A–D contain no fake axes/points/bands/curves unless REAL_DATA provenance is confirmed.
- Verify no text spills outside its panel card.
- Verify no title/panel-letter collisions.
- Verify all output files exist and have nonzero size.
- Save an audit report as text/markdown in the output folder.

Final response after rendering:
- Paste or link the white-background preview PNG.
- Provide paths to SVG, PDF, transparent PNG, white preview PNG, data provenance manifest, and audit report.
- Include the per-panel actual font-size verification table from the SVG.
- Include the collision inventory and final lane audit.
- Stop after rendering; do not keep iterating unless I ask.
