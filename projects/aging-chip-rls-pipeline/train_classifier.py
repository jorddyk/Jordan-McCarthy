"""
train_classifier_fixed.py -- endpoint-trained RLS automation model for yeast aging chips.

This trainer fixes the failure mode exposed by the 2026-08-14 Euler run:
  * RLS is NOT inferred from a fragile six-state sequence or an HMM.
  * A dedicated division-event head is trained directly on the human-defined
    completed-division events used by calculate_trap_rls().
  * A dedicated dead-state head is trained for robust death calls.
  * Frame-state classification remains as an auxiliary task only.
  * The ImageNet backbone is no longer fed an arbitrary random 4->3 mixture at
    startup: the 1x1 adapter is initialized to replicate the CURRENT frame into
    RGB, while a separate motion branch learns from [t-1,t,t+1,heatmap].
  * Model selection is done by trap-level RLS MAE on a calibration split, not
    by frame accuracy or val_loss.
  * Event threshold and refractory gap are calibrated explicitly to minimize
    trap-level RLS MAE. No Viterbi/HMM smoothing is used for RLS.
  * A held-out TEST split is never used for model/threshold selection and is
    reported at the end.
  * Stage-2 backbone fine-tuning is allowed to replace Stage 1 only if it
    improves the calibration RLS endpoint.

Outputs:
  aging_chip_classifier.keras      auxiliary state model (UI-compatible logits)
  aging_chip_rls_detector.keras    two-output [division_logit, dead_logit] model
  class_labels.json
  model_input_meta.json            keeps UI smoothing disabled (T=0)
  rls_detector_meta.json           calibrated RLS/death decoding parameters
  rls_test_concordance.csv         one row per untouched test trap

Environment overrides (same style as the previous trainer):
  AGING_ANNOTATION_PATH
  AGING_TRAPS_DIR              legacy single-chip override only
  AGING_TRAPS_DIRS_JSON         multi-chip JSON mapping: Chip_ID -> extracted_traps path
  AGING_MODEL_OUT
  AGING_RLS_MODEL_OUT
  AGING_BATCH_SIZE
  AGING_LOAD_WORKERS
"""

import os
import re
import sys
import glob
import json
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
import pandas as pd
import tifffile as tif
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ReduceLROnPlateau
from sklearn.preprocessing import LabelEncoder

# ==============================================================================
# CONFIGURATION
# ==============================================================================
ANNOTATION_PATH = os.environ.get(
    "AGING_ANNOTATION_PATH",
    os.path.join("annotation", "master_human_annotations.xlsx"),
)
# Chip-aware trap roots. Keys MUST match Chip_ID values written by the annotator.
# This prevents Pos/Trap identifiers that recur on different physical aging chips
# from ever resolving to the wrong TIFF stack.
# !! KEEP IN SYNC with KNOWN_CHIP_TRAPS_DIRS in human_classifier_ui.py !!
DEFAULT_TRAPS_DIRS = {
    "JM135_CR_Mud1": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps",
    "JM135_CR_Mud1_Chip2_Intronless": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Aging Chip 2 includes intronless Mud1\_1\extracted_traps",
    # Current default chip: six-condition aging chip, acquisition _33. Reuses
    # the same Pos0/Pos1/... names as the chips above; the Chip_ID column is
    # what keeps those annotations separate.
    "JM135_SixCondition_33": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Six condition chip\_33\extracted_traps",
}
LEGACY_TRAPS_DIR_OVERRIDE = os.environ.get("AGING_TRAPS_DIR")
TRAPS_DIRS_JSON_OVERRIDE = os.environ.get("AGING_TRAPS_DIRS_JSON")
STATE_MODEL_OUT = os.environ.get("AGING_MODEL_OUT", "aging_chip_classifier.keras")
RLS_MODEL_OUT = os.environ.get("AGING_RLS_MODEL_OUT", "aging_chip_rls_detector.keras")
RLS_META_OUT = "rls_detector_meta.json"
TEST_REPORT_OUT = "rls_test_concordance.csv"
CLASS_LABELS_OUT = "class_labels.json"
MODEL_META_OUT = "model_input_meta.json"

BATCH_SIZE = int(os.environ.get("AGING_BATCH_SIZE", 32))
LOAD_WORKERS = int(os.environ.get("AGING_LOAD_WORKERS", min(16, os.cpu_count() or 4)))
RANDOM_SEED = 42

# Trap-level split. Splitting is stratified within position when possible.
CAL_FRACTION = 0.15
TEST_FRACTION = 0.15

# Training stages.
EPOCHS_STAGE1 = 35
EPOCHS_STAGE2 = 25
LR_STAGE1 = 5e-4
LR_STAGE2 = 1e-5
FINE_TUNE_TOP_LAYERS = 30
ENDPOINT_PATIENCE_STAGE1 = 7
ENDPOINT_PATIENCE_STAGE2 = 6
MIN_ENDPOINT_EPOCHS = 4

# Loss balance. RLS event detection is the primary objective.
LOSS_W_STATE = 0.35
LOSS_W_DIVISION = 2.5
LOSS_W_DEAD = 0.65
DIVISION_POS_WEIGHT = 8.0
DEAD_POS_WEIGHT = 2.5
LOSS_W_ESCAPE = 0.9
ESCAPE_POS_WEIGHT = 2.0

# Event-target / training-set focus.
EVENT_SOFT_NEIGHBOR = 0.30  # +/-1 frame target around an exact completed division
EVENT_KEEP_RADIUS = 4       # all training frames this close to a true event are retained
TRANSITION_KEEP_RADIUS = 2  # all frames around human state changes are retained
BACKGROUND_STRIDE = 3       # redundant background frames are thinned, never val/cal/test

# Decoder calibration grid.
DIV_THRESHOLDS = np.round(np.arange(0.10, 0.91, 0.05), 2).tolist()
DIV_MIN_GAPS = list(range(2, 10))
DEATH_THRESHOLDS = np.round(np.arange(0.35, 0.91, 0.05), 2).tolist()
DEATH_PERSISTENCES = [2, 3, 4, 5, 7, 10]
ESCAPE_THRESHOLDS = np.round(np.arange(0.35, 0.91, 0.05), 2).tolist()
ESCAPE_PERSISTENCES = [2, 3, 4, 5, 7, 10]

# Deployment gate: production filenames are written ONLY if the untouched test
# set clears these endpoint criteria. A failed candidate is preserved under
# candidate_* filenames and the existing production model is not overwritten.
MAX_DEPLOY_TEST_MAE = 1.00
MIN_DEPLOY_WITHIN1 = 0.85
MIN_DEPLOY_DEATH_AGREEMENT = 0.90
MIN_DEPLOY_ESCAPE_AGREEMENT = 0.90

ESCAPE_CLASS = "Mother Escaped (Ignore Rest)"

EXCLUDE_CLASSES = [
    "2 Cells (Right)",
    "2 Cells",
    "Skipped / Bad Trap",
]

# ==============================================================================
# CANONICAL INPUT GEOMETRY -- must match the annotator inference builder
# ==============================================================================
DISPLAY_SPACE_SIZE = 460.0
MODEL_IMG_SIZE = (128, 128)
HEATMAP_SIGMA = 10.0
GAP_SHIFT_RAW_PX = 25.0
MODEL_INPUT_FORMAT = "temporal_triplet_v2"


def display_to_raw(x, y, raw_w, raw_h):
    try:
        x, y = float(x), float(y)
    except (TypeError, ValueError):
        return np.nan, np.nan
    if np.isnan(x) or np.isnan(y):
        return np.nan, np.nan
    return x * (raw_w / DISPLAY_SPACE_SIZE), y * (raw_h / DISPLAY_SPACE_SIZE)


