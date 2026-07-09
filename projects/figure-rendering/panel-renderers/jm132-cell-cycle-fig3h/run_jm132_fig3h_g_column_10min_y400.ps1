$ErrorActionPreference = "Stop"

$EulerUserHost = "jmccarthy@euler.ethz.ch"
$LocalXlsx = "Y:\Jordan\JM132 Does caloric restriction change cell cycle length in WT and Mud1 Delete backgrounds\JM132 Cell Cycle Length CR.xlsx"
$LocalRoot = Join-Path $env:USERPROFILE "Downloads\JM132_Fig3H_G_COLUMN_10MIN_Y400"
$RemoteRoot = "/cluster/home/jmccarthy/JM132_Fig3H_G_COLUMN_10MIN_Y400_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

if (!(Test-Path $LocalXlsx)) {
    throw "Could not find source workbook: $LocalXlsx"
}

New-Item -ItemType Directory -Force -Path $LocalRoot | Out-Null

$LocalPy = Join-Path $LocalRoot "render_fig3h_g_column_10min_y400.py"
$LocalSh = Join-Path $LocalRoot "run_on_euler.sh"

$PyCode = @'
#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import math
import random
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REMOTE_ROOT = Path(sys.argv[1])
INPUT_XLSX = REMOTE_ROOT / "input" / "JM132_Cell_Cycle_Length_CR.xlsx"
OUT = REMOTE_ROOT / "out"

# requested_panel: Figure 3H, row-as-cell redraw from JM132 Excel.
# source_status: measured JM132 Excel workbook; not RNA-seq; not PPTX crop.
# biological_metric: cell-cycle/interdivision length over division interval number.
# rule: each row is one cell; Excel column G onward contains ordered division frame numbers.
# interval_i_minutes = (frame_column_(i+1) - frame_column_i) * 10.
# A row with k frame values contributes exactly k-1 intervals.
# No sorting. No upper outlier filtering. Visible y-axis fixed at 0-400 min.

# Figure 2 data subset = total/rRNA-depleted JM105 only; no poly-A, P-versus-T, mRNA-like, or P−T construct data.  # not used here.
# NMD_hidden = IR(upf1Δ) - IR(UPF1+)  # not used here.
# candidate_score = min(aging_effect, CR_suppression)  # not used here.
# Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression); y-limits data-driven from computed values, not hardcoded.  # not used here.

LOGICAL_CANVAS_PX = (650, 650)
PNG_SCALE = 4
BASE_DPI = 100
PNG_EXPORT_DPI = BASE_DPI * PNG_SCALE
CANVAS_IN = (LOGICAL_CANVAS_PX[0] / BASE_DPI, LOGICAL_CANVAS_PX[1] / BASE_DPI)
PANEL = "Figure_3H_G_column_10min_y400_all_positive_intervals"

FRAME_START_COL_INDEX = 6
FRAME_START_COL_LETTER = "G"
FRAME_INTERVAL_MIN = 10.0

Y_MIN = 0.0
Y_MAX = 400.0
Y_TICKS = [0, 100, 200, 300, 400]

EXPECTED_CONDITIONS = ["2pct", "CR"]
EXPECTED_GENOTYPES = ["WT", "mud1D"]

PRIMARY_WINDOW_START = 1
PRIMARY_WINDOW_END = 10
MIN_INTERVALS_PER_CELL_PRIMARY = 3
RNG_SEED = 132

WT_COLOR = "#2C8C8C"
MUD1D_COLOR = "#C56A4B"
GRID_COLOR = "#E6EAEE"
TEXT_COLOR = "#202124"


def fail(code: str, message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"NO_RENDER_{code}.txt").write_text(message + "\n", encoding="utf-8")
    print(f"[NO_RENDER] {code}: {message}", file=sys.stderr)
    sys.exit(2)


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.8g}" if math.isfinite(value) else ""
    return str(value)


def safe_float(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"na", "nan", "none", "null"}:
        return None
    try:
        out = float(text.replace(",", ""))
        return out if math.isfinite(out) else None
    except Exception:
        return None


def write_tsv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    seen: Set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fmt(row.get(key)) for key in fields})


