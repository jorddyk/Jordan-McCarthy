# HEARTH Socratic Review — JM-136 Repository Architecture

**Date:** 2026-08-14  
**Status:** decision-support record for repository organization  
**Method:** Socratic interrogation of the current canonical HEARTH records, especially *2026-08-07 — RLS Automation Gate Assessment & HEARTH Socratic Review* and *HEARTH — Source & Records Handling Standard*. This is not a transcript of a separate live agent. It makes the questions explicit and applies the answers already encoded in HEARTH to the present GitHub decision.

## Decision question

How should JM-136 be kept in GitHub so that it remains scientifically trustworthy, usable as a real pipeline, legible to a skeptical software engineer, and maximally useful to Jordan's long-run scientific and company-building goals without prematurely disclosing or overstating an unvalidated asset?

---

## Socratic Round I — What is the object we are preserving?

**Analyst:** Is JM-136 a collection of neural-network experiments?

**HEARTH:** No. That framing is too narrow and would cause the repository to ossify around whatever model happens to be fashionable today. The durable object is the acquisition-to-phenotype system: trap-resolved image identity, preprocessing, annotation, biological state ontology, explicit event semantics, RLS/death/censoring extraction, models, QA, benchmarking, review routing, and experiment-level outputs.

**Analyst:** Then what should the repository optimize for?

**HEARTH:** Reproducibility of the biological endpoint and substitutability of individual implementation components. A CNN may be replaced. The meaning of a trap, a completed division, an observed death, a censoring event, a benchmark unit, and an output record must remain explicit and versioned.

**Repository consequence:** organize around pipeline contracts and provenance, not around a single trainer.

---

## Socratic Round II — Why not simply dump the Desktop folder into GitHub?

**Analyst:** Would a complete desktop dump be the safest way not to lose anything?

**HEARTH:** It would preserve clutter while destroying epistemic status. Generated models, raw image stacks, recovered workbooks, stale experimental scripts, logs, and current source would appear equivalent. A future user would not know which file is authoritative or why it exists.

**Analyst:** What would a strict engineer object to first?

**HEARTH:** Ambiguous canon, magic workstation paths, giant binaries, duplicated implementations of scientific rules, source files whose names encode accidental chronology rather than role, and no test proving that a cleanup preserved behavior.

**Repository consequence:** preserve an exact/current source snapshot first, classify its members, and only then refactor behind tests. Do not rewrite source during ingestion merely to make it look professional.

---

## Socratic Round III — What did the Fable failure teach us?

**Analyst:** What is the strongest procedural lesson from the earlier source-recovery failure?

**HEARTH:** A plausible-looking placeholder is worse than an explicit missing file. The system must never present reconstructed prose, pseudocode, a documentation stub, or a guessed implementation as recovered source.

**Analyst:** What is the proof standard for saying a source file has been preserved?

**HEARTH:** The file body must actually be available; its origin must be recorded; a content fingerprint should be retained; syntax should be checked where applicable; and the committed path must be inspectable. If any one of those is absent, say what is absent.

**Repository consequence:** `docs/source-inventory.md` distinguishes present, verified source from files merely visible in screenshots or remembered from prior work. Missing files are requested rather than recreated.

---

## Socratic Round IV — Why retain failed trainers?

**Analyst:** A clean repository usually deletes failed experiments. Should v6, the sequence refiner, and the temporal residual trainer disappear?

**HEARTH:** Not yet. Their failures contain high-value negative knowledge: HMM persistence can erase real short states; probability-mass counting can miscalibrate divisions; residual temporal correction did not improve the direct detector; a long-context model can achieve respectable event F1 while producing bad lifetime counts. Removing those files without preserving the evidence increases the chance that the same dead ends are rediscovered.

**Analyst:** Does that mean every failed experiment remains forever in the main source tree?

**HEARTH:** No. During active R&D, preserve them in a clearly labeled experimental history. Once stable interfaces and a benchmark ledger exist, old implementations can move to an archive/tag while the lessons remain in documentation and Git history.

**Repository consequence:** experimental trainers are preserved but never labeled production merely because their version number is larger.

---

## Socratic Round V — What is production today?