def resolve_heatmap_anchor(coords, raw_w, raw_h):
    coords = coords or {}
    mx, my = display_to_raw(
        coords.get("Mother_X", np.nan), coords.get("Mother_Y", np.nan), raw_w, raw_h
    )
    if not (np.isnan(mx) or np.isnan(my)):
        return mx, my

    p1x, p1y = display_to_raw(
        coords.get("Pillar_P1_X", np.nan), coords.get("Pillar_P1_Y", np.nan), raw_w, raw_h
    )
    p2x, p2y = display_to_raw(
        coords.get("Pillar_P2_X", np.nan), coords.get("Pillar_P2_Y", np.nan), raw_w, raw_h
    )
    if not any(np.isnan(v) for v in (p1x, p1y, p2x, p2y)):
        gap_x = min(raw_w - 1.0, (p1x + p2x) / 2.0 + GAP_SHIFT_RAW_PX)
        gap_y = (p1y + p2y) / 2.0
        return gap_x, gap_y
    return raw_w / 2.0, raw_h / 2.0


def gaussian_heatmap_uint8(width, height, cx, cy, sigma):
    x = np.arange(width, dtype=np.float32)
    y = np.arange(height, dtype=np.float32)[:, np.newaxis]
    hm = np.exp(-(((x - cx) ** 2) + ((y - cy) ** 2)) / (2.0 * sigma**2))
    return np.clip(hm * 255.0, 0, 255).astype(np.uint8)


def build_model_input(raw_img, coords=None, prev_img=None, next_img=None):
    """4-channel input: [t-1 grayscale, t grayscale, t+1 grayscale, anchor heatmap]."""

    def _norm_gray_128(img):
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        p_low, p_high = np.percentile(img, (0.5, 99.5))
        if p_high > p_low:
            out = np.clip(
                (img.astype(np.float32) - p_low) * (255.0 / (p_high - p_low)), 0, 255
            ).astype(np.uint8)
        else:
            out = img.astype(np.uint8)
        return cv2.resize(out, MODEL_IMG_SIZE)

    raw_h, raw_w = raw_img.shape[:2]
    curr = _norm_gray_128(raw_img)
    prev = _norm_gray_128(prev_img) if prev_img is not None else curr
    nxt = _norm_gray_128(next_img) if next_img is not None else curr

    ax_raw, ay_raw = resolve_heatmap_anchor(coords, raw_w, raw_h)
    ax_model = ax_raw * (MODEL_IMG_SIZE[0] / float(raw_w))
    ay_model = ay_raw * (MODEL_IMG_SIZE[1] / float(raw_h))
    heatmap = gaussian_heatmap_uint8(
        MODEL_IMG_SIZE[0], MODEL_IMG_SIZE[1], ax_model, ay_model, HEATMAP_SIGMA
    )
    return np.dstack([prev, curr, nxt, heatmap])


# ==============================================================================
# SHARED BIOLOGICAL ENDPOINT DEFINITION
# ==============================================================================
def find_division_frames(frame_labels):
    """Completed division = Late Bud -> Mother/Early Bud, bridging gap states."""
    gap_states = ("No Cell", "Out of Focus / Blurry")
    div_frames = []
    for i in range(1, len(frame_labels)):
        curr = frame_labels[i]
        prev = frame_labels[i - 1]
        if curr is None or prev is None:
            continue
        if prev == "Late Bud" and curr in ("Mother", "Early Bud"):
            div_frames.append(i)
        elif curr in ("Mother", "Early Bud"):
            lookback_idx = i - 1
            while lookback_idx >= 0 and frame_labels[lookback_idx] in gap_states:
                lookback_idx -= 1
            if (
                0 <= lookback_idx < i - 1
                and frame_labels[lookback_idx] in ("Early Bud", "Late Bud")
            ):
                div_frames.append(i)
    return div_frames


def calculate_trap_rls(frame_labels):
    valid_living_states = {"Mother", "Early Bud", "Late Bud"}
    rls_count = len(find_division_frames(frame_labels))

    died_on_chip, death_frame_idx = False, None
    for i in range(1, len(frame_labels)):
        if frame_labels[i] != "Dead Cell":
            continue
        lb = i - 1
        while lb >= 0 and frame_labels[lb] in ("Out of Focus / Blurry", None):
            lb -= 1
        if lb >= 0 and frame_labels[lb] in valid_living_states:
            died_on_chip, death_frame_idx = True, i
            break

    return {
        "rls_count": rls_count,
        "died_on_chip": died_on_chip,
        "death_frame": death_frame_idx,
    }


# ==============================================================================
# ANNOTATION CLEANING
# ==============================================================================
LONG_TERMINAL_MOTHER_RUN = 40
TERMINAL_MOTHER_KEEP = 15


def phantom_guard(df):
    """Drops only strong legacy phantom-label signatures; never edits Excel."""
    drop_idx = []
    n_postdeath = n_terminal = affected = 0
    chip_key = df["Chip_ID"] if "Chip_ID" in df.columns else pd.Series("chip", index=df.index)

    for _, g in df.groupby(
        [chip_key, df["Position"].astype(str).str.strip().str.lower(), df["Trap_ID"]]
    ):
        g = g.sort_values("Frame")
        labels = [str(c) for c in g["Class"]]
        idxs = list(g.index)
        rls = calculate_trap_rls(labels)
        removed = set()

        if rls["death_frame"] is not None:
            for j in range(rls["death_frame"] + 1, len(labels)):
                if labels[j] in ("Mother", "Early Bud", "Late Bud"):
                    removed.add(j)
                    n_postdeath += 1

        surviving = [j for j in range(len(labels)) if j not in removed]
        terminal_run = []
        for j in reversed(surviving):
            if labels[j] == "Mother":
                terminal_run.append(j)
            else:
                break
        if len(terminal_run) >= LONG_TERMINAL_MOTHER_RUN:
            for j in sorted(terminal_run)[TERMINAL_MOTHER_KEEP:]:
                removed.add(j)
                n_terminal += 1

        if removed:
            affected += 1
            drop_idx.extend(idxs[j] for j in removed)

    if drop_idx:
        print(
            f"--> Phantom guard: dropped {n_postdeath} post-death living labels and "
            f"{n_terminal} terminal-Mother frames across {affected} traps "
            f"({len(drop_idx)} rows total; Excel untouched)."
        )
        return df.drop(index=drop_idx).reset_index(drop=True)

    print("--> Phantom guard: no contamination signatures found.")
    return df


# ==============================================================================
# CHIP-AWARE TRAP-DIRECTORY RESOLUTION
# ==============================================================================
def _norm_chip_id(value):
    return str(value).strip().lower()


