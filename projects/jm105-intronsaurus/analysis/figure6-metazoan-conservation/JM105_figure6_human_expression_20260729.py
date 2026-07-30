#!/usr/bin/env python3
"""
JM105_figure6_human_expression_20260729.py

Expression-confounder test for the mammalian arm, and a rewrite of two gate
rules that were too weak.

WHY THIS EXISTS

  The human job reported two PASSes that do not survive inspection:

  hgps_cross_cohort_validation PASSED on "signature mean > background mean"
      signature +0.4562 vs background +0.3614, random-set P 0.0000
      BUT the genome-wide Spearman between the two cohorts' per-intron effects
      is -0.009 across 102,931 introns. There is no per-intron agreement at all.
      The background itself sits at +0.36, i.e. essentially every intron moves
      up, so with n = 100,000 a trivial difference returns P = 0. A uniform
      genome-wide shift satisfies that rule. The rule was wrong.

  intervention_combined PASSED on "all three arms negative"
      but the background moves -0.21 to -0.49 in every arm, so everything is
      negative. Uninformative as written.

  CORRECTED RULES, fixed here before the run:
    cross-cohort  requires PER-INTRON RANK CONCORDANCE between cohorts, with a
                  bootstrap interval excluding zero. A global shift moves every
                  intron equally and cannot create rank agreement.
    intervention  requires the signature to move MORE than background, tested as
                  a difference of differences against random intron sets of the
                  same size.

  One encouraging fact makes this worth doing carefully: the human data are far
  denser than the worm data - 39.2% of covered observations in GSE137083 have
  EI + IE > 0, versus 6.6% in worms. The pseudocount therefore dominates far
  less, so a real signal has a genuine chance of surviving. That is also why the
  effect sizes grew on PEI (FTI g -1.87, PML2 KD g -1.98).

  And one warning: GSE222163 bat_cr came out WRONG SIGN on PEI, CI excluding
  zero. Mouse caloric restriction raising retained-intron exposure in brown
  adipose contradicts the prespecified direction. That is reported, not hidden.

TESTS
  T1  is library depth confounded with group, within each contrast
  T2  does the per-intron PEI difference track the per-intron expression
      difference
  T3  contrast effects after residualizing per-intron PEI on per-intron
      log2 EE_total
  T4  RANK-BASED contrast: within-library percentile ranks, immune to any global
      shift by construction
  T5  depth-invariant proportion IR on introns with real unspliced evidence
  G1  corrected cross-cohort concordance
  G2  corrected intervention reversal

BOUNDARY, unchanged: these datasets have no matched UPF1 on/off. This is
steady-state retained-intron exposure and is never called NMD_hidden.
"""
from __future__ import annotations
import argparse, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

MIN_TOTAL_EE, MIN_SAMPLE_EE = 10, 3
CONTRASTS = [
    ("GSE118633", "control", "hgps", +1),
    ("GSE137083", "normal_control", "hgps_control", +1),
    ("GSE137083", "hgps_control", "hgps_fti", -1),
    ("GSE137083", "hgps_control", "hgps_pml2_kd", -1),
    ("GSE137083", "hgps_control", "hgps_pan_pml_kd", -1),
    ("GSE222163", "bat_control", "bat_cr", -1),
    ("GSE222163", "skm_control", "skm_cr", -1),
]
USE = ["intron_id", "gene_name", "dataset", "run", "group", "EI", "IE", "EE_total"]


def load(qdir, ds):
    fs = sorted((qdir / ds).glob("*.introns.tsv.gz"))
    if not fs:
        print(f"FAIL-CLOSED: no files for {ds}", file=sys.stderr); raise SystemExit(2)
    d = pd.concat([pd.read_csv(f, sep="\t", usecols=lambda c: c in USE)
                   for f in fs], ignore_index=True)
    miss = [c for c in USE if c not in d.columns]
    if miss:
        print(f"FAIL-CLOSED: {ds} lacks {miss}", file=sys.stderr); raise SystemExit(3)
    for c in ("EI", "IE", "EE_total"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["EI", "IE", "EE_total"])
    d["PEI"] = np.log2((d.EI + d.IE + .5) / (2 * d.EE_total + .5))
    d["lexp"] = np.log2(d.EE_total + 1)
    den = (d.EI + d.IE) + 2 * d.EE_total
    d["IR"] = np.where(den > 0, (d.EI + d.IE) / den, np.nan)
    return d


