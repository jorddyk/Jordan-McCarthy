# 2026-07-08 Intronsaurus fix9 legacy code backfill handoff

Repo: `jorddyk/Jordan-McCarthy`
Branch: `main`
Project area: `projects/jm105-intronsaurus/intronsaurus-browser/`

## Human purpose

Recover exact useful helper code from the legacy Intronsaurus vNext3AH-fix9 scientific-wording/dino website pass, without committing generated browser archives or raw biological data.

## Files created

- `projects/jm105-intronsaurus/intronsaurus-browser/patches/README.md`
- `projects/jm105-intronsaurus/intronsaurus-browser/patches/upload-prebuilt-scientific-wording-dino-v3ah-fix9.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/patches/retrieve-scientific-wording-dino-v3ah-fix9.ps1`
- `projects/jm105-intronsaurus/intronsaurus-browser/patches/check-scientific-wording-dino-v3ah-fix9-status.sh`

## Files updated

- `projects/jm105-intronsaurus/README.md`

## Files deliberately not committed

- `147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz` — generated website archive / large binary output.
- `interactive/Intronsaurus_Explore_Restored_vNext3AH_fix9.html` — generated 89 MB browser artifact.
- `build_scientific_wording_dino_v3AH_fix9_reference.py` — exact recovered reference patch source exists in the local code bundle, but it patches a sandbox-prepared HTML archive and is not the newest full Intronsaurus builder. It remains documented as a recovery/reference target rather than promoted as canonical current builder code.

## Scientific/data status

The imported files are deployment/retrieval/status helpers only. They do not generate biological data. They preserve existing guardrails: no fake biological data, no raw sequencing/microscopy files, clear distinction between RNA abundance and protein abundance, and no claim that caloric restriction is starvation.

## Implementation notes

This pass used exact source recovered from `/mnt/data/Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9_code_bundle.zip`. The vNext3AH-fix9 archive had previously validated on Euler with flags including `FIX9_SCIENTIFIC_WORDING_APPLIED=True`, `DINO_REPLACED=True`, `HEADER_CR_DEFINED=True`, `HEADER_NMD_DEFINED=True`, `MUD1P_REMOVED=True`, `POLYA_PROCESSED_POOL_WORDING_PRESENT=True`, and `MRNA_LIKE_PHRASE_REMOVED=True`.

The connector was used to verify the repo exists, is private, and is writable before committing.

## Remaining source-recovery targets

- Current full Intronsaurus browser builders/patch chains, especially newer versions already referenced in repo docs.
- Exact ImageJ/Fiji aging-chip macros.
- Exact language-learning HTML apps.
- Remaining JM134 beta-binomial and figure-rendering runnable scripts.