def resolve_traps_dirs(chip_ids):
    """Resolve one extracted-trap directory per Chip_ID.

    Safety rules:
      * Multi-chip annotation files may NEVER use the legacy single AGING_TRAPS_DIR
        override, because identical Pos/Trap names across chips would be ambiguous.
      * AGING_TRAPS_DIRS_JSON may override defaults with a JSON object:
          {"Chip_ID_A": "/path/a", "Chip_ID_B": "/path/b"}
      * Every annotated Chip_ID must resolve to exactly one distinct directory.
    """
    chips = sorted({str(c).strip() for c in chip_ids if str(c).strip() and str(c).lower() != "nan"})
    if not chips:
        raise RuntimeError("No valid Chip_ID values were found in the annotation sheet.")

    if TRAPS_DIRS_JSON_OVERRIDE:
        try:
            raw_mapping = json.loads(TRAPS_DIRS_JSON_OVERRIDE)
        except Exception as e:
            raise RuntimeError(
                "AGING_TRAPS_DIRS_JSON is not valid JSON. Expected a JSON object "
                "mapping Chip_ID -> extracted_traps directory."
            ) from e
        if not isinstance(raw_mapping, dict):
            raise RuntimeError("AGING_TRAPS_DIRS_JSON must decode to a JSON object.")
    elif LEGACY_TRAPS_DIR_OVERRIDE:
        if len(chips) != 1:
            raise RuntimeError(
                "AGING_TRAPS_DIR is a legacy SINGLE-CHIP override, but the annotation "
                f"file contains {len(chips)} chips: {chips}. Refusing to guess which "
                "images belong to which chip. Use AGING_TRAPS_DIRS_JSON instead."
            )
        raw_mapping = {chips[0]: LEGACY_TRAPS_DIR_OVERRIDE}
    else:
        raw_mapping = DEFAULT_TRAPS_DIRS

    normalized_mapping = {_norm_chip_id(k): str(v) for k, v in raw_mapping.items()}
    resolved = {}
    missing = []
    for chip in chips:
        key = _norm_chip_id(chip)
        if key not in normalized_mapping:
            missing.append(chip)
        else:
            resolved[chip] = normalized_mapping[key]

    if missing:
        raise RuntimeError(
            "No extracted-trap directory configured for Chip_ID(s): "
            + ", ".join(missing)
            + ". Add them to DEFAULT_TRAPS_DIRS or AGING_TRAPS_DIRS_JSON."
        )

    # A duplicated root for two Chip_IDs is almost always a catastrophic
    # configuration error because Pos0/Trap0 etc. recur across experiments.
    seen_roots = {}
    for chip, root in resolved.items():
        root_key = os.path.normcase(os.path.normpath(root))
        if root_key in seen_roots:
            raise RuntimeError(
                f"Chip_ID '{chip}' and '{seen_roots[root_key]}' resolve to the same "
                f"trap directory: {root}. Refusing ambiguous multi-chip mapping."
            )
        seen_roots[root_key] = chip

    return resolved


# ==============================================================================
# DATA LOADING
# ==============================================================================
def map_trap_files(traps_dirs):
    """Map (chip_id, position, trap_id) -> TIFF path with collision checks."""
    file_map = {}

    for chip_id, traps_dir in traps_dirs.items():
        all_files = glob.glob(os.path.join(traps_dir, "*.tif")) + glob.glob(
            os.path.join(traps_dir, "**", "*.tif"), recursive=True
        )
        all_files = sorted(set(all_files))
        chip_count = 0

        for fpath in all_files:
            pos_m = re.search(r"(pos\d+)", fpath, re.IGNORECASE)
            trap_m = re.search(r"trap_?(\d+)\.tif", fpath, re.IGNORECASE)
            if not (pos_m and trap_m):
                continue

            key = (_norm_chip_id(chip_id), pos_m.group(1).lower(), int(trap_m.group(1)))
            if key in file_map and os.path.normcase(os.path.normpath(file_map[key])) != os.path.normcase(os.path.normpath(fpath)):
                raise RuntimeError(
                    f"Duplicate TIFF mapping for {key}:\n  {file_map[key]}\n  {fpath}"
                )
            file_map[key] = fpath
            chip_count += 1

        print(f"--> TIFF trap stacks mapped [{chip_id}]: {chip_count} from {traps_dir}")

    return file_map


def row_coords(row):
    return {
        "Pillar_P1_X": row.get("Pillar_P1_X", np.nan),
        "Pillar_P1_Y": row.get("Pillar_P1_Y", np.nan),
        "Pillar_P2_X": row.get("Pillar_P2_X", np.nan),
        "Pillar_P2_Y": row.get("Pillar_P2_Y", np.nan),
        "Mother_X": row.get("Mother_X", np.nan),
        "Mother_Y": row.get("Mother_Y", np.nan),
    }


def _load_one_trap(args):
    fpath, rows = args
    with tif.TiffFile(fpath) as tf_file:
        stack = [page.asarray() for page in tf_file.pages]

    out = []
    for row in rows:
        frame_num = int(row["Frame"])
        if frame_num < 0 or frame_num >= len(stack):
            continue
        prev_img = stack[frame_num - 1] if frame_num > 0 else None
        next_img = stack[frame_num + 1] if frame_num + 1 < len(stack) else None
        img = build_model_input(
            stack[frame_num], coords=row_coords(row), prev_img=prev_img, next_img=next_img
        )
        out.append(
            (
                img,
                int(row["label_idx"]),
                {
                    "chip": str(row.get("Chip_ID", "chip")).strip(),
                    "pos": str(row["Position"]).strip().lower(),
                    "trap_id": int(row["Trap_ID"]),
                    "frame": frame_num,
                    "class_str": str(row["Class"]).strip(),
                },
            )
        )
    return out


def load_frames(df, file_map):
    t0 = time.time()
    by_file, missing = {}, set()
    for _, row in df.iterrows():
        key = (
            _norm_chip_id(row.get("Chip_ID", "chip")),
            str(row["Position"]).strip().lower(),
            int(row["Trap_ID"]),
        )
        if key not in file_map:
            missing.add(key)
            continue
        by_file.setdefault(file_map[key], []).append(row)

    images, labels, metadata = [], [], []
    tasks = sorted(by_file.items())
    with ThreadPoolExecutor(max_workers=max(1, LOAD_WORKERS)) as pool:
        for chunk in pool.map(_load_one_trap, tasks):
            for img, lbl, meta in chunk:
                images.append(img)
                labels.append(lbl)
                metadata.append(meta)

    if missing:
        print(f"--> Warning: {len(missing)} annotated traps had no matching TIFF and were skipped.")
    print(f"--> Loaded frames with {LOAD_WORKERS} workers in {time.time() - t0:.1f}s.")
    return (
        np.asarray(images, dtype=np.uint8),
        np.asarray(labels, dtype=np.int64),
        metadata,
    )


def build_trap_orders(meta_list):
    orders = {}
    for i, m in enumerate(meta_list):
        key = (m["chip"], m["pos"], m["trap_id"])
        orders.setdefault(key, []).append((m["frame"], i))
    for key in orders:
        orders[key].sort()
        orders[key] = [i for _, i in orders[key]]
    return orders


def build_endpoint_targets(meta_list, trap_orders):
    n = len(meta_list)
    div_y = np.zeros(n, dtype=np.float32)
    dead_y = np.zeros(n, dtype=np.float32)
    esc_y = np.zeros(n, dtype=np.float32)
    human_rls = {}

    for key, order in trap_orders.items():
        labels = [meta_list[i]["class_str"] for i in order]
        div_local = find_division_frames(labels)
        rls = calculate_trap_rls(labels)
        esc_local = next(
            (j for j, gi in enumerate(order) if meta_list[gi]["class_str"] == ESCAPE_CLASS),
            None,
        )
        rls["escaped"] = esc_local is not None
        rls["escape_local_idx"] = esc_local
        human_rls[key] = rls

        for j in div_local:
            gi = order[j]
            div_y[gi] = 1.0
            if EVENT_SOFT_NEIGHBOR > 0:
                if j - 1 >= 0:
                    div_y[order[j - 1]] = max(div_y[order[j - 1]], EVENT_SOFT_NEIGHBOR)
                if j + 1 < len(order):
                    div_y[order[j + 1]] = max(div_y[order[j + 1]], EVENT_SOFT_NEIGHBOR)

        for gi in order:
            dead_y[gi] = 1.0 if meta_list[gi]["class_str"] == "Dead Cell" else 0.0
            esc_y[gi] = 1.0 if meta_list[gi]["class_str"] == ESCAPE_CLASS else 0.0

    return div_y, dead_y, esc_y, human_rls


