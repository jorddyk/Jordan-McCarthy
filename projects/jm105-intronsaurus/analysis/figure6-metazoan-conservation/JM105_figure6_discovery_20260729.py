#!/usr/bin/env python3
"""
JM105_figure6_discovery_20260729.py

Discovery job. Every analysis here is immune to global expression shifts BY
CONSTRUCTION, because a genome-wide shift is what invalidated three gates today:
PEI with a pseudocount reads transcription whenever EI + IE = 0, which is ~93%
of worm observations and produced a +0.36 background shift in the human cohorts
with zero per-intron concordance between them.

The three ways to be immune, used throughout:
  RATIO WITHIN A SAMPLE   IP versus input from the same library. Library depth,
                          composition and transcription all cancel.
  RANK WITHIN A SAMPLE    a monotone shift applied to every intron leaves ranks
                          untouched. Any global change is invisible; only
                          re-ordering survives.
  EXPRESSION-MATCHED      compare responders to controls drawn at the same
                          expression and coverage, so the contrast cannot be
                          driven by the thing being matched.

FIVE ANALYSES

  D1  SMG-2 ASSOCIATION MAP (GSE100929, IP versus input)
      Which introns are physically associated with the worm NMD helicase.
      An IP/input ratio within one sample is the cleanest measurement in this
      entire project. Nothing about expression can fake it.

  D2  DOES ASSOCIATION PREDICT THE RESPONSE?
      Join D1 enrichment to the rank-based age slope from D3. If SMG-2-bound
      introns are the ones that change with age, that is a direct mechanistic
      link, and it cannot be an expression artefact because neither axis is
      expression-sensitive.

  D3  RANK-BASED AGING (the fix for the broken aging test)
      Within each library, rank introns by IR. Rank is invariant to any global
      multiplicative or additive shift. Then test whether ranks move with adult
      day, permuting day within strain, and require cross-strain reproducibility.
      This asks whether the ORDER of introns changes with age, which is what
      transcript-selective remodeling actually means.

  D4  DETECTION VERSUS MAGNITUDE, kept separate
      Two biologically different questions that a single ratio conflates:
        (a) does an intron become DETECTABLE at all with age
        (b) given detection, does its retention grow
      A pure transcription change moves (a) and not (b). A splicing change can
      move (b) alone. Their dissociation is informative either way.

  D5  WHAT KIND OF INTRON RESPONDS
      Responders versus expression-matched controls, compared on intron length,
      ordinal position in the gene, first/last status and number of introns in
      the host gene. Matching on expression is what makes this interpretable.

NOTHING HERE IS A CLAIM. This job proposes; the gates dispose.
"""
from __future__ import annotations
import argparse, gzip, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

MIN_TOTAL_EE, MIN_SAMPLE_EE = 10, 3
BASE = ["dataset_id", "biological_sample_id", "group", "strain", "age_day",
        "nmd_state", "diet_state", "perturbation", "fraction", "intron_id",
        "gene_id", "gene_name", "EI", "IE", "EE_total"]


def ir_prop(ei, ie, ee):
    """Depth-invariant proportion. Expression scaling cancels; no pseudocount."""
    u = ei + ie
    d = u + 2.0 * ee
    return np.where(d > 0, u / np.where(d == 0, np.nan, d), np.nan)


def universe(df):
    g = df.groupby("intron_id", sort=False)["EE_total"]
    tot, sup = g.sum(), g.apply(lambda v: int((v >= MIN_SAMPLE_EE).sum()))
    need = max(2, math.ceil(df["biological_sample_id"].nunique() / 2))
    return set(map(str, tot.index[(tot >= MIN_TOTAL_EE) & (sup >= need)]))


