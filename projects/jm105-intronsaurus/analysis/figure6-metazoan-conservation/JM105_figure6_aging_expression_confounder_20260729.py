#!/usr/bin/env python3
"""
JM105_figure6_aging_expression_confounder_20260729.py

Does the worm aging result measure retention, or transcription?

THE PROBLEM, stated as arithmetic rather than as a worry.
    PEI = log2((EI + IE + 0.5) / (2 * EE_total + 0.5))
    About 96% of covered observations have EI + IE = 0, so for those the
    endpoint reduces to
    PEI = log2(0.5 / (2 * EE_total + 0.5))
    which is a pure function of expression. If a gene is transcribed less in old
    worms, EE_total falls and PEI rises mechanically, with no change in
    retention at all. A drop in EE_total from 100 to 10 moves PEI by 3.3 units
    on its own.

    Worse, this does not go away with replication. Both strains downregulate the
    same genes with age, so shared expression trajectories produce exactly the
    cross-strain slope agreement (rho = +0.43) that was offered as evidence the
    effect is real. Reproducibility cannot discriminate here.

WHAT THIS JOB TESTS
  T1  Is sequencing depth confounded with age? Per-library EE_total against day.
  T2  Does the PEI age slope track the expression age slope, per intron?
  T3  Does the result survive residualization on the expression slope?
      Magnitude statistic and cross-strain rho recomputed on residuals, with the
      same within-strain day permutation.
  T4  Does it hold on a DEPTH-INVARIANT endpoint? Restricted to introns with
      real unspliced evidence, using the proportion
          IR = (EI + IE) / ((EI + IE) + 2 * EE_total)
      Expression scaling cancels in a proportion. It does not cancel in a
      pseudocounted log-ratio.

VERDICT RULE, fixed before the run:
    The aging claim survives only if T3 keeps the magnitude significant AND
    cross-strain rho > 0.2, AND T4 reproduces the direction independently.
    If T2 shows a strong negative correlation and T3 collapses, panel B is an
    expression artefact and must not be rendered.
"""
from __future__ import annotations
import argparse, gzip, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

MIN_TOTAL_EE, MIN_SAMPLE_EE = 10, 3
NEED = ["biological_sample_id", "strain", "age_day", "intron_id", "gene_id",
        "gene_name", "EI", "IE", "EE_total"]


def fixed_universe(df):
    g = df.groupby("intron_id", sort=False)["EE_total"]
    tot, sup = g.sum(), g.apply(lambda v: int((v >= MIN_SAMPLE_EE).sum()))
    need = max(2, math.ceil(df["biological_sample_id"].nunique() / 2))
    return set(map(str, tot.index[(tot >= MIN_TOTAL_EE) & (sup >= need)]))


