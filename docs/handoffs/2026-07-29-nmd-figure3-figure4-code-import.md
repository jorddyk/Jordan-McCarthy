# 2026-07-29 NMD-analysis chat code import: Figure 3 v2.1, Figure 4 v11.2, JM100 lifespan converter

- Repo: `jorddyk/Jordan-McCarthy`
- Project area: Figure rendering (JM105 Figure 3 / Figure 4)
- Human purpose: Preserve Claude-authored code from Jordan's NMD-analysis chat that would otherwise only exist in a conversation this automation cannot search (no connector for claude.ai chat history — only Gmail, Google Drive, and GitHub are connected).
- Branch name: `claude/dazzling-turing-a3ujj5`
- PR title: n/a (committed directly to the session's working branch; no PR opened)
- Commit message: see git log on this branch for this date

## Source

Jordan uploaded `713e8717-files.zip` containing three files, stating they were produced by Claude in the NMD-analysis chat and that "code Claude makes is code that goes into the repo, but only if it is the final or most recent version":

- `JM105_figure3_render_v2_1_20260728.py`
- `JM105_figure4_render_v11_2_20260729.py`
- `JM100_lifespan_to_csv_20260728.py`

## Validation performed

- `diff` confirmed each committed file is byte-for-byte identical to the uploaded file.
- `python3 -m py_compile` passed for all three (syntax/compile-level validation only; this sandbox does not have numpy/pandas/scipy/seaborn/matplotlib installed, so no real-data execution was attempted or claimed).
- Read each file in full and checked its embedded `SCHEMA` string, required-column contracts, fail-closed guards (missing files, missing columns, unrecognised labels, synthetic-looking paths, insufficient named-gene fraction, insufficient universe size), and scientific-integrity statements against the repo's standing guardrails (real data only, RNA vs protein abundance distinction, CR-intensity labeling, Mud1 as permissive requirement not fabricated cause).
- Cross-referenced against currently open PRs: the Figure 4 script's title matches PR #12's recorded current Figure 4 authority exactly.

## Project files created/updated

- `projects/figure-rendering/panel-renderers/jm105-figure3-cr-selectivity-v2-1/jm105-figure3-render-v2-1-cr-selectivity.py` (new)
- `projects/figure-rendering/panel-renderers/jm105-figure3-cr-selectivity-v2-1/README.md` (new)
- `projects/figure-rendering/panel-renderers/jm105-figure4-mud1-host-transcript/jm105-figure4-render-v11-2-mud1-coupling.py` (new)
- `projects/figure-rendering/panel-renderers/jm105-figure4-mud1-host-transcript/jm100-lifespan-to-csv.py` (new)
- `projects/figure-rendering/panel-renderers/jm105-figure4-mud1-host-transcript/README.md` (new)
- `projects/figure-rendering/README.md` (canonical code status table + recovery-focus narrative)
- `projects/figure-rendering/docs/legacy-code-backfill.md` (three new "Imported exact runnable source" rows)

## Handoff/audit files created/updated

- `docs/wiki/Jordan-McCarthy-Code-Wiki.md` (Figure rendering canonical code list + today's decision entry)
- `docs/handoffs/2026-07-29-nmd-figure3-figure4-code-import.md` — this file

## Files not to commit

None encountered. No raw data, spreadsheets, generated figures, or secrets were in the upload; only three `.py` source files.

## Scientific/data status

All three scripts require real data and fail closed on missing/unrecognised inputs; none contain embedded biological data or synthetic-data fallbacks. No Euler execution was performed, so no scientific claim from these scripts is validated against real data by this pass — only the source code itself is being preserved.

## Implementation notes

Renamed files from their original upload names to lowercase kebab-case human-readable names while preserving version and purpose (e.g. `JM105_figure4_render_v11_2_20260729.py` → `jm105-figure4-render-v11-2-mud1-coupling.py`), matching this repo's filename convention. File **content** was not modified in any way — copies were verified with `diff` before and after renaming.

Two things are flagged for Jordan rather than resolved unilaterally, per this repo's rule that code-focused automation should name risks, not silently paper over them:

1. Both `figure3` and `figure4` scripts have a stale version number in their own top-of-file docstring (naming themselves `v1`), one or many versions behind the `SCHEMA` constant and the filename each was uploaded under. This looks like a leftover header comment from iteration, not a functional problem — the code and schema tag are internally consistent with the newer version — but it means the docstring header cannot be used as a trustworthy version indicator for future recovery passes; the `SCHEMA` string is the reliable one.
2. This recovery does not resolve whether the new two-figure split (Figure 3 = CR-selectivity in `+MUD1` only; Figure 4 = does Mud1 gate that response) reconciles with the 2026-07-28 handoff's statement that "the locked Figure 3 is the Mud1-dependence figure" and that a CR-selectivity renderer must not be promoted as canonical Figure 3. Both readings are plausible given how often this figure sequence has been revised (see the several "OBSOLETE — superseded by Yves most recent interpretation" folders already in Drive); only Jordan can say which framing is current.

The Figure 4 script also appears to close much of the "exact renderer" gap that draft PR #12 (`handoff/figure4-authority-reset-2026-07-28`, still open/unmerged) was waiting on, since its title matches PR #12's recorded current authority exactly and it needs no separate style-dependency file. PR #12 itself was not touched by this pass — reconciling the two branches is a follow-up action, not something done here per the instruction not to push to branches other than this session's designated one.

## Final code or candidate imports

Three files imported as `RECOVERED` exact source (see table above). None promoted to "canonical accepted figure" status — that requires real-data Euler execution, cross-font collision audit, retrieval/local verification, and Jordan's visual acceptance, per the standing figure-rendering reliability standard.

## Legacy-backfill progress

These three files were not previously tracked anywhere in the legacy-backfill queues (they are a new figure architecture, not a recovery of a previously-known-missing item), so no existing queue row was marked resolved. New rows were added directly to `projects/figure-rendering/docs/legacy-code-backfill.md`.

## Code-focused execution risk and containment

Risk: Claude-authored code produced inside a chat conversation is invisible to this repo's automation unless it lands in Gmail, Drive, or GitHub — the only three connectors available to this session. That gap was surfaced earlier today when Jordan pointed out unpreserved code this automation had no way to find. Containment action: documented the limitation explicitly (in the prior conversation turn and here), and preserved this batch the moment it was made available through a channel this automation can reach (a direct upload). No standing fix for the underlying visibility gap exists yet; future runs should keep asking Jordan directly whether chat-only code exists rather than assuming a clean Drive/Gmail/GitHub sweep is exhaustive.
