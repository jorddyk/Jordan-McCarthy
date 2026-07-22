# 2026-07-22 worm manifest, proxy and submission provenance

## Final canonical state

- Pipeline version: `2026-07-22.3`.
- Manifest gate: passed.
- Full driver: `8176077`.
- Reference job: `8176647`.
- Sample array: `8176648`, 158 tasks, maximum four concurrent.
- Aggregate job: `8176649`.
- At the time of canonicalization, the reference job was running and the sample
  and aggregate jobs were waiting on valid Slurm dependencies.
- No generated biological result was available or committed.

## Failures and exact repairs

1. Driver `8160067` failed before metadata creation because the compute node had
   no external NCBI connectivity. The submission path was repaired to load
   Euler's `eth_proxy` in the login shell and export it to Slurm jobs.
2. Proxy test `8162692` failed with `module: not found` because `sbatch --wrap`
   invoked a shell without the module function. A real Bash compute-node test
   inheriting proxy variables succeeded as job `8163755` with HTTP 200 from
   NCBI E-utilities.
3. Driver `8164359` reached NCBI but failed because
   `work/metadata/raw_metadata/` was not created before the first write. The
   manifest builder now creates the directory explicitly.
4. Driver `8168348` correctly stopped at the manifest gate. The original
   resolver searched SRA using `GSE` accessions directly and pooled incompatible
   `SRP089617` arms.
5. Manifest v2 resolved GEO samples through linked SRA experiment accessions,
   separated baseline, NMD-RNAi and `hrpu-1` arms in `SRP089617`, and recognized
   `Y41E3.11` as `hrpu-1`. Validation job `8172968` then identified one remaining
   missing group: `n2_ev` in `GSE240821`.
6. Manifest v3 replaced the GSE240821 free-text classifier with an exact GSM
   allowlist for the five prespecified groups. The metadata-only gate passed,
   after which the full workflow was submitted.

## Scientific boundaries retained

- `NMD_hidden = IR(NMD off) - IR(matched NMD on)`.
- `candidate_score = min(aging_effect, CR_suppression)` is not used without the
  complete JM105 factorial.
- `eat-2` is genetic dietary restriction; `daf-2` is reduced insulin/IGF
  signalling.
- The five studies remain separate; no cross-study subtraction is allowed.
- SMG-2 IP is association evidence, not proof of cytoplasmic export or
  translation.

## Repository exclusions

No FASTQ/SRA, BAM/BAI, STAR index, logs, scratch folders, caches, archives,
compiled Python files, generated figures or unreviewed biological outputs are
committed.
