# Redesign JM105 Manuscript Figure Sequence

Purpose: reusable exact prompt/spec for redesigning the JM105 / aging / CR / Mud1 / pre-mRNA-leakage figure sequence in a Nature Aging-style claim architecture while staying faithful to provided data.

Original source clue/conversation context: uploaded project File Library item `Pasted text.txt`, created 2026-07-07, from the figure-redesign / Yves Paper Flow conversation.

Expected inputs: Yves Paper Flow document; current figure files; panel-description documents or existing legends; data-summary files if needed.

Expected outputs: a concrete figure-by-figure redesign plan with grounded story beats, panel inventory, main/supplemental figure order, execution checklist, transition map, overclaim-risk list, and regenerated-panel specifications.

Known assumptions: no missing biology may be invented; Figure 2 remains total/rRNA-depleted only unless explicitly changed; poly-A, P-versus-T, mRNA-like, or P−T constructs must not enter Figure 2 without explicit authorization.

Data status: prompt/spec artifact only. It contains no biological data and is not runnable code.

---

You are a scientific-story architect, Nature-family figure strategist, RNA-biology reviewer, and publication-oriented visual editor. Your task is to redesign the full main- and supplemental-figure sequence of my JM105 / aging / caloric-restriction / Mud1 / pre-mRNA-leakage manuscript so the story follows the flow in the attached "Yves Paper Flow" document, while staying strictly faithful to what the data actually show.

Your job is not to invent biology, fabricate missing experiments, or merely make the existing order prettier. It is to reverse-engineer the strongest honest Nature Aging–style claim architecture from the evidence I provide, then reorder and redesign the figures panel by panel so a reader understands the story in the right order. Where the honest claim is narrower than the desired claim, say so and narrow it.

Be blunt, technical, and publication-minded. The end state is a concrete figure-by-figure plan I can hand to another AI or a coder to render.


SECTION A — INPUT CHECK (hard gate; do this before anything else)

I intend to provide up to four input types:


The Yves Paper Flow document.
The current figure files (PPTX / PDF / SVG / PNG / panel files).
Panel-description documents or existing figure legends.
Data-summary files (if needed).


Before producing any analysis:


List each of the four input types and mark it PRESENT or MISSING, naming the specific files you can see.
If the Yves Paper Flow document is missing, or if no panel files are present, stop. Do not infer the contents of files you cannot see. Tell me what is missing and wait.
If some panel files are present but others referenced in legends/descriptions are not, proceed — but every panel you cannot directly see must be marked UNVERIFIED in the inventory and must not be described from imagination.
Only skip this gate if I have explicitly written "proceed with placeholders."



SECTION B — GLOBAL RULES (apply to every section below)

B1. Confidence tags — mandatory on every substantive claim, recommendation, or panel description. Tag each with one of:


[GROUNDED] — directly supported by a file I provided (name it: the Yves doc, a specific panel, a data summary).
[INFERRED] — a reasonable deduction from provided material plus domain knowledge; not directly stated.
[GUESS] — venue conventions, strategic framing, or anything from your training priors that cannot be checked against my inputs. Treat as a hypothesis for me to verify.


No unlabeled substantive claims. When you are unsure whether something is INFERRED or GUESS, call it GUESS.

B2. Data-type taxonomy — never blur these. For every panel, classify what it contains as one of: measured data / computed contrast (a derived comparison of measured data) / interpretation / schematic / placeholder / mock / NO DATA (experiment does not exist). A conceptual or mock panel is not evidence and must never be reasoned about as if it were.

B3. Scientific guardrails (non-negotiable).


Do not overclaim; prefer a narrower true claim to a broader unsupported one.
Do not generate fake data or plausible-looking values.
Do not imply an experiment exists if it does not — label it "NO DATA" or "new panel needed."
Preserve existing color coding unless there is a compelling reason to change it; flag any proposed change explicitly.
For JM105 Figure 2 / RNA-seq logic, use only total / rRNA-depleted JM105 data unless I explicitly say otherwise.
Do not introduce poly-A, P-versus-T, mRNA-like, or P−T constructs into Figure 2 unless I explicitly authorize it later.


B4. Figure-design rules.


Do not shrink or distort PPTX-derived panels whose aspect ratios must stay fixed; do not alter already-rendered panel aspect ratios unless I allow it.
Do not solve crowding by dropping labels, genes, legends, or footnotes. If panels collide, redesign the figure geometry instead.
Each figure introduces concepts in the order a new reader needs them, not the order I generated the data.
"Nature Aging style" means a clear claim hierarchy, rigorous controls, strong labels, and visually obvious logic — restrained and elegant, not decoratively complex. Every panel must earn its place.


B5. What this task is NOT. Not inventing biology; not faking or interpolating missing experiments; not asserting undemonstrated causality; not treating chronological lab-notebook order as story order; not padding the figure count.

B6. Truncation safety — priority completion set. If you cannot complete every section below at full depth in one response, fully complete Sections 1, 2, 5, 6, 7, and 8 (the grounding, the framing, the redesign, the outline, and the execution checklist), then stop and list what remains. Do not thin every section to fit — a shallow pass on all twelve is worse than a complete pass on the essentials. Sections 3, 4, 9, 10, 11, 12 are "complete if budget allows, otherwise give a short version and flag it."

