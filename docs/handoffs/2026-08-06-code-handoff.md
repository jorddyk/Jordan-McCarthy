# CODE HANDOFF — 2026-08-06

## Repo

`jorddyk/Jordan-McCarthy`

## Project area

Cross-project sweep (Google Drive + Gmail) for code/computational artifacts not yet preserved, following on from the 2026-07-28 handoff.

## Human purpose

Check authorized sources for new or updated code, scripts, notebooks, or computational work since the last backfill pass, and preserve anything recoverable.

## Search performed

- Reviewed git history and existing wiki/backfill ledgers to establish the last-covered date (2026-07-28).
- Listed and queried Google Drive for files created/modified since 2026-07-28, including a pass restricted to non-Google-native (uploaded) file types, which most reliably surfaces actual script/code bytes rather than Docs/Sheets.
- Searched Drive by exact filename for every item on the standing priority-recovery queue (Figure 3 v21 pair, Figure 2 public-final renderer, Figure 5 C/D/E renderer, JM101/JM105 integration scripts, JM133/JM134 scripts, synopsis-aligned RNA-seq renderer).
- Searched Gmail for code-handoff/backfill-related threads and any messages carrying code since 2026-07-28.

## Files created

- `docs/handoffs/2026-08-06-code-handoff.md` (this file)

## Files updated

- `projects/figure-rendering/docs/legacy-code-backfill.md` — added a 2026-08-06 recovery-pass section
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md` — added a 2026-08-06 decision entry, bumped last-updated date

## Files deliberately not committed

- No code was committed this pass. The only Drive item modified since 2026-07-28 relevant to figure-rendering is a register/metadata Google Doc (`CURRENT — JM105 Figure 2 v10 lane-locked renderer register`) describing `JM105_figure2_render_v10_lane_locked_20260728.py`; the actual `.py` bytes are not present in Drive under either the v9 or v10 filename, so nothing runnable exists to import. Reconstructing it from the register's prose would violate the no-fabrication rule.
- Two non-Google-native files were modified since 2026-07-28 (`SPARE ROOM — Implementation Directive.md`, `SPARE ROOM — Interrogation Instrument.md`), but they belong to an unrelated personal/planning project tree, are not code, and are out of this repo's scope.
- All other Drive activity since 2026-07-28 is Google Docs/Sheets under unrelated project folders (personal planning/tracking documents), not computational artifacts.

## Scientific/data status

No biological data, generated renders, raw sequencing, microscopy stacks, secrets, or code were fabricated or committed.

## Implementation notes

The new Figure 2 v10 register supersedes the prior v9 status implicitly referenced in the standing priority queue (item 11, Panel F Mud1-dependence). Once actual source bytes for either v9 or v10 become retrievable, they — not the older Panel F patch sequence — are the current scope of truth for the Figure 2 renderer. The register's stated validation boundary is limited to a private layout test; the real-data Euler render and its `render_self_audit.json` had not yet been retrieved as of the register's last edit, so this is not yet a canonical-acceptance signal either.

## Final code paths

```text
projects/figure-rendering/docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
docs/handoffs/2026-08-06-code-handoff.md
```

## Legacy-backfill progress

No new runnable code recovered this pass. One new source-located clue logged (Figure 2 v10 lane-locked renderer, `PARTIAL / SOURCE LOCATED`).

## Remaining source-recovery targets

Unchanged from the 2026-07-16/07-28 state — see `projects/figure-rendering/docs/legacy-code-backfill.md` priority table and `docs/wiki/Jordan-McCarthy-Code-Wiki.md` for the full list (Figure 3 v21 pair, Figure 2 public-final/v10 renderer, Figure 5 C/D/E renderer, JM133/JM134 scripts, JM101/JM105 integration pipeline, synopsis-aligned RNA-seq renderer, Fiji/ImageJ macros).
