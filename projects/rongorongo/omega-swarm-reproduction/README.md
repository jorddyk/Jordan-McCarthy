# OMEGA-SWARM reproduction scripts

Four independent reproduction scripts recovered verbatim from Google Drive documents, each mirroring an executable `.py` from a 2026-07-16/2026-07-17 OMEGA-SWARM adjudication run over the frozen 141-passage Rongorongo corpus (1,021 strict whole tokens). Every run's verdict is **NO SYSTEM SURVIVED**: no proposed decipherment system cleared the preregistered promotion gates (external bridge, stable phonetic/grammatical value, fresh prediction, re-encoding rate, family-blocked significance, continuous passage).

## Files and provenance

| File | Source Drive doc | Doc ID | Modified | Recovers script |
|---|---|---|---|---|
| `reproduce_structural_tests.py` | "OMEGA-SWARM Reproduction Script — OMEGA-ADJ-7A4C9E31" | `1YGrbifOhLNlsdTXfNaq9qIib3qEgDx0FvHmrrRu6cB4` | 2026-07-17 | `reproduce_structural_tests.py` from run OMEGA-ADJ-7A4C9E31 |
| `01_reproduce_tournament.py` | "01_REPRODUCE_TOURNAMENT.py — NATIVE_TEXT_MIRROR — OSD-3D057D4D" | `1NTK4z1jHoSaV48SXBFAmEn2DSDEOxw3ZUcMSaCXK6Xc` | 2026-07-17 | `01_REPRODUCE_TOURNAMENT.py` from run OSD-20260717T092019+0200-3D057D4D |
| `omega_reproduce.py` + `omega_reproduce_manifest.json` | "REPRODUCTION_MANIFEST__OMEGA-20260717T0918+0200-DCE062EF" | `1ovkQ71jWTl43j6p-jcbPrUVolKIClr5-IJ_BOQoaSKc` | 2026-07-17 | `omega_reproduce.py` + `manifest.json` from run OMEGA-20260717T0918+0200-DCE062EF |
| `reproduce_adjudication_omega_swarm_f303e582.py` | "OMEGA-SWARM Reproduction Record — OMEGA-SWARM-F303E582" | `1cDBmgpuWhJ8mAAeRe_TrGCXs30ZBXy4bApPmN96NOE8` | 2026-07-17 | `reproduce_adjudication_OMEGA-SWARM-F303E582.py` from run OMEGA-SWARM-F303E582 |

Each source document was created as a deliberate "native text mirror" of the actual executable delivered in that run's full local package — i.e. Jordan (or the swarm process) already intended these to be readable/recoverable text copies of real code, not just descriptions.

## Status: code RECOVERED, inputs NOT LOCATED

The Python source in every file here is complete and verbatim (validated: `python -m py_compile` passes for all four; the shared `Ba6` exact-probability constant `0.0009492329858462582` was independently recomputed from `math.comb(17,11)/math.comb(27,11)` and matches).

None of these scripts are independently runnable in this repository because their required companion data files were not found in Drive (only referenced by name/SHA-256):

- `reproduce_structural_tests.py` needs `horley_encoding.py`, `horley_parallels.csv`, `frozen_passages.json` (same directory, `--dir` flag).
- `01_reproduce_tournament.py` needs the `RR_SEALED_IDENTITY__actor-KoruAtlas-GPT56T-Sigma__20260716T164620+0200__run-PA3-2C91` Excel workbook (`Passage_Identity` sheet), passed via `--identity`.
- `omega_reproduce.py` needs `passage_atlas_frozen.csv` in the same directory (see `omega_reproduce_manifest.json` for its expected SHA-256 and the full sibling-file hash table).
- `reproduce_adjudication_omega_swarm_f303e582.py` needs `input_manifest_OMEGA-SWARM-F303E582.json` and `systems_OMEGA-SWARM-F303E582.csv` in the same directory.

Do not fabricate these inputs. If recovered later (most likely from local machine, the Euler cluster, or a "downloadable reproduction ZIP" mentioned in the source docs), add them alongside the corresponding script and update this table's status.

## Frozen corpus facts asserted by these scripts (for cross-checking future recoveries)

- 141 admissible passages, 1,021 strict whole tokens, 1,598 Horley-normalized components, 366 structural families, 33 transferable signatures.
- Ba6 free-`063` positions in passage `P053`/line `Ba6`: n=27, k=11, adjacency=0, exact p=0.0009492329858462582 (familywise Monte Carlo p=0.0009199816, seed 32711).
- Terminal core `2a-2a-8-8-4` located at passage/records 27, 28, 144; permutation p=0.0000199998.
- 266 two-part period compounds, 206 unordered pairs, 7 bidirectional ("mirror") pairs; fair-coin-null p=0.0000499975; frequency-propensity-null p=0.157092 (not significant).
