#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared rendering, export, hashing, and text-audit utilities for Figure 3 v22."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text

import Figure_3_render_all_v21 as v21

MM_PER_INCH = 25.4
DPI = 300

# Fixed panel canvases. D inherits the successful historical v21 Panel B canvas.
# G enlarges the successful historical v21 Panel E canvas by 1.25x while
# preserving its aspect ratio so all finite points and labels can be retained.
PANEL_A_SIZE_MM = (150.0, 84.375)
PANEL_D_SIZE_MM = tuple(value * MM_PER_INCH for value in v21.base.CANVAS["3B"])
PANEL_G_SIZE_MM = tuple(
    value * MM_PER_INCH * 1.25 for value in v21.base.CANVAS["3E"]
)

BLUE = v21.BLUE
ORANGE = v21.ORANGE
GRAY = v21.GRAY
LIGHT = v21.LIGHT
DARK = v21.DARK

FS_TICK = 8.0
FS_AXIS = 9.0
FS_GENE = 8.5
FS_TITLE = 9.5
FS_SUBTITLE = 7.6
FS_GROUP = 8.2


def mm_to_inches(size_mm: tuple[float, float]) -> tuple[float, float]:
    """Convert a fixed millimetre canvas to inches for Matplotlib."""

    return size_mm[0] / MM_PER_INCH, size_mm[1] / MM_PER_INCH


def configure_fonts() -> dict[str, Any]:
    """Request Arial while retaining measurable, installed fallbacks on Euler."""

    requested = ["Arial", "Liberation Sans", "DejaVu Sans"]
    available = {entry.name for entry in font_manager.fontManager.ttflist}
    measurement_fonts = [name for name in requested if name in available]
    if not measurement_fonts:
        raise RuntimeError("No Arial-compatible measurement font is installed.")

    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": requested,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": DPI,
            "figure.dpi": 180,
        }
    )
    return {
        "requested_font": "Arial",
        "measurement_fonts": measurement_fonts,
    }


def assert_no_tight_save_calls(paths: Iterable[Path]) -> None:
    """Fail when any source file contains savefig(..., bbox_inches='tight')."""

    forbidden: list[dict[str, Any]] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "savefig":
                continue
            for keyword in node.keywords:
                if keyword.arg != "bbox_inches":
                    continue
                if isinstance(keyword.value, ast.Constant):
                    if str(keyword.value.value).lower() == "tight":
                        forbidden.append(
                            {"path": str(path), "line": int(node.lineno)}
                        )
    if forbidden:
        raise RuntimeError(f"Forbidden tight-crop calls found: {forbidden}")


def save_figure(
    fig: plt.Figure,
    output_dir: Path,
    stem: str,
) -> dict[str, str]:
    """Write fixed-canvas transparent SVG/PDF/PNG and white preview PNG."""

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "svg": output_dir / f"{stem}.transparent.svg",
        "pdf": output_dir / f"{stem}.transparent.pdf",
        "png": output_dir / f"{stem}.transparent.png",
        "preview": output_dir / f"{stem}.preview_white.png",
    }

    fig.patch.set_alpha(0.0)
    fig.savefig(outputs["svg"], transparent=True, facecolor="none")
    fig.savefig(outputs["pdf"], transparent=True, facecolor="none")
    fig.savefig(
        outputs["png"],
        transparent=True,
        facecolor="none",
        dpi=DPI,
    )

    fig.patch.set_alpha(1.0)
    fig.patch.set_facecolor("white")
    fig.savefig(
        outputs["preview"],
        transparent=False,
        facecolor="white",
        dpi=DPI,
    )
    plt.close(fig)
    return {key: str(path) for key, path in outputs.items()}


def audit_text(fig: plt.Figure, panel: str) -> dict[str, Any]:
    """Measure clipping and pairwise text-box overlap on the fixed canvas."""

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    figure_box = fig.bbox

    text_items: list[tuple[str, Any]] = []
    clipped: list[str] = []
    overlaps: list[dict[str, Any]] = []

    for artist in fig.findobj(match=Text):
        if not artist.get_visible():
            continue
        text = artist.get_text().strip()
        if not text:
            continue

        box = artist.get_window_extent(renderer=renderer)
        text_items.append((text, box))
        if (
            box.x0 < figure_box.x0 - 0.5
            or box.y0 < figure_box.y0 - 0.5
            or box.x1 > figure_box.x1 + 0.5
            or box.y1 > figure_box.y1 + 0.5
        ):
            clipped.append(text)

    for index, (text_a, box_a) in enumerate(text_items):
        for text_b, box_b in text_items[index + 1 :]:
            x_overlap = min(box_a.x1, box_b.x1) - max(box_a.x0, box_b.x0)
            y_overlap = min(box_a.y1, box_b.y1) - max(box_a.y0, box_b.y0)
            if x_overlap > 0.8 and y_overlap > 0.8:
                overlaps.append(
                    {
                        "object_a": text_a,
                        "object_b": text_b,
                        "x_overlap_px": round(float(x_overlap), 2),
                        "y_overlap_px": round(float(y_overlap), 2),
                    }
                )

    return {
        "panel": panel,
        "passed": not clipped and not overlaps,
        "clipped_text": clipped,
        "text_overlap_pairs": overlaps,
    }


def cross_font_text_audit(
    fig: plt.Figure,
    panel: str,
) -> dict[str, Any]:
    """Run the text gate under every installed Arial-compatible family."""

    requested = ["Arial", "Liberation Sans", "DejaVu Sans"]
    available = {entry.name for entry in font_manager.fontManager.ttflist}
    tested = [name for name in requested if name in available]
    if not tested:
        raise RuntimeError("No Arial-compatible font is installed for text audit.")

    artists = [
        artist
        for artist in fig.findobj(match=Text)
        if artist.get_visible() and artist.get_text().strip()
    ]
    original_families = [artist.get_fontfamily() for artist in artists]
    per_font: dict[str, Any] = {}

    try:
        for family in tested:
            for artist in artists:
                artist.set_fontfamily(family)
            per_font[family] = audit_text(fig, f"{panel}:{family}")
    finally:
        for artist, original_family in zip(artists, original_families):
            artist.set_fontfamily(original_family)
        fig.canvas.draw()

    return {
        "panel": panel,
        "passed": all(result["passed"] for result in per_font.values()),
        "tested_fonts": tested,
        "per_font": per_font,
    }


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 digest for source and input provenance."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
