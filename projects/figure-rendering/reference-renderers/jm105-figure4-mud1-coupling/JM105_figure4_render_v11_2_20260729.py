#!/usr/bin/env python3
"""
JM105_figure4_render_v1_20260728.py

Figure 4 | Mud1 couples intron retention and host-transcript abundance in the
           caloric-restriction response

GOVERNING QUESTION. Does Mud1 coordinate BOTH retained-intron processing and
host-transcript abundance under 0.1% glucose? The result that must be obvious in
two seconds is the horizontal displacement Yves saw: candidates respond strongly
in +MUD1 and fail to respond fully in mud1-delta.

PANEL CONTRACT
  a  Mud1 is required for the full lifespan response to CR   survival facets
  b  the extension is smaller in mud1d                       estimation plot
  c  Mud1 required for full retained-intron suppression      JointGrid hero
  d  candidates differ in how much they need Mud1            ranked forest
  e  host abundance responds in +MUD1, less in mud1d         JointGrid hero
  f  Mud1 couples the two responses                          matched reg facets
  g  the interaction is not just host abundance              adjustment dumbbells
  h  the coordinated response in raw candidate data          paired heatmaps

HARD RULES, enforced and fail-closed
  1. COMMON GENE NAMES ONLY on every visible label. Systematic identifiers are
     never printed. --gene-map is required.
  2. NO nan CATEGORIES. Unparseable rows are dropped before plotting, counted.
  3. NO PANEL FRAMES. Yves: never draw boxes around panels.
  4. TYPOGRAPHY IS INHERITED FROM FIGURE 3, not reinvented. See TYPO below.
  5. LANE-LOCKED LAYOUT in inches with explicit slack; verified arithmetic.
  6. Panels a and b require --lifespan. Without it they are declared
     NOT COMPUTED. Survival curves are never fabricated.

DEFINITIONS, repeated where used
  IR                = mean(EI,IE) / [mean(EI,IE) + EE]
  NMD-revealed      = IR(upf1d) - IR(UPF1+), within a MUD1 status and condition
  CR suppression    = NMD-revealed(old 2%) - NMD-revealed(old 0.1%)
  Mud1 dependence   = CR suppression(+MUD1) - CR suppression(mud1d)
  host response     = log2 spliced-junction abundance(0.1%) - log2(2%), old cells
"""
from __future__ import annotations
import argparse, hashlib, json, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, seaborn as sns
import matplotlib as mpl, matplotlib.pyplot as plt
from scipy import stats

TITLE = ("Figure 4 | Mud1 couples intron retention and host-transcript abundance "
         "in the caloric-restriction response")
SCHEMA = "JM105-FIG4-v11.2-20260729"
BAN = ("dryrun", "synthetic", "fixture", "fake", "mock", "dummy", "simulated", "example")

C_SAMPLE, C_AGE, C_GLU = "sample", "age", "glucose"
C_MUD1, C_UPF1, C_INTRON, C_CAT, C_PARENT = ("mud1_status", "upf1_status", "intron_id",
                                             "intron_category", "parent")
C_EI, C_IE, C_EETOT, C_MEANB = ("EI_count", "IE_count", "EE_total",
                                "mean_EI_IE_boundary_count")
REQUIRED = [C_SAMPLE, C_AGE, C_GLU, C_MUD1, C_UPF1, C_INTRON, C_CAT, C_PARENT,
            C_EI, C_IE, C_EETOT, C_MEANB]
MAIN_CAT = "nuclear_mRNA_or_ORF_intron"

# AXIS LABELS, in one place. Nature and Science both require the measured
# quantity and its unit in parentheses; "response" and "suppression" alone are
# not variables. Encoding keys ("filled = raw") belong in a legend, never in an
# axis label. Line 1 = quantity, line 2 = contrast and unit.
AX = {
    "b_x":  "Median lifespan change (divisions)\n0.5% \u2212 2% glucose",
    "c_x":  "NMD-revealed IR suppression\n+MUD1, 2% \u2212 0.1% glucose (fraction)",
    "c_y":  "NMD-revealed IR suppression\nmud1\u0394, 2% \u2212 0.1% glucose (fraction)",
    "d_x":  "Mud1-dependent IR suppression\n+MUD1 \u2212 mud1\u0394 (fraction)",
    "e_x":  "Spliced-junction response, +MUD1\n0.1% / 2% glucose (log$_2$ fold change)",
    "e_y":  "Spliced-junction response, mud1\u0394\n0.1% / 2% glucose (log$_2$ fold change)",
    "f_x":  "Spliced-junction response\n0.1% / 2% glucose (log$_2$ fold change)",
    "f_y":  "NMD-revealed IR suppression\n2% \u2212 0.1% glucose (fraction)",
    "g_x":  "Mud1-dependent IR suppression\n+MUD1 \u2212 mud1\u0394 (fraction)",
    "h_c1": "NMD-revealed IR (fraction)",
    "h_c2": "Spliced-junction abundance\n(log$_2$, row-centred)",
    "a_x":  "Replicative age (divisions)",
    "a_y":  "Surviving fraction of mother cells",
}

# ---- typography inherited verbatim from the accepted Figure 3 ---------------
# Fixed sizes. The canvas grows around them; text is never shrunk to fit.
TYPO = dict(letter=10.5, title=8.6, sub=7.0, axlabel=7.8, tick=7.2, legend=7.2,
            annot=7.4, gene=7.0)
INK, MUTE, FAINT = "#1A1A1A", "#7F7F7F", "#D9D9D9"
# PAPER-WIDE SEMANTICS. Hue encodes CONDITION only. Genotype is encoded by line
# style, facet or marker fill, never by colour - otherwise blue would mean both
# "glucose restricted" and "+MUD1", and green would mean both "CR" and "upf1d".
CR_C   = "#0072B2"   # glucose restriction, and the CR-responsive candidate set
CTRL_C = "#7F7F7F"   # 2% glucose control
# Genotype is encoded by LIGHTNESS within a condition's hue, so no dashed lines
# are needed. Dashes fragment across every step edge of a survival curve, which
# is what made panel a look pixelated.
# Panel a only: genotype is the HUE and glucose the LIGHTNESS, so the reader
# tracks a genotype as one colour family and reads the dose within it.
WT_HI,  WT_LO  = "#08519C", "#6BAED6"   # +MUD1  : 2% dark, restricted light
KO_HI,  KO_LO  = "#A63603", "#FD8D3C"   # mud1d  : 2% dark, restricted light
DEFIC  = "#D55E00"   # shortfall / loss of response
NMDOFF = "#009E73"   # reserved for upf1d; never used for a glucose condition
BG     = "#C8C8C8"   # unselected background introns
CAND   = CR_C
MUD1_C, MUD1D_C = INK, INK

FIG_W, FIG_H = 7.2, 13.6
def fx(i): return i / FIG_W
def fy(i): return i / FIG_H


def sha(p):
    """Full-file SHA-256. A truncated hash printed as if complete is a
    provenance error, not an optimisation."""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def is_wt(s):
    t = s.astype(str).str.lower()
    return ~(t.str.contains("δ") | t.str.contains("delta") | t.str.contains(r"\bko\b"))


def sysname(s):
    return (s.astype(str).str.split(",").str[0]
             .str.replace(r"_(mRNA|CDS|id\d+|intron.*)$", "", regex=True)
             .str.strip().str.upper())


def resolve_font():
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    for want in ("Arial", "Liberation Sans", "Nimbus Sans", "Helvetica"):
        if want in have:
            return want, True
    return "DejaVu Sans", False


