# 2026-08-03 code handoff: Rongorongo OMEGA-SWARM/PROMETHEUS recovery

## What changed

- Searched Google Drive (recent files + targeted title/full-text queries) and Gmail (attachment search) for new code, scripts, notebooks, or computational work not yet preserved in this repository.
- Created a new project directory, `projects/rongorongo/`, and imported six complete Python files plus one JSON manifest, recovered verbatim from Google Drive documents dated 2026-07-16/2026-07-17.
- Updated `projects/README.md` and `docs/wiki/Jordan-McCarthy-Code-Wiki.md` to register the new project.

## Files added

| Path | Recovered from (Drive doc ID) | Status |
|---|---|---|
| `projects/rongorongo/omega-swarm-reproduction/reproduce_structural_tests.py` | `1YGrbifOhLNlsdTXfNaq9qIib3qEgDx0FvHmrrRu6cB4` | PARTIAL / code recovered, inputs not located |
| `projects/rongorongo/omega-swarm-reproduction/01_reproduce_tournament.py` | `1NTK4z1jHoSaV48SXBFAmEn2DSDEOxw3ZUcMSaCXK6Xc` | PARTIAL / code recovered, input not located |
| `projects/rongorongo/omega-swarm-reproduction/omega_reproduce.py` + `omega_reproduce_manifest.json` | `1ovkQ71jWTl43j6p-jcbPrUVolKIClr5-IJ_BOQoaSKc` | PARTIAL / code recovered, input not located |
| `projects/rongorongo/omega-swarm-reproduction/reproduce_adjudication_omega_swarm_f303e582.py` | `1cDBmgpuWhJ8mAAeRe_TrGCXs30ZBXy4bApPmN96NOE8` | PARTIAL / code recovered, inputs not located |
| `projects/rongorongo/prometheus-null-compiler/rr_prometheus_compiler.py` | `1oQ78bK-uc0BQ9jfh1o7r6xwxY4sQTTpbWl-Vz9aWJLg` | **RECOVERED** — self-contained, executed and verified |
| `projects/rongorongo/hrfa-validator/rr_hrfa_validator.py` | `1IfHlwm_b8ZZpglemdokqan4d8nmQ-4sC` (native `.py`, not a doc) | PARTIAL / code recovered, input not located |

Each subdirectory has its own README with full provenance, the exact companion files it's missing, and the frozen corpus facts the scripts assert (for cross-checking any future recovery of the missing inputs).

## Validation performed

- All six files pass `python -m py_compile`.
- `rr_prometheus_compiler.py self-test` was actually run (not just read); its output matched the self-test JSON recorded in the source document byte-for-byte.
- The Ba6 exact-probability constant shared by three of the scripts, `math.comb(17,11)/math.comb(27,11) = 0.0009492329858462582`, was independently recomputed in this environment and matches.
- Code was extracted using Drive's plain-text/base64 export path rather than the default markdown-converted view, specifically because the markdown view escapes `<`, `>`, `#!`, `__`, `[`, `]` and similar characters that are meaningful in Python source — using it directly would have silently corrupted the recovered code. This was caught during extraction (the markdown-view copy of one file showed literal `\#\!` and `&lt;`/`&gt;` sequences) and worked around before anything was committed.

## What was deliberately not recovered

Five scripts require companion data files (raw corpus tables, an Excel identity workbook, input manifests) that are referenced by filename and SHA-256 hash throughout the source documents but whose actual bytes were not found anywhere in Drive — only two un-searched Drive folders ("Rongorongo Decipherment", "TAU_RONGORONGO_REPLICATION_PREP_2") remain as leads. Per this repository's standing rule that filenames/hashes/summaries are recovery clues and not recovered runnable source, these inputs were not fabricated or reconstructed. This mirrors the existing JM105 figure-rendering backfill convention (`PARTIAL / SOURCE LOCATED`) applied to a case where, unlike most JM105 examples, the *code* itself (not just its existence) was fully recovered — only the data it consumes is still missing.

## Other projects checked, no action taken

- **JM105 figure-rendering**: re-confirmed the 2026-07-30 finding that the "JM105 Figure 2 v10 lane-locked renderer register" Drive document is descriptive/metadata only (SHA-256, scope, corrections vs. v9) with no embedded `.py` source; the v5/v9/v10 renderer files themselves are not present in Drive. No changes made.
- **Personal intelligence agency**: Drive contains an active, extensive live-state system under this name (Master Interaction Record, Canonical Current State Ledger, Weekly Operating Board, Connection Tracking, Network Profiles, Forecast & Wrong Ledger, and several "HEARTH"/"OP KINSHIP"/"OP COMPASS" operational memos). Per `projects/personal-intelligence-agency/README.md`'s own canonicality rules ("must never contain private raw inbox/calendar exports... do not commit daily private intelligence products... do not store... message text"), none of this was imported. This is a private live operating system, not source code, and is explicitly out of scope for this code vault.
- **Gmail**: attachment search for common code file extensions (`.py`, `.ipynb`, `.sh`, `.R`, `.js`, `.ts`, `.sbatch`, `.ps1`) returned only unrelated personal correspondence (a restaurant billing dispute, travel booking confirmations) — no code attachments found.

## Repository hygiene

No raw sequencing data, generated figures, credentials, private personal-life documents, or fabricated biological/linguistic values were committed. No existing files were modified except the two documentation files listed above.
