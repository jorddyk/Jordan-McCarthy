# JM105 Figure 2B common-name and candidate-audit correction — 2026-07-14

## Canonical rule

The JM105 rendering operating standard requires visible figure labels to use standard/common gene names only. Systematic ORF IDs may appear in source TSVs, audits, and provenance manifests, but not visibly on a figure unless no standard name exists and Jordan explicitly allows the systematic ID.

## What the successful renderer reported

Visible label list:

```text
SRB2, YSF3, BET1, RPL42B, ATG38, RPS24A
```

These six are common names. The systematic identifiers printed in the long terminal table came from provenance columns such as `display_gene`, `systematic_gene`, `name`, `parent`, and `intron_label`. Their presence in the TSV is allowed and is not evidence that they were visible on the rendered panel.

The SVG and white preview still require direct inspection before acceptance.

## Audit bug

The ad hoc audit reported that none of the six visible labels matched the obvious identifier columns. That conclusion was invalid because the audit omitted the existing `standard_gene_name` column from its identifier search. The renderer code uses `standard_gene_name` and `label_text` for visible labels.

Future name audits must inspect at least:

```text
standard_gene_name
label_text
visible_gene_label
systematic_orf
```

and must parse actual SVG text nodes for forbidden systematic IDs.

## Candidate-count interpretation correction

The rendered plot-source TSV contains 284 strict-universe rows and 49 rows with `candidate_passed_strict=True`.

The previously stated `n=2` was not the full strict candidate set. It is the number of rows that both pass the stored strict gate and exceed the additional thresholds:

```text
aging_effect > 0.15
CR_suppression > 0.15
```

The three rows above those thresholds are:

```text
YHR041C / SRB2   candidate_passed_strict=True
YIL111W / COX5B  candidate_passed_strict=False
YNL138W-A         candidate_passed_strict=True
```

Correct terminology:

```text
strict selected set = 49
high-effect threshold set = 3
high-effect threshold set also passing strict gate = 2
```

Future chats must not call the two high-effect rows the full strict candidate set.

## Acceptance requirement

Before accepting Panel B:

1. Parse SVG text nodes and fail if any visible systematic ORF ID is present.
2. Inspect the white preview directly.
3. Confirm every visible gene label against the common-name audit TSV.
4. Retain systematic IDs only in provenance outputs.