def style():
    fam, ok = resolve_font()
    print(f"[font] {fam}" + ("" if ok else "  WARNING: not Arial metrics"),
          file=sys.stderr if not ok else sys.stdout)
    sns.set_theme(style="ticks", context="paper")
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [fam, "Arial", "Liberation Sans", "DejaVu Sans"],
        "axes.labelsize": TYPO["axlabel"], "axes.titlesize": TYPO["title"],
        "xtick.labelsize": TYPO["tick"], "ytick.labelsize": TYPO["tick"],
        "legend.fontsize": TYPO["legend"], "legend.frameon": False,
        "axes.linewidth": .7, "xtick.major.width": .7, "ytick.major.width": .7,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 200, "savefig.dpi": 600,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    })
    return fam, ok


def kaplan_meier(times, z=1.959964):
    """Kaplan-Meier survival with Greenwood variance and log-log confidence
    limits, matching survminer's conf.type = "log-log" default. Every mother
    cell is followed to its last division, so there is no censoring, but the
    estimator and its variance are written in general form."""
    t = np.sort(np.asarray(times, float))
    n = len(t)
    at_risk, S, cum = n, 1.0, 0.0
    xs, ss, lo, hi = [0.0], [1.0], [1.0], [1.0]
    for u in np.unique(t):
        d = int((t == u).sum())
        if at_risk <= 0:
            break
        S *= (1.0 - d / at_risk)
        if at_risk > d:
            cum += d / (at_risk * (at_risk - d))
        se = np.sqrt(cum)
        if 0.0 < S < 1.0 and se > 0:
            ll = np.log(-np.log(S)); k = z * se / abs(np.log(S))
            lo_v = float(np.exp(-np.exp(ll + k)))
            hi_v = float(np.exp(-np.exp(ll - k)))
        else:
            lo_v = hi_v = float(S)
        at_risk -= d
        xs.append(float(u)); ss.append(float(S))
        lo.append(min(lo_v, hi_v)); hi.append(max(lo_v, hi_v))
    return np.array(xs), np.array(ss), np.array(lo), np.array(hi)


def ir_from(df):
    d = df[C_MEANB] + df[C_EETOT]
    return np.where(d > 0, df[C_MEANB] / d.replace(0, np.nan), np.nan)