# ==============================================================================
# TRAP-LEVEL STRATIFIED SPLIT
# ==============================================================================
def stratified_trap_split(trap_orders):
    rng = np.random.RandomState(RANDOM_SEED)
    by_pos = {}
    for key in trap_orders:
        # key = (chip_id, position, trap_id). Treat the same Pos number on two
        # different physical chips as two distinct acquisition positions.
        by_pos.setdefault((key[0], key[1]), []).append(key)

    train_keys, cal_keys, test_keys = set(), set(), set()
    for chip_pos, keys in sorted(by_pos.items()):
        keys = list(keys)
        rng.shuffle(keys)
        n = len(keys)

        if n < 3:
            train_keys.update(keys)
            continue

        n_test = max(1, int(round(n * TEST_FRACTION)))
        n_cal = max(1, int(round(n * CAL_FRACTION)))
        while n - n_test - n_cal < 1:
            if n_test >= n_cal and n_test > 1:
                n_test -= 1
            elif n_cal > 1:
                n_cal -= 1
            else:
                break

        test_keys.update(keys[:n_test])
        cal_keys.update(keys[n_test : n_test + n_cal])
        train_keys.update(keys[n_test + n_cal :])

    return train_keys, cal_keys, test_keys


def indices_for_keys(meta_list, keys):
    return np.asarray(
        [
            i
            for i, m in enumerate(meta_list)
            if (m["chip"], m["pos"], m["trap_id"]) in keys
        ],
        dtype=np.int64,
    )


def focused_training_indices(train_idx, meta_list, trap_orders, div_y):
    train_set = set(int(i) for i in train_idx)
    keep = set()

    for _, full_order in trap_orders.items():
        order = [i for i in full_order if i in train_set]
        if not order:
            continue
        labels = [meta_list[i]["class_str"] for i in order]
        local_keep = np.zeros(len(order), dtype=bool)

        event_locals = [j for j, gi in enumerate(order) if div_y[gi] >= 0.99]
        for j in event_locals:
            local_keep[max(0, j - EVENT_KEEP_RADIUS) : min(len(order), j + EVENT_KEEP_RADIUS + 1)] = True

        for j in range(1, len(order)):
            if labels[j] != labels[j - 1]:
                local_keep[
                    max(0, j - TRANSITION_KEEP_RADIUS) : min(
                        len(order), j + TRANSITION_KEEP_RADIUS + 1
                    )
                ] = True

        local_keep[0] = True
        local_keep[-1] = True
        for j, gi in enumerate(order):
            if local_keep[j] or j % BACKGROUND_STRIDE == 0:
                keep.add(gi)

    return np.asarray(sorted(keep), dtype=np.int64)


# ==============================================================================
# MODEL
# ==============================================================================
@tf.keras.utils.register_keras_serializable(package="AgingChip")
def weighted_division_bce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    loss = tf.nn.weighted_cross_entropy_with_logits(
        labels=y_true, logits=y_pred, pos_weight=tf.cast(DIVISION_POS_WEIGHT, tf.float32)
    )
    return tf.reduce_mean(loss)


@tf.keras.utils.register_keras_serializable(package="AgingChip")
def weighted_dead_bce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    loss = tf.nn.weighted_cross_entropy_with_logits(
        labels=y_true, logits=y_pred, pos_weight=tf.cast(DEAD_POS_WEIGHT, tf.float32)
    )
    return tf.reduce_mean(loss)


@tf.keras.utils.register_keras_serializable(package="AgingChip")
def weighted_escape_bce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    loss = tf.nn.weighted_cross_entropy_with_logits(
        labels=y_true, logits=y_pred, pos_weight=tf.cast(ESCAPE_POS_WEIGHT, tf.float32)
    )
    return tf.reduce_mean(loss)


def build_model(num_classes):
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(*MODEL_IMG_SIZE, 3), include_top=False, weights="imagenet"
    )
    base_model.trainable = False

    inputs = layers.Input(shape=(*MODEL_IMG_SIZE, 4), name="temporal_triplet_heatmap")

    # Geometric augmentation is shared by all four channels so temporal and
    # heatmap geometry remain coherent.
    x_aug = layers.RandomFlip("vertical", name="aug_flip")(inputs)
    x_aug = layers.RandomTranslation(
        0.05, 0.05, fill_mode="constant", fill_value=0.0, name="aug_translate"
    )(x_aug)
    x_aug = layers.RandomZoom(
        0.08, fill_mode="constant", fill_value=0.0, name="aug_zoom"
    )(x_aug)

    # Morphology branch. IMPORTANT: adapter starts as CURRENT-frame replication
    # into RGB rather than a random mixture of temporal/heatmap channels.
    scaled_pm1 = layers.Rescaling(1.0 / 127.5, offset=-1.0, name="morph_rescale")(x_aug)
    init_kernel = np.zeros((1, 1, 4, 3), dtype=np.float32)
    init_kernel[0, 0, 1, :] = 1.0  # current frame = channel 1
    adapter = layers.Conv2D(
        3,
        1,
        padding="same",
        use_bias=False,
        kernel_initializer=tf.keras.initializers.Constant(init_kernel),
        name="spatial_fusion_adapter",
    )(scaled_pm1)
    morph = base_model(adapter, training=False)
    morph = layers.GlobalAveragePooling2D(name="morph_gap")(morph)
    morph = layers.Dense(192, activation="swish", name="morph_dense")(morph)

    # Trainable motion branch reads all four channels directly and therefore can
    # learn t-1 -> t -> t+1 differences without forcing ImageNet features to do it.
    motion = layers.Rescaling(1.0 / 255.0, name="motion_rescale")(x_aug)
    motion = layers.Conv2D(32, 5, strides=2, padding="same", use_bias=False, name="motion_c1")(motion)
    motion = layers.BatchNormalization(name="motion_bn1")(motion)
    motion = layers.Activation("swish", name="motion_a1")(motion)
    motion = layers.Conv2D(64, 3, strides=2, padding="same", use_bias=False, name="motion_c2")(motion)
    motion = layers.BatchNormalization(name="motion_bn2")(motion)
    motion = layers.Activation("swish", name="motion_a2")(motion)
    motion = layers.Conv2D(128, 3, strides=2, padding="same", use_bias=False, name="motion_c3")(motion)
    motion = layers.BatchNormalization(name="motion_bn3")(motion)
    motion = layers.Activation("swish", name="motion_a3")(motion)
    motion = layers.GlobalAveragePooling2D(name="motion_gap")(motion)
    motion = layers.Dense(160, activation="swish", name="motion_dense")(motion)

    fused = layers.Concatenate(name="fused_features")([morph, motion])
    fused = layers.Dense(256, activation="swish", name="fusion_dense")(fused)
    fused = layers.Dropout(0.35, name="fusion_dropout")(fused)

    state_logits = layers.Dense(num_classes, dtype="float32", name="state")(fused)
    division_logit = layers.Dense(1, dtype="float32", name="division")(fused)
    dead_logit = layers.Dense(1, dtype="float32", name="dead")(fused)
    escape_logit = layers.Dense(1, dtype="float32", name="escape")(fused)

    model = models.Model(
        inputs=inputs,
        outputs={
            "state": state_logits,
            "division": division_logit,
            "dead": dead_logit,
            "escape": escape_logit,
        },
        name="aging_chip_multitask_rls",
    )
    rls_probe = models.Model(
        inputs, [division_logit, dead_logit, escape_logit], name="rls_probe"
    )
    return model, base_model, rls_probe