def slope_matrix(Y, day, strain, centre_by_strain=True):
    """Per-row slope on day, optionally centring within strain first."""
    Z = Y.astype(float).copy()
    if centre_by_strain:
        for s in np.unique(strain):
            m = strain == s
            Z[:, m] -= np.nanmean(Z[:, m], axis=1, keepdims=True)
    dc = day - day.mean()
    num = np.nansum(Z * dc, axis=1)
    den = np.nansum(np.isfinite(Z) * dc ** 2, axis=1)
    return np.where(den > 0, num / np.where(den == 0, np.nan, den), np.nan)


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--worm-root", type=Path, required=True)
    a.add_argument("--outdir", type=Path, required=True)
    a.add_argument("--perm", type=int, default=5000)
    a.add_argument("--min-unspliced", type=int, default=10)
    a.add_argument("--seed", type=int, default=20260729)
    g = a.parse_args()
    rng = np.random.default_rng(g.seed)
    AG = g.worm_root / "work/final_figure/cache/AGING.collapsed.tsv.gz"
    if not AG.exists():
        print(f"FAIL-CLOSED: missing {AG}", file=sys.stderr); return 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIG6_EXPR_{stamp}"; out.mkdir(parents=True, exist_ok=True)
    res = {}

    with gzip.open(AG, "rt") as f:
        hdr = f.readline().rstrip("\n").split("\t")
    miss = [c for c in NEED if c not in hdr]
    if miss:
        print(f"FAIL-CLOSED: AGING.collapsed lacks {miss}", file=sys.stderr)
        for i, c in enumerate(hdr, 1): print(f"  {i:>3} {c}", file=sys.stderr)
        return 3
    d = pd.read_csv(AG, sep="\t", usecols=NEED)
    for c in ("EI", "IE", "EE_total", "age_day"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["EI", "IE", "EE_total", "age_day"])
    uni = fixed_universe(d)
    d = d[d.intron_id.astype(str).isin(uni)].copy()
    d["PEI"] = np.log2((d.EI + d.IE + 0.5) / (2 * d.EE_total + 0.5))
    d["lexp"] = np.log2(d.EE_total + 1)
    print(f"[universe] {len(uni):,} introns")

    # ---------------- T1: depth versus age -------------------------------
    print("\n=== T1  is sequencing depth confounded with age? ===")
    lib = (d.groupby(["biological_sample_id", "age_day", "strain"])["EE_total"]
             .sum().reset_index(name="total_EE"))
    r_dep = stats.spearmanr(lib.age_day, lib.total_EE)
    print(lib.groupby("age_day")["total_EE"]
             .agg(["count", "median"]).to_string())
    print(f"  Spearman(day, library EE_total) = {r_dep.statistic:+.3f}  "
          f"P = {r_dep.pvalue:.3g}")
    res["T1_depth_vs_age"] = {"spearman_rho": float(r_dep.statistic),
                              "p": float(r_dep.pvalue),
                              "confounded": bool(abs(r_dep.statistic) > .3
                                                 and r_dep.pvalue < .05)}
    lib.to_csv(out / "library_depth_by_day.tsv", sep="\t", index=False)

    # ---------------- build matrices --------------------------------------
    P = d.pivot_table(index="intron_id", columns="biological_sample_id", values="PEI")
    E = d.pivot_table(index="intron_id", columns="biological_sample_id", values="lexp")
    E = E.reindex(index=P.index, columns=P.columns)
    meta = (d[["biological_sample_id", "age_day", "strain"]].drop_duplicates()
              .set_index("biological_sample_id").loc[P.columns])
    day = meta.age_day.to_numpy(float); strain = meta.strain.astype(str).to_numpy()
    keep = P.notna().sum(axis=1) >= max(6, len(day) // 2)
    P, E = P[keep], E[keep]
    Yp, Ye = P.to_numpy(float), E.to_numpy(float)
    sp, se = slope_matrix(Yp, day, strain), slope_matrix(Ye, day, strain)
    ok = np.isfinite(sp) & np.isfinite(se)
    print(f"\n  {ok.sum():,} introns with both a PEI slope and an expression slope")

    # ---------------- T2: does PEI track expression? ----------------------
    print("\n=== T2  does the PEI age slope track the expression age slope? ===")
    r_t2 = stats.spearmanr(sp[ok], se[ok])
    frac = float(np.mean(np.sign(sp[ok]) != np.sign(se[ok])))
    print(f"  Spearman(PEI slope, log2 EE_total slope) = {r_t2.statistic:+.4f}  "
          f"P = {r_t2.pvalue:.3g}")
    print(f"  {frac:.1%} of introns have opposite-signed PEI and expression slopes")
    res["T2_pei_tracks_expression"] = {
        "spearman_rho": float(r_t2.statistic), "p": float(r_t2.pvalue),
        "fraction_opposite_sign": frac,
        "interpretation": ("a strongly negative rho means PEI is largely reading "
                           "transcription, because the pseudocount numerator is "
                           "fixed when EI+IE = 0")}

    # ---------------- T3: residualize on expression -----------------------
    print("\n=== T3  does the aging signal survive residualization? ===")
    X = np.column_stack([np.ones(ok.sum()), se[ok]])
    beta, *_ = np.linalg.lstsq(X, sp[ok], rcond=None)
    resid = np.full_like(sp, np.nan)
    resid[ok] = sp[ok] - X @ beta
    obs_raw = float(np.nansum(sp ** 2)); obs_res = float(np.nansum(resid ** 2))
    print(f"  slope of PEI on expression = {beta[1]:+.4f}")
    print(f"  sum of squares  raw {obs_raw:.1f}  ->  residual {obs_res:.1f}  "
          f"({100*obs_res/obs_raw:.1f}% retained)")
    null = np.empty(g.perm)
    for b in range(g.perm):
        d2 = day.copy()
        for s in np.unique(strain):
            m = strain == s
            d2[m] = rng.permutation(day[m])
        s1, s2 = slope_matrix(Yp, d2, strain), slope_matrix(Ye, d2, strain)
        o2 = np.isfinite(s1) & np.isfinite(s2)
        if o2.sum() < 100: null[b] = np.nan; continue
        X2 = np.column_stack([np.ones(o2.sum()), s2[o2]])
        b2, *_ = np.linalg.lstsq(X2, s1[o2], rcond=None)
        r2 = s1[o2] - X2 @ b2
        null[b] = float(np.nansum(r2 ** 2))
    p_res = float((1 + np.nansum(null >= obs_res)) / (g.perm + 1))
    print(f"  permutation on residuals (day within strain): P = {p_res:.4g}")
    st = sorted(set(strain)); rho_res = np.nan
    if len(st) == 2:
        def resid_one(s):
            m = strain == s
            a1 = slope_matrix(Yp[:, m], day[m], strain[m])
            a2 = slope_matrix(Ye[:, m], day[m], strain[m])
            o = np.isfinite(a1) & np.isfinite(a2)
            Xo = np.column_stack([np.ones(o.sum()), a2[o]])
            bo, *_ = np.linalg.lstsq(Xo, a1[o], rcond=None)
            r = np.full_like(a1, np.nan); r[o] = a1[o] - Xo @ bo
            return r
        r1, r2 = resid_one(st[0]), resid_one(st[1])
        o = np.isfinite(r1) & np.isfinite(r2)
        rho_res = float(stats.spearmanr(r1[o], r2[o]).statistic) if o.sum() > 50 else np.nan
    print(f"  cross-strain reproducibility of RESIDUAL slopes: rho = {rho_res:+.3f}"
          "   (raw was +0.430)")
    res["T3_residualized"] = {
        "expression_beta": float(beta[1]), "ss_raw": obs_raw, "ss_residual": obs_res,
        "fraction_retained": float(obs_res / obs_raw), "permutation_p": p_res,
        "cross_strain_rho_residual": rho_res,
        "survives": bool(p_res < 0.05 and np.isfinite(rho_res) and rho_res > 0.2)}

    # ---------------- T4: depth-invariant endpoint ------------------------
    print("\n=== T4  depth-invariant endpoint on introns with real evidence ===")
    uns = d.groupby("intron_id")[["EI", "IE"]].sum().sum(axis=1)
    strong = set(uns.index[uns >= g.min_unspliced].astype(str))
    d4 = d[d.intron_id.astype(str).isin(strong)].copy()
    den = (d4.EI + d4.IE) + 2 * d4.EE_total
    d4["IR"] = np.where(den > 0, (d4.EI + d4.IE) / den, np.nan)
    print(f"  {len(strong):,} introns with >= {g.min_unspliced} unspliced reads "
          "summed across libraries")
    if len(strong) < 200:
        print("  too few introns for a depth-invariant test")
        res["T4_depth_invariant"] = {"pass": False, "reason": "too few introns"}
    else:
        P4 = d4.pivot_table(index="intron_id", columns="biological_sample_id",
                            values="IR").reindex(columns=P.columns)
        k4 = P4.notna().sum(axis=1) >= max(6, len(day) // 2)
        P4 = P4[k4]
        s4 = slope_matrix(P4.to_numpy(float), day, strain)
        obs4 = float(np.nansum(s4 ** 2))
        n4 = np.empty(min(g.perm, 2000))
        for b in range(len(n4)):
            d2 = day.copy()
            for s in np.unique(strain):
                m = strain == s
                d2[m] = rng.permutation(day[m])
            n4[b] = float(np.nansum(slope_matrix(P4.to_numpy(float), d2, strain) ** 2))
        p4 = float((1 + (n4 >= obs4).sum()) / (len(n4) + 1))
        up4 = int(np.nansum(s4 > 0)); dn4 = int(np.nansum(s4 < 0))
        rho4 = np.nan
        if len(st) == 2:
            A = P4.to_numpy(float)
            q1 = slope_matrix(A[:, strain == st[0]], day[strain == st[0]],
                              strain[strain == st[0]])
            q2 = slope_matrix(A[:, strain == st[1]], day[strain == st[1]],
                              strain[strain == st[1]])
            o = np.isfinite(q1) & np.isfinite(q2)
            rho4 = float(stats.spearmanr(q1[o], q2[o]).statistic) if o.sum() > 50 else np.nan
        print(f"  {len(P4):,} testable; sum of squares {obs4:.4f} vs null "
              f"{np.mean(n4):.4f}; P = {p4:.4g}")
        print(f"  bidirectional: {up4:,} up, {dn4:,} down; cross-strain "
              f"rho = {rho4:+.3f}")
        res["T4_depth_invariant"] = {
            "pass": bool(p4 < 0.05 and np.isfinite(rho4) and rho4 > 0.2),
            "n_introns": int(len(P4)), "permutation_p": p4, "n_up": up4,
            "n_down": dn4, "cross_strain_rho": rho4,
            "endpoint": "IR proportion; expression scaling cancels"}
        pd.Series(s4, index=P4.index, name="IR_age_slope").to_csv(
            out / "aging_slopes_depth_invariant.tsv", sep="\t")

    surv = bool(res["T3_residualized"]["survives"]
                and res.get("T4_depth_invariant", {}).get("pass"))
    res["VERDICT"] = {
        "aging_panel_survives_expression_confounder": surv,
        "rule": ("T3 residual magnitude P < 0.05 AND residual cross-strain rho "
                 "> 0.2 AND T4 independently reproduces on a depth-invariant "
                 "endpoint"),
        "if_false": ("the aging result is an expression artefact of the PEI "
                     "pseudocount; panel B must not be rendered")}
    (out / "FIGURE6_EXPRESSION_CONFOUNDER.json").write_text(json.dumps(res, indent=2))
    print("\n================ VERDICT ================")
    print(f"  aging survives the expression confounder: {surv}")
    print(f"\n[out] {out/'FIGURE6_EXPRESSION_CONFOUNDER.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
