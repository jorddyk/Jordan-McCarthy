# JM105 Figure 3 rendering incident and learning record

Date: 2026-07-28  
Status: active incident; no renderer from this incident is canonical or accepted yet.

Bible reference: `JM105-FIGURE-BIBLE-v1.0-2026-07-22`, Figure 3 / Panels A-H.

## Executive finding

The incident was not one isolated code typo. It combined specification drift, unverified delivery paths, repeated incomplete preflights, metadata-parser assumptions, and publication-design failures.

The most important scientific correction is that the locked repository defines Figure 3 as the **Mud1-dependence figure**, with public metric `Mud1-dependent CR suppression`. The exploratory renderer launched during this chat instead used the title “Caloric restriction selectively suppresses an age-associated retained-intron program” and displayed `candidate_score`. That conflicts with the locked Figure 3 architecture and must not be promoted as the canonical Figure 3 renderer even if the current Euler job completes.

Current observed run at the time of this record:

- job ID: `8875587`;
- last observed state: `PD (Priority)`;
- real metadata preflight: passed for age, glucose, MUD1 and UPF1 labels;
- acceptance status: not rendered, not retrieved, not visually reviewed, not accepted.

`PD (Priority)` means the valid job is waiting in the shared Euler scheduler. It is not evidence of another parser or plotting failure.

## Locked Figure 3 correction

The authoritative Figure 3 metric is:

```text
NMD_hidden = IR(upf1Δ) − IR(UPF1+)

CR_suppression(genotype)
= NMD_hidden(old 2%, genotype)
− NMD_hidden(old 0.1% CR, genotype)

Mud1-dependent CR suppression
= CR_suppression(+MUD1)
− CR_suppression(mud1Δ)
```

Permanent rule:

- Figure 3 publicly uses Mud1-dependent CR suppression.
- `candidate_score` is not a public Figure 3 concept.
- The hero comparison is candidate-level `CR_suppression(mud1Δ)` versus `CR_suppression(+MUD1)` with a `y=x` reference.
- Visible labels use common gene names only.
- RNA-seq panels use total/rRNA-depleted JM105 only.
- The current exploratory CR-selectivity renderer may be retained only as a noncanonical diagnostic or reassigned after a formal figure crosswalk; it cannot silently replace the locked Figure 3.

## Failure chronology

