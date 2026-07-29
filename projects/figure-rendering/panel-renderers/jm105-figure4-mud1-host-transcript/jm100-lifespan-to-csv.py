#!/usr/bin/env python3
"""
JM100_lifespan_to_csv_20260728.py

Convert JM100.xlsx (replicative lifespan, Caloric Restriction x Mud1) into the
three-column CSV that Figure 4 panels a and b consume.

WHAT THIS FILE IS. 'Buddingcount' is the number of divisions completed by one
mother cell followed in a timelapse; one row per cell. That is a replicative
lifespan. 'Budscarcount' is present for only ~28% of cells and is NOT used.

TWO THINGS THIS SCRIPT FIXES OR FLAGS

  1. The workbook's 'Graphs' summary sheet has the glucose labels TRANSPOSED.
     Its values match the raw Results sheet with 2% and 0.5% swapped
     (MUD1 18.08 is 0.5%, not 2%). Only the Results sheet is read here, and the
     script re-checks the transposition and reports it.

  2. Glucose in JM100 is 2% versus 0.5%. The JM105 RNA-seq CR arm is 0.1%.
     These are DIFFERENT caloric-restriction intensities. The output carries the
     real value so the figure cannot silently imply they are the same.

Strain naming: 'Mud1' in this workbook denotes the deletion. It is mapped
explicitly rather than by delta-symbol detection, which would misread it as
wild type.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

STRAIN = {"WT": "+MUD1", "MUD1": "mud1\u0394", "MUD1D": "mud1\u0394",
          "MUD1DELTA": "mud1\u0394"}
GLU = {0.02: "2%", 0.005: "0.5%", 0.001: "0.1%"}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--xlsx", type=Path, required=True)
    a.add_argument("--out", type=Path, default=Path("JM105_lifespan.csv"))
    a.add_argument("--sheet", default="Results")
    g = a.parse_args()

    if not g.xlsx.exists():
        print(f"FAIL-CLOSED: not found: {g.xlsx}", file=sys.stderr); return 2
    d = pd.read_excel(g.xlsx, sheet_name=g.sheet)
    need = ["Strain", "Glucose percentage", "Buddingcount"]
    miss = [c for c in need if c not in d.columns]
    if miss:
        print(f"FAIL-CLOSED: missing {miss}; observed {list(d.columns)}",
              file=sys.stderr); return 3

    n0 = len(d)
    d = d[d["Strain"].notna() & d["Glucose percentage"].notna()].copy()
    d["divisions"] = pd.to_numeric(d["Buddingcount"], errors="coerce")
    d = d.dropna(subset=["divisions"])
    print(f"[clean] {n0} rows -> {len(d)} cells with a strain, glucose and division count")

    key = d["Strain"].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "",
                                                                     regex=True)
    unknown = sorted(set(key) - set(STRAIN))
    if unknown:
        print(f"FAIL-CLOSED: unrecognised strain labels {unknown}. Add them to STRAIN.",
              file=sys.stderr); return 4
    d["genotype"] = key.map(STRAIN)

    gk = pd.to_numeric(d["Glucose percentage"], errors="coerce").round(4)
    unknown_g = sorted(set(gk.dropna()) - set(GLU))
    if unknown_g:
        print(f"FAIL-CLOSED: unrecognised glucose values {unknown_g}.", file=sys.stderr)
        return 5
    d["glucose"] = gk.map(GLU)

    out = d[["genotype", "glucose", "divisions"]].copy()
    out["divisions"] = out["divisions"].astype(int)
    out.to_csv(g.out, index=False)

    print("\n[design] cells per group:")
    print(out.groupby(["genotype", "glucose"])["divisions"]
             .agg(["count", "median", "mean", "max"]).to_string())

    lo = sorted(out["glucose"].unique(), key=lambda s: float(s.rstrip("%")))[0]
    hi = "2%"
    print(f"\n[effect] CR = {lo} versus {hi}")
    eff = {}
    for gt in out["genotype"].unique():
        s = out[out.genotype == gt]
        a2 = s[s.glucose == hi]["divisions"].to_numpy(float)
        a1 = s[s.glucose == lo]["divisions"].to_numpy(float)
        if len(a2) < 5 or len(a1) < 5: continue
        u = stats.mannwhitneyu(a1, a2, alternative="two-sided")
        eff[gt] = np.median(a1) - np.median(a2)
        print(f"  {gt:8s}: {np.median(a2):.1f} -> {np.median(a1):.1f} divisions "
              f"({eff[gt]:+.1f}), Mann-Whitney P = {u.pvalue:.3g}")
    if len(eff) == 2:
        k = list(eff)
        print(f"  interaction ({k[0]} minus {k[1]}): {eff[k[0]] - eff[k[1]]:+.1f} divisions")

    # re-check the transposed summary sheet, if it is present
    try:
        gr = pd.read_excel(g.xlsx, sheet_name="Graphs").dropna(subset=["Strain"])
        gr["gt"] = (gr["Strain"].astype(str).str.upper()
                    .str.replace(r"[^A-Z0-9]", "", regex=True).map(STRAIN))
        gr["glu"] = pd.to_numeric(gr["Condition"], errors="coerce").round(4).map(GLU)
        real = out.groupby(["genotype", "glucose"])["divisions"].mean()
        same = swapped = 0
        for _, r in gr.iterrows():
            v = float(r["Average Budding count"])
            if (r["gt"], r["glu"]) in real and abs(real[(r["gt"], r["glu"])] - v) < .3:
                same += 1
            other = hi if r["glu"] == lo else lo
            if (r["gt"], other) in real and abs(real[(r["gt"], other)] - v) < .3:
                swapped += 1
        print(f"\n[check] 'Graphs' sheet: {same} of {len(gr)} values match their own "
              f"label; {swapped} match the OTHER glucose condition.")
        if swapped > same:
            print("[check] WARNING: the Graphs summary sheet has 2% and "
                  f"{lo} TRANSPOSED. It must not be used for any figure.",
                  file=sys.stderr)
    except Exception as e:
        print(f"[check] Graphs sheet not verified: {e}")

    print(f"\n[out] {g.out}")
    print(f"[note] JM100 CR is {lo} glucose. The JM105 RNA-seq CR arm is 0.1%. "
          "These are different intensities and the figure states so.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