def compile_model(model, lr):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss={
            "state": tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            "division": weighted_division_bce,
            "dead": weighted_dead_bce,
            "escape": weighted_escape_bce,
        },
        loss_weights={
            "state": LOSS_W_STATE,
            "division": LOSS_W_DIVISION,
            "dead": LOSS_W_DEAD,
            "escape": LOSS_W_ESCAPE,
        },
        metrics={
            "state": ["accuracy"],
            "division": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
            "dead": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
            "escape": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
        },
    )


def make_dataset(X, y_state, y_div, y_dead, y_esc, indices, training):
    Xi = X[indices]
    ys = y_state[indices]
    yd = y_div[indices].reshape(-1, 1)
    ydead = y_dead[indices].reshape(-1, 1)
    yesc = y_esc[indices].reshape(-1, 1)
    ds = tf.data.Dataset.from_tensor_slices(
        (Xi, {"state": ys, "division": yd, "dead": ydead, "escape": yesc})
    )
    if training:
        ds = ds.shuffle(min(len(indices), 20000), seed=RANDOM_SEED, reshuffle_each_iteration=True)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def predict_rls_heads(rls_probe, X, indices=None):
    arr = X if indices is None else X[indices]
    ds = tf.data.Dataset.from_tensor_slices(arr).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    div_logits, dead_logits, esc_logits = rls_probe.predict(ds, verbose=0)
    div_p = tf.math.sigmoid(div_logits).numpy().ravel()
    dead_p = tf.math.sigmoid(dead_logits).numpy().ravel()
    esc_p = tf.math.sigmoid(esc_logits).numpy().ravel()
    return div_p, dead_p, esc_p


# ==============================================================================
# DIRECT RLS DECODER (NO HMM)
# ==============================================================================
def pick_division_events(prob_seq, threshold, min_gap):
    """Local maxima + nonmaximum suppression; returns one pulse per division."""
    p = np.asarray(prob_seq, dtype=np.float64)
    if len(p) == 0:
        return []

    candidates = []
    for i, v in enumerate(p):
        if v < threshold:
            continue
        left = p[i - 1] if i > 0 else -np.inf
        right = p[i + 1] if i + 1 < len(p) else -np.inf
        if v >= left and v >= right:
            candidates.append(i)

    # Highest-confidence peak wins inside each refractory window.
    candidates.sort(key=lambda i: float(p[i]), reverse=True)
    chosen = []
    for i in candidates:
        if all(abs(i - j) >= min_gap for j in chosen):
            chosen.append(i)
    return sorted(chosen)


def sustained_death(prob_seq, threshold, persistence):
    run = 0
    for i, v in enumerate(prob_seq):
        if v >= threshold:
            run += 1
            if run >= persistence:
                return True, i - persistence + 1
        else:
            run = 0
    return False, None


def _split_probs_to_traps(probs, split_indices, meta_list, trap_orders):
    idx_to_local = {int(gi): li for li, gi in enumerate(split_indices)}
    out = {}
    for key, order in trap_orders.items():
        if not order or order[0] not in idx_to_local:
            continue
        local = [idx_to_local[i] for i in order if i in idx_to_local]
        if len(local) == len(order):
            out[key] = np.asarray([probs[j] for j in local], dtype=np.float64)
    return out


def calibrate_division_decoder(div_prob_by_trap, human_rls):
    best = None
    for thr in DIV_THRESHOLDS:
        for gap in DIV_MIN_GAPS:
            signed = []
            abs_err = []
            for key, p in div_prob_by_trap.items():
                pred = len(pick_division_events(p, thr, gap))
                true = int(human_rls[key]["rls_count"])
                signed.append(pred - true)
                abs_err.append(abs(pred - true))
            if not abs_err:
                continue
            a = np.asarray(abs_err)
            s = np.asarray(signed)
            metrics = {
                "threshold": float(thr),
                "min_gap": int(gap),
                "mae": float(a.mean()),
                "bias": float(s.mean()),
                "exact": float((a == 0).mean()),
                "within1": float((a <= 1).mean()),
            }
            rank = (metrics["mae"], -metrics["within1"], -metrics["exact"], abs(metrics["bias"]))
            if best is None or rank < best[0]:
                best = (rank, metrics)
    if best is None:
        raise RuntimeError("Could not calibrate division decoder: no calibration traps.")
    return best[1]


def calibrate_death_decoder(dead_prob_by_trap, human_rls):
    best = None
    for thr in DEATH_THRESHOLDS:
        for persist in DEATH_PERSISTENCES:
            correct = 0
            n = 0
            for key, p in dead_prob_by_trap.items():
                pred, _ = sustained_death(p, thr, persist)
                true = bool(human_rls[key]["died_on_chip"])
                correct += int(pred == true)
                n += 1
            if n == 0:
                continue
            acc = correct / n
            rank = (-acc, persist, -thr)  # prefer shorter persistence, then stricter threshold
            metrics = {
                "threshold": float(thr),
                "persistence": int(persist),
                "agreement": float(acc),
                "correct": int(correct),
                "n": int(n),
            }
            if best is None or rank < best[0]:
                best = (rank, metrics)
    if best is None:
        raise RuntimeError("Could not calibrate death decoder: no calibration traps.")
    return best[1]


def calibrate_escape_decoder(esc_prob_by_trap, human_rls):
    """Escape = the mother leaves the trap; everything after is censored,
    exactly like the human 'Mother Escaped (Ignore Rest)' rule. Uses the
    same sustained-run decode as death."""
    best = None
    for thr in ESCAPE_THRESHOLDS:
        for persist in ESCAPE_PERSISTENCES:
            correct = 0
            n = 0
            frame_errs = []
            for key, p in esc_prob_by_trap.items():
                pred, pred_frame = sustained_death(p, thr, persist)
                true = bool(human_rls[key].get("escaped", False))
                correct += int(pred == true)
                n += 1
                true_local = human_rls[key].get("escape_local_idx")
                if pred and true and true_local is not None:
                    frame_errs.append(abs(int(pred_frame) - int(true_local)))
            if n == 0:
                continue
            acc = correct / n
            med = float(np.median(frame_errs)) if frame_errs else 1e9
            rank = (-acc, med, persist, -thr)
            metrics = {
                "threshold": float(thr),
                "persistence": int(persist),
                "agreement": float(acc),
                "correct": int(correct),
                "n": int(n),
                "median_censor_frame_error": (None if not frame_errs else med),
            }
            if best is None or rank < best[0]:
                best = (rank, metrics)
    if best is None:
        raise RuntimeError("Could not calibrate escape decoder: no calibration traps.")
    return best[1]