| Failure class | Exact failure | Root cause | Permanent prevention |
|---|---|---|---|
| Packaging / user-interface delivery | File paths were printed as plain `/mnt/data/...` text rather than clickable sandbox links. | Delivery was described without verifying the user-visible artifact link format. | Every downloadable artifact must be presented as `[label](sandbox:/mnt/data/file)` and the exact file must be confirmed in the active runtime. |
| Packaging / extraction | The user was told to expand `JM105_Figure3_v3_GFF_SLURM_FLAT.zip`, but that filename was not present in Downloads. | The local filename was assumed rather than discovered. | Use `Get-ChildItem` to discover the actual downloaded filename before extraction; never infer local existence. |
| Packaging / workflow | The upload helper was invoked while still inside a ZIP or from the wrong directory. | Extraction and working-directory state were not verified. | Retrieval/upload helpers must resolve their own script directory and verify required sibling files before external commands. |
| Shell-context confusion | Terminal prompt text and scheduler output were pasted back into Bash, producing syntax errors near `(` and attempts to execute `8872675` or `jmccarthy@...$`. | Commands were not clearly separated from copied output. | Give minimal command-only blocks and explicitly state not to paste prompts/output. Prefer uploaded checked scripts to giant interactive blocks. |
| Slurm resource syntax | Euler rejected `--mem=16G`. | Site-specific Slurm resource rules were not checked. | Use Euler-supported `--mem-per-cpu`; run `sbatch --test-only` or site-compatible preflight when available. |
| Source path | Renderer failed because `SGD_features.tab` did not exist. | A historical annotation filename was assumed. | Source discovery must verify exact current reference paths before submission. The verified current annotation is the SGD R64-5-1 GFF. |
| Metadata semantics | Renderer attempted to derive replicate IDs from sample names and failed on opaque sample `JM1`. | It assumed sample names encoded biological pairing. | Never infer replicate, condition or genotype from opaque sample IDs. Use explicit metadata columns; paired subtraction requires a verified pairing field. |
| Scientific provenance | Arbitrary UPF1+ and upf1Δ libraries risked being paired by ordering. | Replicate pairing was treated as a naming problem rather than a design/provenance problem. | Compute replicate-level `NMD_hidden` only when a verified matched-pair key exists. Otherwise use declared condition means and label the aggregation honestly. |
| Gene aliases | Visible systematic ORF IDs appeared instead of common names. | GFF alias mapping was incomplete or not enforced at the final visible-text gate. | Build a bidirectional alias map; keep systematic IDs in provenance; hard-fail the rendered SVG/text audit when a systematic ORF is visible. |
| Visual communication | Panel B axes said “old − old” and “old − young” without naming glucose or metric. | Mathematical shorthand replaced explicit biological contrasts. | Axis labels must spell out the exact quantities, conditions and direction of subtraction. |
| Visual communication | Panel C introduced `candidate_score` without intuitive biological meaning. | An internal ranking helper was promoted into the public figure. | Do not display `candidate_score` in Figure 3. Use the locked Mud1-dependent CR-suppression metric and an intuitive comparison/gate. |
| Rendering / missing values | Panel D displayed `NaN` cells. | Incomplete rows were passed directly to a publication heatmap. | Publication heatmaps must use an explicitly complete matrix or encode missingness deliberately with a legend; literal `NaN` text is a hard failure. |
| Visual design | Panel E was an unreadable dense ranking. | Too many quantities and labels shared one footprint. | Use one biological visual grammar, common names, a fixed label lane, and a complete table as sidecar. Demote redundant full rankings when the hero panel carries the same conclusion. |
| Visual design | Panel F used unintuitive axes and visually confusing trapezoids/lines. | A complicated derived display obscured the biological comparison. | Figure 3 representative examples must use identical condition order and a simple direct display of source-secure raw IR or honestly labeled NMD-hidden values. Panel F lanes remain separate. |
| Unicode parsing | `upf1Δ` failed because `_norm()` deleted `Δ`, producing `upf1`. | ASCII stripping occurred before transliteration. | Transliterate `Δ`, `δ`, `∆`, and `+` before punctuation removal; include all variants in regression tests. |
| Incomplete regression test | The first parser patch still failed on plain `UPF1`. | The test matrix was too narrow and the intact state relied on specific decorated spellings. | Exact-token sets plus fallback logic must test `WT_UPF1`, `UPF1+`, `UPF1`, `upf1Δ`, `upf1D`, and `upf1delta`. |
| Queue interpretation | A valid pending job felt like another failure because it remained `PD (Priority)`. | Scheduler wait and code failure were not separated in the status language. | Report scheduler state explicitly: `PD (Priority)` = accepted and waiting; `R` = running; `CG` = cleanup; final success/failure comes from `sacct`. Do not resubmit a valid pending job. |
| Specification drift | The renderer was called Figure 3 although it did not implement the locked Mud1-dependence architecture. | The GitHub start-here files and Figure 3 crosswalk were not consulted before code. | No Figure 3 code begins until the bible, start-here files, current crosswalk, source manifest and main/supplement hierarchy are read and locked. |

## What the chat established reliably

1. The current count table uses opaque sample IDs such as `JM1`; those IDs are not valid replicate encodings.
2. The explicit metadata columns include real labels such as `WT_UPF1`, `upf1Δ`, `WT_MUD1`, and `mud1Δ`.
3. The current SGD reference path on Euler is:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/02_reference/SGD_S288C_current/saccharomyces_cerevisiae_R64-5-1_20240529.gff
```

4. The real metadata preflight eventually passed for all observed UPF1, age, glucose and MUD1 labels.
5. The current job `8875587` is scheduler-pending at the last observation, not accepted.
6. No output from this incident may be called final until Euler completion, hard QA, Windows retrieval, local verification, white-preview review and Jordan acceptance all pass.

## Learning loop installed by this incident

The reusable loop is now stored at:

```text
projects/figure-rendering/templates/jm105-figure-rendering-learning-loop.md
```

New permanent sequence:

```text
observe exact failure
-> classify stage
-> state violated invariant
-> patch only that stage
-> add regression test
-> run static and real-table preflights
-> render on Euler
-> run hard visual QA
-> retrieve and verify locally
-> Jordan reviews
-> promote accepted code only
-> record GitHub + Drive learning
```

## Acceptance decision for the current renderer

Even if job `8875587` renders successfully:

- do not commit it as canonical Figure 3;
- inspect it only as an exploratory diagnostic;
- compare it against the locked Figure 3 A-H crosswalk;
- extract any reusable engineering improvements;
- rebuild the accepted Figure 3 only after the source crosswalk and Mud1-dependent metric are restored.

## Next canonical engineering actions

1. Wait for job `8875587`; inspect `sacct`, stdout and stderr once it leaves the queue.
2. Preserve its output and logs as incident evidence.
3. Retrieve and review the white preview without calling it canonical.
4. Build the required Figure 3 source crosswalk and verify the +MUD1 and mud1Δ CR-suppression source cells.
5. Use the locked `paper_style.py`; no locally invented colors.
6. Use the shared hard collision gate and visible-systematic-ID rejection.
7. Commit only the renderer Jordan accepts after the complete end-to-end loop.
