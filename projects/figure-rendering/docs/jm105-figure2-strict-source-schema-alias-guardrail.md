# JM105 Figure 2 strict-source schema alias guardrail

Date: 2026-07-14

## Failure observed

The Figure 2 v3.2 Euler render failed before plotting because the renderer required the enriched columns `standard_gene_name` and `systematic_orf`, while the raw strict source table contained the equivalent raw/provenance fields `display_gene`, `systematic_gene`, `name`, `parent`, and `intron_label` but not the enriched aliases.

This was a renderer/source-contract mismatch, not a biological-data failure.

## Immediate safe recovery

Use the already-confirmed enriched strict-universe table produced by the mature Panel B renderer:

`/cluster/home/jmccarthy/JM105_Figure2_v2_render_20260714_133954/out/B_retry_with_arguments/Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv`

This table contains:

- 284 strict eligible nuclear introns;
- `candidate_passed_strict`;
- all gate columns;
- `systematic_orf`;
- `standard_gene_name`;
- the same aging-effect and CR-suppression values;
- no mitochondrial rows in the strict universe.

Validated counts are 284 strict universe, 64 aging-linked, 53 aging-linked and CR-suppressed, and 49 locked candidates.

## Permanent rule

1. Never require an enriched alias column from a raw source table unless the renderer explicitly performs and audits the normalization.
2. Before rendering, print and verify the actual source schema against the renderer's declared contract.
3. A source adapter must map raw identifiers to canonical fields explicitly. For this source family:
   - `systematic_orf` may be extracted from `display_gene`, `systematic_gene`, `name`, `parent`, or `intron_label` using the yeast ORF pattern;
   - `standard_gene_name` must come from an audited common-name map, never from an unverified guess.
4. Until the adapter is canonicalized, use the confirmed enriched strict-universe export rather than silently fabricating aliases.
5. Visible labels remain common names only. Systematic ORFs remain provenance fields.
6. Run the full A-F renderer locally or in a controlled preflight against the exact chosen schema before launching it on Euler.

## Do not repeat

- Do not assume a derived enriched table and its raw parent have identical columns.
- Do not declare a package validated after testing it only against a different schema.
- Do not respond to a schema error by weakening the common-name rule.
- Do not recompute the strict candidate set from loose thresholds.