**Analyst:** Is v7.1 now the canonical RLS system because it is newest?

**HEARTH:** No. Newness is not validation. The demonstrated direct-event system remains the strongest observed RLS result in the current development sequence; the working human annotation UI remains operational infrastructure. v7.1 is a candidate being evaluated.

**Analyst:** Should the repository use `latest.py`?

**HEARTH:** Avoid it. `latest` is temporal, not semantic. Use names that state role and status, plus a benchmark ledger that records which version currently wins a defined endpoint.

**Repository consequence:** README and benchmark history identify the current demonstrated baseline separately from experimental candidates.

---

## Socratic Round VI — What is the scientific interface?

**Analyst:** Which lines of code are most dangerous to casually refactor?

**HEARTH:** The functions encoding division, death, censoring, frame indexing, coordinate transforms, and trap identity. A one-line semantic drift there can change RLS without changing model weights.

**Analyst:** What should eventually happen to duplicated copies of `find_division_frames()` and related logic?

**HEARTH:** They should converge into one versioned domain module, but only after regression tests demonstrate that the canonical current behavior is reproduced exactly. Refactoring first risks changing the phenotype definition while believing only software structure changed.

**Repository consequence:** future `src/aging_chip/domain/` refactor is gated on semantic fixtures/tests.

---

## Socratic Round VII — What should be invariant, and what may evolve?

**Analyst:** What must remain invariant if JM-136 becomes infrastructure?

**HEARTH:** Traceable trap identity; explicit biological state/event semantics; reproducible preprocessing; versioned models/rules; machine-readable output schemas; censoring policy; benchmark definitions; uncertainty/review behavior; source and data fingerprints.

**Analyst:** What can change aggressively?

**HEARTH:** Backbone architecture, temporal model family, augmentation, UI implementation, GPU hardware, optimization strategy, and model-serving technology—provided the interfaces and endpoint validity survive.

**Repository consequence:** architecture docs distinguish stable contracts from replaceable implementation.

---

## Socratic Round VIII — What validation earns promotion?

**Analyst:** Is frame accuracy a sufficient release criterion?

**HEARTH:** No. The biologically relevant output is the trap trajectory and derived lifespan endpoint. Correlated frames can make frame-level validation look excellent while whole-trap generalization is poor.

**Analyst:** What is the minimum credible model report?

**HEARTH:** Whole-trap holdout, with stricter whole-position/chip/biological-replicate holdout where possible; RLS MAE and exact/±1/±2 agreement; missed/false division events; death/censoring metrics; stratification by biological condition and batch; inference runtime; percentage of traps accepted automatically; and human review burden.

**Analyst:** What error matters most for JM105-style biology?

**HEARTH:** A condition-specific error that changes the inferred interaction or survival difference. A visually ugly confusion matrix can be tolerable if the endpoint remains unbiased; a subtle systematic bias across glucose/genotype is not.

**Repository consequence:** promotion is endpoint-gated and condition-aware.

---

## Socratic Round IX — Why keep the human UI if automation is the goal?

**Analyst:** Would true automation make `human_classifier_ui.py` obsolete?

**HEARTH:** Not immediately and perhaps not entirely. A mature pipeline needs a trusted adjudication surface for uncertain traps, new domains, benchmark creation, active learning, and audit. Removing the human tool too early destroys the mechanism for discovering model failure.

**Analyst:** What should change over time?

**HEARTH:** Human labor should move from frame-by-frame scoring to targeted review of disagreements and out-of-distribution cases. The UI should evolve into a QA/adjudication console rather than disappear.

**Repository consequence:** the UI is a first-class pipeline component, not legacy baggage.

---

## Socratic Round X — What is the moat?

**Analyst:** Is the most advanced neural architecture the commercially valuable asset?

**HEARTH:** Not by itself. Models are replaceable. The stronger moat candidate is the integrated corpus, trap-native representation, biological ontology, event semantics, benchmark set, QA loop, workflow integration, and know-how required to run the assay reliably from acquisition through phenotype.

**Analyst:** What therefore should GitHub make obvious?

**HEARTH:** The interfaces and accumulated know-how of the system, while separating source from raw scientific data and unresolved proprietary/ownership-sensitive material.

