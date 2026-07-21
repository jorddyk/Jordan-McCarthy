# Materials and Methods

*JM105 / Intronsaurus Nature Aging manuscript — living panel-by-panel methods register*


## Document scope and status

This living document is the manuscript methods source of truth for every panel of every main and extended-data figure. Methods are entered only from accessible canonical code, verified experimental records, or reviewed analysis outputs. No missing biological method is reconstructed from memory. The current entry covers the human HGPS and mouse caloric-restriction conservation figure; Figures 1–4 remain intentionally unfilled until their exact panel sources are audited.


## Manuscript-wide definitions and claim boundaries

The yeast JM105 work distinguishes raw retained-intron signal from NMD-hidden signal. NMD_hidden is defined as IR(upf1Δ) − IR(UPF1+). The candidate score is defined as min(aging_effect, CR_suppression). For the JM105 Mud1 panel, the Panel F contrast is computed as the +MUD1 CR-suppression value versus the mud1Δ CR-suppression value, with y-axis limits derived from the computed values rather than hard-coded. Figure 2 is restricted to total or rRNA-depleted JM105 data; poly-A, P-versus-T, mRNA-like and P−T constructs are outside that figure’s scope.

The public human and mouse datasets used below do not contain matched UPF1+ and upf1Δ conditions. They therefore measure steady-state intron-containing or incompletely processed RNA exposure. They do not directly establish nuclear export, translation, or degradation by nonsense-mediated decay, and they cannot be labelled NMD-hidden leakage.


## Figure 1

Methods not yet entered. Exact panel sources must be audited before text is added.


## Figure 2

Methods not yet entered. Scope is locked to total or rRNA-depleted JM105 data only.


## Figure 3

Methods not yet entered. Exact Mud1 panel sources must be audited before text is added.


## Figure 4

Methods not yet entered. Exact substrate and mechanistic panel sources must be audited before text is added.


## Figure 5 — human HGPS and metazoan caloric-restriction conservation


### Figure 5A — study design and dataset selection

The analysis tested two complementary conservation arms without treating Hutchinson–Gilford progeria syndrome (HGPS) as equivalent to physiological aging. The human nuclear-architecture arm asked whether HGPS fibroblasts showed increased intron-containing RNA exposure and whether progerin- or PML-linked interventions moved that state toward control. The intervention arm asked whether bona fide caloric restriction reduced the same prespecified junction-defined metric in mouse tissues.

Three public RNA-seq studies were prespecified. GSE118633 contributed two control and three HGPS human fibroblast RNA-seq runs. GSE137083 contributed three biological replicates each of normal control fibroblasts, untreated HGPS fibroblasts, HGPS fibroblasts after pan-PML knockdown, HGPS fibroblasts after PML2 knockdown, and HGPS fibroblasts treated with lonafarnib plus zoledronate. GSE222163 contributed mouse brown adipose tissue controls (n=3), brown adipose tissue under caloric restriction (n=4), skeletal-muscle controls (n=4), and skeletal muscle under caloric restriction (n=3). Exercise-only and combined exercise-plus-caloric-restriction groups were excluded by the prespecified classifier.

GEO sample metadata and SRA run metadata were resolved programmatically. The manifest was required to recover exactly 34 runs with the expected dataset, group and species assignments before distributed processing could begin. GSE222163 SRA metadata were resolved through BioProject PRJNA918398. Public control titles with replicate suffixes, such as control1, were accepted explicitly.


### Figure 5B — independent human HGPS replication

The primary human comparisons were HGPS versus control in GSE118633 and untreated HGPS versus normal control in GSE137083. For each comparison, a fixed intron universe was defined by requiring a non-missing JM105_IR value in every included run and a maximum raw support of at least 10 informative events in at least one sample. The sample-level score was the median JM105_IR across that fixed universe. Mean JM105_IR and median secondary PEI were retained as supporting summaries.

The prespecified HGPS direction was positive: mean sample-level median JM105_IR in HGPS was expected to exceed the corresponding control value. Replication was considered directionally successful only when both independent human comparisons had the expected sign. Directional gates were kept separate from P values and effect sizes.


### Figure 5C — HGPS intervention-direction tests

Within GSE137083, untreated HGPS fibroblasts were compared separately with HGPS fibroblasts treated with lonafarnib plus zoledronate, HGPS fibroblasts after PML2 knockdown, and HGPS fibroblasts after pan-PML knockdown. The prespecified intervention direction was negative, indicating movement of sample-level median JM105_IR toward the normal-control state. The fixed-universe and sample-score rules were identical to those used for the HGPS replication comparisons.


