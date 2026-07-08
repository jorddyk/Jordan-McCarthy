# CODE HANDOFF — 2026-07-08 Intronsaurus fix28 Gene Stories patch

## Repo

`jorddyk/Jordan-McCarthy`

## Branch

`main`

## Project area

JM105 / Intronsaurus browser.

## Human purpose

Continue the legacy code backfill by preserving the exact small source patch from the current Intronsaurus Gene Stories repair instead of committing the large generated standalone website artifact.

## Files created/updated

Created:

- `projects/jm105-intronsaurus/intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html`
- `docs/handoffs/2026-07-08-intronsaurus-fix28-code-handoff.md`

Updated:

- `projects/jm105-intronsaurus/intronsaurus-browser/patches/README.md`
- `projects/jm105-intronsaurus/README.md`
- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`

## Files deliberately not committed

- `Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html` and ZIP: generated standalone website artifact with embedded processed data and a long patch chain.
- Generated Intronsaurus HTML/archives from fix11–fix27.
- Rejected/unstable CR-tab visual experiments from fix23–fix27.
- Raw sequencing data, generated figure outputs, notebooks/logs, and large binary artifacts.

## Scientific/data status

The imported fix28 patch is UI/provenance code only. It does not create biological values, does not call an AI model, and does not invent fold changes.

It documents that Gene Stories values are read from static embedded JSON fields in the standalone site, especially:

```text
PAYLOAD.stories[].metric_json
PAYLOAD.stories[].sun_metric_json
DATA.geneExpression.hostExpressionAllConditions
```

For condition-matched rows, the browser uses deterministic log2 ratio logic:

```text
log2((condition A + 0.5) / (condition B + 0.5))
```

The patch keeps RNA/host transcript abundance distinct from Sun et al. protein abundance.

## Implementation notes

The imported source was recovered exactly from:

```text
/mnt/data/intronsaurus_fix28_gene_story_sources/Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html
```

Source marker:

```text
fix28: Gene stories duplicate-row labels + provenance note
```

The patch collapses duplicated one-row Gene Stories labels and inserts a collapsible “Where these values come from” drawer. It is a browser DOM patch, not the canonical full Intronsaurus builder.

## Final code paths

```text
projects/jm105-intronsaurus/intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html
projects/jm105-intronsaurus/intronsaurus-browser/patches/README.md
projects/jm105-intronsaurus/README.md
projects/jm105-intronsaurus/docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
```

## Legacy-backfill progress

This pass imported one exact small Intronsaurus browser patch layer and updated JM105 project docs/wiki. It did not import the full standalone site because the HTML is a generated artifact with embedded processed data; the correct next target remains the source builder that produces the site.

## Remaining source-recovery targets

```text
projects/jm105-intronsaurus/intronsaurus-browser/integrate-sun-matched-rna-protein-gene-stories.py
projects/jm105-intronsaurus/analysis/jm105-paired-gene-body-normalized-leakage-test.py
projects/jm105-intronsaurus/figures/jm105-synopsis-aligned-all-intron-rnaseq-plots.py
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/ exact source from PR #1/main reconciliation
projects/imagej-fiji-aging-chips/macros/ JM128/JM129 exact macro bodies
projects/language-learning/active-recall-apps/ complete HTML apps
```
