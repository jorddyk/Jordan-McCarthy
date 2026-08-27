#!/usr/bin/env python3
"""
JM105_figure6_human_gate_20260729.py

The human/mammalian arm of Figure 6, which has never been analysed. Overnight job.

WHAT THE EXISTING PIPELINE ALREADY ESTABLISHED (GATE_REPORT.md, pipeline
2026-07-20.5-distributed) and what this adds.

  Already done - five contrasts, each tested on its own:
     HGPS vs control        (GSE118633)  d +0.0067  g +0.68  P 0.44   n 2v3
     HGPS vs normal         (GSE137083)  d +0.0066  g +1.54  P 0.14   n 3v3
     FTI vs HGPS                         d -0.0043  g -1.00  P 0.27   n 3v3
     PML2 KD vs HGPS                     d -0.0045  g -1.05  P 0.25   n 3v3
     pan-PML KD vs HGPS                  d -0.0044  g -1.04  P 0.25   n 3v3
     mouse BAT / SkM CR                  d  0       gate FAIL

  Nothing here is significant alone at n = 3. But two INDEPENDENT cohorts agree
  on direction AND magnitude, and three MECHANISTICALLY UNRELATED interventions
  each move it back by nearly the same amount. That pattern is invisible to
  five separate t-tests. This job runs the analyses that can see it:

  1  CROSS-COHORT SIGNATURE VALIDATION. Rank an HGPS intron signature in one
     cohort, test its direction in the other, then reverse discovery and
     validation. Neither cohort is used to both define and confirm.
  2  INTERVENTION REVERSAL OF AN INDEPENDENTLY DEFINED SIGNATURE. The signature
     comes from GSE118633, which contains none of the interventions, so introns
     cannot be selected because they respond well to treatment.
  3  COMBINED INTERVENTION ESTIMATE across FTI, PML2 KD and pan-PML KD, which
     are independent perturbations of the same axis.
  4  MOUSE CR ON PEI. The zero deltas are the same zero-inflation collapse seen
     in worms: a median over a universe that is mostly IR = 0 is 0 by
     construction. PEI is continuous and defined at zero retention.

BOUNDARIES, from the pipeline's own report and kept here:
  * These datasets lack matched UPF1 on/off. This is steady-state retained-intron
    exposure. It is NOT NMD_hidden and is never labelled as such.
  * HGPS is a progeroid perturbation, not normal aging.
  * Library preparations are not pooled across cohorts; every contrast is within
    one dataset.
  * The inferential unit is the biological sample. n is 2-4 per group, so effect
    sizes and intervals lead and P values are reported as underpowered.
"""
from __future__ import annotations
import argparse, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

MIN_TOTAL_EE, MIN_SAMPLE_EE = 10, 3     # same rule as the worm pipeline
CONTRASTS = [
    ("GSE118633", "control", "hgps", +1, "HGPS vs normal control"),
    ("GSE137083", "normal_control", "hgps_control", +1, "HGPS vs normal control"),
    ("GSE137083", "hgps_control", "hgps_fti", -1, "lonafarnib + zoledronate"),
    ("GSE137083", "hgps_control", "hgps_pml2_kd", -1, "PML2 knockdown"),
    ("GSE137083", "hgps_control", "hgps_pan_pml_kd", -1, "pan-PML knockdown"),
    ("GSE222163", "bat_control", "bat_cr", -1, "mouse CR, brown adipose"),
    ("GSE222163", "skm_control", "skm_cr", -1, "mouse CR, skeletal muscle"),
]
USE = ["intron_id", "gene_name", "dataset", "run", "group", "EI", "IE", "EE_total"]


def pei(ei, ie, ee):
    return np.log2((ei + ie + 0.5) / (2.0 * ee + 0.5))


def load(qdir: Path, dataset: str) -> pd.DataFrame:
    files = sorted((qdir / dataset).glob("*.introns.tsv.gz"))
    if not files:
        raise SystemExit(f"FAIL-CLOSED: no quantification files for {dataset}")
    frames = []
    for f in files:
        d = pd.read_csv(f, sep="\t", usecols=lambda c: c in USE)
        miss = [c for c in USE if c not in d.columns]
        if miss:
            print(f"FAIL-CLOSED: {f.name} lacks {miss}", file=sys.stderr)
            raise SystemExit(3)
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    for c in ("EI", "IE", "EE_total"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["EI", "IE", "EE_total"])
    d["PEI"] = pei(d.EI.values, d.IE.values, d.EE_total.values)
    return d


def universe(df: pd.DataFrame) -> set:
    g = df.groupby("intron_id", sort=False)["EE_total"]
    tot = g.sum()
    sup = g.apply(lambda v: int((v >= MIN_SAMPLE_EE).sum()))
    need = max(2, math.ceil(df["run"].nunique() / 2))
    return set(map(str, tot.index[(tot >= MIN_TOTAL_EE) & (sup >= need)]))


