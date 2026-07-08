# Intronsaurus browser legacy patch helpers

This folder stores exact small helper scripts and patch layers recovered from legacy Intronsaurus browser build conversations. These files are organized by what they do, not by daily handoff date.

## vNext3AH-fix9 scientific-wording/dino patch

Recovered from the ChatGPT JM105/Intronsaurus conversation around the vNext3AH-fix9 website update. The fix9 pass changed user-facing scientific wording and the dinosaur mascot after test-user feedback.

Imported files:

- `upload-prebuilt-scientific-wording-dino-v3ah-fix9.ps1` — uploads the prebuilt vNext3AH-fix9 archive to Euler and unpacks it.
- `retrieve-scientific-wording-dino-v3ah-fix9.ps1` — retrieves and opens the vNext3AH-fix9 archive from Euler.
- `check-scientific-wording-dino-v3ah-fix9-status.sh` — checks the Euler output folder and validation report.

Not imported here:

- `147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz` — generated website archive; deliberately not committed as a large binary output.
- `build_scientific_wording_dino_v3AH_fix9_reference.py` — exact source recovered in the local code bundle, but it is a reference patch script against a sandbox-prepared HTML archive, not the newest full Intronsaurus builder. Kept as a source-recovery target in `docs/legacy-code-backfill.md` rather than promoted as canonical full builder.

Scientific/data status: these helpers do not generate biological data. They operate on the Intronsaurus browser archive and preserve the project guardrails: no fake biological data, no unsupported CR/starvation equivalence, and clear distinction between RNA and protein abundance.

## vNext3AH-fix28 Gene Stories source/provenance patch

Recovered from the current Intronsaurus website repair conversation and the exact standalone artifact:

```text
/mnt/data/intronsaurus_fix28_gene_story_sources/Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html
```

Imported file:

- `vnext3ah-fix28-gene-story-sources-patch.html` — exact CSS/JavaScript patch layer that removes duplicate one-row Gene Stories labels and adds a collapsible source/provenance box explaining the embedded data fields and deterministic log2 fold-change calculation.

Not imported here:

- `Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html` and the matching ZIP — generated standalone website artifact with embedded processed data and a long patch chain. It is deliberately not committed as a large generated HTML/data artifact.
- Rejected or unstable CR-tab visual experiments from fix23–fix27 are not promoted as canonical source. Only the exact fix28 Gene Stories duplicate-label/provenance patch was imported from that chain.

Scientific/data status: this patch does not create biological values. It documents that Gene Stories reads static embedded JSON (`PAYLOAD.stories[].metric_json`, `PAYLOAD.stories[].sun_metric_json`, and condition tables under `DATA.geneExpression.hostExpressionAllConditions`) and either displays stored values or computes deterministic log2 ratios from stored CPM values. It keeps RNA/host transcript abundance distinct from Sun et al. protein abundance.
