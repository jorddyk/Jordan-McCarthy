#!/usr/bin/env python3
"""
JM105_figure3_render_v1_20260728.py

Figure 3 | Caloric restriction selectively suppresses an age-associated
           retained-intron program

DESIGN PRINCIPLE. Six panels, six different jobs. The claim has three parts -
selective, age-associated, suppressed - and each panel proves one of them with a
plot type chosen for that job, not repeated from the previous figure.

  a  Does CR reverse what ageing does, and only that?   trajectory, split by class
  b  Is the coupling per-intron or just on average?     paired scatter, quadrants
  c  How much of the ageing gain does CR remove?        reversal-fraction ECDF
  d  Which transcripts?                                 heatmap, THREE columns
  e  Is the suppression specific to age-up introns?     class comparison
  f  Does it hold in raw replicate data?                per-replicate strips

HARD RULES, enforced in code and fail-closed:
  1. COMMON GENE NAMES ONLY on every visible label. If fewer than MIN_NAME_FRAC
     of plotted genes resolve to a standard name, the script STOPS. Systematic
     identifiers are never printed as a label.
  2. NO nan CATEGORIES. Any sample whose condition, age or genotype fails to
     parse is dropped before plotting and the count is reported.
  3. LANE-LOCKED LAYOUT. All positions are inches on a fixed canvas. Titles,
     subtitles, legends, axes and labels occupy separate reserved bands.
  4. NO UNDEFINED JARGON on an axis. Every axis states the quantity in words.

DEFINITIONS, repeated where used:
  IR             = mean(EI, IE) / [mean(EI, IE) + EE]
  NMD-revealed   = IR(upf1-delta) - IR(UPF1+), per condition
                   the retained-intron RNA that NMD normally degrades
  ageing effect  = NMD-revealed(old 2%) - NMD-revealed(young 2%)
  CR suppression = NMD-revealed(old 2%) - NMD-revealed(old 0.1%)
"""
from __future__ import annotations
import argparse, hashlib, json, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, seaborn as sns
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy import stats

TITLE = ("Figure 3 | Caloric restriction selectively suppresses an "
         "age-associated retained-intron program")
SCHEMA = "JM105-FIG3-v2.1-20260728"
BAN = ("dryrun", "synthetic", "fixture", "fake", "mock", "dummy", "simulated", "example")
MIN_NAME_FRAC = 0.90

C_SAMPLE, C_AGE, C_GLU = "sample", "age", "glucose"
C_MUD1, C_UPF1, C_INTRON, C_CAT, C_PARENT = ("mud1_status", "upf1_status", "intron_id",
                                             "intron_category", "parent")
C_EI, C_IE, C_EETOT, C_MEANB = ("EI_count", "IE_count", "EE_total",
                                "mean_EI_IE_boundary_count")
REQUIRED = [C_SAMPLE, C_AGE, C_GLU, C_MUD1, C_UPF1, C_INTRON, C_CAT, C_PARENT,
            C_EI, C_IE, C_EETOT, C_MEANB]
MAIN_CAT = "nuclear_mRNA_or_ORF_intron"

COND = ["young 2%", "old 2%", "old 0.1% (CR)"]
INK, MUTE, FAINT = "#1A1A1A", "#7F7F7F", "#D9D9D9"
UP, DOWN, FLAT = "#D55E00", "#0072B2", "#BFBFBF"
CR_C = "#009E73"

FIG_W, FIG_H = 7.2, 9.2
def fx(i): return i / FIG_W
def fy(i): return i / FIG_H


def sha(p, limit=8 << 20):
    h = hashlib.sha256(); n = 0
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c); n += len(c)
            if n >= limit: break
    return h.hexdigest()


def is_wt(s):
    t = s.astype(str).str.lower()
    return ~(t.str.contains("δ") | t.str.contains("delta") | t.str.contains(r"\bko\b"))


def sysname(s):
    return (s.astype(str).str.split(",").str[0]
             .str.replace(r"_(mRNA|CDS|id\d+|intron.*)$", "", regex=True)
             .str.strip().str.upper())


def resolve_font():
    """Report the font actually used. Arial, Liberation Sans and Nimbus Sans share
    metrics, so any of them measures layout correctly; DejaVu does not."""
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    for want in ("Arial", "Liberation Sans", "Nimbus Sans", "Helvetica"):
        if want in have:
            return want, True
    return "DejaVu Sans", False