def read_tsv(path: Path) -> List[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def excel_col_to_index(col: str) -> int:
    value = 0
    for ch in col.upper():
        if "A" <= ch <= "Z":
            value = value * 26 + (ord(ch) - ord("A") + 1)
    return value - 1


def index_to_excel_col(index: int) -> str:
    index += 1
    out = ""
    while index:
        index, rem = divmod(index - 1, 26)
        out = chr(ord("A") + rem) + out
    return out


def cell_ref_to_col_index(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Z]", "", cell_ref.upper())
    return excel_col_to_index(letters)


def read_shared_strings(z: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    strings: List[str] = []
    for si in root.findall("a:si", ns):
        strings.append("".join((t.text or "") for t in si.findall(".//a:t", ns)))
    return strings


def worksheet_paths(z: zipfile.ZipFile) -> List[str]:
    return sorted(
        [name for name in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", name)],
        key=lambda x: int(re.search(r"sheet(\d+)\.xml$", x).group(1)),
    )


def read_worksheet_matrix(z: zipfile.ZipFile, shared: List[str], sheet_path: str) -> List[List[object]]:
    root = ET.fromstring(z.read(sheet_path))
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    sparse: Dict[int, Dict[int, object]] = defaultdict(dict)
    max_row = 0
    max_col = 0

    for row in root.findall(".//a:sheetData/a:row", ns):
        row_idx = int(row.attrib.get("r", "1")) - 1
        max_row = max(max_row, row_idx)

        for cell in row.findall("a:c", ns):
            ref = cell.attrib.get("r", "")
            if not ref:
                continue

            col_idx = cell_ref_to_col_index(ref)
            max_col = max(max_col, col_idx)

            cell_type = cell.attrib.get("t", "")
            value_node = cell.find("a:v", ns)
            inline_node = cell.find("a:is/a:t", ns)

            value = None
            if cell_type == "s" and value_node is not None:
                shared_index = int(value_node.text or "0")
                value = shared[shared_index] if 0 <= shared_index < len(shared) else ""
            elif cell_type == "inlineStr" and inline_node is not None:
                value = inline_node.text or ""
            elif value_node is not None:
                raw = value_node.text or ""
                try:
                    number = float(raw)
                    value = int(number) if number.is_integer() else number
                except Exception:
                    value = raw
            elif inline_node is not None:
                value = inline_node.text or ""

            sparse[row_idx][col_idx] = value

    return [[sparse.get(r, {}).get(c, None) for c in range(max_col + 1)] for r in range(max_row + 1)]


def find_header_row(rows: List[List[object]]) -> Optional[int]:
    for i, row in enumerate(rows[:20]):
        lowered = [str(x or "").strip().lower() for x in row]
        if "genotype" in lowered and "glucose percentage" in lowered:
            return i
    return None


def read_xlsx_best_sheet(path: Path) -> Tuple[List[List[object]], str]:
    if not path.exists():
        fail("XLSX_MISSING", f"Missing workbook: {path}")

    with zipfile.ZipFile(path) as z:
        shared = read_shared_strings(z)
        candidates: List[dict] = []
        matrices: Dict[str, List[List[object]]] = {}

        for sheet_path in worksheet_paths(z):
            matrix = read_worksheet_matrix(z, shared, sheet_path)
            matrices[sheet_path] = matrix
            header_idx = find_header_row(matrix)
            nonempty = sum(1 for row in matrix for value in row if value not in {None, ""})
            score = nonempty + (100000 if header_idx is not None else 0)
            candidates.append({
                "sheet_path": sheet_path,
                "header_row_index_0based": header_idx if header_idx is not None else "",
                "nonempty_cells": nonempty,
                "score": score,
            })

    candidates.sort(key=lambda r: int(r["score"]), reverse=True)
    write_tsv(OUT / "xlsx_sheet_inventory.tsv", candidates)

    if not candidates or candidates[0]["header_row_index_0based"] == "":
        fail("HEADER_NOT_FOUND", "Could not find sheet with Genotype and Glucose Percentage headers.")

    selected = str(candidates[0]["sheet_path"])
    return matrices[selected], selected


def normalize_genotype(value: object) -> Optional[str]:
    text = str(value or "").strip()
    low = text.lower()
    if low in {"wt", "wild type", "wild-type"}:
        return "WT"
    if "mud1" in low or "delete" in low or "delta" in low or "Δ" in text:
        return "mud1D"
    return None


def normalize_condition(value: object) -> Optional[str]:
    x = safe_float(value)
    if x is None:
        return None
    if abs(x - 2.0) < 1e-6:
        return "2pct"
    if abs(x - 0.5) < 1e-6:
        return "CR"
    return None


def condition_label(condition: str) -> str:
    return "2% glucose" if condition == "2pct" else "0.5% glucose CR"


def genotype_label(genotype: str) -> str:
    return "WT" if genotype == "WT" else "mud1Δ"


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: List[float]) -> float:
    values = sorted(values)
    n = len(values)
    if n == 0:
        return float("nan")
    if n % 2 == 1:
        return values[n // 2]
    return 0.5 * (values[n // 2 - 1] + values[n // 2])


def parse_records(rows: List[List[object]]) -> Tuple[List[dict], List[dict], List[dict]]:
    header_idx = find_header_row(rows)
    if header_idx is None:
        fail("HEADER_NOT_FOUND", "Header row not found.")

    header = [str(x or "").strip().lower() for x in rows[header_idx]]
    genotype_col = header.index("genotype")
    glucose_col = header.index("glucose percentage")
    dies_col = header.index("dies on chip?") if "dies on chip?" in header else None
    position_col = header.index("position") if "position" in header else None
    cell_col = header.index("cell number") if "cell number" in header else None

    records: List[dict] = []
    pair_audit: List[dict] = []
    row_audit: List[dict] = []

    for excel_row, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        genotype = normalize_genotype(row[genotype_col] if genotype_col < len(row) else None)
        condition = normalize_condition(row[glucose_col] if glucose_col < len(row) else None)

        if genotype is None or condition is None:
            continue

        dies = str(row[dies_col] if dies_col is not None and dies_col < len(row) else "").strip()
        position = row[position_col] if position_col is not None and position_col < len(row) else ""
        cell_number = row[cell_col] if cell_col is not None and cell_col < len(row) else ""
        cell_id = f"row{excel_row}_pos{position}_cell{cell_number}"

        frames: List[Tuple[int, float]] = []
        first_blank = ""

        for col_idx in range(FRAME_START_COL_INDEX, len(row)):
            value = safe_float(row[col_idx])
            if value is None:
                first_blank = index_to_excel_col(col_idx)
                break
            frames.append((col_idx, value))

        max_possible_intervals_for_cell = max(0, len(frames) - 1)

        row_audit.append({
            "excel_row": excel_row,
            "cell_id": cell_id,
            "condition": condition,
            "genotype": genotype,
            "dies_on_chip": dies,
            "included": True,
            "first_frame_column": FRAME_START_COL_LETTER,
            "n_contiguous_frame_values_from_G": len(frames),
            "max_possible_intervals_for_this_cell": max_possible_intervals_for_cell,
            "first_blank_column_after_G_run": first_blank,
        })

        for i in range(max_possible_intervals_for_cell):
            col_a, frame_a = frames[i]
            col_b, frame_b = frames[i + 1]
            delta_frames = frame_b - frame_a
            minutes = delta_frames * FRAME_INTERVAL_MIN
            interval = i + 1
            status = "used" if delta_frames > 0 else "skipped_nonpositive_delta"

            audit_row = {
                "excel_row": excel_row,
                "cell_id": cell_id,
                "condition": condition,
                "genotype": genotype,
                "dies_on_chip": dies,
                "division_interval_number": interval,
                "cell_max_possible_intervals": max_possible_intervals_for_cell,
                "start_column": index_to_excel_col(col_a),
                "next_column": index_to_excel_col(col_b),
                "start_frame": frame_a,
                "next_frame": frame_b,
                "delta_frames": delta_frames,
                "cell_cycle_length_minutes": minutes,
                "status": status,
            }
            pair_audit.append(audit_row)

            if status != "used":
                continue

            records.append({
                **audit_row,
                "condition_label": condition_label(condition),
                "genotype_label": genotype_label(genotype),
                "frame_interval_minutes": FRAME_INTERVAL_MIN,
                "source_workbook": str(INPUT_XLSX),
            })

    if not records:
        fail("NO_VALID_INTERVALS", "No positive adjacent G-forward intervals.")

    return records, pair_audit, row_audit


def summarize(records: List[dict]) -> List[dict]:
    grouped: Dict[Tuple[str, str, int], List[float]] = defaultdict(list)
    for row in records:
        grouped[(row["condition"], row["genotype"], int(row["division_interval_number"]))].append(float(row["cell_cycle_length_minutes"]))

    out: List[dict] = []
    for (condition, genotype, interval), values in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        n = len(values)
        m = mean(values)
        sd = math.sqrt(sum((x - m) ** 2 for x in values) / (n - 1)) if n > 1 else 0.0
        sem = sd / math.sqrt(n) if n > 1 else 0.0
        out.append({
            "condition": condition,
            "condition_label": condition_label(condition),
            "genotype": genotype,
            "genotype_label": genotype_label(genotype),
            "division_interval_number": interval,
            "n": n,
            "mean_minutes": m,
            "sd_minutes": sd,
            "sem_minutes": sem,
            "mean_minus_sem": m - sem,
            "mean_plus_sem": m + sem,
            "errorbar_plotted": "SEM",
        })
    return out


def cell_endpoints(records: List[dict]) -> List[dict]:
    grouped: Dict[Tuple[str, str, str], List[float]] = defaultdict(list)
    for row in records:
        interval = int(row["division_interval_number"])
        if PRIMARY_WINDOW_START <= interval <= PRIMARY_WINDOW_END:
            grouped[(row["condition"], row["genotype"], row["cell_id"])].append(float(row["cell_cycle_length_minutes"]))

    out: List[dict] = []
    for (condition, genotype, cell_id), values in sorted(grouped.items()):
        if len(values) < MIN_INTERVALS_PER_CELL_PRIMARY:
            continue
        out.append({
            "condition": condition,
            "genotype": genotype,
            "cell_id": cell_id,
            "n_intervals": len(values),
            "cell_mean_minutes": mean(values),
            "cell_median_minutes": median(values),
        })
    return out


def permutation_p(wt: List[float], mud: List[float], rng: random.Random, max_perm: int = 50000) -> Tuple[float, str, int]:
    if len(wt) < 2 or len(mud) < 2:
        return float("nan"), "insufficient", 0

    observed = abs(mean(mud) - mean(wt))
    pooled = wt + mud
    n_wt = len(wt)
    n_total = len(pooled)

    total = math.comb(n_total, n_wt)
    extreme = 0
    used = 0

    if total <= max_perm:
        mode = "exact"
        for wt_idx_tuple in itertools.combinations(range(n_total), n_wt):
            wt_idx = set(wt_idx_tuple)
            a = [pooled[i] for i in range(n_total) if i in wt_idx]
            b = [pooled[i] for i in range(n_total) if i not in wt_idx]
            if abs(mean(b) - mean(a)) >= observed - 1e-12:
                extreme += 1
            used += 1
        return extreme / used, mode, used

    mode = "monte_carlo"
    all_idx = list(range(n_total))
    for _ in range(max_perm):
        wt_idx = set(rng.sample(all_idx, n_wt))
        a = [pooled[i] for i in all_idx if i in wt_idx]
        b = [pooled[i] for i in all_idx if i not in wt_idx]
        if abs(mean(b) - mean(a)) >= observed - 1e-12:
            extreme += 1
        used += 1

    return (extreme + 1) / (used + 1), mode, used


def stats(cell_rows: List[dict]) -> List[dict]:
    rng = random.Random(RNG_SEED)
    rows: List[dict] = []

    for condition in EXPECTED_CONDITIONS:
        wt = [float(r["cell_mean_minutes"]) for r in cell_rows if r["condition"] == condition and r["genotype"] == "WT"]
        mud = [float(r["cell_mean_minutes"]) for r in cell_rows if r["condition"] == condition and r["genotype"] == "mud1D"]
        p, mode, n_used = permutation_p(wt, mud, rng)
        delta = mean(mud) - mean(wt) if wt and mud else float("nan")

        rows.append({
            "condition": condition,
            "condition_label": condition_label(condition),
            "statistical_unit": "mother_cell",
            "endpoint": "cell_mean_minutes_divisions_1_to_10",
            "n_cells_WT": len(wt),
            "n_cells_mud1D": len(mud),
            "delta_mud1D_minus_WT_minutes": delta,
            "permutation_p_two_sided": p,
            "permutation_mode": mode,
            "n_permutations_or_partitions": n_used,
        })

    return rows


def format_p(p: float) -> str:
    if not math.isfinite(p):
        return "P=NA"
    if p < 0.001:
        return f"P={p:.1e}"
    return f"P={p:.3f}"


def stat_label(stat_rows: List[dict], condition: str) -> str:
    matches = [r for r in stat_rows if r["condition"] == condition]
    if not matches:
        return ""
    row = matches[0]
    return (
        "Cell mean d1–10\n"
        f"Δ={float(row['delta_mud1D_minus_WT_minutes']):+.1f} min\n"
        f"{format_p(float(row['permutation_p_two_sided']))}; n={int(row['n_cells_WT'])}/{int(row['n_cells_mud1D'])}"
    )


def png_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as handle:
        sig = handle.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not PNG: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        ctype = handle.read(4)
        if ctype != b"IHDR" or length < 8:
            raise ValueError(f"Bad PNG IHDR: {path}")
        width, height = struct.unpack(">II", handle.read(8))
    return int(width), int(height)


def render(records: List[dict], summary: List[dict], stat_rows: List[dict], x_max: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "Liberation Sans", "DejaVu Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42

    fig = plt.figure(figsize=CANVAS_IN, dpi=BASE_DPI, facecolor="none")
    ax_top = fig.add_axes([0.140, 0.575, 0.820, 0.350])
    ax_bottom = fig.add_axes([0.140, 0.130, 0.820, 0.350])
    axes = {"2pct": ax_top, "CR": ax_bottom}

    xticks = [1, 5, 10, 15, 20, 25, 30, 34]
    if x_max not in xticks:
        xticks.append(x_max)
    xticks = [x for x in sorted(set(xticks)) if 1 <= x <= x_max]

    rng = random.Random(RNG_SEED)

    for condition, ax in axes.items():
        for genotype in EXPECTED_GENOTYPES:
            color = WT_COLOR if genotype == "WT" else MUD1D_COLOR

            recs = [r for r in records if r["condition"] == condition and r["genotype"] == genotype]
            sums = sorted(
                [r for r in summary if r["condition"] == condition and r["genotype"] == genotype],
                key=lambda r: int(r["division_interval_number"]),
            )

            for r in recs:
                x = float(r["division_interval_number"]) + rng.uniform(-0.13, 0.13)
                y = float(r["cell_cycle_length_minutes"])
                ax.scatter(x, y, s=6.0, color=color, alpha=0.15, linewidths=0, zorder=1)

            xs = [int(r["division_interval_number"]) for r in sums]
            ys = [float(r["mean_minutes"]) for r in sums]
            yerr = [float(r["sem_minutes"]) for r in sums]

            ax.errorbar(
                xs,
                ys,
                yerr=yerr,
                color=color,
                marker="o",
                markersize=3.0,
                linewidth=1.35,
                elinewidth=0.75,
                capsize=1.8,
                alpha=0.98,
                label=genotype_label(genotype),
                zorder=3,
            )

        ax.set_title(condition_label(condition), loc="left", fontsize=11.5, fontweight="bold", pad=2.5)
        ax.set_xlim(0.5, x_max + 0.5)
        ax.set_ylim(Y_MIN, Y_MAX)
        ax.set_xticks(xticks)
        ax.set_yticks(Y_TICKS)
        ax.grid(True, color=GRID_COLOR, linewidth=0.62)
        ax.tick_params(axis="both", labelsize=8.7, length=2.8, width=0.7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_linewidth(0.80)
        ax.spines["bottom"].set_linewidth(0.80)
        ax.set_xlabel("Division interval number", fontsize=9.7, labelpad=4)

        ax.text(
            0.985,
            0.955,
            stat_label(stat_rows, condition),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=7.1,
            color=TEXT_COLOR,
            bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": "#CDD5DF", "linewidth": 0.62, "alpha": 0.92},
            zorder=10,
        )

    ax_top.legend(
        loc="upper center",
        bbox_to_anchor=(0.50, 1.18),
        ncol=2,
        frameon=False,
        fontsize=9.4,
        handlelength=1.65,
        columnspacing=1.55,
        borderpad=0.1,
        title="mean ± SEM",
        title_fontsize=7.2,
    )

    fig.text(0.045, 0.525, "Cell-cycle length (minutes)", rotation=90, ha="center", va="center", fontsize=10.3, color=TEXT_COLOR)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    text_rows: List[dict] = []
    texts: List[Tuple[int, str, object]] = []

    for i, text in enumerate(fig.findobj(match=lambda obj: hasattr(obj, "get_text") and hasattr(obj, "get_window_extent"))):
        value = text.get_text()
        if not value:
            continue
        bbox = text.get_window_extent(renderer=renderer)
        clipped = bbox.x0 < 0 or bbox.y0 < 0 or bbox.x1 > fig.bbox.width or bbox.y1 > fig.bbox.height
        text_rows.append({"text_id": i, "text": value, "x0_px": bbox.x0, "y0_px": bbox.y0, "x1_px": bbox.x1, "y1_px": bbox.y1, "clipped_to_canvas": clipped})
        texts.append((i, value, bbox))

    overlaps: List[dict] = []
    for (ia, ta, ba), (ib, tb, bb) in itertools.combinations(texts, 2):
        if ba.overlaps(bb):
            area = max(0.0, min(ba.x1, bb.x1) - max(ba.x0, bb.x0)) * max(0.0, min(ba.y1, bb.y1) - max(ba.y0, bb.y0))
            if area > 3.0:
                overlaps.append({"text_a_id": ia, "text_a": ta, "text_b_id": ib, "text_b": tb, "overlap_area_px2": area})

    write_tsv(OUT / "text_layout_audit.tsv", text_rows)
    write_tsv(OUT / "text_overlap_audit.tsv", overlaps)

    base = OUT / PANEL

    # Render contract: fixed canvas, editable SVG text, transparent outputs; bbox_inches='tight' does not appear as a savefig argument.
    fig.savefig(str(base) + ".svg", transparent=True, facecolor="none")
    fig.savefig(str(base) + ".pdf", transparent=True, facecolor="none")
    fig.savefig(str(base) + ".png", dpi=PNG_EXPORT_DPI, transparent=True, facecolor="none")
    fig.savefig(str(base) + "_white_preview.png", dpi=PNG_EXPORT_DPI, transparent=False, facecolor="white")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    rows, selected_sheet = read_xlsx_best_sheet(INPUT_XLSX)
    records, pair_audit, row_audit = parse_records(rows)
    summary = summarize(records)
    endpoints = cell_endpoints(records)
    stat_rows = stats(endpoints)

    skipped_nonpositive = [r for r in pair_audit if r["status"] == "skipped_nonpositive_delta"]

    max_interval_from_rows = max(int(r["max_possible_intervals_for_this_cell"]) for r in row_audit)
    max_interval_in_records = max(int(r["division_interval_number"]) for r in records)

    if max_interval_in_records > max_interval_from_rows:
        fail("IMPOSSIBLE_MAX_INTERVAL", f"records max interval {max_interval_in_records} > row-derived max {max_interval_from_rows}")

    sem_bounds = [float(r["mean_minus_sem"]) for r in summary] + [float(r["mean_plus_sem"]) for r in summary]
    raw_values = [float(r["cell_cycle_length_minutes"]) for r in records]
    values_above_axis = [r for r in records if float(r["cell_cycle_length_minutes"]) > Y_MAX]
    summary_above_axis = [r for r in summary if float(r["mean_plus_sem"]) > Y_MAX or float(r["mean_minutes"]) > Y_MAX]

    write_tsv(OUT / "panel_input_all_positive_adjacent_G_10min_intervals.tsv", records)
    write_tsv(OUT / "adjacent_frame_pair_audit_all_pairs.tsv", pair_audit)
    write_tsv(OUT / "row_inclusion_audit_all_cells.tsv", row_audit)
    write_tsv(OUT / "skipped_nonpositive_intervals_audit.tsv", skipped_nonpositive)
    write_tsv(OUT / "summary_mean_sem_by_division.tsv", summary)
    write_tsv(OUT / "primary_cell_endpoints_d1_to_d10.tsv", endpoints)
    write_tsv(OUT / "stats_cell_level_d1_to_d10.tsv", stat_rows)
    write_tsv(OUT / "values_above_visible_y_axis_audit.tsv", values_above_axis)
    write_tsv(OUT / "summary_mean_or_sem_above_visible_y_axis_audit.tsv", summary_above_axis)

    write_tsv(OUT / "y_axis_audit.tsv", [{
        "axis_basis": "fixed_visible_axis_requested_for_Figure_3H",
        "chosen_y_min": Y_MIN,
        "chosen_y_max": Y_MAX,
        "ticks": ",".join(str(x) for x in Y_TICKS),
        "raw_min": min(raw_values),
        "raw_max": max(raw_values),
        "mean_sem_bound_min": min(sem_bounds),
        "mean_sem_bound_max": max(sem_bounds),
        "raw_points_above_visible_axis": len(values_above_axis),
        "summary_rows_mean_or_sem_above_visible_axis": len(summary_above_axis),
        "shared_axis_across_subplots": True,
        "note": "No values are removed; fixed 0-400 display may clip values above 400, which are audited.",
    }])

    group_counts: List[dict] = []
    for condition in EXPECTED_CONDITIONS:
        for genotype in EXPECTED_GENOTYPES:
            recs = [r for r in records if r["condition"] == condition and r["genotype"] == genotype]
            group_counts.append({
                "condition": condition,
                "genotype": genotype,
                "n_cells": len({r["cell_id"] for r in recs}),
                "n_positive_intervals": len(recs),
                "max_division_interval": max([int(r["division_interval_number"]) for r in recs], default=0),
                "max_interval_minutes": max([float(r["cell_cycle_length_minutes"]) for r in recs], default=float("nan")),
            })
    write_tsv(OUT / "group_counts_audit.tsv", group_counts)

    write_tsv(OUT / "source_manifest.tsv", [{
        "input_xlsx": str(INPUT_XLSX),
        "selected_sheet": selected_sheet,
        "figure_panel": "3H",
        "parser": "Each row is one cell; Excel column G onward; adjacent frame subtraction only; no sorting",
        "frame_interval_minutes": FRAME_INTERVAL_MIN,
        "included_cells": "all cells regardless of Dies on chip",
        "valid_interval_filter": "positive adjacent deltas only; no upper outlier filter",
        "visible_y_axis": "0 to 400 minutes fixed, requested",
        "values_above_visible_y_axis_audited_not_removed": len(values_above_axis),
        "max_interval_from_row_frame_counts": max_interval_from_rows,
        "max_interval_in_records": max_interval_in_records,
        "errorbars": "SEM",
        "skipped_nonpositive_count": len(skipped_nonpositive),
        "fake_data_used": "False",
        "data_changed": "False",
    }])

    render(records, summary, stat_rows, max_interval_from_rows)

    transparent_png = OUT / f"{PANEL}.png"
    white_png = OUT / f"{PANEL}_white_preview.png"
    observed_transparent_size = png_size(transparent_png)
    observed_white_size = png_size(white_png)

    write_tsv(OUT / "png_resolution_audit.tsv", [
        {"file": transparent_png.name, "observed_width_px": observed_transparent_size[0], "observed_height_px": observed_transparent_size[1], "expected_width_px": LOGICAL_CANVAS_PX[0] * PNG_SCALE, "expected_height_px": LOGICAL_CANVAS_PX[1] * PNG_SCALE, "pass": observed_transparent_size == (LOGICAL_CANVAS_PX[0] * PNG_SCALE, LOGICAL_CANVAS_PX[1] * PNG_SCALE)},
        {"file": white_png.name, "observed_width_px": observed_white_size[0], "observed_height_px": observed_white_size[1], "expected_width_px": LOGICAL_CANVAS_PX[0] * PNG_SCALE, "expected_height_px": LOGICAL_CANVAS_PX[1] * PNG_SCALE, "pass": observed_white_size == (LOGICAL_CANVAS_PX[0] * PNG_SCALE, LOGICAL_CANVAS_PX[1] * PNG_SCALE)},
    ])

    write_tsv(OUT / "lane_audit.tsv", [
        {"lane": "descriptor/title", "status": "absent", "object": "composite supplies panel letter/title"},
        {"lane": "plot", "status": "present", "object": "2% glucose row-as-cell plot"},
        {"lane": "plot", "status": "present", "object": "0.5% glucose CR row-as-cell plot"},
        {"lane": "label", "status": "present", "object": "condition labels"},
        {"lane": "legend", "status": "present", "object": "WT/mud1Δ mean ± SEM"},
        {"lane": "x-tick", "status": "present", "object": "division interval number"},
        {"lane": "group label", "status": "present", "object": "glucose condition labels"},
        {"lane": "right-stat", "status": "present", "object": "cell mean d1-10 statistic boxes"},
        {"lane": "footer", "status": "absent", "object": "audits/manifests only"},
    ])

    write_tsv(OUT / "collision_audit.tsv", [
        {"collision": "15 min/frame x correct timing", "resolution": "use 10 min/frame"},
        {"collision": "column H start x actual workbook", "resolution": "start at column G"},
        {"collision": "row-as-cell x impossible late intervals", "resolution": "row with k frames contributes exactly k-1 intervals"},
        {"collision": "auto y-axis x intended panel", "resolution": "fixed visible y-axis 0-400"},
        {"collision": "outlier filtering x honest data", "resolution": "no upper filter; above-axis values audited"},
        {"collision": "SD x intended plot", "resolution": "SEM error bars"},
    ])

    summary_text = (
        "Figure 3H G-column 10-minute y400 render\n"
        "=======================================\n"
        f"Workbook: {INPUT_XLSX}\n"
        f"Selected sheet: {selected_sheet}\n"
        "Parser: each row is one cell; column G onward; adjacent frame subtraction; no sorting.\n"
        "Inclusion: all cells regardless of Dies on chip.\n"
        f"Frame interval: {FRAME_INTERVAL_MIN:.0f} minutes/frame.\n"
        "Valid intervals: positive adjacent deltas only; no upper outlier filter.\n"
        "Visible y-axis: 0 to 400 minutes.\n"
        f"Values above visible y-axis audited, not removed: {len(values_above_axis)}.\n"
        f"Summary rows with mean or SEM above visible y-axis: {len(summary_above_axis)}.\n"
        f"Maximum interval from row frame counts: {max_interval_from_rows}.\n"
        f"Maximum interval in plotted records: {max_interval_in_records}.\n"
        f"Skipped nonpositive intervals: {len(skipped_nonpositive)}.\n"
        f"Positive plotted intervals: {len(records)}.\n"
        f"Summary rows: {len(summary)}.\n"
        "Error bars: SEM.\n"
        f"PNG export: {LOGICAL_CANVAS_PX[0] * PNG_SCALE}x{LOGICAL_CANVAS_PX[1] * PNG_SCALE} px.\n"
        "DATA_CHANGED=False\n"
    )
    (OUT / "RUN_SUMMARY.txt").write_text(summary_text, encoding="utf-8")
    print(summary_text)
    print("Output files:")
    for path in sorted(OUT.iterdir()):
        print("  " + path.name)


if __name__ == "__main__":
    main()
'@

$ShCode = @'
#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="$1"
OUT="$REMOTE_ROOT/out"
PY="$REMOTE_ROOT/render.py"

mkdir -p "$OUT"

module purge >/dev/null 2>&1 || true
module load stack/2024-06 >/dev/null 2>&1 || true
module load gcc/12.2.0 >/dev/null 2>&1 || true
module load python/3.11.6 >/dev/null 2>&1 || module load python >/dev/null 2>&1 || true

python3 -m py_compile "$PY"
python3 "$PY" "$REMOTE_ROOT" 2>&1 | tee "$OUT/render.log"
'@

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($LocalPy, $PyCode, $Utf8NoBom)
[System.IO.File]::WriteAllText($LocalSh, $ShCode, $Utf8NoBom)

ssh $EulerUserHost "mkdir -p '$RemoteRoot/input' '$RemoteRoot/out'"
scp $LocalXlsx "${EulerUserHost}:$RemoteRoot/input/JM132_Cell_Cycle_Length_CR.xlsx"
scp $LocalPy "${EulerUserHost}:$RemoteRoot/render.py"
scp $LocalSh "${EulerUserHost}:$RemoteRoot/run_on_euler.sh"

ssh $EulerUserHost "perl -pi -e 's/\r$//' '$RemoteRoot/run_on_euler.sh' '$RemoteRoot/render.py' && chmod +x '$RemoteRoot/run_on_euler.sh' && bash '$RemoteRoot/run_on_euler.sh' '$RemoteRoot'"

$LocalOut = Join-Path $LocalRoot "out"
if (Test-Path $LocalOut) {
    Remove-Item -Recurse -Force $LocalOut
}
scp -r "${EulerUserHost}:$RemoteRoot/out" $LocalOut

$Preview = Join-Path $LocalOut "Figure_3H_G_column_10min_y400_all_positive_intervals_white_preview.png"

Write-Host ""
Write-Host "[Fig3H] Retrieved output:"
Write-Host $LocalOut
Write-Host ""

if (Test-Path $Preview) {
    Start-Process $Preview
} else {
    Get-ChildItem $LocalOut
    throw "Render did not produce expected preview. Open render.log and RUN_SUMMARY.txt in $LocalOut"
}
