# Intronsaurus vNext3AH-fix9 backfill note

_Date: 2026-07-08 Europe/Zurich_

## Canonical location

`projects/jm105-intronsaurus/intronsaurus-browser/patches/`

## Imported helper scripts

- `upload-prebuilt-scientific-wording-dino-v3ah-fix9.ps1`
- `retrieve-scientific-wording-dino-v3ah-fix9.ps1`
- `check-scientific-wording-dino-v3ah-fix9-status.sh`

## Purpose

Preserve exact helper code from the Intronsaurus vNext3AH-fix9 scientific-wording/dino patch bundle. The helpers upload, retrieve, and validate the already-built browser archive on Euler.

## Scientific/data status

These are deployment and status scripts only. No raw data, generated HTML, tarballs, or fake biological data were committed.

## Deliberately not promoted as current full builder

The bundle also contained `build_scientific_wording_dino_v3AH_fix9_reference.py`, but it was a reference patch against a prepared HTML archive rather than the newest full Intronsaurus builder. The exact source remains recoverable from the local bundle and is tracked in the handoff as a source-recovery target.

## Related handoff

`docs/handoffs/2026-07-08-intronsaurus-fix9-legacy-code-backfill.md`
