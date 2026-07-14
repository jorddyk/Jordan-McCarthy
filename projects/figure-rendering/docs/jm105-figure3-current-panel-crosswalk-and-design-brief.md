# JM105 Figure 3 current-panel crosswalk and redesign brief

Date: 2026-07-14
Status: starting brief for the next Figure 3 chat; source and panel-role crosswalk must be confirmed after the current PowerPoint and Yves flow are uploaded there.

## Current PowerPoint identity baseline

Current Figure 3 title:

> Mud1 is required for caloric restriction to suppress age-linked intron leakage

Current eight panel identities:

| Current PPT panel | Current title | Current visual job |
|---|---|---|
| A | mud1Δ weakens the CR lifespan benefit | phenotype/lifespan context |
| B | CR suppression is reduced without Mud1 | set-level paired +MUD1 versus mud1Δ suppression comparison |
| C | Most selected introns suppress better with Mud1 | direct candidate-level +MUD1 versus mud1Δ scatter |
| D | Candidate-by-candidate CR responses reveal Mud1 dependence | candidate paired-response detail |
| E | Ranking introns by Mud1-dependent CR suppression | ranked effect detail |
| F | Representative introns lose CR suppression in mud1Δ | representative NMD-hidden profiles |
| G | Host RNA abundance does not explain the intron effect | expression/host-RNA control |
| H | mud1Δ does not cause gross cell-cycle slowing | phenotype/control panel |

The current slide uses eight near-equal rounded boxes. This equal weighting is a likely hierarchy problem, but panel identity and source provenance remain authoritative until a crosswalk is approved.

## Current measured PowerPoint slots

The current 13.333 × 7.5 inch slide uses approximately these normalized panel boxes:

| Panel | x | y | width | height |
|---|---:|---:|---:|---:|
| A | 0.0115 | 0.1273 | 0.2345 | 0.2924 |
| B | 0.2563 | 0.1273 | 0.2314 | 0.4036 |
| C | 0.5000 | 0.1273 | 0.2330 | 0.4015 |
| D | 0.7433 | 0.1273 | 0.2534 | 0.4036 |
| E | 0.0115 | 0.4751 | 0.2361 | 0.4851 |
| F | 0.2621 | 0.5471 | 0.2306 | 0.4131 |
| G | 0.5050 | 0.5471 | 0.2288 | 0.4131 |
| H | 0.7433 | 0.5475 | 0.2334 | 0.4127 |

These coordinates are a current-layout audit, not a required final layout.

## Google Drive acceptance-matrix roles

The current Drive matrix assigns:

- A: biological relevance/lifespan context;
- B: Figure 3 hero, set-level +MUD1 versus mud1Δ suppression comparison;
- C: broad candidate-by-candidate suppression comparison;
- D: ranked support/detail;
- E: representative condition profiles;
- F: selected-subset coherence scatter;
- G: host-RNA abundance control;
- H: cell-cycle/growth control.

The PowerPoint and matrix letters do not align cleanly for C–F. Future work must match analyses by biology and source, not by letter alone.

## Locked Figure 3 metric

```text
NMD_hidden = IR(upf1Δ) − IR(UPF1+)

CR_suppression(genotype)
= NMD_hidden(old 2%, genotype)
− NMD_hidden(old 0.1% CR, genotype)

Mud1-dependent CR suppression
= CR_suppression(+MUD1)
− CR_suppression(mud1Δ)
```

Figure 3 should publicly use Mud1-dependent CR suppression, not `candidate_score`.

## Design hypothesis to test

A prior critique correctly identifies that the present figure reads as many co-equal analyses rather than one causal test. Treat the following as a hypothesis to validate against source coverage and Yves flow:

1. Make the direct candidate-level +MUD1 versus mud1Δ CR-suppression comparison the largest hero panel, with a y=x diagonal.
2. Fold the sign count, median difference, paired p value, and exact n into a right-stat inset when they derive from the same points.
3. Keep one candidate-detail view full size; demote the redundant ranking to a narrow strip or supplement while exporting the full table.
4. Use 3–4 representative introns for the example panel, with identical condition order and source-secure raw/NMD-hidden values.
5. Make host-RNA and cell-cycle controls visibly subordinate.
6. Keep lifespan context smaller than the RNA-seq hero.
7. Compare at least two measured composite layouts before rendering.

No analysis may be silently deleted. Merged or demoted analyses must remain represented as an inset, audit/table, or explicitly proposed supplement.

## Required crosswalk before rendering

The next chat must produce a table with:

```text
current PowerPoint letter
authoritative current title
current visual/analysis type
Drive matrix claim
Yves-flow role
proposed new letter/role
keep / merge as inset / demote / supplement
source table/workbook
```

The Figure 3 renderer may not proceed until this crosswalk, the source manifest, and the main/supplement hierarchy are locked.