**Repository consequence:** documentation centers the pipeline and benchmark rather than marketing one network.

---

## Socratic Round XI — Open standards versus ownership

**Analyst:** Do historical importance and economic ownership require opposite repository strategies?

**HEARTH:** No. That is the zero-sum framing to avoid. Common event semantics, benchmark definitions, and interoperable outputs can increase coordination value and scientific adoption. High-quality execution, adaptation, QA, assay operations, specialized data, chip know-how, and legitimately controlled software can retain economic value around an open or semi-open measurement standard.

**Analyst:** Should the repository therefore be public now?

**HEARTH:** No. Openness is irreversible and the relevant ETH/data/software/know-how ownership questions are not resolved here. Keep the canonical working repository private. Decide later which neutral standards or benchmark artifacts should be public after scientific validation and rights review.

**Repository consequence:** private by default; disclosure is a deliberate later decision, not an incidental Git setting.

---

## Socratic Round XII — Why link OpenBIS?

**Analyst:** Why should GitHub know about the JM-136 OpenBIS experiment at all?

**HEARTH:** Because code without experimental identity becomes detached from the scientific record. The OpenBIS identifier gives the software project a stable laboratory referent without copying raw data into GitHub.

**Analyst:** Why not copy the whole ELN record?

**HEARTH:** Canonicality. OpenBIS remains the experimental record; GitHub remains the software/provenance record. Link rather than duplicate.

**Repository consequence:** README carries the exact OpenBIS link; no duplicate laboratory ledger is created.

---

## Socratic Round XIII — Why not use the literal folder name with a colon?

**Analyst:** The human title is `JM-136: Automating Aging Chip Analysis`. Why is the filesystem folder `jm136-aging-chip-analysis`?

**HEARTH:** Because Jordan uses Windows, where `:` is illegal in ordinary file names. A repository path that cannot be checked out cleanly on the primary workstation is bad engineering. Preserve the exact human title in README and metadata, not as an incompatible path.

**Repository consequence:** cross-platform path; exact project title preserved inside it.

---

## Socratic Round XIV — What belongs in GitHub?

**Analyst:** Should raw trap TIFFs, annotations, `.keras` models, and recovered Excel files be committed for reproducibility?

**HEARTH:** Not by default. Large/sensitive scientific data and mutable annotation workbooks belong in approved scientific storage. Generated model binaries can be registered by hash and location or a controlled artifact system. GitHub should contain source, bounded configuration, tests, schemas, benchmark summaries, and provenance documentation.

**Analyst:** Does excluding binaries weaken reproducibility?

**HEARTH:** Only if provenance is poor. Record model hashes, code revision, training data snapshot hash, split definition, configuration, and output metrics. Reproducibility is not equivalent to putting every byte into Git.

**Repository consequence:** aggressive `.gitignore`; explicit artifact provenance.

---

## Socratic Round XV — How should paths be handled?

**Analyst:** Several scripts contain Windows drive letters or historic Mac paths. Should ingestion rewrite them now?

**HEARTH:** No. The exact snapshot should preserve what was actually run. The refactored pipeline should later replace machine-specific defaults with a single configuration layer and environment/CLI overrides.

**Analyst:** Why keep ugly historic paths at all?

**HEARTH:** Because changing them while claiming to preserve a source version obscures provenance. A strict engineer would rather see an ugly truthful snapshot plus a clean refactor than a cosmetically improved pseudo-history.

**Repository consequence:** source snapshot is immutable evidence; future `src/` package owns cleaned configuration.

---

## Socratic Round XVI — What should tests protect first?

**Analyst:** What are the first regression tests worth writing?

**HEARTH:** Not neural-network unit tests. First protect the scientific invariants: frame-number mapping, display-to-raw coordinate conversion, trap filename identity, `Late Bud -> Mother/Early` division counting including permitted gap bridging, death bridging semantics, censoring, end-of-stack behavior, and agreement between UI and trainer implementations.

**Analyst:** What comes after that?

**HEARTH:** Small deterministic fixtures for preprocessing, event collapse/decoder behavior, and benchmark/report generation. Then model smoke tests using tiny synthetic arrays, not proprietary raw stacks.

