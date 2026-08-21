#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JM105 Figure 3 targeted A/D/G publication renderer, v22.

Imports the exact recovered historical v21 source files and reuses their data
loading and biological computation functions.

Scope fence: RNA panels D and G use only total / rRNA-depleted JM105 inputs.
No poly-A, P-versus-T, mRNA-like, or P−T data are loaded.

NMD_hidden = IR(upf1Δ) − IR(UPF1+)
candidate_score = min(aging_effect, CR_suppression)
Panel F contrast = computed (+MUD1 CR-suppression) versus
                   (mud1Δ CR-suppression).
Panel F is not rerendered by this targeted A/D/G script.

Every panel uses a fixed canvas and exports transparent SVG/PDF/PNG plus a white
preview PNG. SVG text remains editable and Arial-requested. No save call uses
bbox_inches="tight".
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import Figure_3_render_all_v21 as v21
import figure3_base_renderer as base
from figure3_adg_v22_common import (
    PANEL_A_SIZE_MM,
    PANEL_D_SIZE_MM,
    PANEL_G_SIZE_MM,
    assert_no_tight_save_calls,
    configure_fonts,
    sha256,
)
from figure3_adg_v22_manifest import (
    write_collision_inventory,
    write_lane_map,
    write_provenance,
    write_run_summary,
)
from figure3_adg_v22_panel_a import render_panel_a
from figure3_adg_v22_panel_d import load_preflight_pair_tables, render_panel_d
from figure3_adg_v22_panel_g import render_panel_g


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jm100-xlsx", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--jm105-root")
    parser.add_argument("--candidate-file")
    parser.add_argument("--stats-file")
    parser.add_argument("--preflight-source-dir")
    return parser.parse_args()


def load_raw_jm105(jm105_root, candidate_file, stats_file, output_dir):
    """Load total/rRNA-depleted JM105 through exact v21 helpers."""

    audit = base.Audit()
    candidates = v21.sanitize_visible_labels(
        base.load_candidates(candidate_file, jm105_root, audit)
    )
    stats = base.load_stats(stats_file, audit)

    # NMD_hidden = IR(upf1Δ) − IR(UPF1+)
    nmd_hidden = base.nmd_hidden_from_stats(stats, candidates, audit)

    # candidate_score = min(aging_effect, CR_suppression)
    _candidate_effects, paired_effects = base.compute_effects(nmd_hidden, audit)
    host_changes = base.compute_host_changes(stats, audit)
    audit.write(output_dir / "Figure_3_ADG_data_integrity_audit.tsv")

    source_record = {
        "root": str(jm105_root),
        "candidate_file": str(candidate_file),
        "candidate_sha256": sha256(candidate_file),
        "stats_file": str(stats_file),
        "stats_sha256": sha256(stats_file),
    }
    return nmd_hidden, paired_effects, host_changes, source_record


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=False)

    source_files = [
        Path(__file__).resolve(),
        Path(__file__).with_name("figure3_adg_v22_common.py"),
        Path(__file__).with_name("figure3_adg_v22_manifest.py"),
        Path(__file__).with_name("figure3_adg_v22_panel_a.py"),
        Path(__file__).with_name("figure3_adg_v22_panel_d.py"),
        Path(__file__).with_name("figure3_adg_v22_panel_g.py"),
    ]
    assert_no_tight_save_calls(source_files)
    font_record = configure_fonts()

    if args.preflight_source_dir:
        preflight_dir = Path(args.preflight_source_dir).resolve()
        nmd_hidden, paired_effects = load_preflight_pair_tables(preflight_dir)
        host_changes = pd.read_csv(
            preflight_dir / "Figure_3E_plot_source.tsv", sep="\t"
        )
        data_mode = "recovered_v21_plot_source_preflight"
        source_record = {
            "source_dir": str(preflight_dir),
            "Figure_3B_plot_source_sha256": sha256(
                preflight_dir / "Figure_3B_plot_source.tsv"
            ),
            "Figure_3E_plot_source_sha256": sha256(
                preflight_dir / "Figure_3E_plot_source.tsv"
            ),
        }
    else:
        if not all([args.jm105_root, args.candidate_file, args.stats_file]):
            raise RuntimeError(
                "Raw mode requires --jm105-root, --candidate-file and --stats-file."
            )
        nmd_hidden, paired_effects, host_changes, source_record = load_raw_jm105(
            Path(args.jm105_root).resolve(),
            Path(args.candidate_file).resolve(),
            Path(args.stats_file).resolve(),
            output_dir,
        )
        data_mode = "raw_total_rRNA_depleted_JM105"

    jm100_path = Path(args.jm100_xlsx).resolve()
    panel_a_paths, panel_a_stats, panel_a_audit = render_panel_a(
        jm100_path, output_dir
    )
    panel_d_paths, panel_d_audit = render_panel_d(
        nmd_hidden, paired_effects, output_dir
    )
    panel_g_paths, panel_g_range, panel_g_audit = render_panel_g(
        host_changes, output_dir
    )

    write_lane_map(output_dir / "Figure_3_ADG_lane_map.tsv")
    write_collision_inventory(
        output_dir / "Figure_3_ADG_collision_inventory.tsv"
    )

    text_audits = {
        "A": panel_a_audit,
        "D": panel_d_audit,
        "G": panel_g_audit,
    }
    provenance = {
        "renderer_entrypoint": str(Path(__file__).resolve()),
        "renderer_entrypoint_sha256": sha256(Path(__file__).resolve()),
        "renderer_modules": {
            path.name: sha256(path) for path in source_files[1:]
        },
        "exact_v21_renderer": str(Path(v21.__file__).resolve()),
        "exact_v21_renderer_sha256": sha256(Path(v21.__file__).resolve()),
        "exact_base_renderer": str(Path(base.__file__).resolve()),
        "exact_base_renderer_sha256": sha256(Path(base.__file__).resolve()),
        "jm100_xlsx": str(jm100_path),
        "jm100_sha256": sha256(jm100_path),
        "data_mode": data_mode,
        "sources": source_record,
        "font": font_record,
        "fixed_canvas_mm": {
            "A": list(PANEL_A_SIZE_MM),
            "D": list(PANEL_D_SIZE_MM),
            "G": list(PANEL_G_SIZE_MM),
        },
        "scope": "total / rRNA-depleted JM105 only for RNA panels D/G",
        "definitions": {
            "NMD_hidden": "IR(upf1Δ) − IR(UPF1+)",
            "candidate_score": "min(aging_effect, CR_suppression)",
            "Panel_F_contrast": (
                "computed (+MUD1 CR-suppression) versus "
                "(mud1Δ CR-suppression); Panel F not rerendered"
            ),
        },
        "panel_D_marker_rule": {
            "open": "old 2% glucose",
            "filled": "old 0.1% glucose CR",
            "line": "same intron paired across conditions",
        },
        "outputs": {
            "A": panel_a_paths,
            "D": panel_d_paths,
            "G": panel_g_paths,
        },
        "panel_A_statistics": panel_a_stats,
        "panel_G_range_audit": panel_g_range,
        "text_audits": text_audits,
        "bbox_inches_tight": False,
    }
    write_provenance(output_dir, provenance)
    passed = write_run_summary(
        output_dir, data_mode, text_audits, panel_g_range
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
