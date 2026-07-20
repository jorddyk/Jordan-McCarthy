# JM105 HGPS + metazoan CR conservation pipeline

## Strategic question

This workflow tests a two-arm conservation model without defining physiological aging as damage or abnormality:

1. **Nuclear-architecture arm:** HGPS-derived fibroblasts are used as a sensitized perturbation of nuclear organization. The pipeline asks whether they show greater exposure of intron-containing RNA and whether progerin-linked interventions move that state toward control.
2. **Intervention arm:** bona fide mouse caloric restriction is used to ask whether dietary restriction suppresses the same prespecified pre-mRNA exposure metric in a metazoan.

HGPS is not used as evidence that caloric restriction works in humans, and it is not treated as equivalent to normal chronological aging.

## Primary metric

For each representative protein-coding intron:

```text
PEI = log2((EI + IE + 0.5) / (2 × S + 0.5))
```

- `EI`: unique read names spanning the upstream exon–intron boundary without a splice.
- `IE`: unique read names spanning the intron–downstream exon boundary without a splice.
- `S`: unique read names carrying the annotated exon–exon splice junction.

Interior intronic read density is retained as a secondary validation measure.

This is called **pre-mRNA exposure** or **intron-containing RNA exposure**. Whole-cell RNA-seq does not prove export, translation or NMD degradation.

## Prespecified datasets

- `GSE118633`: 2 control versus 3 HGPS RNA-seq samples, total/rRNA-depleted discovery/validation.
- `GSE137083`: normal control, HGPS control, pan-PML knockdown, PML2 knockdown, and lonafarnib plus zoledronate.
- `GSE222163` / `PRJNA918398`: control versus caloric restriction in mouse brown adipose tissue and skeletal muscle; exercise-containing groups are excluded.

The script resolves GEO and SRA metadata at runtime and fails before downloading if the expected groups cannot be recovered.

The Euler launcher executes `run_hgps_metazoan_conservation_manifest_hotfix.py`, a narrow wrapper that records the evidence-backed GSE118633 replicate count and resolves GSE222163 through `PRJNA918398` before entering the unchanged canonical analysis.

## Outputs

```text
work/
  metadata/
    run_manifest.tsv
    manifest_gate.tsv
  alignment/
  quantification/
  results/
    GATE_REPORT.md
    sample_pre_mrna_exposure_scores.tsv
    contrast_summary.tsv
    alignment_qc.tsv
    all_intron_measurements.parquet
    contrasts/*.per_intron.tsv
```

Raw FASTQ, BAM, STAR indices, logs and caches remain under Euler scratch and are not repository artifacts.

## One-command Windows execution

Run the companion PowerShell uploader from the extracted bundle. It uploads the complete bundle and submits one Slurm job.

## Main-figure gate

A main Figure 5 human/metazoan arm is supported only when:

1. the HGPS-associated direction replicates;
2. at least one HGPS intervention moves PEI toward control; and
3. at least one bona fide metazoan CR tissue reduces PEI.

Until those gates pass, this package produces tables and a written report only. It does not render a manuscript figure or insert `NO DATA` panels.

## JM105 manuscript definitions retained

```text
NMD_hidden = IR(upf1Δ) − IR(UPF1+)
candidate_score = min(aging_effect, CR_suppression)
Panel F contrast = computed (+MUD1 CR-suppression) versus
                   (mud1Δ CR-suppression), with data-driven y-limits.
```

These definitions are not recalculated in this public human/mouse workflow.
