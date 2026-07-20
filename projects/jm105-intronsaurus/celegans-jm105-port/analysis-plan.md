# Worm Figure 5 and analysis plan

## Figure 5 headline

**Dietary restriction remodels an RNP-2-dependent, NMD-hidden intron-leakage state across eukaryotes**

The figure is organized around regulated spliceosome allocation, not aging damage. NMD is the detector of cytoplasm-accessible intron-containing RNA; it is not presented as the cause of leakage.

## Intended final panel architecture

### 5A — Conserved contrast logic

Show the matched yeast and worm definitions:

1. NMD-hidden retained-intron signal.
2. Age-linked change in that hidden signal.
3. Dietary-restriction suppression of the age-linked signal.
4. Mud1/RNP-2 dependence of dietary-restriction suppression.

### 5B — Aging changes the NMD-hidden intron state in worms

Use intron counts normalized with host-exon-derived size factors and the same JM105 sign orientation. Show the full distribution plus biologically coherent intron classes; do not reduce the conclusion to a global burden score alone.

### 5C — Dietary restriction suppresses the age-linked state

Estimate the age × diet × NMD interaction. The main visual should show that dietary restriction changes the NMD-hidden retained-intron trajectory with age.

### 5D — RNP-2 is the conserved genetic handle

Estimate the age × diet × NMD × RNP-2 interaction. The matched JM105 prediction is that loss of RNP-2 weakens or abolishes dietary-restriction suppression. RNP-2 deletion is not assumed to be the suppressive intervention.

### 5E — Cytoplasmic accessibility of the retained-intron transcripts

Use matched nuclear and cytoplasmic RNA where available. Public fractionated RNA-seq can define a cytoplasm-accessible intron set, but the strongest version is matched cytoplasmic RNA-seq in the definitive worm factorial. Show that age-linked NMD-hidden events are enriched in the cytoplasmic fraction rather than merely abundant in whole-worm RNA.

### 5F — Positive-sum cross-species model

Aging changes spliceosome allocation and partitions selected intron-containing transcripts among fully spliced, nuclear-retained, and cytoplasm-accessible/NMD-hidden RNA fates. Dietary restriction shifts this allocation. Mud1 in yeast and RNP-2 in worms provide homologous U1-associated genetic handles, while species-specific substrate sets remain allowed.

## Why this is editorially strong

- Nutrition and metabolism: a genuine dietary-restriction mechanism is central rather than appended.
- RNA surveillance and proteostasis: NMD reveals a normally concealed RNA-fate state and direct SMG-2 evidence establishes surveillance engagement.
- Comparative aging: the same quantitative contrast is tested in yeast and a metazoan without requiring identical introns or pretending the organisms regulate every substrate identically.
- Broad conceptual advance: observed aging transcriptomes are filtered outputs of spliceosome allocation, nuclear export, and NMD.

## Step-by-step execution

### Step 0 — Freeze the claim and signs

Use the definitions in the repository README. Forbidden framing includes aging as damage, abnormality, failure, collapse, or generic loss of fidelity. Preferred language is spliceosome allocation, intron-containing RNA fate, cytoplasmic accessibility, leakage, and NMD-hidden signal.

### Step 1 — Audit public accessions and contrast capability

Resolve every candidate GEO, SRA, DDBJ, and BioProject accession. Capture raw run metadata, read layout, read length, library selection, raw FASTQ availability, age, diet, NMD state, RNP-2 state, and nuclear/cytoplasmic fraction. Produce an explicit matrix showing which JM105 contrasts are estimable within each study. No FASTQ is downloaded in this step.

### Step 2 — Recover the exact JM105 quantification implementation

Locate the current canonical JM105 intron/exon counting code, exon-derived DESeq2 size factors, filters, NMD-hidden contrasts, and figure source tables. Any unavailable historical code must be marked as a documented reimplementation rather than presented as recovered original code.

### Step 3 — Build one stable worm reference and strict intron universe

Use one recorded WormBase release. Construct gene exons, strict introns, permissive introns, splice junctions, transcript-to-gene mapping, operon annotations, trans-splice annotations, mappability, and yeast–worm orthology. Exclude ambiguous intron/exon overlaps from the primary universe.

### Step 4 — Pilot each library class