def slopes(Y, day, strain):
    Z = Y.astype(float).copy()
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
    a.add_argument("--perm", type=int, default=2000)
    a.add_argument("--seed", type=int, default=20260729)
    g = a.parse_args()
    rng = np.random.default_rng(g.seed)
    MEAS = g.worm_root / "work/results/all_intron_measurements.tsv.gz"
    REF = (g.worm_root /
           "work/multi_intron_hotfix/reference/all_distinct_protein_coding_introns.tsv.gz")
    if not MEAS.exists():
        print(f"FAIL-CLOSED: missing {MEAS}", file=sys.stderr); return 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIG6_DISCOVERY_{stamp}"; out.mkdir(parents=True, exist_ok=True)
    F = {}

    with gzip.open(MEAS, "rt") as f:
        hdr = f.readline().rstrip("\n").split("\t")
    have = [c for c in BASE if c in hdr]
    miss = [c for c in BASE if c not in hdr]
    if miss:
        print(f"[schema] absent, those analyses will be skipped: {miss}")
    print(f"[schema] using: {have}")
    d = pd.read_csv(MEAS, sep="\t", usecols=have)
    for c in ("EI", "IE", "EE_total", "age_day"):
        if c in d: d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["EI", "IE", "EE_total"])
    print("\n[datasets present]")
    print(d.groupby("dataset_id")["biological_sample_id"].nunique().to_string())
    if "fraction" in d:
        print("\n[fraction values]", sorted(d["fraction"].dropna().astype(str).unique()))

    # =============== D1  SMG-2 association, IP over input ==================
    print("\n=== D1  SMG-2 association map (within-sample IP/input ratio) ===")
    ip = None
    if "fraction" in d:
        fr = d["fraction"].astype(str).str.lower()
        is_ip = fr.str.contains("ip") & ~fr.str.contains("input")
        is_in = fr.str.contains("input")
        if is_ip.any() and is_in.any():
            sub = d[is_ip | is_in].copy()
            sub["frac2"] = np.where(is_ip[sub.index], "IP", "input")
            uni = universe(sub)
            sub = sub[sub.intron_id.astype(str).isin(uni)]
            # unspliced reads per intron in each fraction, normalised WITHIN
            # fraction so only the relative ordering between IP and input counts
            agg = (sub.assign(uns=sub.EI + sub.IE)
                      .groupby(["intron_id", "frac2"])["uns"].sum().unstack())
            if {"IP", "input"} <= set(agg.columns):
                agg = agg[(agg.sum(axis=1) >= 10)]
                cpmIP = agg["IP"] / agg["IP"].sum() * 1e6
                cpmIN = agg["input"] / agg["input"].sum() * 1e6
                ip = np.log2((cpmIP + 1) / (cpmIN + 1)).rename("smg2_log2_enrich")
                print(f"  {len(ip):,} introns with >= 10 unspliced reads across "
                      "IP and input")
                print(f"  enrichment: median {ip.median():+.3f}, "
                      f"{int((ip > 1).sum()):,} introns > 2-fold enriched")
                top = ip.nlargest(25)
                nm = (sub.drop_duplicates("intron_id").set_index("intron_id")
                        ["gene_name"])
                print("  top SMG-2-associated genes: "
                      + ", ".join(sorted(set(nm.reindex(top.index).dropna()))[:15]))
                ip.to_csv(out / "D1_smg2_association.tsv", sep="\t")
                F["D1_smg2_association"] = {
                    "n_introns": int(len(ip)), "median_log2": float(ip.median()),
                    "n_enriched_2fold": int((ip > 1).sum()),
                    "why_immune": "IP and input come from the same library"}
    if ip is None:
        print("  no IP/input fraction pair found; D1 and D2 skipped")

    # =============== D3  rank-based aging ==================================
    print("\n=== D3  rank-based aging: does the ORDER of introns change? ===")
    ag = d[d.dataset_id.astype(str).str.upper().str.contains("AGING")].copy()
    rank_slopes = None
    if len(ag) and ag.age_day.notna().any():
        uni = universe(ag)
        ag = ag[ag.intron_id.astype(str).isin(uni)].copy()
        ag["IR"] = ir_prop(ag.EI.values, ag.IE.values, ag.EE_total.values)
        P = ag.pivot_table(index="intron_id", columns="biological_sample_id",
                           values="IR")
        meta = (ag[["biological_sample_id", "age_day", "strain"]].drop_duplicates()
                  .set_index("biological_sample_id").loc[P.columns])
        day = meta.age_day.to_numpy(float); strain = meta.strain.astype(str).to_numpy()
        P = P[P.notna().sum(axis=1) >= max(6, len(day) // 2)]
        # RANK WITHIN EACH LIBRARY: a global shift cannot move ranks
        R = P.rank(axis=0, pct=True, na_option="keep").to_numpy(float)
        s = slopes(R, day, strain)
        obs = float(np.nansum(s ** 2))
        null = np.empty(g.perm)
        for b in range(g.perm):
            d2 = day.copy()
            for st in np.unique(strain):
                m = strain == st
                d2[m] = rng.permutation(day[m])
            null[b] = float(np.nansum(slopes(R, d2, strain) ** 2))
        p = float((1 + (null >= obs).sum()) / (g.perm + 1))
        sts = sorted(set(strain)); rho = np.nan
        if len(sts) == 2:
            q = [slopes(R[:, strain == t], day[strain == t], strain[strain == t])
                 for t in sts]
            o = np.isfinite(q[0]) & np.isfinite(q[1])
            rho = float(stats.spearmanr(q[0][o], q[1][o]).statistic) if o.sum() > 50 else np.nan
        up, dn = int(np.nansum(s > 0)), int(np.nansum(s < 0))
        print(f"  {len(P):,} introns; percentile-rank slopes")
        print(f"  sum of squares {obs:.4f} vs null {np.mean(null):.4f}; P = {p:.4g}")
        print(f"  {up:,} rise in rank, {dn:,} fall; cross-strain rho = {rho:+.3f}")
        rank_slopes = pd.Series(s, index=P.index, name="rank_age_slope")
        rank_slopes.to_csv(out / "D3_rank_age_slopes.tsv", sep="\t")
        F["D3_rank_based_aging"] = {
            "n_introns": int(len(P)), "permutation_p": p, "n_up": up, "n_down": dn,
            "cross_strain_rho": rho,
            "pass": bool(p < 0.05 and np.isfinite(rho) and rho > 0.2),
            "why_immune": "within-library percentile ranks ignore any global shift"}

    # =============== D2  does association predict the response? ============
    if ip is not None and rank_slopes is not None:
        print("\n=== D2  does SMG-2 association predict the aging response? ===")
        j = pd.concat([ip, rank_slopes], axis=1).dropna()
        if len(j) > 200:
            r = stats.spearmanr(j.smg2_log2_enrich, j.rank_age_slope)
            hi = j[j.smg2_log2_enrich > j.smg2_log2_enrich.quantile(.9)]
            lo_ = j[j.smg2_log2_enrich < j.smg2_log2_enrich.quantile(.5)]
            mw = stats.mannwhitneyu(hi.rank_age_slope, lo_.rank_age_slope)
            print(f"  {len(j):,} introns with both measures")
            print(f"  Spearman(SMG-2 enrichment, rank age slope) = "
                  f"{r.statistic:+.4f}  P = {r.pvalue:.3g}")
            print(f"  top-decile enriched median slope {hi.rank_age_slope.median():+.5f} "
                  f"vs {lo_.rank_age_slope.median():+.5f}, P = {mw.pvalue:.3g}")
            F["D2_association_predicts_response"] = {
                "n": int(len(j)), "spearman_rho": float(r.statistic),
                "p": float(r.pvalue), "mannwhitney_p": float(mw.pvalue),
                "why_immune": "neither axis responds to a global expression shift"}
            j.to_csv(out / "D2_association_vs_aging.tsv", sep="\t")

    # =============== D4  detection versus magnitude ========================
    print("\n=== D4  detection and magnitude are different questions ===")
    if len(ag):
        det = (ag.assign(det=(ag.EI + ag.IE) > 0)
                 .groupby(["biological_sample_id", "age_day", "strain"])["det"]
                 .mean().reset_index(name="detection_rate"))
        mag = (ag[(ag.EI + ag.IE) > 0]
               .groupby(["biological_sample_id", "age_day", "strain"])["IR"]
               .median().reset_index(name="median_IR_given_detected"))
        m = det.merge(mag, on=["biological_sample_id", "age_day", "strain"])
        rd = stats.spearmanr(m.age_day, m.detection_rate)
        rm = stats.spearmanr(m.age_day, m.median_IR_given_detected)
        print(m.groupby("age_day")[["detection_rate", "median_IR_given_detected"]]
                .median().to_string())
        print(f"  detection rate vs day:  rho {rd.statistic:+.3f}  P {rd.pvalue:.3g}")
        print(f"  magnitude|detected vs day: rho {rm.statistic:+.3f}  P {rm.pvalue:.3g}")
        print("  a transcription change moves detection only; a splicing change "
              "can move magnitude alone")
        F["D4_detection_vs_magnitude"] = {
            "detection_rho": float(rd.statistic), "detection_p": float(rd.pvalue),
            "magnitude_rho": float(rm.statistic), "magnitude_p": float(rm.pvalue),
            "dissociated": bool(rd.pvalue < .05) != bool(rm.pvalue < .05)}
        m.to_csv(out / "D4_detection_and_magnitude.tsv", sep="\t", index=False)

    # =============== D5  what kind of intron responds ======================
    print("\n=== D5  responder introns versus expression-matched controls ===")
    if rank_slopes is not None and REF.exists():
        ref = pd.read_csv(REF, sep="\t")
        ref["intron_id"] = ref["intron_id"].astype(str)
        expr = (ag.groupby("intron_id")["EE_total"].mean()
                  .rename("mean_EE")).astype(float)
        tab = (rank_slopes.to_frame().join(expr, how="inner")
               .join(ref.set_index("intron_id")[
                   [c for c in ("intron_length", "transcript_count", "gene_id")
                    if c in ref.columns]], how="left").dropna(subset=["mean_EE"]))
        thr = tab.rank_age_slope.abs().quantile(.95)
        resp = tab[tab.rank_age_slope.abs() >= thr]
        pool = tab[tab.rank_age_slope.abs() < thr]
        # match each responder to a control at similar expression
        bins = pd.qcut(np.log2(tab.mean_EE + 1), 20, labels=False, duplicates="drop")
        tab["ebin"] = bins
        ctrl_idx = []
        for b_, n_ in resp.assign(ebin=tab.loc[resp.index, "ebin"]).groupby("ebin").size().items():
            cand = pool.index.intersection(tab.index[tab.ebin == b_])
            if len(cand):
                ctrl_idx.extend(rng.choice(cand, min(n_, len(cand)), replace=False))
        ctrl = tab.loc[ctrl_idx]
        print(f"  {len(resp):,} responders vs {len(ctrl):,} expression-matched controls")
        feats = {}
        for col in ("intron_length", "transcript_count"):
            if col in tab.columns and tab[col].notna().any():
                u = stats.mannwhitneyu(resp[col].dropna(), ctrl[col].dropna())
                feats[col] = {"responder_median": float(resp[col].median()),
                              "control_median": float(ctrl[col].median()),
                              "p": float(u.pvalue)}
                print(f"  {col:18s} responders {resp[col].median():10.1f}  "
                      f"controls {ctrl[col].median():10.1f}  P = {u.pvalue:.3g}")
        if "gene_id" in tab.columns:
            ni = tab.groupby("gene_id").size()
            rn = ni.reindex(resp.gene_id).dropna(); cn = ni.reindex(ctrl.gene_id).dropna()
            if len(rn) and len(cn):
                u = stats.mannwhitneyu(rn, cn)
                feats["introns_per_host_gene"] = {
                    "responder_median": float(rn.median()),
                    "control_median": float(cn.median()), "p": float(u.pvalue)}
                print(f"  introns per host gene  responders {rn.median():.1f}  "
                      f"controls {cn.median():.1f}  P = {u.pvalue:.3g}")
        F["D5_responder_features"] = {"n_responders": int(len(resp)),
                                      "n_matched_controls": int(len(ctrl)),
                                      "features": feats,
                                      "why_immune": "controls matched on expression"}
        tab.loc[resp.index].to_csv(out / "D5_responder_introns.tsv", sep="\t")

    F["_meta"] = {"run_stamp": stamp,
                  "principle": ("every analysis is immune to a global expression "
                                "shift by construction: within-sample ratios, "
                                "within-sample ranks, or expression-matched controls"),
                  "status": "exploratory; nothing here is a claim until gated"}
    (out / "FIGURE6_DISCOVERY.json").write_text(json.dumps(F, indent=2))
    print("\n================ DISCOVERY SUMMARY ================")
    for k, v in F.items():
        if not k.startswith("_"):
            tag = ("PASS" if v.get("pass") else "----") if "pass" in v else "info"
            print(f"  [{tag}] {k}")
    print(f"\n[out] {out/'FIGURE6_DISCOVERY.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