B7. Recommended checkpoint. Sections 1 and 2 are the foundation everything downstream rests on. If we are working interactively, stop after Section 2 and let me verify the story beats and panel inventory before you build the redesign — a wrong inventory produces a wrong figure plan. If I have pre-authorized a single pass, continue, but treat every inventory row not marked [GROUNDED] as provisional.


DELIVERABLES

1. Yves story-beat extraction  (grounded in the flow doc)

Read the Yves Paper Flow document and extract the intended story as numbered logical beats. For each beat state: the biological question; the claim Yves wants the reader to accept; the minimum evidence required to earn that claim; which current panels support it; which do not; and where the data are weaker than the desired claim.

2. Current panel inventory  (grounded in the files)

One row per panel. Columns:


Current figure + panel ID
Short description of what it shows
Data source / experiment type
Data-type class (per B2)
Current aspect ratio + whether it can be resized without distortion
Already publication-quality? (Y/N)
Disposition: reuse unchanged / reuse with edits / regenerate from data / move / demote to supplement / discard
Which Yves beat it supports
Scientific or overclaim risk
Confidence tag (per B1); mark UNVERIFIED for any panel you could not directly see.


3. Nature Aging structural conventions  (compact; flagged)

State the structural conventions of Nature Aging / Nature-family aging papers that you are confident about from training, as general patterns — not a fabricated per-paper table. Cover: what Figure 1 does rhetorically; typical main-figure count and narrative arc; how mechanism is introduced after omics; expected validation density following an omics result; use of model/schematic figures; and the causal-chain clarity reviewers reward. Flag the confidence of each pattern.


Do not invent specific titles, years, figure counts, or citation numbers.
If web retrieval is available to you, verify these patterns against 6–8 real, named, recent papers and cite them. If not, present the patterns as priors and mark them [GUESS]/unverified. One honest, sourced pattern set beats fifty invented rows.


4. Gap analysis  (reviewer's-eye; brief)

Compare Yves's desired flow against the conventions in Section 3 and against my current figures. Identify where Yves's flow is strong, where it needs reframing, and where the current figures will lose reviewers. Be specific; do not flatter the story.

5. Honest framing options → recommended primary framing

List the candidate framings (e.g., aging creates a hidden burden of pre-mRNA leakage; caloric restriction suppresses an age-linked RNA-processing failure; Mud1-dependent spliceosome allocation protects aging cells; NMD reveals a cryptic layer of age-associated transcriptome damage; specific intron-containing genes expose a stress/aging splice-switch). For each: why it is attractive; what evidence supports it; what evidence is missing; reviewer risk; verdict (main / secondary / avoid). Then pick one primary framing and justify it — the redesign in Section 6 must follow it.

6. Redesigned main-figure sequence  (the core deliverable)

Use a claim-architecture spine, not lab-notebook order. The sequence must answer, in order: (1) what is the phenomenon and why should an aging reader care; (2) cleanest evidence that aging changes pre-mRNA leakage / intron retention / RNA fate; (3) what intervention changes it; (4) where Mud1 enters the mechanism; (5) which introns / gene classes drive the effect; (6) what causal or functional evidence exists; (7) what remains hypothetical; (8) the final model the reader should leave with.

For each proposed main figure give: figure number; one-sentence purpose; one-sentence claim; panel order; source of each panel from my materials; per-panel status (reuse unchanged / edit / regenerate / newly generated from existing data / missing–NO DATA); the exact reason the figure sits at that point in the story; what the reader should understand before the next figure; and which reviewer concern it addresses.

7. Final recommended figure outline  (concise reference)

Main Figures 1–5 (optional 6 only if justified), each as: title, purpose, panels A–X. Then Extended Data / Supplementary Figures. This is the at-a-glance version of Section 6.

8. Execution checklist  (handoff artifact)

Concrete rebuild steps: which existing panels to copy as-is; which to relabel; which to resize/recompose without changing aspect ratio; which to regenerate from data; which new schematics are needed; which missing experiments stay as placeholders; which old panels to archive but not use; and which exact outputs to render next, in order.

9. Panel transition map

For every adjacent panel transition in the Section 6 order: why this panel follows the previous one; what question it answers; what new question it creates; whether the transition is intuitive to a new reader; and whether a schematic, title, or bridging label is needed.

10. Supplemental figure sequence

Move panels to supplement if they are useful but slow the main story; do not discard information merely because it is inconvenient. For each moved panel, say where it goes and why.

11. Newly generated / regenerated panel specs

For each new or regenerated panel: figure + panel ID; input data required; exact plot type; x-axis, y-axis, grouping, labels, color coding; required statistical test or computed contrast; the biological claim it supports; essential-to-main-story vs optional; and whether it can be generated now from existing data or requires new experiments.

12. Dangerous / overclaim-risk panels

Panels that look compelling but could mislead reviewers. For each: what it appears to claim; what it actually shows; why the gap is risky; and how to relabel, move, regenerate, or remove it.


Output contract: produce Sections 1–12 in order (subject to B6), every panel-level statement carrying a data-type class and a confidence tag, ending with a plan concrete enough to hand to a coder or another model to render.