def evaluate_split(
    div_prob_by_trap, dead_prob_by_trap, esc_prob_by_trap, human_rls, div_cfg, dead_cfg, esc_cfg
):
    rows = []
    for key in sorted(div_prob_by_trap):
        true_rls = int(human_rls[key]["rls_count"])
        pred_events = pick_division_events(
            div_prob_by_trap[key], div_cfg["threshold"], div_cfg["min_gap"]
        )
        pred_rls = len(pred_events)
        pred_dead, pred_death_frame = sustained_death(
            dead_prob_by_trap[key], dead_cfg["threshold"], dead_cfg["persistence"]
        )
        pred_escaped, pred_escape_frame = sustained_death(
            esc_prob_by_trap[key], esc_cfg["threshold"], esc_cfg["persistence"]
        )
        if pred_escaped:
            # Escape censors everything after it, exactly like the human rule.
            pred_events = [e for e in pred_events if e < pred_escape_frame]
            pred_rls = len(pred_events)
            if pred_death_frame is None or pred_death_frame >= pred_escape_frame:
                pred_dead, pred_death_frame = False, None
        true_dead = bool(human_rls[key]["died_on_chip"])
        true_escaped = bool(human_rls[key].get("escaped", False))
        rows.append(
            {
                "chip": key[0],
                "position": key[1],
                "trap_id": key[2],
                "true_rls": true_rls,
                "pred_rls": pred_rls,
                "signed_error": pred_rls - true_rls,
                "abs_error": abs(pred_rls - true_rls),
                "true_died": true_dead,
                "pred_died": bool(pred_dead),
                "pred_death_frame": pred_death_frame,
                "true_escaped": true_escaped,
                "pred_escaped": bool(pred_escaped),
                "pred_escape_frame": pred_escape_frame,
                "true_escape_local_idx": human_rls[key].get("escape_local_idx"),
            }
        )

    report = pd.DataFrame(rows)
    if report.empty:
        return report, {
            "mae": np.nan,
            "bias": np.nan,
            "exact": np.nan,
            "within1": np.nan,
            "death_agreement": np.nan,
            "escape_agreement": np.nan,
            "n_traps": 0,
        }
    metrics = {
        "mae": float(report["abs_error"].mean()),
        "bias": float(report["signed_error"].mean()),
        "exact": float((report["abs_error"] == 0).mean()),
        "within1": float((report["abs_error"] <= 1).mean()),
        "death_agreement": float((report["true_died"] == report["pred_died"]).mean()),
        "escape_agreement": float(
            (report["true_escaped"] == report["pred_escaped"]).mean()
        ),
        "n_traps": int(len(report)),
    }
    return report, metrics


def candidate_endpoint(rls_probe, X, split_idx, meta_list, trap_orders, human_rls):
    div_p, dead_p, esc_p = predict_rls_heads(rls_probe, X, split_idx)
    div_by = _split_probs_to_traps(div_p, split_idx, meta_list, trap_orders)
    dead_by = _split_probs_to_traps(dead_p, split_idx, meta_list, trap_orders)
    esc_by = _split_probs_to_traps(esc_p, split_idx, meta_list, trap_orders)
    div_cfg = calibrate_division_decoder(div_by, human_rls)
    dead_cfg = calibrate_death_decoder(dead_by, human_rls)
    esc_cfg = calibrate_escape_decoder(esc_by, human_rls)
    _, metrics = evaluate_split(
        div_by, dead_by, esc_by, human_rls, div_cfg, dead_cfg, esc_cfg
    )
    return div_cfg, dead_cfg, esc_cfg, metrics


def endpoint_rank(metrics):
    return (
        metrics["mae"],
        -metrics["within1"],
        -metrics["exact"],
        -metrics["death_agreement"],
        -metrics["escape_agreement"],
        abs(metrics["bias"]),
    )


class RLSEndpointCallback(tf.keras.callbacks.Callback):
    """Early stopping/checkpointing on calibrated trap-level RLS, not val_loss."""

    def __init__(
        self,
        rls_probe,
        X,
        cal_idx,
        meta_list,
        trap_orders,
        human_rls,
        checkpoint_path,
        patience,
        min_epochs,
        stage_name,
    ):
        super().__init__()
        self.rls_probe = rls_probe
        self.X = X
        self.cal_idx = cal_idx
        self.meta_list = meta_list
        self.trap_orders = trap_orders
        self.human_rls = human_rls
        self.checkpoint_path = checkpoint_path
        self.patience = patience
        self.min_epochs = min_epochs
        self.stage_name = stage_name
        self.best_rank = None
        self.best_epoch = None
        self.best_div_cfg = None
        self.best_dead_cfg = None
        self.best_esc_cfg = None
        self.best_metrics = None
        self.bad_epochs = 0

    def on_epoch_end(self, epoch, logs=None):
        div_cfg, dead_cfg, esc_cfg, metrics = candidate_endpoint(
            self.rls_probe,
            self.X,
            self.cal_idx,
            self.meta_list,
            self.trap_orders,
            self.human_rls,
        )
        rank = endpoint_rank(metrics)
        print(
            f"\n[{self.stage_name} endpoint] epoch {epoch + 1}: "
            f"RLS_MAE={metrics['mae']:.2f} bias={metrics['bias']:+.2f} "
            f"exact={metrics['exact']*100:.1f}% within1={metrics['within1']*100:.1f}% "
            f"death={metrics['death_agreement']*100:.1f}% "
            f"escape={metrics['escape_agreement']*100:.1f}% | "
            f"div_thr={div_cfg['threshold']:.2f} gap={div_cfg['min_gap']} "
            f"dead_thr={dead_cfg['threshold']:.2f} persist={dead_cfg['persistence']} "
            f"esc_thr={esc_cfg['threshold']:.2f} epersist={esc_cfg['persistence']}"
        )

        if self.best_rank is None or rank < self.best_rank:
            self.best_rank = rank
            self.best_epoch = epoch + 1
            self.best_div_cfg = div_cfg
            self.best_dead_cfg = dead_cfg
            self.best_esc_cfg = esc_cfg
            self.best_metrics = metrics
            self.bad_epochs = 0
            self.model.save_weights(self.checkpoint_path)
            print(f"[{self.stage_name} endpoint] new best -> saved {self.checkpoint_path}")
        else:
            self.bad_epochs += 1

        if epoch + 1 >= self.min_epochs and self.bad_epochs >= self.patience:
            print(
                f"[{self.stage_name} endpoint] no RLS improvement for {self.bad_epochs} epochs; stopping."
            )
            self.model.stop_training = True


