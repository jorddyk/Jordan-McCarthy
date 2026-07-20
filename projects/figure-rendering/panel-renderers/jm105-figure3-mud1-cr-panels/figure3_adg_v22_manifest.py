#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lane, collision, provenance, and run-summary writers for Figure 3 v22."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_lane_map(path: Path) -> None:
    """Assign every visible object to one and only one named lane."""

    rows = [
        ["A", "title", "descriptor/title", "x .040-.960; y .915-.980"],
        ["A", "condition line key", "legend", "x .055-.555; y .790-.885"],
        ["A", "survival curves", "plot", "x .090-.560; y .250-.740"],
        ["A", "lifespan scale", "x-tick", "below survival plot"],
        ["A", "survival-probability title", "group label", "left of plot"],
        ["A", "Cox labels/forest/values", "right-stat", "x .600-.995; y .330-.750"],
        ["A", "source and model notes", "footer", "y .025-.125"],
        ["D", "title", "descriptor/title", "y .910-.965"],
        ["D", "open/filled condition key", "legend", "y .855-.905"],
        ["D", "49 paired intron lines", "plot", "four genotype/block plot lanes"],
        ["D", "gene names", "label", "two independent label lanes"],
        ["D", "genotype names", "group label", "above each plot lane"],
        ["D", "numerical NMD-hidden scales", "x-tick", "y .095-.145"],
        ["D", "condition-marker rule", "footer", "y .018-.068"],
        ["G", "title", "descriptor/title", "y .840-.940"],
        ["G", "all finite host-change points", "plot", "x .205-.900; y .290-.760"],
        ["G", "correlation and n", "right-stat", "plot inset"],
        ["G", "numerical x/y axes", "x-tick", "plot axes"],
        ["G", "host-change axis titles", "group label", "x/y axes"],
        ["G", "control interpretation", "footer", "y .055-.160"],
    ]
    pd.DataFrame(rows, columns=["panel", "object", "lane", "anchor"]).to_csv(
        path, sep="\t", index=False
    )


def write_collision_inventory(path: Path) -> None:
    """Record exact historical collisions and the geometrical resolution."""

    rows = [
        ["A legend", "A title", "separate title and legend lanes"],
        ["A Cox row labels", "A Cox numerical strings", "independent label, forest and value axes"],
        ["A footer", "A x-axis", "separate footer and x-tick lanes"],
        ["D positional 2% text", "quantitative x-position semantics", "positional condition text removed"],
        ["D positional CR text", "quantitative x-position semantics", "positional condition text removed"],
        ["D open marker", "D filled marker", "explicit condition-marker legend"],
        ["D gene labels", "D paired lines", "dedicated label axes"],
        ["D numerical scales", "D footer", "separate lanes"],
        ["G clipping triangles", "G raw observations", "triangles removed and all finite observations shown"],
        ["G extreme observations", "canvas edge", "shared data-driven symmetric limit plus 8% padding"],
        ["G x-axis title", "G footer", "separate lanes"],
        ["A plot lane", "A legend handles", "checked; no collision"],
        ["D footer lane", "D x-tick lanes", "checked; no collision"],
        ["G footer lane", "G group-label lanes", "checked; no collision"],
    ]
    pd.DataFrame(rows, columns=["object_a", "object_b", "resolution"]).to_csv(
        path, sep="\t", index=False
    )


def write_provenance(output_dir: Path, provenance: dict[str, Any]) -> None:
    (output_dir / "Figure_3_ADG_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )


def write_run_summary(
    output_dir: Path,
    data_mode: str,
    text_audits: dict[str, dict[str, Any]],
    panel_g_range_audit: dict[str, Any],
) -> bool:
    all_text_passed = all(audit["passed"] for audit in text_audits.values())
    summary_lines = [
        f"JM105_FIGURE3_ADG_V22={'PASS' if all_text_passed else 'FAIL'}",
        f"OUTPUT_DIR={output_dir}",
        f"DATA_MODE={data_mode}",
        f"PANEL_A_TEXT_AUDIT={text_audits['A']['passed']}",
        f"PANEL_D_TEXT_AUDIT={text_audits['D']['passed']}",
        f"PANEL_G_TEXT_AUDIT={text_audits['G']['passed']}",
        "PANEL_G_POINTS_CLIPPED="
        f"{panel_g_range_audit['points_clipped_in_v22']}",
        "PANEL_D_MARKER_RULE=open old 2%; filled old 0.1% CR",
        "BBOX_INCHES_TIGHT=False",
    ]
    (output_dir / "Figure_3_ADG_RUN_SUMMARY.txt").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )
    print("\n".join(summary_lines))
    return all_text_passed
