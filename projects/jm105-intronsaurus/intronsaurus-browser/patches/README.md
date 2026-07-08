# Intronsaurus browser legacy patch helpers

This folder stores exact small helper scripts recovered from legacy Intronsaurus browser build conversations. These files are organized by what they do, not by daily handoff date.

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