**Repository consequence:** refactor begins only after these tests exist.

---

## Socratic Round XVII — How should model experiments be compared?

**Analyst:** Can each new script define its own split and metric?

**HEARTH:** No. That produces narrative drift. A benchmark harness should own the evaluation contract, and model experiments should produce predictions consumed by that harness. Otherwise every architecture can accidentally choose a favorable definition.

**Analyst:** What should be the champion rule?

**HEARTH:** The current demonstrated champion remains the fallback. A candidate becomes champion only if it adds value on pre-declared grouped endpoint metrics without creating unacceptable condition-specific bias or review burden.

**Repository consequence:** benchmark history is append-only evidence; higher version numbers have no authority.

---

## Socratic Round XVIII — How should active learning work?

**Analyst:** If the final ambition is full automation, is routing uncertain traps to Jordan a failure?

**HEARTH:** No. Targeted adjudication is positive-sum. The model handles easy repeated structure; the human spends attention where disagreement has maximal information value; those adjudications become future training/benchmark examples. The failure would be requiring broad frame-by-frame review while calling the system automated.

**Repository consequence:** uncertainty/review queue is a planned output contract, and percentage auto-accepted is a core benchmark metric.

---

## Socratic Round XIX — What would make this historically important rather than merely useful?

**Analyst:** What separates an excellent Barral-lab tool from a field-level contribution?

**HEARTH:** External transportability and coordination. If a frozen measurement system produces biologically valid RLS across new chips, strains, batches, operators, and eventually another lab—and if others preserve its endpoint definitions or benchmark because compatibility is useful—it begins to function as infrastructure rather than private automation.

**Analyst:** What evidence should the repository accumulate toward that possibility?

**HEARTH:** Versioned benchmark sets, reproducible scoring, domain-shift challenge results, operator-independent runs, schema stability, and documented external use. The future intron-free yeast strain is particularly valuable as a severe prospective domain-shift challenge if an untouched subset can be preserved.

**Repository consequence:** design now for transportability, but do not claim adoption before it exists.

---

## Socratic Round XX — What should the next refactor look like?

**Analyst:** If a strict coder took over tomorrow, what would they want after the source snapshot?

**HEARTH:** A small package with one definition of each scientific contract, explicit configuration, typed records, CLI entry points, tests, and dependency locking. They would not want nine trainers importing one another by filename and reproducing core biology in copy-pasted functions.

**Analyst:** Why not perform that refactor immediately in this handoff?

**HEARTH:** Because the current priority is faithful preservation and an honest benchmark while the model direction is still changing. First freeze source and behavior. Then refactor with tests so every semantic change is deliberate.

**Repository consequence:** proposed future architecture:

```text
src/aging_chip/
  domain/        # RLS, events, death, censoring, identity
  io/            # TIFF/annotation/config readers
  geometry/      # coordinate systems, trap anchors, alignment
  annotation/    # UI/adjudication interfaces
  models/        # state/event/death model interfaces
  evaluation/    # grouped splits, metrics, benchmark harness
  pipeline/      # end-to-end orchestration
  cli/           # executable entry points

tests/
  fixtures/
  test_domain_semantics.py
  test_frame_mapping.py
  test_geometry.py
  test_benchmark_contract.py
```

This is a destination, not a rewritten pseudo-history.

---

## Final HEARTH judgment

JM-136 should be kept as **provenance-critical candidate platform infrastructure**, not a loose ML experiment and not yet a public product repository. Preserve the exact development record; protect the current working annotation/state/death machinery; let new RLS experts compete against the best demonstrated baseline; centralize biological semantics behind regression tests before refactoring; keep raw scientific data and generated model binaries outside Git; and make grouped endpoint validation plus bounded human-QC burden the promotion gate.

This structure serves both poles of the North Star without forcing a false tradeoff. Scientifically, it makes the work legible, reproducible, benchmarkable, and potentially adoptable. Strategically, it preserves the integrated know-how and provenance required to establish contribution, negotiate ownership, support publication, and—if rights and demand align—turn the aging-chip workflow into a scalable platform rather than a one-off lab script.
