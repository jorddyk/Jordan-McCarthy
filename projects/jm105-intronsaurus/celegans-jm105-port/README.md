# JM105–C. elegans conservation analysis

This working branch tests whether the JM105 logic extends from budding yeast to a metazoan without framing aging as damage, abnormality, failure, or collapse.

## Central model

Aging changes spliceosome allocation and the RNA fate of selected intron-containing transcripts. Some pre-mRNAs become detectable outside the nucleus and are normally concealed by cytoplasmic nonsense-mediated decay. Dietary restriction can shift this allocation state and suppress the age-linked NMD-hidden retained-intron signal. RNP-2, the C. elegans U1A ortholog and direct functional counterpart of yeast Mud1, is tested as the conserved genetic handle.

## Frozen sign conventions

- `IRratio = (intron_count + 1) / (host_exon_count + 1)` for replicate-level visualization.
- `NMD_hidden = IR(NMD off) - IR(matched NMD on)`.
- `age_linked_NMD_hidden = NMD_hidden(old) - NMD_hidden(young)`.
- `CR_suppression = age_linked_NMD_hidden(control diet) - age_linked_NMD_hidden(DR)`.
- `RNP2_dependent_CR_suppression = CR_suppression(RNP-2+) - CR_suppression(rnp-2 perturbed)`.

A positive final quantity means RNP-2 is required or permissive for full dietary-restriction suppression, matching the JM105 Mud1 logic.

## Current status

Step 1 audits public repositories and produces a run-level capability matrix before any FASTQ download. It explicitly tests whether public datasets contain the cells required for NMD-hidden IR, age linkage, dietary-restriction suppression, RNP-2 dependency, and cytoplasmic localization.

See:

- `analysis-plan.md`
- `step01-metadata-audit/`
