# JM105 transformation-protocol RNA-seq

Purpose: recover and preserve the workflow that produced the plain four-column deliverable for the transformation-protocol samples.

## Human deliverable

Excel/CSV table with:

```text
Gene, LOG, PEG, AFTER_HS, 2H_RECOVERY
```

Values are transcript abundance relative to housekeeping gene `TFC1`, after read-depth/count normalization where applicable.

## Real-data provenance from project history

- Euler user: `jmccarthy`
- Sample subset: JM62-JM73, 12 samples
- Conditions: `LOG`, `PEG`, `AFTER_HS`, `2H_RECOVERY`
- Housekeeping gene: `TFC1` (`YBR123C`)
- Reported output: 6,613 genes
- Reported TFC1 TPM CV across 12 samples: 23.06%
- Windows destination used historically: `Y:\Jordan\JM105 Total RNA Seq on Mud1 deletes in aging and caloric restriction\Transformation Protocol RNA Seq`

## Imported code

```text
resolve-fastq-files.py
transformation-protocol-samples.tsv
run-transformation-expression.sbatch
check-transformation-job.ps1
```

## Source files still targeted for import

Exact source was found locally in `/mnt/data/JM105_Transformation_Protocol_Pipeline/`, but the following files still need to be imported as complete text source:

```text
01_JM105_Upload_And_Submit.ps1
02_JM105_Download_Results.ps1
JM105_run_transformation_expression.sh
JM105_build_relative_abundance_excel.py
README_JM105_Transformation_Protocol.txt
```

Binary/generated files deliberately not committed:

```text
JM105_Transformation_Protocol_Relative_Transcript_Abundance_TEMPLATE.xlsx
JM105_Transformation_Protocol_Relative_Transcript_Abundance.xlsx
JM105_Transformation_Protocol_Relative_Transcript_Abundance.csv
```

## Scientific status

This workflow is real JM105 RNA-seq support code. It does not generate fake biological data.