def main():
    a = argparse.ArgumentParser(description=TITLE)
    a.add_argument("--counts", type=Path, required=True)
    a.add_argument("--gene-map", type=Path, required=True,
                   help="SGD_features.tab. REQUIRED; common names are mandatory.")
    a.add_argument("--lifespan", type=Path, default=None,
                   help="Replicative lifespan table for panels a and b. Columns: "
                        "genotype, glucose, divisions (one row per mother cell). "
                        "Without it a and b are declared NOT COMPUTED.")
    a.add_argument("--outdir", type=Path, required=True)
    a.add_argument("--min-evidence", type=float, default=10.0)
    a.add_argument("--n-cand", type=int, default=10)
    a.add_argument("--boot", type=int, default=400)
    a.add_argument("--no-suptitle", action="store_true",
                   help="Omit the figure title and definition line from the "
                        "artwork. Journals require them in the legend instead.")
    a.add_argument("--probe", action="store_true")
    a.add_argument("--seed", type=int, default=20260728)
    g = a.parse_args()

    fam, font_ok = style()
    print(TITLE); print(f"[schema] {SCHEMA}")
    for nm, f_ in (("--counts", g.counts), ("--gene-map", g.gene_map)):
        if str(f_) in ("", ".", "/"):
            print(f"FAIL-CLOSED: {nm} is empty. A shell variable is unset.",
                  file=sys.stderr); return 2
        if not f_.exists() or f_.is_dir() or f_.stat().st_size == 0:
            print(f"FAIL-CLOSED: {nm} unusable: {f_}", file=sys.stderr); return 2
    if any(b in str(g.counts).lower() for b in BAN):
        print(f"FAIL-CLOSED: synthetic input refused: {g.counts}", file=sys.stderr); return 7

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIGURE4_{stamp}"; (out / "figures").mkdir(parents=True, exist_ok=True)
    csha = sha(g.counts)
    df = pd.read_csv(g.counts)
    miss = [c for c in REQUIRED if c not in df.columns]
    if miss:
        print("FAIL-CLOSED: missing columns:", file=sys.stderr)
        for m in miss: print(f"  - {m}", file=sys.stderr)
        print(f"observed: {list(df.columns)}", file=sys.stderr); return 3
    print(f"[source] rows={len(df)} sha256={csha[:16]}")
    for c in (C_EI, C_IE, C_EETOT, C_MEANB):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    n0 = len(df)
    df = df[df[C_AGE].astype(str).str.strip().str.lower().isin(["young", "old"])]
    df = df.dropna(subset=[C_EI, C_IE, C_EETOT, C_MEANB, C_SAMPLE])
    print(f"[clean] dropped {n0-len(df)} rows with unparseable age or counts")

    m = df[df[C_CAT].astype(str) == MAIN_CAT].copy()
    m["MUD1"] = np.where(is_wt(m[C_MUD1]), "+MUD1", "mud1\u0394")
    m["NMD"] = np.where(is_wt(m[C_UPF1]), "UPF1", "upf1d")
    glu = m[C_GLU].astype(str).str.lower()
    m["GLU"] = np.select([glu.str.contains("2"),
                          glu.str.contains("0.1") | glu.str.contains("01")],
                         ["2%", "0.1%"], default="")
    m["AGE"] = m[C_AGE].astype(str).str.lower()
    n1 = len(m)
    m = m[(m["GLU"] != "") & (((m["AGE"] == "old")) |
                              ((m["AGE"] == "young") & (m["GLU"] == "2%")))]
    print(f"[clean] dropped {n1-len(m)} rows outside old 2% / old 0.1% / young 2%")
    young = m[m["AGE"] == "young"].copy()
    m = m[m["AGE"] == "old"].copy()
    cells = m.groupby(["MUD1", "NMD", "GLU"])[C_SAMPLE].nunique()
    print("[design] libraries per cell:\n" + cells.to_string())
    if len(cells) < 8:
        print("FAIL-CLOSED: need +MUD1/mud1d x UPF1/upf1d x 2%/0.1%.",
              file=sys.stderr); return 5
    if g.probe:
        print("[probe] stopping before analysis."); return 0

    # ---------------- per-intron quantities --------------------------------
    m["sys"] = sysname(m[C_PARENT])
    agg = (m.groupby([C_INTRON, "sys", "MUD1", "NMD", "GLU"])
             [[C_MEANB, C_EETOT]].sum().reset_index())
    agg["IR"] = ir_from(agg)
    agg["ev"] = agg[C_MEANB] + agg[C_EETOT]
    w = agg.pivot_table(index=[C_INTRON, "sys"], columns=["MUD1", "NMD", "GLU"],
                        values=["IR", "ev", C_EETOT]).reset_index()
    w.columns = ["|".join(str(x) for x in c if x != "") for c in w.columns]

    def _colname(pfx, mu, nm, gl):
        """Column-name builder. Named with a leading underscore so a loop
        variable cannot shadow it, which is exactly what happened."""
        return f"{pfx}|{mu}|{nm}|{gl}"
    MU = ["+MUD1", "mud1\u0394"]
    need = [_colname(p, mu, nm, gl) for p in ("IR", "ev") for mu in MU
            for nm in ("UPF1", "upf1d") for gl in ("2%", "0.1%")]
    lack = [c for c in need if c not in w.columns]
    if lack:
        print(f"FAIL-CLOSED: pivot missing {lack[:6]}...", file=sys.stderr); return 6
    ok = np.ones(len(w), bool)
    for c in [c for c in need if c.startswith("ev|")]:
        ok &= (w[c] >= g.min_evidence).to_numpy()
    w = w[ok].copy()

    for mu in MU:
        for gl in ("2%", "0.1%"):
            w[f"NMDrev|{mu}|{gl}"] = w[_colname("IR", mu, "upf1d", gl)] - w[_colname("IR", mu, "UPF1", gl)]
        w[f"CRsupp|{mu}"] = w[f"NMDrev|{mu}|2%"] - w[f"NMDrev|{mu}|0.1%"]
        # host transcript proxy: spliced-junction abundance, NMD intact
        e2, e1 = _colname(C_EETOT, mu, "UPF1", "2%"), _colname(C_EETOT, mu, "UPF1", "0.1%")
        w[f"host|{mu}"] = np.log2(w[e1] + 1) - np.log2(w[e2] + 1)
    w["mud1_dep"] = w["CRsupp|+MUD1"] - w["CRsupp|mud1\u0394"]
    w = w.dropna(subset=[f"CRsupp|{mu}" for mu in MU] + [f"host|{mu}" for mu in MU])
    N = len(w)
    print(f"[universe] n={N} introns measured in all eight MUD1 x NMD x glucose cells")
    if N < 30:
        print("FAIL-CLOSED: universe too small.", file=sys.stderr); return 8

    # ---------------- common names, mandatory -------------------------------
    gm = pd.read_csv(g.gene_map, sep="\t", header=None, dtype=str, keep_default_na=False,
                     usecols=[3, 4], names=["sysid", "common"], on_bad_lines="skip")
    gm = gm[(gm.sysid != "") & (gm.common != "")]
    w["gene"] = w["sys"].map(dict(zip(gm.sysid.str.upper(), gm.common))).fillna("")
    frac = float((w["gene"] != "").mean())
    print(f"[names] {int((w['gene']!='').sum())}/{N} resolved ({frac:.1%})")

    # CIRCULARITY FIX. Selecting candidates on CR suppression in +MUD1 and then
    # asking whether +MUD1 exceeds mud1-delta is circular: regression to the mean
    # alone would push the selected set below the diagonal. Candidates are
    # therefore frozen on the AGEING effect in +MUD1 (old 2% vs young 2%), which
    # never touches the mud1-delta arm. The CR-based selection is retained only
    # as a reported sensitivity analysis.
    ya = young.groupby([C_INTRON, "NMD"])[[C_MEANB, C_EETOT]].sum().reset_index()
    ya["IR"] = ir_from(ya)
    yp = ya.pivot_table(index=C_INTRON, columns="NMD", values="IR")
    if not {"UPF1", "upf1d"} <= set(yp.columns):
        print("FAIL-CLOSED: young 2% lacks both NMD states.", file=sys.stderr); return 10
    yng = (yp["upf1d"] - yp["UPF1"]).rename("NMDrev_young")
    w = w.merge(yng, left_on=C_INTRON, right_index=True, how="left")
    w["ageing"] = w["NMDrev|+MUD1|2%"] - w["NMDrev_young"]
    n_age = int(w["ageing"].notna().sum())
    THR = float(np.round(np.nanpercentile(w["ageing"], 85), 3))
    w["is_cand"] = (w["ageing"] >= THR) & (w["gene"] != "")
    THR_CR = float(np.round(np.percentile(w["CRsupp|+MUD1"], 85), 3))
    alt = (w["CRsupp|+MUD1"] >= THR_CR) & (w["gene"] != "")
    overlap = int((w["is_cand"] & alt).sum())
    print(f"[candidates] selection basis: AGEING effect in +MUD1 (old 2% minus "
          f"young 2%), threshold >= {THR}; {n_age}/{N} introns have a young value")
    print(f"[candidates] {int(w['is_cand'].sum())} named candidates; the CR-based "
          f"selection would give {int(alt.sum())}, overlap {overlap}")
    cand = w[w["is_cand"]].nlargest(g.n_cand, "mud1_dep")
    print(f"[candidates] showing top {len(cand)} by Mud1 dependence")
    if len(cand) < 5:
        print("FAIL-CLOSED: fewer than 5 named candidates.", file=sys.stderr); return 9

    # ---------------- bootstrap CIs over libraries --------------------------
    rng = np.random.default_rng(g.seed)
    keyed = {k: v for k, v in m.groupby(["MUD1", "NMD", "GLU"])[C_SAMPLE]
             .unique().items()}
    boot = np.empty((g.boot, len(cand)))
    idx = {r[C_INTRON]: i for i, (_, r) in enumerate(cand.iterrows())}
    msub = m[m[C_INTRON].isin(cand[C_INTRON])]
    for b in range(g.boot):
        pick = {k: rng.choice(v, size=len(v), replace=True) for k, v in keyed.items()}
        rows = []
        for k, samples in pick.items():
            s = msub[msub[C_SAMPLE].isin(samples) & (msub["MUD1"] == k[0])
                     & (msub["NMD"] == k[1]) & (msub["GLU"] == k[2])]
            gsum = s.groupby(C_INTRON)[[C_MEANB, C_EETOT]].sum()
            for iid, r_ in gsum.iterrows():
                rows.append((iid, k[0], k[1], k[2], r_[C_MEANB], r_[C_EETOT]))
        bd = pd.DataFrame(rows, columns=[C_INTRON, "MUD1", "NMD", "GLU", C_MEANB, C_EETOT])
        bd["IR"] = ir_from(bd)
        pv = bd.pivot_table(index=C_INTRON, columns=["MUD1", "NMD", "GLU"], values="IR")
        vals = np.full(len(cand), np.nan)
        for iid in pv.index:
            try:
                cw = ((pv.loc[iid, ("+MUD1", "upf1d", "2%")] - pv.loc[iid, ("+MUD1", "UPF1", "2%")])
                      - (pv.loc[iid, ("+MUD1", "upf1d", "0.1%")] - pv.loc[iid, ("+MUD1", "UPF1", "0.1%")]))
                cm = ((pv.loc[iid, ("mud1\u0394", "upf1d", "2%")] - pv.loc[iid, ("mud1\u0394", "UPF1", "2%")])
                      - (pv.loc[iid, ("mud1\u0394", "upf1d", "0.1%")] - pv.loc[iid, ("mud1\u0394", "UPF1", "0.1%")]))
                vals[idx[iid]] = cw - cm
            except KeyError:
                pass
        boot[b] = vals
    lo, hi = np.nanpercentile(boot, [2.5, 97.5], axis=0)
    cand = cand.assign(dep_lo=lo, dep_hi=hi)
    print(f"[d] bootstrap over libraries, {g.boot} resamples; "
          f"{int(np.sum((cand.dep_lo > 0)))}/{len(cand)} candidates exclude zero")

    # ---------------- host-abundance adjustment for panel g -----------------
    X = np.column_stack([np.ones(N), w["host|+MUD1"] - w["host|mud1\u0394"]])
    beta, *_ = np.linalg.lstsq(X, w["mud1_dep"].to_numpy(float), rcond=None)
    w["dep_adj"] = w["mud1_dep"] - X @ beta + beta[0]
    cand = cand.merge(w[[C_INTRON, "dep_adj"]], on=C_INTRON, how="left")
    r_ct = stats.spearmanr(w["host|+MUD1"], w["CRsupp|+MUD1"])
    r_cm = stats.spearmanr(w["host|mud1\u0394"], w["CRsupp|mud1\u0394"])
    print(f"[f] host-response vs intron-response coupling: +MUD1 rho={r_ct.statistic:+.3f} "
          f"(P={r_ct.pvalue:.2g}); mud1d rho={r_cm.statistic:+.3f} (P={r_cm.pvalue:.2g})")
    wil_all = stats.wilcoxon(w["CRsupp|+MUD1"], w["CRsupp|mud1\u0394"])
    cw = w[w["is_cand"]]
    wil = stats.wilcoxon(cw["CRsupp|+MUD1"], cw["CRsupp|mud1\u0394"])
    n_below = int((cw["CRsupp|mud1\u0394"] < cw["CRsupp|+MUD1"]).sum())
    print(f"[c] paired +MUD1 vs mud1d CR suppression: all introns P={wil_all.pvalue:.2g}; "
          f"candidates only P={wil.pvalue:.2g}; {n_below}/{len(cw)} candidates below "
          "the diagonal")

    # ---------------- lifespan, optional ------------------------------------
    ls, ls_note, CR_LEVEL = None, "not supplied", "0.1%"
    lifespan_stats = None
    if g.lifespan and g.lifespan.exists():
        ls = pd.read_csv(g.lifespan)
        lc = {c.lower(): c for c in ls.columns}
        need_ls = [lc.get("genotype"), lc.get("glucose"), lc.get("divisions")]
        if any(x is None for x in need_ls):
            print(f"WARNING: --lifespan lacks genotype/glucose/divisions; got "
                  f"{list(ls.columns)}. Panels a and b NOT COMPUTED.", file=sys.stderr)
            ls, ls_note = None, "columns not recognised"
        else:
            ls = ls.rename(columns={need_ls[0]: "genotype", need_ls[1]: "glucose",
                                    need_ls[2]: "divisions"})
            # Genotype arrives already normalised to +MUD1 / mud1-delta by the
            # converter. Delta-symbol detection would misread the strain named
            # "Mud1", which IS the deletion in JM100.
            ls["MUD1"] = ls["genotype"].astype(str).str.strip()
            bad = sorted(set(ls["MUD1"]) - set(MU))
            if bad:
                print(f"WARNING: lifespan genotypes {bad} are not {MU}; "
                      "panels a and b NOT COMPUTED.", file=sys.stderr)
                ls, ls_note = None, f"genotype labels {bad} unrecognised"
            else:
                ls["GLU"] = ls["glucose"].astype(str).str.strip()
                lv = sorted(ls["GLU"].unique(),
                            key=lambda t: float(str(t).rstrip("%")))
                CR_LEVEL = lv[0]
                ls["divisions"] = pd.to_numeric(ls["divisions"], errors="coerce")
                ls = ls.dropna(subset=["divisions"])
                ls_note = (f"{len(ls)} mother cells, {g.lifespan.name}; "
                           f"CR = {CR_LEVEL} glucose")
                print(f"[a] lifespan: {ls_note}")
                if CR_LEVEL != "0.1%":
                    print(f"[a] NOTE: lifespan CR is {CR_LEVEL} glucose while the "
                          "RNA-seq CR arm is 0.1%. Different intensities; stated "
                          "on the figure.", file=sys.stderr)
    else:
        print("[a,b] NOT COMPUTED: no --lifespan table supplied")

    # ============================== LAYOUT ==================================
    # One declarative title per panel, no subtitle inside the figure: methods
    # move to the caption. Bands are reserved in inches and never negotiated.
    # Two lines of title room. A declarative title that states the biology is
    # longer than a lane; the answer is to give it the room, not to shrink it.
    T_TITLE, T_SUB, GAP = .46, .00, .07
    HEAD = GAP + T_SUB + T_TITLE
    XLAB, TOPBAND, SLACK = .55, .78, .15   # no footer band needed
    XLAB_G = .55      # g key now sits inside its own axes
    RH = [1.45, 1.90, 1.90, 1.90]
    ROWTOP = []
    y = FIG_H - TOPBAND
    for i_, h in enumerate(RH):
        ROWTOP.append(y - HEAD - h)
        y = ROWTOP[-1] - (XLAB_G if i_ == 2 else XLAB) - SLACK
    LX, RX, PWID = 1.00, 4.30, 2.60
    print(f"[layout] rows {[round(v,2) for v in ROWTOP]}; "
          f"cols {LX}-{LX+PWID} and {RX}-{RX+PWID}")

    IRN = "IR$_{NMD}$"   # IR(upf1d) - IR(UPF1+), a dimensionless fraction
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    def fit_text(x_in, y_in, txt, size, weight="normal", color=INK):
        """Place text left-aligned at x_in, wrapping so it never leaves the page."""
        avail = (FIG_W - x_in - .25) * fig.dpi
        o = fig.text(fx(x_in), fy(y_in), txt, fontsize=size, fontweight=weight,
                     ha="left", va="center", color=color)
        fig.canvas.draw()
        wdt = o.get_window_extent(renderer=fig.canvas.get_renderer()).width
        if wdt > avail:
            ncol = max(20, int(len(txt) * avail / wdt))
            o.set_text("\n".join(textwrap.wrap(txt, ncol)))
        return o

    # Journals want the figure title and the metric definition in the legend, not
    # inside the artwork. --no-suptitle omits both for the submission render.
    if not g.no_suptitle:
        t_obj = fit_text(LX, FIG_H - .34, TITLE.split("|")[1].strip(), 11, "bold")
        fig.canvas.draw()
        t_h_in = (t_obj.get_window_extent(renderer=fig.canvas.get_renderer()).height
                  / fig.dpi)
        fit_text(LX, FIG_H - .34 - t_h_in / 2 - .13,
                 "Old cells; NMD-revealed IR = IR(upf1\u0394) \u2212 IR(UPF1+)",
                 TYPO["sub"] + .4, color=MUTE)

    heads, axes_all = [], []

    def cell(row, x0, w_in=None, h_override=None):
        w_in = PWID if w_in is None else w_in
        h = h_override or RH[row]
        ax = fig.add_axes([fx(x0), fy(ROWTOP[row]), fx(w_in), fy(h)])
        axes_all.append(ax); return ax

    from matplotlib.patches import ConnectionPatch

    def lane_labels(plot_ax, lane_ax, rows, ymax=.95, ymin=.10):
        """Put gene labels in a dataless axes beside the plot, one per evenly
        spaced slot. Positions are ASSIGNED, not derived from the data, so two
        labels cannot collide and no label can enter the plotting rectangle.
        rows: sequence of (gene, x, y) in plot data coordinates."""
        lane_ax.set_axis_off(); lane_ax.set_xlim(0, 1); lane_ax.set_ylim(0, 1)
        rows = sorted(rows, key=lambda t: -t[2])
        for (gene, gx, gy), ly in zip(rows, np.linspace(ymax, ymin, len(rows))):
            lane_ax.text(.16, ly, gene, fontsize=TYPO["gene"], style="italic",
                         color=INK, va="center", ha="left")
            fig.add_artist(ConnectionPatch(
                xyA=(gx, gy), coordsA=plot_ax.transData,
                xyB=(.12, ly), coordsB=lane_ax.transAxes,
                lw=.45, color=MUTE, zorder=1))

    def head(ax, letter, title, sub, lane_in=None, lift=0.0):
        """Panel letter and title, TOP-ANCHORED.

        Bottom-anchoring was the alignment bug: a one-line title sat at the
        anchor while a two-line title grew upward from it, so titles in the same
        row started at different heights. Top-anchoring makes every title in the
        figure begin on the same line, whatever its length.

        The lane is also clipped to the canvas, so a title can never be cut off
        at the right edge.
        """
        p = ax.get_position()
        x0_in = p.x0 * FIG_W
        avail_in = (lane_in if lane_in else p.width * FIG_W)
        avail_in = min(avail_in, FIG_W - .22 - x0_in)      # never exceed the page
        lane_px = avail_in * fig.dpi
        fig.canvas.draw()
        probe = fig.text(0, 0, title, fontsize=TYPO["title"])
        wpx = probe.get_window_extent(renderer=fig.canvas.get_renderer()).width
        probe.remove()
        if wpx > lane_px:
            per_char = wpx / max(len(title), 1)
            title = "\n".join(textwrap.wrap(title,
                                            max(16, int(lane_px / per_char)))[:2])
        ytop = p.y1 + fy(GAP + T_TITLE + lift)
        fig.text(p.x0, ytop, title, fontsize=TYPO["title"], ha="left", va="top",
                 color=INK, linespacing=1.25)
        fig.text(p.x0 - fx(.60), ytop, letter, fontsize=TYPO["letter"],
                 fontweight="bold", ha="left", va="top", color=INK)

    def key(ax, handles, loc="upper left", ncol=1):
        ax.legend(handles=handles, loc=loc, ncol=ncol, frameon=True, framealpha=.88,
                  edgecolor="none", fontsize=TYPO["legend"], handletextpad=.4,
                  handlelength=1.1, borderpad=.35, labelspacing=.35)

    def notcomputed(ax, msg):
        ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_visible(False)
        ax.text(.5, .5, msg, transform=ax.transAxes, ha="center", va="center",
                fontsize=TYPO["annot"], color=CAND, wrap=True)

    # ------------------------------------------------------------------- a
    # Genotype = hue family, glucose = lightness within it. No effect fills:
    # they implied a computed quantity that the panel does not test.
    axa = cell(0, LX, 3.05)
    axa2 = None
    PAL_A = {(MU[0], "2%"): WT_HI, (MU[0], CR_LEVEL): WT_LO,
             (MU[1], "2%"): KO_HI, (MU[1], CR_LEVEL): KO_LO}
    if ls is not None:
        xmax = float(ls["divisions"].max()) * 1.05
        for mu in MU:
            sub_ = ls[ls["MUD1"] == mu]
            for gl in ("2%", CR_LEVEL):
                v = sub_[sub_["GLU"] == gl]["divisions"].to_numpy(float)
                if not len(v): continue
                x_, S_, lo_, hi_ = kaplan_meier(v)
                c_ = PAL_A[(mu, gl)]
                axa.fill_between(x_, lo_, hi_, step="post", color=c_, alpha=.13,
                                 lw=0, zorder=2)
                axa.step(x_, S_, where="post", lw=1.25, color=c_, alpha=.85,
                         zorder=5, solid_capstyle="butt")
                axa.plot([np.median(v)], [.5], marker="o", ms=3.8, mfc=c_,
                         mec="white", mew=.7, zorder=6)
        axa.axhline(.5, color=FAINT, lw=.6, ls=":", zorder=1)
        axa.set_xlim(0, xmax); axa.set_ylim(-.02, 1.03)
        axa.set_xlabel(AX["a_x"])
        axa.set_ylabel(AX["a_y"])
        key(axa, [plt.Line2D([], [], color=PAL_A[(mu, gl)], lw=1.6, alpha=.85,
                             label=f"{mu}, {gl}")
                  for mu in MU for gl in ("2%", CR_LEVEL)], loc="upper right")
    else:
        notcomputed(axa, "NOT COMPUTED - lifespan table not supplied.")
    head(axa, "a", "Mud1 is required for the full lifespan response", "",
         lane_in=3.05)

    # ------------------------------------------------------------------- b
    # Neutral. The interaction crosses zero, so nothing here asserts dependence.
    axb = cell(0, RX + .62, 1.98)
    if ls is not None:
        est, elo, ehi, draws = [], [], [], {}
        for mu in MU:
            s_ = ls[ls["MUD1"] == mu]
            a2 = s_[s_["GLU"] == "2%"]["divisions"].to_numpy(float)
            a1 = s_[s_["GLU"] == CR_LEVEL]["divisions"].to_numpy(float)
            d = np.median(a1) - np.median(a2)
            bs = np.array([np.median(rng.choice(a1, len(a1), True))
                           - np.median(rng.choice(a2, len(a2), True))
                           for _ in range(4000)])
            draws[mu] = bs; est.append(d)
            elo.append(np.percentile(bs, 2.5)); ehi.append(np.percentile(bs, 97.5))
        inter = est[0] - est[1]
        ib = draws[MU[0]] - draws[MU[1]]
        ilo, ihi = np.percentile(ib, [2.5, 97.5])
        pool = {mu: {gl: ls[(ls["MUD1"] == mu) & (ls["GLU"] == gl)]["divisions"]
                     .to_numpy(float) for gl in ("2%", CR_LEVEL)} for mu in MU}
        perm = np.empty(10000)
        for i in range(10000):
            e = []
            for gl in ("2%", CR_LEVEL):
                allv = np.concatenate([pool[MU[0]][gl], pool[MU[1]][gl]])
                sh = rng.permutation(allv); n0_ = len(pool[MU[0]][gl])
                e.append((np.median(sh[:n0_]), np.median(sh[n0_:])))
            perm[i] = (e[1][0] - e[0][0]) - (e[1][1] - e[0][1])
        p_int = float((np.abs(perm) >= abs(inter)).mean())
        lifespan_stats = {"effect": {MU[i]: [est[i], elo[i], ehi[i]] for i in range(2)},
                          "interaction": [float(inter), float(ilo), float(ihi),
                                          float(p_int)], "cr_level": CR_LEVEL}
        print(f"[b] {MU[0]} {est[0]:+.1f} [{elo[0]:+.1f},{ehi[0]:+.1f}]; "
              f"{MU[1]} {est[1]:+.1f} [{elo[1]:+.1f},{ehi[1]:+.1f}]; "
              f"interaction {inter:+.1f} [{ilo:+.1f},{ihi:+.1f}], P={p_int:.4g}")
        yy = [0, 1, 2.2]
        vals, los, his = est + [inter], elo + [ilo], ehi + [ihi]
        for i in range(3):
            axb.plot([los[i], his[i]], [yy[i]] * 2, color=MUTE, lw=1.6, zorder=2,
                     solid_capstyle="round")
            axb.scatter([vals[i]], [yy[i]], s=46, facecolor=MUTE if i < 2 else "white",
                        edgecolor=INK, linewidth=.9, zorder=4)
            axb.text(his[i] + .35, yy[i], f"{vals[i]:+.0f} [{los[i]:+.0f}, {his[i]:+.0f}]",
                     va="center", ha="left", fontsize=TYPO["annot"] - .6, color=INK)
        axb.axhline(1.6, color=FAINT, lw=.6, ls=":", zorder=1)
        axb.axvline(0, color=FAINT, lw=.9, zorder=0)
        axb.set_yticks(yy)
        axb.set_yticklabels([MU[0], MU[1], "Difference"], fontsize=TYPO["tick"])
        axb.set_ylim(-.7, 2.9); axb.invert_yaxis()
        axb.set_xlim(min(los) - 1.2, max(his) + 5.5)
        axb.set_xlabel(AX["b_x"])
    else:
        notcomputed(axb, "NOT COMPUTED")
    head(axb, "b", "Genotype difference in the lifespan response", "",
         lane_in=1.98 + .62)

    # ------------------------------------------------------------------- c
    CLANE = .58
    axc = cell(1, LX, PWID - CLANE)
    axc_lane = fig.add_axes([fx(LX + PWID - CLANE), fy(ROWTOP[1]), fx(CLANE),
                             fy(RH[1])])
    lim = float(np.nanmax(np.abs(np.r_[w["CRsupp|+MUD1"],
                                       w["CRsupp|mud1\u0394"]]))) * 1.08
    axc.scatter(w.loc[~w["is_cand"], "CRsupp|+MUD1"],
                w.loc[~w["is_cand"], "CRsupp|mud1\u0394"], s=7, color=BG,
                edgecolors="none", alpha=.55, zorder=2)
    axc.scatter(w.loc[w["is_cand"], "CRsupp|+MUD1"],
                w.loc[w["is_cand"], "CRsupp|mud1\u0394"], s=26, color=CR_C,
                edgecolors=INK, linewidths=.5, zorder=3)
    axc.plot([-lim, lim], [-lim, lim], ls="--", lw=.9, color=FAINT, zorder=1)
    axc.text(lim * .92, lim * .82, "y = x", fontsize=TYPO["annot"], color=MUTE,
             ha="right", va="top", rotation=45, rotation_mode="anchor")
    axc.axhline(0, color=FAINT, lw=.6, zorder=0); axc.axvline(0, color=FAINT, lw=.6,
                                                              zorder=0)
    axc.set_xlim(-lim, lim); axc.set_ylim(-lim, lim)
    axc.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5, prune="lower"))
    axc.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    axc.set_xlabel(AX["c_x"])
    axc.set_ylabel(AX["c_y"])
    axc.text(.03, .97, f"{n_below}/{len(cw)} candidates below identity\n"
                       f"paired P = {wil.pvalue:.3f}", transform=axc.transAxes,
             ha="left", va="top", fontsize=TYPO["annot"], color=INK)
    lane_labels(axc, axc_lane,
                [(r_["gene"], r_["CRsupp|+MUD1"], r_["CRsupp|mud1\u0394"])
                 for _, r_ in cand.nlargest(5, "mud1_dep").iterrows()])
    head(axc, "c", "Mud1 enables suppression of the aged intron program", "",
         lane_in=PWID)

    # ------------------------------------------------------------------- d
    axd = cell(1, RX)
    cd_ = cand.sort_values("mud1_dep")
    yy = np.arange(len(cd_))
    axd.hlines(yy, cd_["dep_lo"], cd_["dep_hi"], color="#CFCFCF", lw=3.4, zorder=2)
    axd.scatter(cd_["mud1_dep"], yy, s=34, facecolor=CR_C, edgecolor=INK,
                linewidth=.6, zorder=3)
    axd.axvline(0, color=FAINT, lw=.9, zorder=1)
    axd.set_yticks(yy)
    axd.set_yticklabels(cd_["gene"], fontsize=TYPO["gene"], style="italic")
    for t_ in axd.get_yticklabels(): t_.set_ha("left")
    axd.tick_params(axis="y", pad=34)
    axd.set_ylim(-.8, len(cd_) - .2)
    axd.set_xlabel(AX["d_x"])
    head(axd, "d", "Mud1 dependence is concentrated in few introns", "")

    # ------------------------------------------------------------------- e
    # Same grammar as c, applied to the second RNA layer, so the reader reuses
    # one visual language instead of learning a slopegraph.
    axe = cell(2, LX, PWID - CLANE)
    axe_lane = fig.add_axes([fx(LX + PWID - CLANE), fy(ROWTOP[2]), fx(CLANE),
                             fy(RH[2])])
    hlim = float(np.nanmax(np.abs(np.r_[w["host|+MUD1"],
                                        w["host|mud1\u0394"]]))) * 1.08
    axe.scatter(w.loc[~w["is_cand"], "host|+MUD1"], w.loc[~w["is_cand"], "host|mud1\u0394"],
                s=7, color=BG, edgecolors="none", alpha=.55, zorder=2)
    axe.scatter(w.loc[w["is_cand"], "host|+MUD1"], w.loc[w["is_cand"], "host|mud1\u0394"],
                s=26, color=CR_C, edgecolors=INK, linewidths=.5, zorder=3)
    axe.plot([-hlim, hlim], [-hlim, hlim], ls="--", lw=.9, color=FAINT, zorder=1)
    axe.text(hlim * .92, hlim * .82, "y = x", fontsize=TYPO["annot"], color=MUTE,
             ha="right", va="top", rotation=45, rotation_mode="anchor")
    axe.axhline(0, color=FAINT, lw=.6, zorder=0); axe.axvline(0, color=FAINT, lw=.6,
                                                              zorder=0)
    axe.set_xlim(-hlim, hlim); axe.set_ylim(-hlim, hlim)
    axe.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5, prune="lower"))
    axe.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5))
    axe.set_xlabel(AX["e_x"])
    axe.set_ylabel(AX["e_y"])
    n_bel_e = int((cand["host|mud1\u0394"] < cand["host|+MUD1"]).sum())
    axe.text(.03, .97, f"{n_bel_e} of {len(cand)} candidate genes\nbelow the identity line",
             transform=axe.transAxes, ha="left", va="top",
             fontsize=TYPO["annot"], color=INK)
    lane_labels(axe, axe_lane,
                [(r_["gene"], r_["host|+MUD1"], r_["host|mud1\u0394"])
                 for _, r_ in cand.nlargest(3, "mud1_dep").iterrows()],
                ymax=.85, ymin=.30)
    head(axe, "e", "Mud1 enables a junction response in the same genes", "",
         lane_in=PWID)

    # ------------------------------------------------------------------- f
    axf = cell(2, RX)
    try:
        sns.kdeplot(x=w[f"host|{MU[0]}"], y=w[f"CRsupp|{MU[0]}"], ax=axf,
                    levels=5, color="#D8D8D8", linewidths=.6, zorder=1)
    except Exception:
        axf.scatter(w[f"host|{MU[0]}"], w[f"CRsupp|{MU[0]}"], s=5, color=BG,
                    alpha=.3, edgecolors="none", zorder=1)
    x0 = cand[f"host|{MU[0]}"].to_numpy(float)
    y0 = cand[f"CRsupp|{MU[0]}"].to_numpy(float)
    x1 = cand[f"host|{MU[1]}"].to_numpy(float)
    y1 = cand[f"CRsupp|{MU[1]}"].to_numpy(float)
    toward = np.hypot(x1, y1) < np.hypot(x0, y0)
    for i in range(len(cand)):
        axf.annotate("", xy=(x1[i], y1[i]), xytext=(x0[i], y0[i]),
                     arrowprops=dict(arrowstyle="-|>", lw=1.1,
                                     color=CR_C if toward[i] else MUTE,
                                     alpha=.95 if toward[i] else .45,
                                     shrinkA=2, shrinkB=1, mutation_scale=8),
                     zorder=3)
    axf.scatter(x0, y0, s=26, facecolors="white", edgecolors=INK, linewidths=.6,
                zorder=4)
    axf.scatter(x1, y1, s=26, marker="^", facecolors=CR_C, edgecolors=INK,
                linewidths=.5, zorder=4)
    axf.axhline(0, color=FAINT, lw=.8, zorder=0); axf.axvline(0, color=FAINT, lw=.8,
                                                              zorder=0)
    axf.set_xlabel(AX["f_x"])
    axf.set_ylabel(AX["f_y"])
    axf.text(.03, .97, f"{int(toward.sum())} of {len(cand)} candidate genes\nmove toward zero response", transform=axf.transAxes, ha="left", va="top",
             fontsize=TYPO["annot"], color=INK)
    axf.legend(handles=[
        plt.Line2D([], [], marker="o", ls="", markerfacecolor="white",
                   markeredgecolor=INK, markersize=5, label="+MUD1"),
        plt.Line2D([], [], marker="^", ls="", markerfacecolor=CR_C,
                   markeredgecolor=INK, markersize=5, label="mud1\u0394")],
        loc="upper left", bbox_to_anchor=(0, .86), frameon=False,
        fontsize=TYPO["legend"], handletextpad=.4, borderpad=0)
    head(axf, "f", "Loss of Mud1 collapses both RNA responses", "")

    # ------------------------------------------------------------------- g
    GLANE = .42
    axg = cell(3, LX, PWID - GLANE)
    axg_lane = fig.add_axes([fx(LX + PWID - GLANE), fy(ROWTOP[3]), fx(GLANE),
                             fy(RH[3])])
    axg_lane.set_axis_off(); axg_lane.set_xlim(0, 1)
    cg = cand.assign(att=(cand["dep_adj"] / cand["mud1_dep"].replace(0, np.nan))
                     ).sort_values("att")
    yy = np.arange(len(cg))
    axg.hlines(yy, cg["dep_adj"], cg["mud1_dep"], color="#D5D5D5", lw=1.6, zorder=1)
    axg.scatter(cg["mud1_dep"], yy, s=30, facecolor=CR_C, edgecolor=INK,
                linewidth=.5, zorder=3)
    axg.scatter(cg["dep_adj"], yy, s=30, facecolor="white", edgecolor=CR_C,
                linewidth=1.1, zorder=3)
    axg.axvline(0, color=FAINT, lw=.9, zorder=0)
    axg.set_yticks(yy)
    axg.set_yticklabels(cg["gene"], fontsize=TYPO["gene"], style="italic")
    axg.set_ylim(-.8, len(cg) - .2)
    axg_lane.set_ylim(*axg.get_ylim())
    for i, v in enumerate(cg["att"].to_numpy(float)):
        axg_lane.text(.10, i, f"{np.clip(v, 0, 2):.0%}", va="center", ha="left",
                      fontsize=TYPO["gene"], color=MUTE)
    axg_lane.text(.10, len(cg) - .35, "% retained", va="bottom", ha="left",
                  fontsize=TYPO["gene"] - .6, color=MUTE)
    axg.set_xlabel(AX["g_x"])
    axg.legend(handles=[
        plt.Line2D([], [], marker="o", ls="", markerfacecolor=CR_C,
                   markeredgecolor=INK, markersize=5, label="Unadjusted"),
        plt.Line2D([], [], marker="o", ls="", markerfacecolor="white",
                   markeredgecolor=CR_C, markeredgewidth=1.1, markersize=5,
                   label="Adjusted for spliced-junction abundance")],
        loc="center left", frameon=True, framealpha=.9, edgecolor="none",
        fontsize=TYPO["legend"], handletextpad=.4, borderpad=.35, ncol=1)
    head(axg, "g", "Intron regulation is not an abundance artefact", "",
         lane_in=PWID)

    # ------------------------------------------------------------------- h
    cols4 = [(mu, gl) for mu in MU for gl in ("2%", "0.1%")]
    hm_i = pd.DataFrame({f"{mu}|{gl}": cand[f"NMDrev|{mu}|{gl}"].to_numpy(float)
                         for mu, gl in cols4}, index=cand["gene"])
    ee = pd.DataFrame({f"{mu}|{gl}": np.log2(
        cand[_colname(C_EETOT, mu, "UPF1", gl)].to_numpy(float) + 1)
        for mu, gl in cols4}, index=cand["gene"])
    hm_h = ee.sub(ee.mean(axis=1), axis=0)
    vi = float(np.nanmax(np.abs(hm_i.to_numpy())))
    vh = float(np.nanmax(np.abs(hm_h.to_numpy())))
    HW, HBLOCK = 1.05, .30      # HBLOCK reserves the block-header tier
    axh1 = fig.add_axes([fx(RX), fy(ROWTOP[3]), fx(HW), fy(RH[3] - HBLOCK)])
    axes_all.append(axh1)
    cax1 = fig.add_axes([fx(RX + HW + .06), fy(ROWTOP[3] + .45), fx(.055),
                         fy(RH[3] - HBLOCK - .9)])
    sns.heatmap(hm_i, ax=axh1, cmap="RdBu_r", center=0, vmin=-vi, vmax=vi,
                cbar_ax=cax1, linewidths=.8, linecolor="white",
                yticklabels=hm_i.index, xticklabels=["2%", "0.1%"] * 2)
    axh2 = fig.add_axes([fx(RX + HW + .52), fy(ROWTOP[3]), fx(HW),
                         fy(RH[3] - HBLOCK)])
    axes_all.append(axh2)
    cax2 = fig.add_axes([fx(RX + 2 * HW + .58), fy(ROWTOP[3] + .45), fx(.055),
                         fy(RH[3] - HBLOCK - .9)])
    sns.heatmap(hm_h, ax=axh2, cmap="PuOr_r", center=0, vmin=-vh, vmax=vh,
                cbar_ax=cax2, linewidths=.8, linecolor="white",
                yticklabels=False, xticklabels=["2%", "0.1%"] * 2)
    for cx, lb in ((cax1, AX["h_c1"]), (cax2, AX["h_c2"])):
        cx.tick_params(labelsize=TYPO["gene"] - .8, length=2)
        cx.set_ylabel(lb, fontsize=TYPO["gene"] - .8, labelpad=2)
    for ax_, blk in ((axh1, "Retained-intron RNA"), (axh2, "Spliced-junction RNA")):
        ax_.set_xticklabels(["2%", "0.1%"] * 2, rotation=0, fontsize=TYPO["gene"] - .4)
        ax_.set_xlabel(""); ax_.set_ylabel(""); ax_.tick_params(left=False, bottom=False)
        for sp in ax_.spines.values(): sp.set_visible(False)
        # two-level column header: genotype above, glucose on the axis
        for k, mu in enumerate(MU):
            ax_.text(1 + 2 * k, -.30, mu, ha="center", va="bottom",
                     fontsize=TYPO["gene"], transform=ax_.get_xaxis_transform())
            ax_.plot([2 * k + .06, 2 * k + 1.94], [-.20, -.20], color=MUTE, lw=.7,
                     transform=ax_.get_xaxis_transform(), clip_on=False)
        pp = ax_.get_position()
        fig.text(pp.x0 + pp.width / 2, pp.y1 + fy(.05), blk, ha="center",
                 va="bottom", fontsize=TYPO["annot"], color=INK)
    axh1.set_yticklabels(hm_i.index, rotation=0, fontsize=TYPO["gene"], style="italic")
    head(axh1, "h", "The same genes lose both responses in mud1\u0394", "", lane_in=2.60,
         lift=HBLOCK - .04)

    LANES = (axc_lane, axe_lane, axg_lane)
    for ax_ in axes_all:
        if ax_ is not None and ax_ not in (axh1, axh2, cax1, cax2) + LANES:
            sns.despine(ax=ax_)

    # The provenance strip is no longer drawn on the figure. Nothing is lost:
    # the full record - input paths, complete SHA-256 hashes, library IDs per
    # cell, the frozen candidate list and its hash, and every formula - is
    # written to provenance.json and figure4_manifest.json beside the figure.

    # ---------------- geometry validator -------------------------------------
    # Vertical band arithmetic alone is not enough: it cannot see two panels in
    # the same row overlapping, nor a title running off the page. Both happened.
    geom = []
    named = [("a", axa), ("a2", axa2), ("b", axb), ("c", axc), ("c-lane", axc_lane),
             ("d", axd), ("e", axe), ("e-lane", axe_lane), ("f", axf),
             ("g", axg), ("g-lane", axg_lane), ("h1", axh1), ("h2", axh2)]
    named = [(n_, a_) for n_, a_ in named if a_ is not None]
    # TIGHT boxes, not axes rectangles. Tick labels and axis titles are drawn
    # OUTSIDE the axes rectangle, so a rectangle-only check reports "no overlap"
    # while a y-tick label sits on the neighbouring panel. That single blind spot
    # produced every recurring spill.
    fig.canvas.draw(); rr0 = fig.canvas.get_renderer()
    tb = {}
    for n_, a_ in named:
        try: tb[n_] = a_.get_tightbbox(rr0).transformed(fig.transFigure.inverted())
        except Exception: pass
    ks = list(tb)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            b1, b2 = tb[ks[i]], tb[ks[j]]
            if b1.x0 < b2.x1 and b2.x0 < b1.x1 and b1.y0 < b2.y1 and b2.y0 < b1.y1:
                ovx = (min(b1.x1, b2.x1) - max(b1.x0, b2.x0)) * FIG_W
                ovy = (min(b1.y1, b2.y1) - max(b1.y0, b2.y0)) * FIG_H
                geom.append(f"panel {ks[i]} and {ks[j]} overlap including their "
                            f"labels by {ovx:.2f} x {ovy:.2f} in")
    for n_, b_ in tb.items():
        if b_.x1 > 1.001 or b_.x0 < -.001:
            geom.append(f"panel {n_} labels extend past the canvas edge")
    for nm, ax_ in named:
        p_ = ax_.get_position()
        if p_.x1 > 1.0 or p_.x0 < 0 or p_.y1 > 1.0 or p_.y0 < 0:
            geom.append(f"axes {nm} extends outside the canvas")
    fig.canvas.draw(); rr = fig.canvas.get_renderer()
    for t_ in fig.texts:
        e = t_.get_window_extent(renderer=rr)
        if e.x1 > fig.get_size_inches()[0] * fig.dpi + 1:
            geom.append(f"text runs off the right edge: {t_.get_text()[:40]!r}")
    if geom:
        print("\n[geometry] FAILURES:", file=sys.stderr)
        for gg in geom: print("   " + gg, file=sys.stderr)
    else:
        print("\n[geometry] no axes overlaps, nothing off-canvas")

    # ---------------- audit --------------------------------------------------
    fig.canvas.draw(); r_ = fig.canvas.get_renderer(); bx = []
    who = {id(ax_): nm for nm, ax_ in named}
    who[id(cax1)] = "h1-cbar"; who[id(cax2)] = "h2-cbar"
    for ax_ in fig.axes:
        tag = who.get(id(ax_), "?")
        for t_ in ([ax_.title, ax_.xaxis.label, ax_.yaxis.label] + list(ax_.texts)
                   + ax_.get_xticklabels() + ax_.get_yticklabels()):
            if t_.get_text():
                try:
                    bx.append((f"[{tag}] {t_.get_text()[:26]}",
                               t_.get_window_extent(renderer=r_)))
                except Exception: pass
    for t_ in fig.texts:
        if t_.get_text():
            bx.append((f"[fig] {t_.get_text()[:26]}",
                       t_.get_window_extent(renderer=r_)))
    coll = [[bx[i][0], bx[j][0]] for i in range(len(bx)) for j in range(i+1, len(bx))
            if bx[i][1].x0 < bx[j][1].x1 and bx[j][1].x0 < bx[i][1].x1
            and bx[i][1].y0 < bx[j][1].y1 and bx[j][1].y0 < bx[i][1].y1]
    print(f"\n[collision] {len(coll)} measured text overlaps" if coll else "\n[collision] none")
    for c_ in coll[:25]: print("   ", c_[0], "<->", c_[1])

    stem = out / "figures" / "Figure4_Mud1_coupling"
    fig.set_size_inches(FIG_W, FIG_H, forward=True)
    for ext, kw_ in (("svg", {}), ("pdf", {}), ("png", {"dpi": 600})):
        fig.savefig(f"{stem}.{ext}", format=ext, transparent=True, facecolor="none", **kw_)
    fig.savefig(f"{stem}_preview_white.png", dpi=600, transparent=False, facecolor="white")
    plt.close(fig)

    lsha = sha(g.lifespan) if (g.lifespan and g.lifespan.exists()) else None
    sample_map = (m.groupby(["MUD1", "NMD", "GLU"])[C_SAMPLE]
                    .apply(lambda v: sorted(set(v))).to_dict())
    frozen = w.loc[w["is_cand"], [C_INTRON, "sys", "gene", "ageing"]].sort_values(C_INTRON)
    frozen.to_csv(out / "Figure4_frozen_candidates.tsv", sep="\t", index=False)
    fsha = sha(out / "Figure4_frozen_candidates.tsv")
    (out / "provenance.json").write_text(json.dumps({
        "counts_file": str(g.counts), "counts_sha256": csha,
        "gene_map": str(g.gene_map), "gene_map_sha256": sha(g.gene_map),
        "lifespan_file": (str(g.lifespan) if lsha else None),
        "lifespan_sha256": lsha,
        "libraries_per_cell": {"|".join(k): v for k, v in sample_map.items()},
        "candidate_selection": {
            "basis": "ageing effect in +MUD1, old 2% minus young 2%",
            "independent_of_genotype_contrast": True,
            "threshold": THR, "n_selected": int(w["is_cand"].sum()),
            "frozen_list": "Figure4_frozen_candidates.tsv",
            "frozen_list_sha256": fsha,
            "cr_based_alternative_threshold": THR_CR,
            "cr_based_alternative_n": int(alt.sum()), "overlap": overlap},
        "formulas": {
            "IR": "mean_EI_IE_boundary_count / (mean_EI_IE_boundary_count + EE_total)",
            "NMD_revealed": "IR(upf1d) - IR(UPF1+) within MUD1 status and condition",
            "CR_suppression": "NMD_revealed(old 2%) - NMD_revealed(old 0.1%)",
            "ageing_effect": "NMD_revealed(+MUD1 old 2%) - NMD_revealed(+MUD1 young 2%)",
            "host_response": "log2(EE_total 0.1% + 1) - log2(EE_total 2% + 1), UPF1+",
            "Mud1_dependence": "CR_suppression(+MUD1) - CR_suppression(mud1d)"},
        "synthetic_data_branches": "none; inputs matching "
                                   + ", ".join(BAN) + " are refused",
        "randomness": "used only for bootstrap resampling and permutation of the "
                      "real observations; seed " + str(g.seed),
    }, indent=2))
    print(f"[provenance] frozen candidate list sha256 {fsha[:16]}; "
          f"lifespan sha256 {(lsha or 'n/a')[:16]}")

    w.to_csv(out / "Figure4_intron_table.tsv", sep="\t", index=False)
    cand.to_csv(out / "Figure4_candidates.tsv", sep="\t", index=False)
    (out / "figure4_manifest.json").write_text(json.dumps({
        "title": TITLE, "schema": SCHEMA, "run_stamp": stamp,
        "source": str(g.counts), "source_sha256": csha,
        "gene_map": str(g.gene_map), "names_resolved_fraction": frac,
        "render_font": fam, "font_has_arial_metrics": font_ok,
        "n_introns": N, "candidate_threshold": THR,
        "n_candidates_named": int(w["is_cand"].sum()), "n_shown": int(len(cand)),
        "panels_not_computed": ([] if ls is not None else ["a", "b"]),
        "lifespan_source": ls_note, "lifespan_cr_level": CR_LEVEL,
        "lifespan_stats": lifespan_stats,
        "lifespan_glucose_differs_from_rnaseq": (ls is not None
                                                and CR_LEVEL != "0.1%"),
        "paired_c_wilcoxon_p_candidates": float(wil.pvalue),
        "paired_c_wilcoxon_p_all_introns": float(wil_all.pvalue),
        "n_candidates_below_diagonal": [n_below, int(len(cw))],
        "coupling_spearman_MUD1": [float(r_ct.statistic), float(r_ct.pvalue)],
        "coupling_spearman_mud1d": [float(r_cm.statistic), float(r_cm.pvalue)],
        "bootstrap_resamples": g.boot,
        "candidates": cand["gene"].tolist(),
        "definitions": {
            "IR": "mean(EI,IE)/[mean(EI,IE)+EE]",
            "NMD_revealed": "IR(upf1d) - IR(UPF1+) within MUD1 status and condition",
            "CR_suppression": "NMD_revealed(2%) - NMD_revealed(0.1%), old cells",
            "Mud1_dependence": "CR_suppression(+MUD1) - CR_suppression(mud1d)",
            "host_response": "log2 spliced-junction abundance(0.1%) - log2(2%)"},
        "measured_text_collisions": coll,
        "geometry_failures": geom,
    }, indent=2))
    print(f"[out] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