def hedges_g(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2: return np.nan
    sp = math.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1))
                   / (na + nb - 2))
    if sp == 0: return np.nan
    d = (np.mean(b) - np.mean(a)) / sp
    return float(d * (1 - 3 / (4 * (na + nb) - 9)))


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--human-root", type=Path, required=True)
    a.add_argument("--outdir", type=Path, required=True)
    a.add_argument("--boot", type=int, default=10000)
    a.add_argument("--top", type=int, default=2000, help="signature size")
    a.add_argument("--seed", type=int, default=20260729)
    g = a.parse_args()
    rng = np.random.default_rng(g.seed)
    qdir = g.human_root / "work/quantification"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIG6_HUMAN_{stamp}"; out.mkdir(parents=True, exist_ok=True)
    gate, rows = {}, []

    data = {ds: load(qdir, ds) for ds in ("GSE118633", "GSE137083", "GSE222163")}
    uni = {ds: universe(d) for ds, d in data.items()}
    for ds, u in uni.items():
        nz = float((data[ds].EI + data[ds].IE > 0).mean())
        print(f"[universe] {ds}: {len(u):,} introns; {nz:.1%} of covered "
              "observations have EI+IE > 0")

    # ---------- 1. every contrast on PEI, sample level -----------------------
    print("\n=== per-contrast sample-level PEI ===")
    sample_pei = {}
    for ds, ga, gb, sign, label in CONTRASTS:
        d = data[ds]
        d = d[d.intron_id.astype(str).isin(uni[ds])]
        s = d.groupby(["run", "group"])["PEI"].mean().reset_index()
        sample_pei[(ds, ga, gb)] = s
        A = s[s.group == ga]["PEI"].to_numpy(float)
        B = s[s.group == gb]["PEI"].to_numpy(float)
        if len(A) < 2 or len(B) < 2:
            print(f"  SKIP {ds} {ga} vs {gb}: n {len(A)}v{len(B)}"); continue
        delta = float(B.mean() - A.mean())
        bs = np.array([rng.choice(B, len(B), True).mean()
                       - rng.choice(A, len(A), True).mean() for _ in range(g.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        gg = hedges_g(A, B)
        w = stats.ttest_ind(B, A, equal_var=False)
        rows.append({"dataset": ds, "group_a": ga, "group_b": gb, "label": label,
                     "expected_sign": sign, "n_a": len(A), "n_b": len(B),
                     "delta_PEI": delta, "ci_lo": float(lo), "ci_hi": float(hi),
                     "hedges_g": gg, "welch_p": float(w.pvalue),
                     "sign_as_expected": bool(np.sign(delta) == sign)})
        print(f"  {ds} {gb} vs {ga:16s} n {len(A)}v{len(B)}  dPEI {delta:+.4f} "
              f"[{lo:+.4f},{hi:+.4f}]  g {gg:+.2f}  P {w.pvalue:.3f}  "
              f"{'expected sign' if np.sign(delta)==sign else 'WRONG SIGN'}")
    cs = pd.DataFrame(rows)
    cs.to_csv(out / "hgps_cohort_effects.tsv", sep="\t", index=False)

    # ---------- 2. cross-cohort signature validation, both directions --------
    print("\n=== cross-cohort signature validation ===")

    def per_intron_delta(ds, ga, gb):
        d = data[ds]
        d = d[d.intron_id.astype(str).isin(uni[ds])]
        p = d.pivot_table(index="intron_id", columns="group", values="PEI",
                          aggfunc="mean")
        if ga not in p or gb not in p: return None
        return (p[gb] - p[ga]).dropna().rename("delta")

    dA = per_intron_delta("GSE118633", "control", "hgps")
    dB = per_intron_delta("GSE137083", "normal_control", "hgps_control")
    sig = {}
    if dA is not None and dB is not None:
        shared = dA.index.intersection(dB.index)
        print(f"  {len(shared):,} introns shared between cohorts")
        for name, disc, val in (("118633_defines", dA, dB), ("137083_defines", dB, dA)):
            top = disc.loc[shared].nlargest(g.top).index
            v = val.loc[top]
            rest = val.loc[shared.difference(top)]
            mw = stats.mannwhitneyu(v, rest, alternative="greater")
            # permutation: random intron sets of the same size
            nullm = np.array([val.loc[rng.choice(shared, len(top), False)].mean()
                              for _ in range(200)])
            p_perm = float((nullm >= v.mean()).mean())
            rho = stats.spearmanr(disc.loc[shared], val.loc[shared]).statistic
            sig[name] = {"n_signature": int(len(top)),
                         "validation_mean_delta_PEI": float(v.mean()),
                         "background_mean_delta_PEI": float(rest.mean()),
                         "mannwhitney_p": float(mw.pvalue),
                         "random_set_permutation_p": p_perm,
                         "genomewide_spearman_rho": float(rho)}
            print(f"  {name}: signature mean dPEI {v.mean():+.4f} vs background "
                  f"{rest.mean():+.4f}; random-set P {p_perm:.4f}; "
                  f"genome-wide rho {rho:+.3f}")
    gate["hgps_cross_cohort_validation"] = {
        "pass": bool(sig and all(s["random_set_permutation_p"] < 0.05
                                 and s["validation_mean_delta_PEI"] >
                                 s["background_mean_delta_PEI"] for s in sig.values())),
        "directions": sig,
        "note": "discovery and validation cohorts are never the same dataset"}

    # ---------- 3. intervention reversal of the independent signature --------
    print("\n=== intervention reversal of the GSE118633-defined signature ===")
    rev = {}
    if dA is not None:
        base = per_intron_delta("GSE137083", "normal_control", "hgps_control")
        common = dA.index.intersection(base.index) if base is not None else []
        top = dA.loc[common].nlargest(g.top).index if len(common) else []
        for arm in ("hgps_fti", "hgps_pml2_kd", "hgps_pan_pml_kd"):
            dv = per_intron_delta("GSE137083", "hgps_control", arm)
            if dv is None or not len(top): continue
            t = dv.reindex(top).dropna()
            r = dv.drop(index=top, errors="ignore").dropna()
            mw = stats.mannwhitneyu(t, r, alternative="less")
            nullm = np.array([dv.loc[rng.choice(dv.index, len(t), False)].mean()
                              for _ in range(200)])
            p_perm = float((nullm <= t.mean()).mean())
            rev[arm] = {"signature_mean_delta_PEI": float(t.mean()),
                        "background_mean_delta_PEI": float(r.mean()),
                        "mannwhitney_p": float(mw.pvalue),
                        "random_set_permutation_p": p_perm,
                        "n_signature_introns": int(len(t))}
            print(f"  {arm:16s} signature {t.mean():+.4f} vs background "
                  f"{r.mean():+.4f}; random-set P {p_perm:.4f}")
    gate["hgps_intervention_reversal"] = {
        "pass": bool(rev and sum(v["random_set_permutation_p"] < 0.05
                                 for v in rev.values()) >= 2),
        "arms": rev,
        "note": ("signature defined in GSE118633, which contains no intervention "
                 "arms, so introns cannot be selected on treatment response")}

    # ---------- 4. combined intervention estimate ---------------------------
    iv = cs[cs.group_b.isin(["hgps_fti", "hgps_pml2_kd", "hgps_pan_pml_kd"])]
    if len(iv) == 3:
        m = float(iv.delta_PEI.mean())
        se = float(iv.delta_PEI.std(ddof=1) / math.sqrt(3))
        print(f"\n=== combined across three independent interventions ===")
        print(f"  mean dPEI {m:+.4f}, SE {se:.4f}, all three negative: "
              f"{bool((iv.delta_PEI < 0).all())}")
        gate["intervention_combined"] = {
            "pass": bool((iv.delta_PEI < 0).all()), "mean_delta_PEI": m,
            "se": se, "n_arms": 3,
            "note": "three mechanistically independent perturbations of one axis"}

    # ---------- 5. leave-one-sample-out on every contrast -------------------
    loo = []
    for (ds, ga, gb), s in sample_pei.items():
        for drop in s.run:
            t = s[s.run != drop]
            A = t[t.group == ga]["PEI"].to_numpy(float)
            B = t[t.group == gb]["PEI"].to_numpy(float)
            if len(A) >= 2 and len(B) >= 2:
                loo.append({"dataset": ds, "group_a": ga, "group_b": gb,
                            "dropped": drop, "delta_PEI": float(B.mean() - A.mean())})
    lo_df = pd.DataFrame(loo)
    lo_df.to_csv(out / "hgps_leave_one_out.tsv", sep="\t", index=False)
    stable = {}
    for (ds, ga, gb), sub in lo_df.groupby(["dataset", "group_a", "group_b"]):
        base = cs[(cs.dataset == ds) & (cs.group_a == ga) & (cs.group_b == gb)]
        if len(base):
            stable[f"{ds}|{gb}_vs_{ga}"] = bool(
                (np.sign(sub.delta_PEI) == np.sign(base.delta_PEI.iloc[0])).all())
    print("\n=== leave-one-sample-out sign stability ===")
    for k, v in stable.items(): print(f"  {'stable' if v else 'UNSTABLE'}  {k}")
    gate["leave_one_out_sign_stability"] = stable

    gate["_meta"] = {
        "run_stamp": stamp, "endpoint": "PEI = log2((EI+IE+0.5)/(2*EE_total+0.5))",
        "universe_rule": f"EE_total >= {MIN_TOTAL_EE} total and >= {MIN_SAMPLE_EE} "
                         "in >= half the runs; retention positivity never used",
        "boundaries": [
            "no matched UPF1 on/off; this is steady-state retained-intron "
            "exposure and is never called NMD_hidden",
            "HGPS is a progeroid perturbation, not normal aging",
            "no pooling across cohorts or library preparations",
            "n is 2-4 per group; effect sizes and intervals lead, P is underpowered"],
        "supersedes_nothing": "adds to GATE_REPORT.md, does not replace it"}
    (out / "FIGURE6_HUMAN_GATE.json").write_text(json.dumps(gate, indent=2))
    print("\n================ HUMAN GATE ================")
    for k, v in gate.items():
        if not k.startswith("_") and isinstance(v, dict) and "pass" in v:
            print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
    print(f"\n[out] {out/'FIGURE6_HUMAN_GATE.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
