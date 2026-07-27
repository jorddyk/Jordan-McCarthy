# Daily Code Handoff — Figure 2/NMD source location — 2026-07-27

## Sources searched

- Authorized File Library uploads created on 2026-07-27.
- Same-day terminal transcripts for JM105 NMD Figure 2, `JM105_NMD_AUDIT`, and Yves Figures 1/2 attempts.
- Private canonical repository `jorddyk/Jordan-McCarthy` and open draft PRs.
- Gmail attachments from the preceding two days.

## Exact source located

Complete File Library source objects:

```text
JM105_figure2_render_v1_2_20260727.py
JM105_figure2_render_v3_NMDoff_20260727.py
```

Status: `PARTIAL / EXACT SOURCE LOCATED`.

The files are complete source objects in the authorized File Library, but the current file connector exposed only searchable source chunks and did not provide byte-complete file transfer for GitHub import. No code was reconstructed from snippets.

## Verified scientific boundaries

- Figure 2 uses the 2% glucose, WT MUD1, young/old × UPF1+/upf1Δ slice.
- Caloric restriction is excluded and remains a Figure 3 question.
- Raw NMD-off/upf1Δ retained-intron signal is distinct from `NMD_hidden = IR(upf1Δ) - IR(UPF1+)`.
- Both renderers reject synthetic/mock/fake inputs.
- Host abundance is explicitly host RNA, not protein abundance.
- NMD2/UPF2 is identified as an absent orthogonal experiment and is not fabricated.

## Missing intake components

Before a canonical renderer can be chosen and committed, recover:

1. byte-complete copies of both located Python files;
2. exact `paper_style.py` used by them;
3. exact launcher and Slurm script;
4. environment/dependency record;
5. full-file SHA-256 hashes;
6. input table path and schema provenance;
7. successful Euler job ID, output directory, status and validation manifest.

## Diagnostic workflows deliberately not canonicalized

Same-day records also describe `JM105_NMD_AUDIT` and Yves Figures 1/2 attempts. These include multiple revisions and failures:

- obsolete 42,301-byte audit ZIP with `ValidateSet('Probe', 'Run')` and no `Provenance` stage;
- later provenance-aware revision not available as a transferable exact bundle;
- launcher/PowerShell failures;
- Yves Figures 1/2 failure: `Missing condition cell in raw table: ('young', 'off')`.

These are retained as recovery evidence only, not publication-canonical code.

## Repository paths changed

```text
projects/jm105-intronsaurus/README.md
projects/jm105-intronsaurus/docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
docs/handoffs/2026-07-27-figure2-nmd-source-location.md
```

## Next source target

Retrieve the exact complete 2026-07-27 Figure 2/NMD execution package from Jordan's Downloads or its Euler run `code/` directory, including both renderer candidates, `paper_style.py`, launcher/sbatch, hashes and successful-run proof. Do not infer the canonical winner from filenames or snippets alone.