Pilot one sample from each distinct library architecture. Infer strandedness, read length, insert structure, junction yield, rRNA fraction, unique mapping, gene-body coverage, and intronic fraction. Do not combine paired-end and short single-end libraries blindly.

### Step 5 — Align and count with JM105-compatible logic

Generate host-exon counts, strict-intron counts, exon–intron boundary counts, intron–exon boundary counts, and spliced-junction counts. Derive normalization from host-exon counts and freeze it before applying it to introns.

For visualization only:

`IRratio = (intron_count + 1) / (host_exon_count + 1)`

For inference, use raw counts with the recovered JM105-compatible count model and exon-derived normalization.

### Step 6 — Establish worm NMD-hidden IR

Within each matched NMD study calculate:

`NMD_hidden = IR(NMD off) - IR(NMD on)`

Use SMG-2/UPF1 perturbation as the primary detector. Validate directness with SMG-2 association and independent NMD-null datasets. Keep whole-worm, poly(A), total, and fractionated libraries separate.

### Step 7 — Establish the aging-linked worm state

Use replicated adult aging RNA-seq to estimate old-minus-young or an age slope for each intron. Test whether age-increasing IR events are preferentially NMD hidden in independent NMD datasets. This is triangulation unless age and NMD were manipulated in the same study.

### Step 8 — Test dietary-restriction suppression

In the best supported diet × NMD dataset calculate:

`DR_x_NMD = (NMDoff - NMDon)_DR - (NMDoff - NMDon)_control`

For an age-linked candidate set, a negative interaction is consistent with dietary restriction suppressing the NMD-hidden state. Model each study separately and integrate effects by rank, direction, and meta-analysis rather than subtracting normalized values across studies.

### Step 9 — Test RNP-2 dependency

RNP-2 is the worm U1A ortholog corresponding to yeast Mud1. The decisive contrast is:

`RNP2_dependent_CR_suppression = CR_suppression(RNP-2+) - CR_suppression(rnp-2 perturbed)`

Public GSE113301 must first pass the mRNA/junction-read gate; its published emphasis is small RNA. If no public age × diet × NMD × RNP-2 matrix exists, the public reanalysis becomes discovery and the definitive panel requires a targeted worm experiment.

Because RNP-2 and RNP-3 can compensate for each other, include RNP-3 as a biological specificity/redundancy control. A modest rnp-2 single-mutant effect does not by itself falsify a conserved U1 allocation mechanism.

### Step 10 — Establish cytoplasmic leakage

Use public nuclear/cytoplasmic RNA-seq to predefine cytoplasm-accessible retained introns. The definitive experiment should sequence matched total and cytoplasmic rRNA-depleted RNA from the core factorial. Require enrichment of intron-containing RNA in cytoplasm plus NMD-dependent stabilization before using the strongest leakage language.

### Step 11 — Cross-species integration

Compare:

- effect directions under age, diet, NMD, and Mud1/RNP-2 perturbation;
- one-to-one ortholog host genes;
- pathway and transcript-class enrichment;
- intron length and splice-site architecture;
- ribosomal, mitochondrial, proteostasis, and RNA-processing modules;
- candidate-score concordance.

Do not require exact intron identity for conservation. Preserve both shared and species-specific allocation programmes.

### Step 12 — Promotion gate for the main figure

Promote the worm analysis to main Figure 5 when:

1. age changes a reproducible retained-intron state;
2. the relevant events are NMD hidden;
3. dietary restriction shifts the state in the JM105-consistent direction;
4. the shift is weakened in rnp-2 perturbation or a justified RNP-2/RNP-3 allocation perturbation;
5. cytoplasmic accessibility is supported;
6. results survive host-expression, read-architecture, annotation, and leave-one-replicate-out controls;
7. cross-species convergence is present at gene, pathway, transcript class, or intron-feature level.

## Definitive new worm design if the public factorial is absent

Use total/rRNA-depleted RNA-seq and matched cytoplasmic RNA-seq with biological replication across:

- young and old adults;
- control diet and dietary restriction;
- NMD on and `smg-2` off;
- RNP-2+ and `rnp-2` loss.

This is the direct worm analogue of JM105. A staged design can first establish age × diet × NMD in RNP-2+ animals, then test RNP-2 dependency in old adults to reduce library count while preserving the decisive interaction.