### Figure 5D — caloric restriction in mouse tissues

Mouse brown adipose tissue and skeletal muscle were analysed as separate tissue-specific contrasts. Caloric-restriction samples were compared with their matched tissue controls using the same representative-transcript intron set, junction-counting method and exact JM105_IR definition. The prespecified direction was a reduction in sample-level median JM105_IR under caloric restriction. A tissue-specific result was not generalized to all mammalian tissues.


### Figure 5E — per-intron convergence and ranked effects

For each prespecified contrast, intron-level JM105_IR values were compared between groups only when at least two finite replicate values were present in each group and the intron passed the fixed-universe support gate. The reported effect was group B minus group A. Welch’s unequal-variance t-test was used for each intron, Hedges’ g was calculated as a standardized effect size, and P values were adjusted within each contrast by the Benjamini–Hochberg procedure. The number of introns with false-discovery rate below 0.05 was reported, while the main directional gate remained based on the sample-level score.

Convergence analyses are intended to test whether introns or gene modules elevated in HGPS are preferentially shifted in the opposite direction by HGPS interventions and by caloric restriction. Exact one-to-one conservation of individual yeast and mammalian introns is not assumed because mammalian transcript architecture is substantially more complex. Orthology and functional-module analyses must be reported separately from the primary junction metric.


### Figure 5F — bounded synthesis model

The synthesis panel is a data-bounded model rather than an additional experiment. It may state that a junction-defined intron-containing RNA state is associated with a human nuclear-architecture perturbation and is modulated by intervention and caloric restriction only when the corresponding empirical gates pass. It must not claim that HGPS is normal aging or that the mammalian data demonstrate NMD-hidden leakage, nuclear export, translation, or a universal tissue response.


## Common computational methods for Figure 5


### Reference genomes and annotation

Species assignment was determined from the prespecified dataset manifest rather than inferred from read sequences. GSE118633 and GSE137083 were assigned to human; GSE222163 was assigned to mouse. Human reads were aligned to the GRCh38 primary assembly using GENCODE release 50 annotation. Mouse reads were aligned to the GRCm39 primary assembly using GENCODE M39 annotation. Separate STAR indices were generated and validated for each species, and each manifest row selected only the matching species-specific index and GTF.


### Representative protein-coding transcript and intron definition

Only protein-coding genes and protein-coding transcripts in the matching GENCODE GTF were considered. One representative transcript was selected per gene by prioritizing MANE Select, then APPRIS principal annotation, then coding-sequence length and total exon span. Exons were ordered in transcript direction, adjacent-exon intervals were converted to zero-based half-open intron coordinates, and introns shorter than 40 bp were excluded. The resulting representative intron table was frozen separately for human and mouse.


### Public-read acquisition and alignment

SRA objects were downloaded with SRA Toolkit prefetch using an unrestricted maximum-size setting and converted with fasterq-dump using split-file output and up to eight conversion threads. Reads were aligned with STAR 2.7.11b. The relevant STAR parameters were: coordinate-sorted BAM output; outSAMstrandField=intronMotif; outFilterMultimapNmax=20; alignSJoverhangMin=8; alignSJDBoverhangMin=1; outFilterMismatchNoverReadLmax=0.04; quantMode=GeneCounts; and limitBAMsortRAM=12,000,000,000. BAM files were indexed with samtools 1.21. STAR ReadsPerGene output was retained for host-gene expression sensitivity analyses.


### Name sorting and fragment-level deduplication

Each coordinate-sorted BAM was sorted by query name with samtools before intron quantification. All primary alignments sharing a query name were accumulated as one fragment. For a given intron, a query name could increment EI, IE or EE_total no more than once, so paired mates supporting the same event were not double-counted. Unmapped, secondary and supplementary alignments were excluded. PCR or optical duplicate flags were not explicitly removed by the quantifier.


### EI and IE boundary evidence

For every annotated intron, the lower genomic coordinate was stored as start0 and the higher coordinate as end0. A contiguous aligned block counted as boundary evidence only when it extended at least 8 aligned bases on both sides of the boundary. Operationally, a block spanning start0 contributed to EI and a block spanning end0 contributed to IE when block_start ≤ boundary − 8 and block_end ≥ boundary + 8. Spliced CIGAR N operations did not create unspliced boundary evidence because read.get_blocks() returns only contiguous aligned blocks.

