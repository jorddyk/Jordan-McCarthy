# JM-136 Benchmark History

This file is an evidence ledger, not a leaderboard generated from version numbers. A model is promoted only on declared endpoint metrics under grouped validation. Failed experiments are retained because they contain negative knowledge that should not be rediscovered.

## Current demonstrated benchmark history

| System | Validation unit | RLS MAE | Bias | Exact | ±1 | Death | Other | Status |
|---|---|---:|---:|---:|---:|---:|---|---|
| six-state frame classifier | held-out split used at the time | 5.22 | -0.90 | 4.3% | 13.0% | 15/23 | frame acc ~0.592 | superseded for RLS |
| direct event/death trainer | untouched test traps, n=16 | **2.44** | +1.06 | 31.2% | 43.8% | **93.8%** | div threshold 0.50, min gap 5 | **current demonstrated RLS baseline** |
| sequence count refiner | untouched test traps, n=16 | 2.62 | +2.12 | 12.5% | 56.2% | 93.8% | calibration needed +2.90 count offset | rejected as endpoint replacement |
| temporal residual corrector | untouched test traps, n=16 | 2.44 | +1.06 | 31.2% | 43.8% | 93.8% | best calibration epoch = 0 | no improvement; baseline retained |
| long-context v6 | pooled trap-level OOF, n=91 | 5.47 | -1.49 | 4.4% | 20.9% | 80.2% | event F1 ±2 frames = 0.750 | rejected as endpoint system; event signal potentially reusable |
| v7.1 SSL + 11-frame Transformer | position-grouped experiment | pending | pending | pending | pending | pending | 124 embedded manual-gold RLS mappings; self-supervised pretraining on all trap images | experimental, training in progress 2026-08-14 |

## Interpretation

### Frame classifier / HMM failure

The early system demonstrated that reasonable frame accuracy is not enough to preserve every cell cycle over a long trajectory. Viterbi/HMM persistence additionally erased short but biologically real states and produced catastrophic RLS under-counting. Conclusion: do not use generic state persistence as the primary RLS decoder.

### Direct-event breakthrough

Moving the optimization target toward completed division events reduced held-out RLS MAE from roughly 5.22 to 2.44 and improved death calling to ~93.8%. This remains the best demonstrated endpoint result in the current sequence. Its main limitation is accumulation of missed/extra events across long lifespans.

### Sequence-refiner failure

The first TCN refiner improved ±1 agreement but worsened MAE and developed a positive bias. Its differentiable probability-mass count was not calibrated in units of biological divisions; the subsequent affine calibration required a large offset. Conclusion: summed sparse-event probability is not itself an RLS count target.

### Temporal-residual null result

A zero-initialized temporal residual model preserved the direct detector at epoch 0 and was allowed to replace it only if calibration RLS improved. It did not. This is a useful negative result: adding temporal correction to frozen direct-model representations did not improve the endpoint.

### v6 long-context failure with useful event signal

The 21-frame long-context model produced poor pooled OOF RLS and death performance, but event F1 of 0.750 ±2 frames showed that the network often localized divisions approximately correctly. Conclusion: event perception and lifetime counting can fail independently. A globally rejected model may still be useful as one expert in a future adjudication ensemble, but it is not a production RLS system.

### v7.1 hypothesis

v7.1 borrows only compatible ideas from recent yeast/microscopy sequence work: trap-domain self-supervised morphology learning plus an 11-frame temporal event expert, while retaining the existing working UI/pipeline and evaluating against independent manual trap-level JM135 RLS. It uses position grouping and refuses to overwrite existing production artifacts. It is explicitly **not validated yet**.

## Gold-vs-frame annotation audit discovered by v7.1

At v7.1 startup on 2026-08-14:

- TIFF traps: 304
- clean dense-label traps: 90
- manual-gold mapped TIFF traps: 124 across positions 3, 5, 7, 12, 13, 15, 18
- manual gold vs frame-derived RLS raw MAE: 6.613 divisions
- exact agreement: 62.9%
- within ±1: 66.1%
- 41/124 traps exceeded an absolute difference of 2 and were excluded from supervised event training

This discrepancy must be explained before any “superhuman” claim is credible. Candidate explanations include incomplete frame annotation, legacy annotation contamination, trap-ID/position mapping errors, or genuine manual-versus-state-rule disagreement. v7.1 preserves those images for self-supervised learning while withholding unsafe event supervision.

## Promotion rule

Higher version number is irrelevant. A candidate must add value relative to the best demonstrated baseline on predeclared grouped endpoint metrics, while preserving or improving death/censoring behavior and avoiding condition-specific bias.

A future automated system should additionally report the fraction of traps that can be accepted with no human intervention. “Good average RLS” is insufficient if most traps still require manual frame-by-frame review.