def universe(df):
    g = df.groupby("intron_id", sort=False)["EE_total"]
    tot, sup = g.sum(), g.apply(lambda v: int((v >= MIN_SAMPLE_EE).sum()))
    need = max(2, math.ceil(df["run"].nunique() / 2))
    return set(map(str, tot.index[(tot >= MIN_TOTAL_EE) & (sup >= need)]))


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--human-root", type=Path, required=True)
    a.add_argument("--outdir", type=Path, required=True)
    a.add_argument("--boot", type=int, default=4000)
    a.add_argument("--nrand", type=int, default=500)
    a.add_argument("--top", type=int, default=2000)
    a.add_argument("--min-unspliced", type=int, default=10)
    a.add_argument("--seed", type=int, default=20260729)
    g = a.parse_args()
    rng = np.random.default_rng(g.seed)
    qdir = g.human_root / "work/quantification"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIG6_HEXPR_{stamp}"; out.mkdir(parents=True, exist_ok=True)
    R = {}

    data, uni = {}, {}
    for ds in ("GSE118633", "GSE137083", "GSE222163"):
        data[ds] = load(qdir, ds)
        uni[ds] = universe(data[ds])
        nz = float((data[ds].EI + data[ds].IE > 0).mean())
        print(f"[universe] {ds}: {len(uni[ds]):,} introns, {nz:.1%} non-zero")
        data[ds] = data[ds][data[ds].intron_id.astype(str).isin(uni[ds])]

    # ---------- T1 depth versus group -----------------------------------
    print("\n=== T1  is depth confounded with group? ===")
    dep = []
    for ds, ga, gb, sgn in CONTRASTS:
        d = data[ds]
        t = d.groupby(["run", "group"])["EE_total"].sum().reset_index()
        A = t[t.group == ga]["EE_total"].to_numpy(float)
        B = t[t.group == gb]["EE_total"].to_numpy(float)
        if len(A) < 2 or len(B) < 2: continue
        lfc = float(np.log2(B.mean() / A.mean()))
        dep.append({"dataset": ds, "a": ga, "b": gb, "log2_depth_ratio": lfc})
        print(f"  {ds} {gb:16s} vs {ga:16s}  log2 depth ratio {lfc:+.3f}"
              + ("   CONFOUNDED" if abs(lfc) > .3 else ""))
    R["T1_depth_by_group"] = dep
    pd.DataFrame(dep).to_csv(out / "T1_depth_by_group.tsv", sep="\t", index=False)

    # ---------- per-intron deltas ---------------------------------------
    def deltas(ds, ga, gb, col):
        d = data[ds]
        p = d.pivot_table(index="intron_id", columns="group", values=col,
                          aggfunc="mean")
        if ga not in p or gb not in p: return None
        return (p[gb] - p[ga]).dropna()

    # ---------- T2/T3 residualize ---------------------------------------
    print("\n=== T2/T3  does PEI track expression, and does it survive? ===")
    rows = []
    for ds, ga, gb, sgn in CONTRASTS:
        dp, de = deltas(ds, ga, gb, "PEI"), deltas(ds, ga, gb, "lexp")
        if dp is None or de is None: continue
        i = dp.index.intersection(de.index)
        x, y = de.loc[i].to_numpy(float), dp.loc[i].to_numpy(float)
        ok = np.isfinite(x) & np.isfinite(y)
        r = stats.spearmanr(x[ok], y[ok])
        X = np.column_stack([np.ones(ok.sum()), x[ok]])
        b, *_ = np.linalg.lstsq(X, y[ok], rcond=None)
        res = y[ok] - X @ b
        raw_mean, res_mean = float(np.mean(y[ok])), float(np.mean(res))
        rows.append({"dataset": ds, "a": ga, "b": gb, "expected_sign": sgn,
                     "n_introns": int(ok.sum()),
                     "spearman_PEI_vs_expression": float(r.statistic),
                     "expression_beta": float(b[1]),
                     "mean_delta_PEI_raw": raw_mean,
                     "mean_delta_PEI_residual": res_mean,
                     "fraction_retained": float(abs(res_mean) / abs(raw_mean))
                     if raw_mean else np.nan})
        print(f"  {ds} {gb:16s} rho(PEI,expr) {r.statistic:+.3f}  "
              f"mean dPEI raw {raw_mean:+.4f} -> residual {res_mean:+.4f}")
    t23 = pd.DataFrame(rows)
    t23.to_csv(out / "T2_T3_residualized_contrasts.tsv", sep="\t", index=False)
    R["T2_T3"] = rows

    # ---------- T4 rank-based contrast ----------------------------------
    print("\n=== T4  rank-based contrast (immune to any global shift) ===")
    rk = []
    for ds, ga, gb, sgn in CONTRASTS:
        d = data[ds]
        p = d.pivot_table(index="intron_id", columns="run", values="IR")
        meta = d.drop_duplicates("run").set_index("run")["group"].reindex(p.columns)
        Rk = p.rank(axis=0, pct=True, na_option="keep")
        A = Rk.loc[:, (meta == ga).to_numpy()].mean(axis=1)
        B = Rk.loc[:, (meta == gb).to_numpy()].mean(axis=1)
        dd = (B - A).dropna()
        if not len(dd): continue
        nA, nB = int((meta == ga).sum()), int((meta == gb).sum())
        w = stats.wilcoxon(dd) if len(dd) > 20 else None
        rk.append({"dataset": ds, "a": ga, "b": gb, "expected_sign": sgn,
                   "n_a": nA, "n_b": nB, "mean_rank_shift": float(dd.mean()),
                   "median_rank_shift": float(dd.median()),
                   "frac_up": float((dd > 0).mean()),
                   "wilcoxon_p": float(w.pvalue) if w else np.nan})
        print(f"  {ds} {gb:16s} mean rank shift {dd.mean():+.5f}  "
              f"{100*(dd>0).mean():.1f}% up  n {nA}v{nB}")
    pd.DataFrame(rk).to_csv(out / "T4_rank_contrasts.tsv", sep="\t", index=False)
    R["T4_rank_based"] = rk

    # ---------- G1 corrected cross-cohort concordance --------------------
    print("\n=== G1  CORRECTED cross-cohort test: per-intron rank concordance ===")
    dA = deltas("GSE118633", "control", "hgps", "PEI")
    dB = deltas("GSE137083", "normal_control", "hgps_control", "PEI")
    g1 = {}
    if dA is not None and dB is not None:
        i = dA.index.intersection(dB.index)
        rho = float(stats.spearmanr(dA.loc[i], dB.loc[i]).statistic)
        bs = np.array([stats.spearmanr(dA.loc[s], dB.loc[s]).statistic
                       for s in (rng.choice(i, len(i), True) for _ in range(200))])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        # same on residualized deltas
        def resid(ds, ga, gb):
            dp, de = deltas(ds, ga, gb, "PEI"), deltas(ds, ga, gb, "lexp")
            j = dp.index.intersection(de.index)
            X = np.column_stack([np.ones(len(j)), de.loc[j].to_numpy(float)])
            b, *_ = np.linalg.lstsq(X, dp.loc[j].to_numpy(float), rcond=None)
            return pd.Series(dp.loc[j].to_numpy(float) - X @ b, index=j)
        rA, rB = resid("GSE118633", "control", "hgps"), \
                 resid("GSE137083", "normal_control", "hgps_control")
        k = rA.index.intersection(rB.index)
        rho_res = float(stats.spearmanr(rA.loc[k], rB.loc[k]).statistic)
        print(f"  {len(i):,} shared introns")
        print(f"  raw per-intron Spearman between cohorts  {rho:+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]")
        print(f"  after residualizing on expression        {rho_res:+.4f}")
        g1 = {"n_shared": int(len(i)), "spearman_raw": rho,
              "ci95": [float(lo), float(hi)], "spearman_residualized": rho_res,
              "pass": bool(lo > 0.05),
              "old_rule": "signature mean > background mean - satisfied by a "
                          "uniform shift; withdrawn",
              "new_rule": "per-intron Spearman between cohorts, CI excluding 0.05"}
    R["G1_cross_cohort_concordance"] = g1

    # ---------- G2 corrected intervention reversal -----------------------
    print("\n=== G2  CORRECTED reversal: signature must move MORE than background ===")
    g2 = {}
    if dA is not None:
        top = dA.nlargest(g.top).index
        for arm in ("hgps_fti", "hgps_pml2_kd", "hgps_pan_pml_kd"):
            dv = deltas("GSE137083", "hgps_control", arm, "PEI")
            if dv is None: continue
            t = dv.reindex(top).dropna()
            bg = dv.drop(index=top, errors="ignore").dropna()
            diff = float(t.mean() - bg.mean())
            null = np.array([float(dv.loc[rng.choice(dv.index, len(t), False)].mean()
                                   - bg.mean()) for _ in range(g.nrand)])
            p = float((null <= diff).mean())
            g2[arm] = {"signature_mean": float(t.mean()),
                       "background_mean": float(bg.mean()),
                       "difference_of_differences": diff,
                       "random_set_p_more_negative": p,
                       "moves_more_than_background": bool(diff < 0 and p < .05)}
            print(f"  {arm:16s} signature {t.mean():+.4f}  background "
                  f"{bg.mean():+.4f}  difference {diff:+.4f}  P {p:.4f}")
        g2["pass"] = bool(sum(v.get("moves_more_than_background", False)
                              for v in g2.values() if isinstance(v, dict)) >= 2)
        g2["old_rule"] = ("all three arms negative - but background is negative "
                          "in all three, so uninformative; withdrawn")
    R["G2_intervention_reversal"] = g2

    # ---------- T5 depth-invariant endpoint ------------------------------
    print("\n=== T5  depth-invariant IR on introns with real unspliced evidence ===")
    t5 = []
    for ds, ga, gb, sgn in CONTRASTS:
        d = data[ds]
        uns = d.groupby("intron_id")[["EI", "IE"]].sum().sum(axis=1)
        keep = set(uns.index[uns >= g.min_unspliced].astype(str))
        dd = d[d.intron_id.astype(str).isin(keep)]
        s = dd.groupby(["run", "group"])["IR"].mean().reset_index()
        A = s[s.group == ga]["IR"].to_numpy(float)
        B = s[s.group == gb]["IR"].to_numpy(float)
        if len(A) < 2 or len(B) < 2: continue
        delta = float(B.mean() - A.mean())
        bs = np.array([rng.choice(B, len(B), True).mean()
                       - rng.choice(A, len(A), True).mean() for _ in range(g.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        t5.append({"dataset": ds, "a": ga, "b": gb, "expected_sign": sgn,
                   "n_introns": len(keep), "delta_IR": delta,
                   "ci_lo": float(lo), "ci_hi": float(hi),
                   "sign_as_expected": bool(np.sign(delta) == sgn),
                   "ci_excludes_zero": bool(lo * hi > 0)})
        print(f"  {ds} {gb:16s} dIR {delta:+.5f} [{lo:+.5f},{hi:+.5f}]  "
              f"{'expected' if np.sign(delta)==sgn else 'WRONG SIGN'}"
              f"{'  CI excludes 0' if lo*hi>0 else ''}")
    pd.DataFrame(t5).to_csv(out / "T5_depth_invariant.tsv", sep="\t", index=False)
    R["T5_depth_invariant"] = t5

    R["_meta"] = {"run_stamp": stamp,
                  "withdrawn_gates": ["hgps_cross_cohort_validation as first "
                                      "written", "intervention_combined"],
                  "boundary": ("no matched UPF1 on/off; steady-state retained-"
                               "intron exposure, never NMD_hidden"),
                  "note": ("human data are 39% non-zero versus 6.6% in worms, so "
                           "the pseudocount dominates far less here")}
    (out / "FIGURE6_HUMAN_EXPRESSION.json").write_text(json.dumps(R, indent=2))
    print("\n================ SUMMARY ================")
    print(f"  G1 cross-cohort concordance: "
          f"{'PASS' if g1.get('pass') else 'FAIL'}")
    print(f"  G2 intervention reversal:    "
          f"{'PASS' if g2.get('pass') else 'FAIL'}")
    print(f"\n[out] {out/'FIGURE6_HUMAN_EXPRESSION.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