The implementation names the lower-coordinate boundary EI and the higher-coordinate boundary IE on both strands. On minus-strand transcripts, these labels are reversed relative to transcriptional direction. This does not alter the primary metric because EI and IE enter only as their sum. When the two boundaries are presented separately, they should be described as lower-coordinate and higher-coordinate unspliced boundaries unless strand-aware relabelling is applied.


### EE_total exact splice-junction evidence

EE_total was derived directly from the CIGAR string. For each CIGAR N operation, the donor coordinate was the reference position immediately before the skipped interval and the acceptor coordinate was donor plus the skipped length. The query name contributed to EE_total only when this donor–acceptor pair exactly matched the annotated intron start0–end0 interval. Nearby or alternative junctions did not count for that intron.

The Python counter imposed no additional anchor-length threshold after reading the BAM. Anchor acceptance was therefore inherited from STAR. Novel junctions required alignSJoverhangMin=8, whereas annotated GENCODE junctions could use alignSJDBoverhangMin=1. Because EE_total tests exact junctions present in the supplied annotation, an annotated junction could in principle be represented with a 1-bp STAR anchor, whereas EI and IE each required 8 aligned bases on both sides.


### Primary and secondary intron metrics

For each intron and sample, unspliced boundary support was EI + IE and the exact primary metric was JM105_IR = (EI + IE) / ((EI + IE) + 2 × EE_total). No pseudocount was used. A zero denominator was assigned missing rather than zero. The factor of two places the single exon–exon splice-junction count on the same two-boundary scale as EI + IE.

The secondary sensitivity metric was PEI = log2[(EI + IE + 0.5)/(2 × EE_total + 0.5)]. PEI was retained for numerical stability and sensitivity analysis but was not the primary cross-species effect scale.


### Multimapping and mapping-quality boundary

STAR permitted up to 20 reported mapping locations. The quantifier excluded secondary alignments but did not require NH=1 or impose a MAPQ threshold, so the retained primary record of a multimapping fragment could contribute. Before manuscript submission, the principal conclusions should be re-tested using uniquely mapped fragments only and should be reported as a sensitivity analysis rather than silently changing the primary implementation.


### Sample-level and statistical summaries

Within each contrast, sample-level median JM105_IR values were compared using Welch’s unequal-variance t-test and a two-sided Mann–Whitney U test. Hedges’ g was reported as the standardized effect size. For per-intron tests, Welch’s test and Benjamini–Hochberg false-discovery-rate correction were applied within each contrast. The prespecified directional gate was determined from the sign of the difference between group means of the sample-level median JM105_IR values and was not treated as equivalent to statistical significance.


### Quality control and publication sensitivity analyses

STAR alignment summaries were retained for every sample, including input-read, unique-mapping, multimapping, mismatch and splice-junction metrics available in Log.final.out. Every sample received a completion marker containing the BAM and quantification checksums. Publication-level review should include replicate outlier inspection, leave-one-replicate-out stability, comparison with host-gene counts, uniquely mapped-fragment analysis, and boundary-flank sensitivity at 6, 8 and 10 bp. Conclusions should be retained only when their direction is not dependent on a single sample or one permissive mapping choice.


### Software and distributed execution

The environment used Python 3.11, pandas 2.2, NumPy 2.1, SciPy 1.15, pysam 0.23, STAR 2.7.11b, samtools 1.21 and SRA Toolkit 3.2.1. Human and mouse reference jobs ran in parallel. Thirty-four sample tasks were submitted as a Slurm array with at most six concurrent tasks, followed by a dependency-controlled aggregate job. The quantifier scanned each name-sorted BAM once and counted all representative introns in one pass.


### Computational provenance and interrupted-run note

In the initial distributed execution, 31 of 34 sample tasks completed. Tasks 1, 5 and 33 exited before public-read download or biological analysis because concurrent micromamba run processes contended for the same home-directory process lock. The aggregate job was consequently cancelled by its after-success dependency. The repair replaced micromamba run inside array tasks with direct invocation of the already-created environment Python executable, reran only tasks 1, 5 and 33, and submitted a new aggregate job dependent on those repairs. This event did not alter read data, alignment parameters, intron definitions, counting logic or biological values.


## Extended Data figures

Methods will be added panel by panel after the corresponding final panel sources and numerical inputs are verified.
