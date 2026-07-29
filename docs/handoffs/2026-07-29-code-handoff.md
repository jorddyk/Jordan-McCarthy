# 2026-07-29 Code Handoff

- Repo: `jorddyk/Jordan-McCarthy`
- Project area: JM105 / Intronsaurus (figure-rendering)
- Human purpose: Search Jordan's authorized sources for code/computational artifacts not yet preserved in the repo, validate and document them, and preserve anything recoverable.
- Branch name: `claude/dazzling-turing-a3ujj5`
- PR title: n/a (documentation-only change, committed directly to the session's working branch; no PR opened)
- Commit message: see git log on this branch for this date

## Sources searched

- GitHub: confirmed repo access (`get_me`, `list_pull_requests`), reviewed all open/closed PRs (#1-#12) for existing in-flight recovery state before writing anything new.
- Google Drive: `list_recent_files`, and `search_files` for `modifiedTime > '2026-07-28T00:00:00Z'` (global, not folder-scoped), plus targeted title/fullText queries for the new artifact's filename.
- Gmail: `search_threads` for recent attachments (any age, common code extensions), and for JM105/Euler/renderer/sbatch/intronsaurus/fiji/groovy keywords in the last 3 days.

## Project files created/updated

- `projects/jm105-intronsaurus/docs/legacy-code-backfill.md` — added priority-queue row 16 and a "2026-07-29 recovery pass" section for the Figure 2 v10 lane-locked renderer register.
- `projects/jm105-intronsaurus/README.md` — added a "Verified external recovery clue added 2026-07-29" section.

## Handoff/audit files created/updated

- `docs/wiki/Jordan-McCarthy-Code-Wiki.md` — updated last-updated date, added a Figure 2 v10 entry under JM105/Intronsaurus, and a 2026-07-29 entry under last-known canonical decisions.
- `docs/handoffs/2026-07-29-code-handoff.md` — this file.

## Files not to commit

None encountered. No raw sequencing data, generated renders, binaries, logs, caches, scratch folders, or secrets were found or committed.

## Scientific/data status

Documentation only. No biological data, simulated data, or code was generated or reconstructed. The one located artifact remains `PARTIAL / SOURCE LOCATED` per repo convention (register/hash exists; runnable `.py` bytes are not accessible to this automation).

## Implementation notes

Found one new artifact not previously tracked anywhere in the repo: a Google Doc titled "CURRENT — JM105 Figure 2 v10 lane-locked renderer register" in Drive folder `06 Current Figure Rendering Code` (created 2026-07-28 08:42 CEST). It describes `JM105_figure2_render_v10_lane_locked_20260728.py` (supersedes a `v9_FINAL` renderer), gives a SHA-256 hash, required inputs, an Euler command, and states its own validation boundary is a schema-matched private layout test only — not yet a re-verified real-data Euler render. No matching `.py` file object exists anywhere else in Drive, so nothing was imported; the register was recorded as a source clue only, per the "recovery clue vs. recovered code" rule.

No other new or updated code, scripts, notebooks, or computational artifacts were found. Gmail attachments/keywords over the last several days returned only personal correspondence, insurance/invoice receipts, and prior automation status emails (Daily Intelligence Brief, Devil's Advocate, and prior Daily Code Handoff notifications) — none contained code.

Other recently modified Drive items (a rowing-log spreadsheet, a forecast/ledger spreadsheet, a "Connection Tracking" spreadsheet, and a "Direct Decipherment Run Intake Register" spreadsheet tied to the separate Rongorongo work already visible in PR history) are personal/administrative or belong to an out-of-scope project and are not computational artifacts for this repo's project areas.

## Final code or candidate imports

No code imported this run. Candidate import pending exact-byte recovery: `figures/jm105-figure2-render-v10-lane-locked.py` (see legacy-backfill ledger for the exact recovery action).

## Legacy-backfill progress

Existing priority queues (JM101/JM105 integration scripts, Rsubread/DESeq2/IRFinder, Intronsaurus builders, JM133/JM134, Figure 3 v21, Figure 2 public-final, Figure 5 C/D/E, ImageJ/Fiji macros) are unchanged this run; no new evidence was found for those items. One new row (16) added to the JM105 queue for the Figure 2 v10 lane-locked renderer, status `PARTIAL / SOURCE LOCATED`.

## Code-focused execution risk and containment

Risk: a same-day register document (created 2026-07-28) sat one full day without being logged anywhere in the repo, which is exactly the "legacy code trapped outside the repo while remembered filenames create false confidence" risk this ledger exists to contain. Containment action taken: logged the clue immediately with its hash and validation boundary in the JM105 legacy-backfill ledger, README, and code wiki, so the next run (or Jordan) can go straight to exact-byte retrieval instead of re-discovering it.
