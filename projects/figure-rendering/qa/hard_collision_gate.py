"""Hard render-collision gate for JM105 publication figures.

This module is intentionally generic. A renderer must call the gate after
fig.canvas.draw() and before accepting or packaging any output. The gate
measures the actual rendered extents, not source-code intentions.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import numpy as np
from matplotlib.text import Text

SYSTEMATIC_ORF_RE = re.compile(r"\bY[A-P][LR]\d{3}[WC](?:-[A-Z])?\b", re.IGNORECASE)


@dataclass
class HardCollisionResult:
    clipped_text: list[str]
    text_overlap_pairs: list[dict[str, Any]]
    visible_systematic_ids: list[str]
    label_point_violations: list[dict[str, Any]]
    legend_data_overlap: bool

    @property
    def passed(self) -> bool:
        return not (
            self.clipped_text
            or self.text_overlap_pairs
            or self.visible_systematic_ids
            or self.label_point_violations
            or self.legend_data_overlap
        )


def _overlap(a: Any, b: Any, gap_px: float) -> tuple[float, float]:
    return (
        min(a.x1, b.x1) - max(a.x0, b.x0) - gap_px,
        min(a.y1, b.y1) - max(a.y0, b.y0) - gap_px,
    )


def audit_figure(
    fig: Any,
    *,
    label_artists: list[Text] | None = None,
    point_display_xy: np.ndarray | None = None,
    legend: Any | None = None,
    data_axes: Any | None = None,
    minimum_text_gap_px: float = 0.8,
) -> HardCollisionResult:
    """Measure the final render and return a fail-closed collision result."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    figure_box = fig.bbox

    text_items: list[tuple[str, Any]] = []
    clipped: list[str] = []
    systematic_ids: set[str] = set()

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
        systematic_ids.update(match.group(0) for match in SYSTEMATIC_ORF_RE.finditer(text))

    overlaps: list[dict[str, Any]] = []
    for left_index in range(len(text_items)):
        left_text, left_box = text_items[left_index]
        for right_index in range(left_index + 1, len(text_items)):
            right_text, right_box = text_items[right_index]
            x_overlap, y_overlap = _overlap(left_box, right_box, minimum_text_gap_px)
            if x_overlap > 0 and y_overlap > 0:
                overlaps.append(
                    {
                        "object_a": left_text,
                        "object_b": right_text,
                        "x_overlap_px": round(float(x_overlap), 2),
                        "y_overlap_px": round(float(y_overlap), 2),
                    }
                )

    point_violations: list[dict[str, Any]] = []
    if label_artists and point_display_xy is not None and len(point_display_xy):
        for artist in label_artists:
            box = artist.get_window_extent(renderer=renderer).expanded(1.05, 1.10)
            inside = (
                (point_display_xy[:, 0] >= box.x0)
                & (point_display_xy[:, 0] <= box.x1)
                & (point_display_xy[:, 1] >= box.y0)
                & (point_display_xy[:, 1] <= box.y1)
            )
            if inside.any():
                point_violations.append(
                    {
                        "label": artist.get_text(),
                        "points_inside_label_bbox": int(inside.sum()),
                    }
                )

    legend_data_overlap = False
    if legend is not None and data_axes is not None:
        legend_box = legend.get_window_extent(renderer=renderer)
        axes_box = data_axes.get_window_extent(renderer=renderer)
        x_overlap, y_overlap = _overlap(legend_box, axes_box, 0.0)
        legend_data_overlap = x_overlap > 0 and y_overlap > 0

    return HardCollisionResult(
        clipped_text=clipped,
        text_overlap_pairs=overlaps,
        visible_systematic_ids=sorted(systematic_ids),
        label_point_violations=point_violations,
        legend_data_overlap=legend_data_overlap,
    )


def require_pass(result: HardCollisionResult, panel_name: str) -> None:
    """Stop the renderer before packaging when any measured defect remains."""
    if not result.passed:
        raise RuntimeError(f"{panel_name} failed hard collision gate: {result}")