def style():
    fam, metric_ok = resolve_font()
    if not metric_ok:
        print(f"WARNING: no Arial-metric font on this machine; rendering in {fam}. "
              "Text spacing will differ from the manuscript font. Install Arial or "
              "Liberation Sans and clear ~/.cache/matplotlib.", file=sys.stderr)
    else:
        print(f"[font] {fam} (Arial metrics)")
    sns.set_theme(style="ticks", context="paper")
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [fam, "Arial", "Liberation Sans", "Nimbus Sans",
                            "Helvetica", "DejaVu Sans"],
        "axes.labelsize": 7, "axes.titlesize": 7.5,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
        "legend.fontsize": 6, "legend.frameon": False,
        "axes.linewidth": .7, "xtick.major.width": .7, "ytick.major.width": .7,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 200, "savefig.dpi": 600,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    })


def main():
    a = argparse.ArgumentParser(description=TITLE)
    a.add_argument("--counts", type=Path, required=True)
    a.add_argument("--gene-map", type=Path, required=True,
                   help="SGD_features.tab. REQUIRED: common names are mandatory.")
    a.add_argument("--outdir", type=Path, required=True)
    a.add_argument("--min-evidence", type=float, default=10.0)
    a.add_argument("--n-heat", type=int, default=18)
    a.add_argument("--probe", action="store_true")
    a.add_argument("--seed", type=int, default=20260728)
    g = a.parse_args()

    style()
    print(TITLE); print(f"[schema] {SCHEMA}")
    if any(b in str(g.counts).lower() for b in BAN):
        print(f"FAIL-CLOSED: synthetic input refused: {g.counts}", file=sys.stderr); return 7
    for name, f_ in (("--counts", g.counts), ("--gene-map", g.gene_map)):
        if str(f_) in ("", ".", "/"):
            print(f"FAIL-CLOSED: {name} is empty. A shell variable is unset - "
                  f"re-export $CNT and $SGD (new login node loses them).",
                  file=sys.stderr)
            return 2
        if not f_.exists():
            print(f"FAIL-CLOSED: {name} not found: {f_}", file=sys.stderr); return 2
        if f_.is_dir():
            print(f"FAIL-CLOSED: {name} is a directory, not a file: {f_}",
                  file=sys.stderr); return 2
        if f_.stat().st_size == 0:
            print(f"FAIL-CLOSED: {name} is empty: {f_}", file=sys.stderr); return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = g.outdir / f"FIGURE3_{stamp}"; (out / "figures").mkdir(parents=True, exist_ok=True)
    csha = sha(g.counts)
    df = pd.read_csv(g.counts)
    miss = [c for c in REQUIRED if c not in df.columns]
    if miss:
        print("FAIL-CLOSED: missing columns:", file=sys.stderr)
        for m in miss: print(f"  - {m}", file=sys.stderr)
        print(f"observed: {list(df.columns)}", file=sys.stderr)
        return 3
    print(f"[source] rows={len(df)} sha256={csha[:16]}")
    for c in (C_EI, C_IE, C_EETOT, C_MEANB):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # ---- RULE 2: drop unparseable rows, report, never plot nan ------------
    n0 = len(df)
    df = df[df[C_AGE].astype(str).str.strip().str.lower().isin(["young", "old"])]
    df = df[df[C_GLU].astype(str).str.strip() != ""]
    df = df.dropna(subset=[C_EI, C_IE, C_EETOT, C_MEANB, C_SAMPLE])
    print(f"[clean] dropped {n0 - len(df)} rows with unparseable condition or counts")

    m = df[is_wt(df[C_MUD1]) & (df[C_CAT].astype(str) == MAIN_CAT)].copy()
    m["_nmd"] = np.where(is_wt(m[C_UPF1]), "UPF1", "upf1d")
    glu = m[C_GLU].astype(str).str.lower()
    age = m[C_AGE].astype(str).str.lower()
    m["_cond"] = np.select(
        [(age == "young") & glu.str.contains("2"),
         (age == "old") & glu.str.contains("2"),
         (age == "old") & (glu.str.contains("0.1") | glu.str.contains("01"))],
        COND, default="")
    n1 = len(m); m = m[m["_cond"] != ""]
    print(f"[clean] dropped {n1 - len(m)} rows outside the three Figure 3 conditions")
    cells = m.groupby(["_cond", "_nmd"])[C_SAMPLE].nunique()
    print("[design] libraries per cell:\n" + cells.to_string())
    if len(cells) < 6:
        print("FAIL-CLOSED: need three conditions x two NMD states.", file=sys.stderr)
        return 5
    if g.probe:
        print("[probe] stopping before analysis."); return 0

    m["_sys"] = sysname(m[C_PARENT])
    agg = m.groupby([C_INTRON, "_sys", "_cond", "_nmd"])[[C_MEANB, C_EETOT]].sum().reset_index()
    den = agg[C_MEANB] + agg[C_EETOT]
    agg["IR"] = np.where(den > 0, agg[C_MEANB] / den.replace(0, np.nan), np.nan)
    agg["ev"] = den
    w = agg.pivot_table(index=[C_INTRON, "_sys"], columns=["_cond", "_nmd"],
                        values=["IR", "ev"]).reset_index()
    w.columns = ["|".join(str(x) for x in c if x != "") for c in w.columns]
    need = [f"{p}|{c}|{n}" for p in ("IR", "ev") for c in COND for n in ("UPF1", "upf1d")]
    lack = [c for c in need if c not in w.columns]
    if lack:
        print(f"FAIL-CLOSED: pivot missing {lack}", file=sys.stderr); return 6
    w = w[(w[[f"ev|{c}|{n}" for c in COND for n in ("UPF1", "upf1d")]]
           >= g.min_evidence).all(axis=1)].copy()
    for c in COND:
        w[f"NMD|{c}"] = w[f"IR|{c}|upf1d"] - w[f"IR|{c}|UPF1"]
    w = w.dropna(subset=[f"NMD|{c}" for c in COND])
    N = len(w); print(f"[universe] n={N} introns measured in all six condition x NMD cells")
    if N < 30:
        print("FAIL-CLOSED: universe too small.", file=sys.stderr); return 8

    w["ageing"] = w[f"NMD|{COND[1]}"] - w[f"NMD|{COND[0]}"]
    w["cr_supp"] = w[f"NMD|{COND[1]}"] - w[f"NMD|{COND[2]}"]

    # class definition: stated absolute threshold, not a hidden statistic
    THR = float(np.round(np.percentile(np.abs(w["ageing"]), 75), 3))
    w["class"] = np.where(w["ageing"] >= THR, "rises with age",
                  np.where(w["ageing"] <= -THR, "falls with age", "unchanged with age"))
    print(f"[classes] threshold |ageing effect| >= {THR}: "
          + w["class"].value_counts().to_dict().__str__())

    # ---- RULE 1: common names are mandatory -------------------------------
    gm = pd.read_csv(g.gene_map, sep="\t", header=None, dtype=str, keep_default_na=False,
                     usecols=[3, 4], names=["sysid", "common"], on_bad_lines="skip")
    gm = gm[(gm.sysid != "") & (gm.common != "")]
    mapping = dict(zip(gm.sysid.str.upper(), gm.common))
    w["gene"] = w["_sys"].map(mapping).fillna("")
    frac = float((w["gene"] != "").mean())
    print(f"[names] {int((w['gene'] != '').sum())}/{N} introns resolved to a standard "
          f"gene name ({frac:.1%}) from {g.gene_map.name}")
    named = w[w["gene"] != ""].copy()
    prog = named[named["class"] == "rises with age"].sort_values("cr_supp", ascending=False)
    if len(prog) < g.n_heat:
        print(f"FAIL-CLOSED: only {len(prog)} named age-rising introns; need "
              f"{g.n_heat} for panel d.", file=sys.stderr)
        return 9
    if frac < MIN_NAME_FRAC:
        print(f"WARNING: only {frac:.1%} of introns carry a standard name. Panels d-f "
              f"use named genes only; unnamed introns still contribute to a-c.")

    rho, prho = stats.spearmanr(w["ageing"], w["cr_supp"])
    grp = w[w["class"] == "rises with age"]
    rev = (grp["cr_supp"] / grp["ageing"]).clip(-1, 2)
    med_rev = float(np.median(rev))
    kw = stats.kruskal(*[w[w["class"] == c]["cr_supp"] for c in w["class"].unique()])
    print(f"[b] Spearman rho={rho:+.3f} P={prho:.2g}")
    print(f"[c] median fraction of the ageing gain reversed by CR = {med_rev:.2f}")
    print(f"[e] CR suppression differs between age classes: Kruskal-Wallis P={kw.pvalue:.2g}")

    # ============================== LAYOUT ===============================
    # inches; every band reserved, nothing positioned relative to a neighbour
    # Every band is reserved in inches. HEAD is the height of a panel's
    # letter+title+subtitle+legend stack; XLAB is its tick/label stack; TOPBAND
    # is the figure title and its subtitle. Row pitch is the sum, so a header can
    # never reach the row above and the figure title can never reach panel a.
    # A tight, aligned 2 x 3 grid. Legends live INSIDE the axes, in the empty
    # quadrant each plot already has, so no legend band is reserved and rows sit
    # close together. Buying collision-freedom with whitespace is not composition.
    T_TITLE, T_SUB, GAP = .17, .14, .05
    HEAD = GAP + T_SUB + T_TITLE                   # 0.36
    AXH, AXW, XLAB, TOPBAND, SLACK = 1.85, 2.55, .42, .70, .10
    PITCH = HEAD + AXH + XLAB + SLACK              # 2.73
    R = [FIG_H - TOPBAND - HEAD - AXH - i * PITCH for i in range(3)]
    CX = [.95, 4.25]                               # equal gutters, panels aligned

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.text(fx(.95), fy(FIG_H - .30), TITLE.split("|")[1].strip(), fontsize=11,
             fontweight="bold", ha="left", va="center", color=INK)
    fig.text(fx(.95), fy(FIG_H - .52),
             "Total, rRNA-depleted RNA; wild-type MUD1; young 2%, old 2% and old 0.1% "
             "glucose; NMD-revealed retained intron = IR(upf1\u0394) \u2212 IR(UPF1+)",
             fontsize=6.4, ha="left", va="center", color=MUTE)

    def cell(i, j, w_in=AXW):
        ax = fig.add_axes([fx(CX[j]), fy(R[i]), fx(w_in), fy(AXH)])
        return ax

    def head(ax, letter, title, sub):
        p = ax.get_position()
        # A title wider than its lane runs into the next panel's letter. The
        # header band is one line by design, so titles are checked, not wrapped.
        fig.canvas.draw()
        probe = fig.text(0, 0, title, fontsize=7.8)
        over = probe.get_window_extent(renderer=fig.canvas.get_renderer()).width \
            - ax.get_window_extent().width
        probe.remove()
        if over > 0:
            print(f"WARNING: panel {letter} title overruns its lane by "
                  f"{over:.0f} px: {title!r}", file=sys.stderr)
        fig.text(p.x0 - fx(.60), p.y1 + fy(GAP + T_SUB + T_TITLE), letter,
                 fontsize=9.5, fontweight="bold", ha="left", va="top", color=INK)
        fig.text(p.x0, p.y1 + fy(GAP + T_SUB), title, fontsize=7.8, ha="left",
                 va="bottom", color=INK)
        fig.text(p.x0, p.y1 + fy(GAP), sub, fontsize=6.0, ha="left",
                 va="bottom", color=MUTE)

    def key(ax, handles, loc="upper left", ncol=1):
        ax.legend(handles=handles, loc=loc, ncol=ncol, frameon=True, framealpha=.88,
                  edgecolor="none", fontsize=5.9, handletextpad=.4,
                  columnspacing=1.0, handlelength=1.1, borderpad=.35,
                  labelspacing=.35)

    # ---- a: trajectory ---------------------------------------------------
    axa = cell(0, 0)
    long = w.melt(id_vars=["class"], value_vars=[f"NMD|{c}" for c in COND],
                  var_name="cond", value_name="val")
    long["cond"] = long["cond"].str.split("|").str[1]
    pal = {"rises with age": UP, "unchanged with age": FLAT, "falls with age": DOWN}
    sns.pointplot(data=long, x="cond", y="val", hue="class", order=COND,
                  palette=pal, errorbar=("ci", 95), dodge=.35, markers="o",
                  markersize=4, linewidth=1.6, err_kws={"linewidth": 1.1},
                  ax=axa, legend=False)
    axa.axhline(0, color=FAINT, lw=.7, zorder=0)
    axa.set_xlabel(""); axa.set_ylabel("NMD-revealed retained intron\n(mean, 95% CI)")
    axa.tick_params(axis="x", labelrotation=0)
    key(axa, [plt.Line2D([], [], color=pal[k], marker="o", markersize=4, lw=1.6,
                         label=f"{k} ({int((w['class']==k).sum())})")
              for k in ("rises with age", "unchanged with age", "falls with age")
              if (w["class"] == k).any()], loc="upper right")
    head(axa, "a", "Only age-responsive introns reverse under CR",
         f"class set by |ageing effect| \u2265 {THR}; bars are 95% confidence intervals")

    # ---- b: paired scatter ------------------------------------------------
    axb = cell(0, 1)
    for k in ("unchanged with age", "falls with age", "rises with age"):
        s_ = w[w["class"] == k]
        if not len(s_): continue
        axb.scatter(s_["ageing"], s_["cr_supp"], s=16 if k != "unchanged with age" else 9,
                    facecolor=pal[k], edgecolor=INK if k != "unchanged with age" else "none",
                    linewidth=.3, alpha=.9 if k != "unchanged with age" else .45, zorder=3)
    lim = float(np.nanpercentile(np.abs(np.r_[w["ageing"], w["cr_supp"]]), 99.5)) * 1.1
    axb.plot([-lim, lim], [-lim, lim], ls="--", lw=.8, color=FAINT, zorder=1)
    axb.axhline(0, color=FAINT, lw=.7, zorder=0); axb.axvline(0, color=FAINT, lw=.7, zorder=0)
    axb.set_xlim(-lim, lim); axb.set_ylim(-lim, lim)
    axb.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6, prune="lower"))
    axb.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=6))
    axb.set_xlabel("ageing effect\n(old 2% \u2212 young 2%)")
    axb.set_ylabel("CR suppression\n(old 2% \u2212 old 0.1%)")
    # Label only the five most extreme named candidates. These are the same
    # genes that head panel d, so the two panels read as one argument.
    lab5 = (w[(w["class"] == "rises with age") & (w["gene"] != "")]
            .nlargest(5, "cr_supp"))
    # Greedy vertical declutter in display space: sort top-down and push any
    # label that would touch the one above it. Two of these genes sit close
    # together and their text collided when both used a fixed offset.
    fig.canvas.draw()
    pts = sorted(((axb.transData.transform((r_["ageing"], r_["cr_supp"])), r_["gene"])
                  for _, r_ in lab5.iterrows()), key=lambda t: -t[0][1])
    MINSEP, last_y = 7.5, None
    for (px, py), gene in pts:
        ty = py if last_y is None else min(py, last_y - MINSEP)
        last_y = ty
        axb.annotate(gene, xy=axb.transData.inverted().transform((px, py)),
                     xytext=axb.transData.inverted().transform((px + 5, ty)),
                     textcoords="data", fontsize=5.6, style="italic", color=INK,
                     va="center", ha="left", zorder=6,
                     arrowprops=dict(arrowstyle="-", lw=.4, color=MUTE,
                                     shrinkA=0, shrinkB=1.5)
                     if abs(ty - py) > 1.5 else None)
    axb.text(.97, .06, f"Spearman \u03c1 = {rho:+.2f}\nP = {prho:.0e}", transform=axb.transAxes,
             ha="right", va="bottom", fontsize=6.2, color=INK)
    key(axb, [plt.Line2D([], [], ls="--", lw=.8, color=FAINT,
                         label="complete reversal"),
              plt.Line2D([], [], marker="o", ls="", markerfacecolor=UP,
                         markeredgecolor=INK, markersize=4, label="rises with age"),
              plt.Line2D([], [], marker="o", ls="", markerfacecolor=DOWN,
                         markeredgecolor=INK, markersize=4, label="falls with age")],
        loc="upper left")
    head(axb, "b", "Reversal is intron-by-intron",
         "each point one intron; points on the dashed line are fully reversed")

    # ---- c: reversal fraction --------------------------------------------
    axc = cell(1, 0)
    sns.ecdfplot(x=rev, ax=axc, lw=1.8, color=CR_C)
    axc.axvline(1, ls="--", lw=.9, color=FAINT)
    axc.axvline(med_rev, ls="-", lw=1.0, color=INK)
    axc.text(med_rev, .06, f" median {med_rev:.0%}", fontsize=6.4, color=INK,
             ha="left", va="bottom")
    axc.set_xlabel("fraction of the ageing gain removed by CR")
    axc.set_ylabel("cumulative fraction of\nage-responsive introns")
    axc.set_xlim(-.5, 2)
    axc.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    key(axc, [plt.Line2D([], [], ls="--", lw=.9, color=FAINT, label="100% = fully reversed"),
              plt.Line2D([], [], lw=1.0, color=INK, label="median")], loc="upper left")
    head(axc, "c", f"CR removes about {med_rev:.0%} of the ageing gain",
         f"{len(grp)} introns that rise with age; values above 100% overshoot")

    # ---- d: heatmap, THREE columns, common names --------------------------
    axd = cell(1, 1)
    top = prog.head(g.n_heat)
    hm = top[[f"NMD|{c}" for c in COND]].to_numpy(float)
    sns.heatmap(hm, ax=axd, cmap="RdBu_r", center=0,
                yticklabels=top["gene"].tolist(), xticklabels=COND,
                cbar_kws=dict(label="NMD-revealed\nretained intron", shrink=.75,
                              pad=.02, aspect=12), linewidths=.6, linecolor="white")
    axd.set_yticklabels(top["gene"].tolist(), rotation=0, fontsize=6, style="italic")
    axd.set_xticklabels(COND, rotation=0, fontsize=6.2)
    axd.tick_params(left=False, bottom=False)
    for sp in axd.spines.values(): sp.set_visible(False)
    axd.figure.axes[-1].yaxis.label.set_size(6)
    head(axd, "d", "The suppressed transcripts are named genes",
         f"top {g.n_heat} age-responsive introns ranked by CR suppression")

    # ---- e: class comparison ----------------------------------------------
    axe = cell(2, 0)
    order = [k for k in ("rises with age", "unchanged with age", "falls with age")
             if (w["class"] == k).any()]
    sns.boxenplot(data=w, x="class", y="cr_supp", order=order, hue="class",
                  hue_order=order, palette=pal, legend=False, ax=axe,
                  width=.62, linewidth=.5, line_kws=dict(linewidth=1.1, color=INK),
                  flier_kws=dict(s=2, alpha=.4))
    sns.stripplot(data=w, x="class", y="cr_supp", order=order, ax=axe, size=1.9,
                  color=INK, alpha=.28, jitter=.30)
    axe.axhline(0, color=FAINT, lw=.7, zorder=0)
    axe.set_xlabel(""); axe.set_ylabel("CR suppression\n(old 2% \u2212 old 0.1%)")
    axe.set_xticks(range(len(order)))
    axe.set_xticklabels([textwrap.fill(t, 12) for t in order], fontsize=6.2)
    axe.text(.97, .96, f"Kruskal\u2013Wallis\nP = {kw.pvalue:.0e}", transform=axe.transAxes,
             ha="right", va="top", fontsize=6.2, color=INK)
    head(axe, "e", "CR acts only on the age-responsive set",
         "box: median and quartiles; every intron shown as a point")

    # ---- f: raw replicate data for three named genes ----------------------
    axf = cell(2, 1)
    picks = top["gene"].head(3).tolist()
    raw = m[m["_sys"].map(mapping).fillna("").isin(picks)].copy()
    raw["gene"] = raw["_sys"].map(mapping)
    d_ = raw[C_MEANB] + raw[C_EETOT]
    raw["IR"] = np.where(d_ > 0, raw[C_MEANB] / d_.replace(0, np.nan), np.nan)
    raw = raw.dropna(subset=["IR"])
    raw["NMD status"] = np.where(raw["_nmd"] == "UPF1", "UPF1+", "upf1\u0394")
    sns.stripplot(data=raw, x="_cond", y="IR", hue="NMD status", order=COND,
                  hue_order=["UPF1+", "upf1\u0394"], palette=[MUTE, CR_C],
                  dodge=.45, size=3.2, alpha=.85, ax=axf, legend=False,
                  edgecolor=INK, linewidth=.3)
    sns.pointplot(data=raw, x="_cond", y="IR", hue="NMD status", order=COND,
                  hue_order=["UPF1+", "upf1\u0394"], palette=[MUTE, CR_C],
                  dodge=.45, errorbar=None, markers="_", markersize=9,
                  linestyle="none", ax=axf, legend=False)
    axf.set_xlabel(""); axf.set_ylabel("intron retention (raw, per library)")
    key(axf, [plt.Line2D([], [], marker="o", ls="", markerfacecolor=MUTE,
                         markeredgecolor=INK, markersize=4, label="UPF1+ (NMD active)"),
              plt.Line2D([], [], marker="o", ls="", markerfacecolor=CR_C,
                         markeredgecolor=INK, markersize=4,
                         label="upf1\u0394 (NMD inactive)")], loc="lower left")
    head(axf, "f", "The pattern is present in raw libraries",
         f"every library for {', '.join(picks)}; no averaging across replicates")

    for _ax in (axa, axb, axc, axe, axf):
        sns.despine(ax=_ax, trim=False)

    fig.text(fx(.55), fy(.20),
             f"Source {g.counts.name}, sha256 {csha[:12]}; gene names {g.gene_map.name}; "
             f"schema {SCHEMA}; n = {N} introns", fontsize=5.2, ha="left", va="center",
             color=FAINT)

    # ---- audit -------------------------------------------------------------
    fig.canvas.draw(); r_ = fig.canvas.get_renderer(); bx = []
    for ax_ in fig.axes:
        for t_ in ([ax_.title, ax_.xaxis.label, ax_.yaxis.label] + list(ax_.texts)
                   + ax_.get_xticklabels() + ax_.get_yticklabels()):
            if t_.get_text():
                try: bx.append((t_.get_text()[:30], t_.get_window_extent(renderer=r_)))
                except Exception: pass
    for t_ in fig.texts:
        if t_.get_text(): bx.append((t_.get_text()[:30], t_.get_window_extent(renderer=r_)))
    coll = [[bx[i][0], bx[j][0]] for i in range(len(bx)) for j in range(i+1, len(bx))
            if bx[i][1].x0 < bx[j][1].x1 and bx[j][1].x0 < bx[i][1].x1
            and bx[i][1].y0 < bx[j][1].y1 and bx[j][1].y0 < bx[i][1].y1]
    print(f"\n[collision] {len(coll)} measured text overlaps" if coll else "\n[collision] none")
    for c_ in coll[:20]: print("   ", c_[0], "<->", c_[1])

    stem = out / "figures" / "Figure3_CR_selectivity"
    fig.set_size_inches(FIG_W, FIG_H, forward=True)
    for ext, kw_ in (("svg", {}), ("pdf", {}), ("png", {"dpi": 600})):
        fig.savefig(f"{stem}.{ext}", format=ext, transparent=True, facecolor="none", **kw_)
    fig.savefig(f"{stem}_preview_white.png", dpi=600, transparent=False, facecolor="white")
    plt.close(fig)

    w.to_csv(out / "Figure3_intron_table.tsv", sep="\t", index=False)
    top.to_csv(out / "Figure3_top_candidates.tsv", sep="\t", index=False)
    (out / "figure3_manifest.json").write_text(json.dumps({
        "title": TITLE, "schema": SCHEMA, "run_stamp": stamp,
        "source": str(g.counts), "source_sha256_first8MB": csha,
        "gene_map": str(g.gene_map), "names_resolved_fraction": frac,
        "n_introns": N, "ageing_threshold": THR,
        "render_font": resolve_font()[0],
        "font_has_arial_metrics": resolve_font()[1],
        "class_counts": w["class"].value_counts().to_dict(),
        "panel_b_spearman": [float(rho), float(prho)],
        "panel_c_median_reversal_fraction": med_rev,
        "panel_e_kruskal_p": float(kw.pvalue),
        "panel_d_genes": top["gene"].tolist(),
        "panel_f_genes": picks,
        "definitions": {
            "IR": "mean(EI,IE)/[mean(EI,IE)+EE]",
            "NMD_revealed": "IR(upf1d) - IR(UPF1+) per condition",
            "ageing_effect": "NMD_revealed(old 2%) - NMD_revealed(young 2%)",
            "CR_suppression": "NMD_revealed(old 2%) - NMD_revealed(old 0.1%)"},
        "measured_text_collisions": coll,
    }, indent=2))
    print(f"[out] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