# ==============================================================================
# EXPORT
# ==============================================================================
def export_inference_models(
    model, class_names, div_cfg, dead_cfg, esc_cfg, test_metrics, split_info, deployment_ok
):
    # Fresh uncompiled submodels avoid custom-loss deserialization in the UI.
    state_model = models.Model(model.input, model.get_layer("state").output, name="aging_chip_classifier")
    rls_model = models.Model(
        model.input,
        [
            model.get_layer("division").output,
            model.get_layer("dead").output,
            model.get_layer("escape").output,
        ],
        name="aging_chip_rls_detector",
    )

    if deployment_ok:
        state_path = STATE_MODEL_OUT
        rls_path = RLS_MODEL_OUT
        labels_path = CLASS_LABELS_OUT
        model_meta_path = MODEL_META_OUT
        rls_meta_path = RLS_META_OUT
    else:
        state_path = "candidate_" + os.path.basename(STATE_MODEL_OUT)
        rls_path = "candidate_" + os.path.basename(RLS_MODEL_OUT)
        labels_path = "candidate_" + CLASS_LABELS_OUT
        model_meta_path = "candidate_" + MODEL_META_OUT
        rls_meta_path = "candidate_" + RLS_META_OUT

    state_model.save(state_path)
    rls_model.save(rls_path)

    with open(labels_path, "w") as f:
        json.dump(class_names, f, indent=2)

    with open(model_meta_path, "w") as f:
        json.dump(
            {
                "model_input_format": MODEL_INPUT_FORMAT,
                "viterbi_temperature": 0.0,
                "rls_source": os.path.basename(rls_path) + " (direct division-event detector)",
                "deployment_ok": bool(deployment_ok),
            },
            f,
            indent=2,
        )

    meta = {
        "model_input_format": MODEL_INPUT_FORMAT,
        "rls_method": "direct division-event peak detector; no HMM",
        "division_decoder": div_cfg,
        "death_decoder": dead_cfg,
        "escape_decoder": esc_cfg,
        "test_metrics": test_metrics,
        "split": split_info,
        "event_definition": "Late Bud -> Mother/Early Bud, bridging No Cell/Blurry gaps",
        "event_soft_neighbor_target": EVENT_SOFT_NEIGHBOR,
        "deployment_ok": bool(deployment_ok),
        "deployment_gate": {
            "max_test_mae": MAX_DEPLOY_TEST_MAE,
            "min_within1": MIN_DEPLOY_WITHIN1,
            "min_death_agreement": MIN_DEPLOY_DEATH_AGREEMENT,
            "min_escape_agreement": MIN_DEPLOY_ESCAPE_AGREEMENT,
        },
    }
    with open(rls_meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n--> Saved state model: {state_path}")
    print(f"--> Saved DIRECT RLS model: {rls_path}")
    print(f"--> Saved decoding metadata: {rls_meta_path}")


# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    np.random.seed(RANDOM_SEED)
    tf.random.set_seed(RANDOM_SEED)

    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for g in gpus:
            try:
                tf.config.experimental.set_memory_growth(g, True)
            except Exception:
                pass
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
        print(f"--> {len(gpus)} GPU(s) detected: mixed_float16 enabled.")
    else:
        print("--> No GPU detected: running on CPU.")

    if not os.path.exists(ANNOTATION_PATH):
        raise FileNotFoundError(f"Annotation file not found: {ANNOTATION_PATH}")

    print(f"--> Annotation file: {ANNOTATION_PATH}")

    df = pd.read_excel(ANNOTATION_PATH, sheet_name="Frame_Annotations")
    n_raw = len(df)
    df = df.dropna(subset=["Class"]).copy()
    df["Class"] = df["Class"].astype(str).str.strip()
    df = df[df["Class"].str.lower() != "nan"].reset_index(drop=True)
    print(f"--> Labeled rows: {len(df)} / {n_raw}")

    # Escaped traps are KEPT in full. Post-escape frames supervise the new
    # escape head, and calibration/test decoding therefore sees the same
    # full-stack reality the annotator UI decodes live. (Until 2026-08-26
    # these rows were trimmed here, which left every endpoint metric blind
    # to post-escape runaway division counting -- the failure seen on Pos41.)
    escaped = {}
    for _, row in df[df["Class"].isin([ESCAPE_CLASS, "Mother Escaped"])].iterrows():
        key = (
            _norm_chip_id(row.get("Chip_ID", "chip")),
            str(row["Position"]).strip().lower(),
            int(row["Trap_ID"]),
        )
        escaped[key] = min(escaped.get(key, 10**9), int(row["Frame"]))
    print(
        f"--> Escape supervision: {len(escaped)} escaped traps kept in full "
        f"({int((df['Class'] == ESCAPE_CLASS).sum())} post-escape frames)."
    )
    df = phantom_guard(df)
    df = df[~df["Class"].isin(EXCLUDE_CLASSES)].reset_index(drop=True)

    label_encoder = LabelEncoder()
    df["label_idx"] = label_encoder.fit_transform(df["Class"])
    class_names = list(label_encoder.classes_)
    num_classes = len(class_names)
    print(f"--> Auxiliary state classes ({num_classes}): {class_names}")

    annotated_chips = sorted(df["Chip_ID"].dropna().astype(str).str.strip().unique())
    traps_dirs = resolve_traps_dirs(annotated_chips)
    print("--> Resolved chip -> extracted-traps directories:")
    for _chip, _root in traps_dirs.items():
        print(f"    {_chip}: {_root}")

    file_map = map_trap_files(traps_dirs)
    print(f"--> TIFF trap stacks found across all chips: {len(file_map)}")

    mapped_chip_ids = {key[0] for key in file_map}
    missing_chip_maps = [c for c in annotated_chips if _norm_chip_id(c) not in mapped_chip_ids]
    if missing_chip_maps:
        raise RuntimeError(
            "No TIFF trap stacks were found for annotated Chip_ID(s): "
            + ", ".join(missing_chip_maps)
            + ". Refusing to train on a partial/miswired multi-chip dataset."
        )

    X, y_state, meta_list = load_frames(df, file_map)
    if len(X) == 0:
        sys.exit(
            f"\nFATAL: no annotated frames matched TIFF stacks.\n"
            f"Configured chip directories: {traps_dirs}\n"
            f"Check AGING_TRAPS_DIRS_JSON and transferred *_trap_*.tif files."
        )

    loaded_chips = {str(m["chip"]).strip() for m in meta_list}
    missing_loaded_chips = [c for c in annotated_chips if c not in loaded_chips]
    if missing_loaded_chips:
        raise RuntimeError(
            "Annotations exist but zero frames loaded for Chip_ID(s): "
            + ", ".join(missing_loaded_chips)
            + ". Refusing to silently omit an experiment."
        )

    for _chip in annotated_chips:
        _n_frames = sum(1 for m in meta_list if str(m["chip"]).strip() == _chip)
        _n_traps = len({
            (m["pos"], m["trap_id"])
            for m in meta_list
            if str(m["chip"]).strip() == _chip
        })
        print(f"--> Loaded [{_chip}]: {_n_frames} frames from {_n_traps} traps")

    trap_orders = build_trap_orders(meta_list)
    y_div, y_dead, y_esc, human_rls = build_endpoint_targets(meta_list, trap_orders)
    exact_divisions = int(np.sum(y_div >= 0.99))
    print(
        f"--> Loaded {len(X)} frames from {len(trap_orders)} usable traps | "
        f"{exact_divisions} true division events."
    )

    train_keys, cal_keys, test_keys = stratified_trap_split(trap_orders)
    train_idx_full = indices_for_keys(meta_list, train_keys)
    cal_idx = indices_for_keys(meta_list, cal_keys)
    test_idx = indices_for_keys(meta_list, test_keys)
    train_idx = focused_training_indices(train_idx_full, meta_list, trap_orders, y_div)

    if len(cal_keys) == 0 or len(test_keys) == 0:
        raise RuntimeError("Not enough traps for independent calibration and test splits.")

    print(
        f"--> Trap split: {len(train_keys)} train / {len(cal_keys)} calibration / "
        f"{len(test_keys)} untouched test"
    )
    for _chip in annotated_chips:
        _train_n = sum(1 for k in train_keys if str(k[0]).strip() == _chip)
        _cal_n = sum(1 for k in cal_keys if str(k[0]).strip() == _chip)
        _test_n = sum(1 for k in test_keys if str(k[0]).strip() == _chip)
        print(
            f"    split [{_chip}]: {_train_n} train / {_cal_n} calibration / "
            f"{_test_n} test traps"
        )
    print(
        f"--> Training frames: {len(train_idx_full)} full -> {len(train_idx)} focused | "
        f"cal={len(cal_idx)} | test={len(test_idx)}"
    )
    print(
        f"--> Training exact division prevalence: "
        f"{np.mean(y_div[train_idx] >= 0.99)*100:.2f}%"
    )

    train_ds = make_dataset(X, y_state, y_div, y_dead, y_esc, train_idx, training=True)
    cal_ds = make_dataset(X, y_state, y_div, y_dead, y_esc, cal_idx, training=False)

    model, base_model, rls_probe = build_model(num_classes)

    # ------------------------------- STAGE 1 ---------------------------------
    compile_model(model, LR_STAGE1)
    stage1_ckpt = "stage1_best.weights.h5"
    cb1 = RLSEndpointCallback(
        rls_probe,
        X,
        cal_idx,
        meta_list,
        trap_orders,
        human_rls,
        stage1_ckpt,
        ENDPOINT_PATIENCE_STAGE1,
        MIN_ENDPOINT_EPOCHS,
        "STAGE1",
    )
    print("\n================ STAGE 1: direct RLS heads + frozen ImageNet backbone ================")
    model.fit(
        train_ds,
        validation_data=cal_ds,
        epochs=EPOCHS_STAGE1,
        callbacks=[
            cb1,
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=2e-6),
        ],
        verbose=1 if sys.stdout.isatty() else 2,
    )
    model.load_weights(stage1_ckpt)
    stage1_div, stage1_dead, stage1_esc, stage1_metrics = candidate_endpoint(
        rls_probe, X, cal_idx, meta_list, trap_orders, human_rls
    )
    # Store the actual Stage-1 endpoint weights before fine-tuning mutates them.
    stage1_final_ckpt = "stage1_endpoint_best.weights.h5"
    model.save_weights(stage1_final_ckpt)

    print(
        f"\n--> Stage 1 best calibration endpoint: MAE={stage1_metrics['mae']:.2f}, "
        f"within1={stage1_metrics['within1']*100:.1f}%, "
        f"death={stage1_metrics['death_agreement']*100:.1f}%, "
        f"escape={stage1_metrics['escape_agreement']*100:.1f}%"
    )

    # ------------------------------- STAGE 2 ---------------------------------
    base_model.trainable = True
    for layer in base_model.layers:
        layer.trainable = False
    for layer in base_model.layers[-FINE_TUNE_TOP_LAYERS:]:
        if not isinstance(layer, layers.BatchNormalization):
            layer.trainable = True

    compile_model(model, LR_STAGE2)
    stage2_ckpt = "stage2_best.weights.h5"
    cb2 = RLSEndpointCallback(
        rls_probe,
        X,
        cal_idx,
        meta_list,
        trap_orders,
        human_rls,
        stage2_ckpt,
        ENDPOINT_PATIENCE_STAGE2,
        MIN_ENDPOINT_EPOCHS,
        "STAGE2",
    )
    print(
        f"\n================ STAGE 2: top {FINE_TUNE_TOP_LAYERS} backbone layers, endpoint-gated ================"
    )
    model.fit(
        train_ds,
        validation_data=cal_ds,
        epochs=EPOCHS_STAGE2,
        callbacks=[
            cb2,
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6),
        ],
        verbose=1 if sys.stdout.isatty() else 2,
    )
    model.load_weights(stage2_ckpt)
    stage2_div, stage2_dead, stage2_esc, stage2_metrics = candidate_endpoint(
        rls_probe, X, cal_idx, meta_list, trap_orders, human_rls
    )

    print(
        f"\n--> Stage 2 best calibration endpoint: MAE={stage2_metrics['mae']:.2f}, "
        f"within1={stage2_metrics['within1']*100:.1f}%, "
        f"death={stage2_metrics['death_agreement']*100:.1f}%, "
        f"escape={stage2_metrics['escape_agreement']*100:.1f}%"
    )

    # Endpoint-gated winner: fine-tuning cannot degrade the deployable model.
    if endpoint_rank(stage2_metrics) < endpoint_rank(stage1_metrics):
        winner = "stage2"
        chosen_div, chosen_dead, chosen_esc, chosen_cal_metrics = (
            stage2_div,
            stage2_dead,
            stage2_esc,
            stage2_metrics,
        )
        print("--> WINNER: Stage 2 improved the RLS endpoint; keeping fine-tuned weights.")
    else:
        winner = "stage1"
        model.load_weights(stage1_final_ckpt)
        chosen_div, chosen_dead, chosen_esc, chosen_cal_metrics = (
            stage1_div,
            stage1_dead,
            stage1_esc,
            stage1_metrics,
        )
        print("--> WINNER: Stage 1. Fine-tuning did NOT improve RLS, so it was rejected.")

    # --------------------------- UNTOUCHED TEST -------------------------------
    test_div_p, test_dead_p, test_esc_p = predict_rls_heads(rls_probe, X, test_idx)
    test_div_by = _split_probs_to_traps(test_div_p, test_idx, meta_list, trap_orders)
    test_dead_by = _split_probs_to_traps(test_dead_p, test_idx, meta_list, trap_orders)
    test_esc_by = _split_probs_to_traps(test_esc_p, test_idx, meta_list, trap_orders)
    test_report, test_metrics = evaluate_split(
        test_div_by,
        test_dead_by,
        test_esc_by,
        human_rls,
        chosen_div,
        chosen_dead,
        chosen_esc,
    )
    test_report.to_csv(TEST_REPORT_OUT, index=False)

    print("\n================ UNTOUCHED TEST REPORT ================")
    print(f"Winner:               {winner}")
    print(f"Test traps:            {test_metrics['n_traps']}")
    print(f"RLS MAE:               {test_metrics['mae']:.2f} divisions")
    print(f"RLS bias:              {test_metrics['bias']:+.2f} divisions")
    print(f"Exact RLS match:       {test_metrics['exact']*100:.1f}%")
    print(f"Within +/-1 division:  {test_metrics['within1']*100:.1f}%")
    print(f"Death-call agreement:  {test_metrics['death_agreement']*100:.1f}%")
    print(f"Escape-call agreement: {test_metrics['escape_agreement']*100:.1f}%")
    print(
        f"Decoder: division threshold={chosen_div['threshold']:.2f}, "
        f"min_gap={chosen_div['min_gap']} | death threshold={chosen_dead['threshold']:.2f}, "
        f"persistence={chosen_dead['persistence']} | escape threshold={chosen_esc['threshold']:.2f}, "
        f"persistence={chosen_esc['persistence']}"
    )

    split_info = {
        "random_seed": RANDOM_SEED,
        "n_train_traps": len(train_keys),
        "n_calibration_traps": len(cal_keys),
        "n_test_traps": len(test_keys),
        "winner": winner,
        "calibration_metrics": chosen_cal_metrics,
    }
    deployment_ok = (
        test_metrics["mae"] <= MAX_DEPLOY_TEST_MAE
        and test_metrics["within1"] >= MIN_DEPLOY_WITHIN1
        and test_metrics["death_agreement"] >= MIN_DEPLOY_DEATH_AGREEMENT
        and test_metrics["escape_agreement"] >= MIN_DEPLOY_ESCAPE_AGREEMENT
    )
    print(
        f"\nDEPLOYMENT GATE: {'PASS' if deployment_ok else 'FAIL'} | "
        f"requires MAE<={MAX_DEPLOY_TEST_MAE:.2f}, "
        f"within1>={MIN_DEPLOY_WITHIN1*100:.0f}%, "
        f"death>={MIN_DEPLOY_DEATH_AGREEMENT*100:.0f}%, "
        f"escape>={MIN_DEPLOY_ESCAPE_AGREEMENT*100:.0f}%"
    )

    export_inference_models(
        model,
        class_names,
        chosen_div,
        chosen_dead,
        chosen_esc,
        test_metrics,
        split_info,
        deployment_ok,
    )

    print(f"--> Test concordance table: {TEST_REPORT_OUT}")
    if deployment_ok:
        print("\nDONE: held-out endpoint gate PASSED. Production RLS artifacts were written.")
    else:
        print(
            "\nCANDIDATE REJECTED: held-out endpoint gate failed. Existing production artifacts "
            "were NOT overwritten; inspect candidate_* files and rls_test_concordance.csv."
        )
        sys.exit(2)