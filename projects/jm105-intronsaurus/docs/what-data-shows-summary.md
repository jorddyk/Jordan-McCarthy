# What Data Shows — JM105 / CR / Mud1 / intron leakage

Purpose: preserve the user-provided scientific interpretation summary that constrains JM105 manuscript and figure-rendering work.

Original source clue/conversation context: uploaded file `What Data Shows.docx`, created 2026-07-07 in the Figure 5 / manuscript-redesign materials.

Expected inputs: JM105 lifespan/cell-cycle data, NMD-off/upf1Δ RNA-seq contrasts, CR and mud1Δ comparisons, Mud1-GFP data, intron-architecture plots, RP-stratified plots, and Parenteau comparison outputs.

Expected outputs: interpretation guardrails for manuscript/figure code and future analysis. This is not a runnable script.

Known assumptions: this document summarizes a scientific read of existing project data; individual claims should be linked back to source figures/tables before manuscript submission.

Data status: user-provided interpretation summary; no fake biological data; no raw sequencing/microscopy data.

---

My read is that CR creates a protective Mud1-dependent splicing/QC state, and when Mud1 is missing, CR no longer protects the cell from age-associated intron leakage. In fact, CR becomes partially maladaptive in mud1Δ.

The core story is not “Mud1 deletion makes cells generally sick.” The lifespan plot argues for a specific interaction: WT cells benefit from CR, but mud1Δ cells lose much of that benefit, with a strong Cox interaction. The cell-cycle plots also matter because they show mud1Δ is not simply causing a gross slow-growth artifact. So the lifespan phenotype is likely tied to a specific CR-aging mechanism rather than generic sickness.

The most important mechanistic clue is the NMD-off signal. When NMD is disabled, many candidate introns become visible. That means these RNAs are probably not just sitting quietly in the nucleus as unspliced precursors. They are entering an RNA-output pathway where NMD can normally see and destroy them. So the “leakage” signal is plausibly: intron-containing transcripts escape nuclear/splicing control, reach the cytoplasmic/NMD surveillance layer, and are normally degraded before they accumulate.

CR suppresses that NMD-revealed leakage for selected targets, but the suppression is much stronger when Mud1 is present. For SRB2, ERV1, BET1, IWR1, RPS24A, YSF3, and PTC7, the teal bars are generally larger than the orange bars. That says: CR normally reduces leakage, but it needs Mud1 to do it fully. Without Mud1, some targets barely respond, and some even go the wrong way.

The Mud1-GFP data makes this more biologically coherent. Under CR, Mud1-GFP intensity rises in older cells, while under 2% glucose it falls or stays lower. The tagged strain remains CR-responsive, so this is not obviously a broken fusion artifact. That suggests old CR cells actively maintain or accumulate Mud1 as part of the protective state. In simple language: CR seems to keep the early spliceosome/U1-associated layer competent in old cells, and Mud1 is part of that adaptation.

The intron-architecture figures are especially interesting. The vulnerable introns are not just random. The strongest architecture effect appears in 0.1% glucose + mud1Δ, where age-linked leaky introns have longer introns and branchpoints farther from the 5′ splice site. That points to a specific failure mode: Mud1 is especially important when the spliceosome has to coordinate longer intron architecture, especially long 5′SS-to-branchpoint geometry. When Mud1 is absent, CR-aged cells fail to protect this architecture class.

The RP-stratified plots sharpen this. At first glance, one might say, “maybe this is just ribosomal-protein introns.” But when you split RP and non-RP introns, the significant architecture shift is clearest in the non-RP introns, while RP introns are not significant. So the vulnerable feature is not simply “RP identity.” It is more like: long/RP-like intron architecture becomes dangerous when CR is trying to remodel splicing without Mud1.

The Parenteau comparisons add a second layer. Young CR cells reuse a starvation-like intron program, but old CR cells do not. High-glucose aging is weakly starvation-like, while low-glucose aging is inversely related to the starvation program. That means CR is not just “starvation turned on harder.” Instead, the cell’s interpretation of low glucose changes with age. My interpretation is:

Young cells enter a controlled, adaptive starvation/CR splicing program. Old high-glucose cells drift into a starvation-like stress program. Old CR cells avoid or invert that drift, but this protective rerouting requires Mud1.

So what is happening in the cell?

Aging pushes the RNA-processing system toward intron leakage. Under normal NMD, much of that leakage is hidden because the bad RNA is degraded. CR normally counters this by creating a Mud1-supported splicing state that protects vulnerable introns from entering the leak-and-decay pathway. Mud1 likely helps early intron recognition or commitment, especially for introns with demanding geometry. When Mud1 is missing, CR can no longer stabilize this state. The result is that low glucose no longer gives a full lifespan benefit, and the cell accumulates NMD-revealed leakage in a specific subset of introns.

What is newly learned:

1. Mud1 is a conditional CR-longevity factor, not just a spliceosome component.
The lifespan interaction says Mud1 matters specifically for the CR benefit.

2. CR suppresses intron leakage through an RNA-quality-control-visible pathway.
The NMD-off effect shows the relevant RNAs are being exposed to NMD, not merely retained invisibly in the nucleus.

3. The vulnerable class has structure.
Longer introns and longer 5′SS-to-branchpoint distances become especially vulnerable in CR-aged mud1Δ cells.

4. Aging, CR, and starvation are separable splicing states.
Young CR resembles starvation. Old CR does not. High-glucose aging partially resembles starvation. So the cell has multiple intron-remodeling modes, not one generic “stress splicing” mode.

5. The effect is targeted, not a global splicing collapse.
The functional-category plots show many introns barely move, with medians near zero, while selected mitochondrial/respiration and candidate introns move strongly. That makes the story more publishable: this is regulated remodeling, not nonspecific RNA-seq chaos.

The cleanest model is:

CR normally induces a Mud1-dependent protective spliceosome state that prevents age-associated leakage of architecturally vulnerable introns. In old cells, Mud1 becomes necessary to keep CR beneficial. Without Mud1, CR fails to suppress leak-and-decay substrates, especially long/5′SS-branchpoint-challenging introns, and the lifespan benefit collapses.
