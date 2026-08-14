"""
train_classifier.py -- long-context, event/phase, renewal-decoded RLS trainer.

WHY THIS EXISTS
---------------
Previous versions exposed three concrete failure modes:
  1) six-way frame classification was not accurate enough to preserve every cell cycle;
  2) HMM/Viterbi smoothing deleted short biologically real states and catastrophically
     under-counted RLS;
  3) local peak thresholding of a 3-frame direct-event detector plateaued around
     ~2.4 divisions MAE, while post-hoc sequence refiners did not improve it.

This trainer attacks the remaining bottleneck at the image level:
  * LONG RAW-IMAGE CONTEXT: each prediction sees 21 consecutive trap frames. In the
    current annotation database the median inter-division interval is ~7 frames and
    ~95% of intervals are <=19 frames, so one clip usually contains an entire cycle.
  * MICROSCOPY-NATIVE ENCODER: no ImageNet dependency. A shared CNN encodes every
    frame, then a bidirectional GRU + temporal convolution interprets the whole clip.
  * MULTI-TASK BIOLOGY: state, circular cell-cycle phase, completed-division event,
    and dead-cell heads are trained jointly.
  * EVENT-CENTRIC SAMPLING: every true division and its neighborhood is retained,
    while redundant negatives are thinned and class-balanced.
  * RENEWAL DECODER: final divisions are selected by dynamic programming using both
    network event evidence and a learned inter-division-interval prior. This encodes
    the biological fact that divisions form a renewal process without forcing long
    state dwell times as the failed HMM did.
  * HONEST 3-FOLD OOF GATE: every production metric is out-of-fold at the TRAP level.
    Decoder parameters are calibrated only on training-side calibration traps.
    Nothing is promoted to production unless pooled OOF RLS clears the hard gate.
  * FINAL FIT: only after OOF success, one final model is trained on all eligible traps
    for the median cross-validated best epoch count and exported for deployment.

This script cannot guarantee perfection on future unseen biology. It is designed so
that it cannot *claim* success unless it demonstrates it out-of-fold.

Environment variables:
  AGING_ANNOTATION_PATH   default annotation/master_human_annotations.xlsx
  AGING_TRAPS_DIR         directory containing Pos*_trap_*.tif
  AGING_BATCH_SIZE        default 20
  AGING_N_FOLDS           default 3
  AGING_MAX_EPOCHS        default 36

Outputs on OOF PASS:
  aging_chip_classifier.keras          final long-context model
  class_labels.json
  rls_decoder_meta.json                renewal/death decoder + input format
  rls_oof_concordance.csv              honest per-trap OOF report

Outputs on OOF FAIL:
  candidate_fold_*.keras                fold models retained for diagnosis
  candidate_rls_decoder_meta.json
  rls_oof_concordance.csv

The UI/inference pipeline must build the same 21-frame clip before using this model.
"""

import os
import re
import sys
import json
import math
import time
import random
import hashlib
from collections import defaultdict, Counter

import cv2
import numpy as np
import pandas as pd
import tifffile as tif
import tensorflow as tf
from tensorflow.keras import layers, models

# =============================================================================
# CONFIG
# =============================================================================
ANNOTATION_PATH = os.environ.get(
    "AGING_ANNOTATION_PATH", os.path.join("annotation", "master_human_annotations.xlsx")
)
TRAPS_DIR = os.environ.get(
    "AGING_TRAPS_DIR", r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps"
)

RANDOM_SEED = 42
N_FOLDS = int(os.environ.get("AGING_N_FOLDS", 3))
MAX_EPOCHS = int(os.environ.get("AGING_MAX_EPOCHS", 36))
BATCH_SIZE = int(os.environ.get("AGING_BATCH_SIZE", 20))
ENDPOINT_PATIENCE = 5
ENDPOINT_EVERY = 2
MIN_EPOCHS = 8

IMG_SIZE = 96
CLIP_RADIUS = 10
CLIP_LEN = 2 * CLIP_RADIUS + 1
DISPLAY_SPACE_SIZE = 460.0
HEATMAP_SIGMA = 8.0
GAP_SHIFT_RAW_PX = 25.0

# Endpoint eligibility. Very short partial annotation fragments are useful neither
# as lifespans nor as stable sequence supervision.
MIN_ENDPOINT_FRAMES = 40

# Training sample construction.
EVENT_NEIGHBOR_RADIUS = 3
TRANSITION_NEIGHBOR_RADIUS = 3
MAX_RANDOM_PER_CLASS_PER_TRAP = 70
MAX_BACKGROUND_PER_TRAP = 100

# Loss weights.
LOSS_W_STATE = 0.55
LOSS_W_PHASE = 0.25
LOSS_W_EVENT = 2.80
LOSS_W_DEAD = 0.55
EVENT_FOCAL_ALPHA = 0.70
EVENT_FOCAL_GAMMA = 2.0

# Hard deployment gate. This is intentionally strict.
MAX_DEPLOY_OOF_MAE = 1.00
MIN_DEPLOY_OOF_WITHIN1 = 0.85
MIN_DEPLOY_OOF_DEATH = 0.90

# Renewal decoder calibration grids.
CANDIDATE_THRESHOLDS = (0.03, 0.06, 0.10, 0.16, 0.24)
EVENT_PENALTIES = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)
PHASE_WEIGHTS = (0.0, 0.35, 0.70, 1.05)
GAP_WEIGHTS = (0.0, 0.35, 0.70, 1.05, 1.40)
DEATH_THRESHOLDS = (0.50, 0.60, 0.70, 0.80, 0.90)
DEATH_PERSISTENCES = (2, 3, 5, 7, 9)

EXCLUDE_CLASSES = {
    "Mother Escaped (Ignore Rest)", "Mother Escaped", "Skipped / Bad Trap",
    "2 Cells", "2 Cells (Right)"
}
STATE_CLASSES = [
    "Dead Cell", "Early Bud", "Late Bud", "Mother", "No Cell", "Out of Focus / Blurry"
]
STATE_TO_IDX = {c: i for i, c in enumerate(STATE_CLASSES)}
LIVING_STATES = {"Mother", "Early Bud", "Late Bud"}
GAP_STATES = {"No Cell", "Out of Focus / Blurry"}

MODEL_OUT = "aging_chip_classifier.keras"
CLASS_LABELS_OUT = "class_labels.json"
META_OUT = "rls_decoder_meta.json"
CANDIDATE_META_OUT = "candidate_rls_decoder_meta.json"
OOF_CSV = "rls_oof_concordance.csv"

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# =============================================================================
# CANONICAL HUMAN RLS DEFINITION
# =============================================================================
def find_division_frames(frame_labels):
    """Exact human RLS event rule used throughout this pipeline.

    A completed division is Late Bud -> Mother/Early Bud, optionally after a
    run of No Cell / Blurry observations. None is NOT bridged, matching the
    annotator's current semantics.
    """
    div_frames = []
    for i in range(1, len(frame_labels)):
        curr = frame_labels[i]
        prev = frame_labels[i - 1]
        if curr is None or prev is None:
            continue
        if prev == "Late Bud" and curr in ("Mother", "Early Bud"):
            div_frames.append(i)
        elif curr in ("Mother", "Early Bud"):
            lb = i - 1
            while lb >= 0 and frame_labels[lb] in GAP_STATES:
                lb -= 1
            if 0 <= lb < i - 1 and frame_labels[lb] in ("Early Bud", "Late Bud"):
                div_frames.append(i)
    return div_frames


def calculate_trap_rls(frame_labels):
    divs = find_division_frames(frame_labels)
    died, death_frame = False, None
    for i in range(1, len(frame_labels)):
        if frame_labels[i] != "Dead Cell":
            continue
        lb = i - 1
        while lb >= 0 and frame_labels[lb] in ("Out of Focus / Blurry", None):
            lb -= 1
        if lb >= 0 and frame_labels[lb] in LIVING_STATES:
            died, death_frame = True, i
            break
    return {
        "rls_count": len(divs),
        "division_frames": divs,
        "died_on_chip": died,
        "death_frame": death_frame,
    }

# =============================================================================
# GEOMETRY / INPUT BUILDING
# =============================================================================
def display_to_raw(x, y, raw_w, raw_h):
    try:
        x, y = float(x), float(y)
    except (TypeError, ValueError):
        return np.nan, np.nan
    if np.isnan(x) or np.isnan(y):
        return np.nan, np.nan
    return x * raw_w / DISPLAY_SPACE_SIZE, y * raw_h / DISPLAY_SPACE_SIZE


def resolve_heatmap_anchor(coords, raw_w, raw_h):
    coords = coords or {}
    mx, my = display_to_raw(coords.get("Mother_X", np.nan), coords.get("Mother_Y", np.nan), raw_w, raw_h)
    if not (np.isnan(mx) or np.isnan(my)):
        return mx, my
    p1x, p1y = display_to_raw(coords.get("Pillar_P1_X", np.nan), coords.get("Pillar_P1_Y", np.nan), raw_w, raw_h)
    p2x, p2y = display_to_raw(coords.get("Pillar_P2_X", np.nan), coords.get("Pillar_P2_Y", np.nan), raw_w, raw_h)
    if not any(np.isnan(v) for v in (p1x, p1y, p2x, p2y)):
        return min(raw_w - 1.0, (p1x + p2x) / 2.0 + GAP_SHIFT_RAW_PX), (p1y + p2y) / 2.0
    return raw_w / 2.0, raw_h / 2.0


def gaussian_heatmap(width, height, cx, cy, sigma):
    x = np.arange(width, dtype=np.float32)
    y = np.arange(height, dtype=np.float32)[:, None]
    hm = np.exp(-(((x - cx) ** 2) + ((y - cy) ** 2)) / (2.0 * sigma ** 2))
    return np.clip(hm * 255.0, 0, 255).astype(np.uint8)


def normalize_gray96(img):
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    p0, p1 = np.percentile(img, (0.5, 99.5))
    if p1 > p0:
        img = np.clip((img.astype(np.float32) - p0) * 255.0 / (p1 - p0), 0, 255)
    return cv2.resize(img.astype(np.uint8), (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

# =============================================================================
# DATA AUDIT + TRAP PREPARATION
# =============================================================================
def map_trap_files(traps_dir):
    files = []
    for root, _, names in os.walk(traps_dir):
        for n in names:
            if n.lower().endswith(".tif"):
                files.append(os.path.join(root, n))
    out = {}
    for fp in files:
        pm = re.search(r"(pos\d+)", fp, re.IGNORECASE)
        tm = re.search(r"trap_?(\d+)\.tif$", fp, re.IGNORECASE)
        if pm and tm:
            out[(pm.group(1).lower(), int(tm.group(1)))] = fp
    return out


def phantom_guard(df):
    """Remove the known legacy phantom-Mother signature from model input only."""
    drop_idx = []
    for _, g in df.groupby([
        df["Chip_ID"].astype(str),
        df["Position"].astype(str).str.strip().str.lower(),
        df["Trap_ID"],
    ]):
        g = g.sort_values("Frame")
        labels = g["Class"].tolist()
        idxs = list(g.index)
        # Living labels after observed death are impossible.
        r = calculate_trap_rls(labels)
        removed = set()
        if r["death_frame"] is not None:
            for j in range(r["death_frame"] + 1, len(labels)):
                if labels[j] in LIVING_STATES:
                    removed.add(j)
        # Classic legacy bug: terminal Mother run extending dozens/hundreds of frames.
        survivors = [j for j in range(len(labels)) if j not in removed]
        run = []
        for j in reversed(survivors):
            if labels[j] == "Mother":
                run.append(j)
            else:
                break
        if len(run) >= 40:
            # Keep only the earliest 15 frames of that terminal run.
            for j in sorted(run)[15:]:
                removed.add(j)
        drop_idx.extend(idxs[j] for j in removed)
    if drop_idx:
        print(f"--> Phantom guard dropped {len(drop_idx)} suspect rows (Excel untouched).")
        return df.drop(index=drop_idx).reset_index(drop=True)
    print("--> Phantom guard: no suspect rows found.")
    return df


def load_annotation_df():
    if not os.path.exists(ANNOTATION_PATH):
        raise FileNotFoundError(f"Annotation file not found: {ANNOTATION_PATH}")
    df = pd.read_excel(ANNOTATION_PATH, sheet_name="Frame_Annotations")
    df = df.dropna(subset=["Class"]).copy()
    df["Class"] = df["Class"].astype(str).str.strip()
    df = df[df["Class"].str.lower() != "nan"].reset_index(drop=True)
    df["Position"] = df["Position"].astype(str).str.strip()
    df["Chip_ID"] = df.get("Chip_ID", "chip").astype(str).str.strip()
    df["Trap_ID"] = df["Trap_ID"].astype(int)
    df["Frame"] = df["Frame"].astype(int)
    df = phantom_guard(df)
    return df


def build_trap_records(df, file_map):
    records = {}
    dropped_excluded = 0
    dropped_missing = 0
    for (chip, pos, tid), g in df.groupby(["Chip_ID", "Position", "Trap_ID"]):
        key2 = (str(pos).strip().lower(), int(tid))
        if key2 not in file_map:
            dropped_missing += 1
            continue
        g = g.sort_values("Frame")
        labels_raw = g["Class"].tolist()
        if any(x in EXCLUDE_CLASSES for x in labels_raw):
            dropped_excluded += 1
            continue
        unknown = sorted(set(labels_raw) - set(STATE_CLASSES))
        if unknown:
            print(f"--> Warning: skipping {pos} trap {tid}; unsupported classes {unknown}")
            continue
        with tif.TiffFile(file_map[key2]) as tf_file:
            n_frames = len(tf_file.pages)
        labels = [None] * n_frames
        coords = [None] * n_frames
        annotated = np.zeros(n_frames, dtype=bool)
        for _, row in g.iterrows():
            fr = int(row["Frame"])
            if not (0 <= fr < n_frames):
                continue
            labels[fr] = str(row["Class"])
            coords[fr] = {
                "Pillar_P1_X": row.get("Pillar_P1_X", np.nan), "Pillar_P1_Y": row.get("Pillar_P1_Y", np.nan),
                "Pillar_P2_X": row.get("Pillar_P2_X", np.nan), "Pillar_P2_Y": row.get("Pillar_P2_Y", np.nan),
                "Mother_X": row.get("Mother_X", np.nan), "Mother_Y": row.get("Mother_Y", np.nan),
            }
            annotated[fr] = True
        rls = calculate_trap_rls(labels)
        records[(str(chip), str(pos).strip().lower(), int(tid))] = {
            "chip": str(chip), "pos": str(pos).strip().lower(), "trap": int(tid),
            "path": file_map[key2], "n_frames": n_frames,
            "labels": labels, "coords": coords, "annotated": annotated,
            "rls": rls,
        }
    print(f"--> Trap records: {len(records)} usable | excluded={dropped_excluded} | missing TIFF={dropped_missing}")
    return records


def record_endpoint_eligible(rec):
    return int(rec["annotated"].sum()) >= MIN_ENDPOINT_FRAMES


def summarize_dataset(records):
    rows = []
    gaps = []
    for key, r in records.items():
        if not record_endpoint_eligible(r):
            continue
        divs = r["rls"]["division_frames"]
        gaps.extend(np.diff(divs).tolist() if len(divs) >= 2 else [])
        rows.append({
            "key": key, "position": r["pos"], "frames": int(r["annotated"].sum()),
            "rls": int(r["rls"]["rls_count"]), "died": bool(r["rls"]["died_on_chip"]),
        })
    summary = pd.DataFrame(rows)
    if summary.empty:
        raise RuntimeError("No endpoint-eligible traps after filtering.")
    print(f"--> Endpoint-eligible traps: {len(summary)}")
    print(f"--> RLS median={summary['rls'].median():.1f}, range={summary['rls'].min()}..{summary['rls'].max()}, "
          f"death observed in {summary['died'].mean()*100:.1f}%")
    if gaps:
        q = np.percentile(gaps, [5, 25, 50, 75, 90, 95, 99])
        print("--> Human inter-division gap frames [p5,p25,p50,p75,p90,p95,p99]: " +
              ", ".join(f"{x:.0f}" for x in q))
    return summary, np.asarray(gaps, dtype=int)

# =============================================================================
# PRECOMPUTED IMAGE CACHE
# =============================================================================
def prepare_image_cache(records, keys):
    """Precompute 96x96 grayscale and heatmaps once. Around ~1 GB for 60k frames."""
    cache = {}
    t0 = time.time()
    keys = list(keys)
    for qi, key in enumerate(keys, 1):
        rec = records[key]
        with tif.TiffFile(rec["path"]) as tf_file:
            raw_stack = [p.asarray() for p in tf_file.pages]
        T = len(raw_stack)
        gray = np.empty((T, IMG_SIZE, IMG_SIZE), dtype=np.uint8)
        heat = np.empty((T, IMG_SIZE, IMG_SIZE), dtype=np.uint8)
        for i, img in enumerate(raw_stack):
            gray[i] = normalize_gray96(img)
            h, w = img.shape[:2]
            ax, ay = resolve_heatmap_anchor(rec["coords"][i], w, h)
            ax *= IMG_SIZE / float(w)
            ay *= IMG_SIZE / float(h)
            heat[i] = gaussian_heatmap(IMG_SIZE, IMG_SIZE, ax, ay, HEATMAP_SIGMA)
        cache[key] = {"gray": gray, "heat": heat}
        if qi % 10 == 0 or qi == len(keys):
            print(f"    image cache {qi}/{len(keys)} traps ({time.time()-t0:.1f}s)")
    return cache


def build_clip(cache_entry, center):
    gray = cache_entry["gray"]
    heat = cache_entry["heat"]
    T = len(gray)
    idx = np.clip(np.arange(center - CLIP_RADIUS, center + CLIP_RADIUS + 1), 0, T - 1)
    g = gray[idx]
    h = heat[idx]
    # Absolute frame difference makes daughter release / bud morphology change explicit.
    d = np.zeros_like(g)
    d[1:] = np.abs(g[1:].astype(np.int16) - g[:-1].astype(np.int16)).astype(np.uint8)
    # uint8 [time, y, x, channels]
    return np.stack([g, d, h], axis=-1)

# =============================================================================
# TARGETS + SAMPLING
# =============================================================================
def phase_target(label):
    # Circular encoding: Mother -> Early -> Late -> Mother is a phase loop.
    if label == "Mother":
        a = 0.0
    elif label == "Early Bud":
        a = 2.0 * np.pi / 3.0
    elif label == "Late Bud":
        a = 4.0 * np.pi / 3.0
    else:
        return np.array([0.0, 0.0], dtype=np.float32), 0.0
    return np.array([np.cos(a), np.sin(a)], dtype=np.float32), 1.0


def event_soft_targets(rec):
    T = rec["n_frames"]
    y = np.zeros(T, dtype=np.float32)
    for e in rec["rls"]["division_frames"]:
        if 0 <= e < T:
            y[e] = max(y[e], 1.0)
            for d, val in ((1, 0.60), (2, 0.28)):
                if e - d >= 0:
                    y[e - d] = max(y[e - d], val)
                if e + d < T:
                    y[e + d] = max(y[e + d], val)
    return y


def build_centers(records, keys, training, rng):
    centers = []
    for key in keys:
        rec = records[key]
        labels = rec["labels"]
        ann = rec["annotated"]
        valid = np.where(ann & np.array([x in STATE_TO_IDX if x is not None else False for x in labels]))[0]
        if len(valid) == 0:
            continue
        if not training:
            centers.extend((key, int(i)) for i in valid)
            continue

        keep = set()
        # Every division neighborhood.
        for e in rec["rls"]["division_frames"]:
            for j in range(max(0, e - EVENT_NEIGHBOR_RADIUS), min(rec["n_frames"], e + EVENT_NEIGHBOR_RADIUS + 1)):
                if ann[j] and labels[j] in STATE_TO_IDX:
                    keep.add(j)
        # Every state transition neighborhood = hard morphology boundary.
        for i in range(1, rec["n_frames"]):
            if not (ann[i] and ann[i-1]):
                continue
            if labels[i] != labels[i-1]:
                for j in range(max(0, i - TRANSITION_NEIGHBOR_RADIUS), min(rec["n_frames"], i + TRANSITION_NEIGHBOR_RADIUS + 1)):
                    if ann[j] and labels[j] in STATE_TO_IDX:
                        keep.add(j)
        # Balanced class background.
        by_class = defaultdict(list)
        for i in valid:
            by_class[labels[i]].append(int(i))
        for cls, inds in by_class.items():
            if len(inds) > MAX_RANDOM_PER_CLASS_PER_TRAP:
                inds = rng.choice(inds, MAX_RANDOM_PER_CLASS_PER_TRAP, replace=False).tolist()
            keep.update(inds)
        # Generic background negatives.
        rem = [int(i) for i in valid if i not in keep]
        if len(rem) > MAX_BACKGROUND_PER_TRAP:
            rem = rng.choice(rem, MAX_BACKGROUND_PER_TRAP, replace=False).tolist()
        keep.update(rem)
        centers.extend((key, int(i)) for i in sorted(keep))
    return centers


class ClipSequence(tf.keras.utils.Sequence):
    def __init__(self, records, cache, centers, batch_size, training=False, seed=42):
        super().__init__()
        self.records = records
        self.cache = cache
        self.centers = list(centers)
        self.batch_size = batch_size
        self.training = training
        self.rng = np.random.RandomState(seed)
        self.soft_event = {k: event_soft_targets(records[k]) for k in set(k for k, _ in centers)}
        self.class_weights = self._class_weights()
        self.indices = np.arange(len(self.centers))
        self.on_epoch_end()

    def _class_weights(self):
        counts = Counter()
        for k, fr in self.centers:
            counts[self.records[k]["labels"][fr]] += 1
        if not counts:
            return {c: 1.0 for c in STATE_CLASSES}
        total = sum(counts.values())
        raw = {c: total / (len(STATE_CLASSES) * max(1, counts.get(c, 0))) for c in STATE_CLASSES}
        # cap to keep rare blur/no-cell from dominating.
        return {c: float(np.clip(w, 0.4, 3.0)) for c, w in raw.items()}

    def __len__(self):
        return int(math.ceil(len(self.indices) / self.batch_size))

    def on_epoch_end(self):
        if self.training:
            self.rng.shuffle(self.indices)

    def __getitem__(self, batch_index):
        sl = self.indices[batch_index*self.batch_size:(batch_index+1)*self.batch_size]
        n = len(sl)
        X = np.empty((n, CLIP_LEN, IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
        y_state = np.empty(n, dtype=np.int32)
        y_event = np.empty((n, 1), dtype=np.float32)
        y_dead = np.empty((n, 1), dtype=np.float32)
        y_phase = np.empty((n, 2), dtype=np.float32)
        sw_state = np.empty(n, dtype=np.float32)
        sw_event = np.empty(n, dtype=np.float32)
        sw_dead = np.empty(n, dtype=np.float32)
        sw_phase = np.empty(n, dtype=np.float32)

        for bi, ci in enumerate(sl):
            key, fr = self.centers[int(ci)]
            rec = self.records[key]
            lbl = rec["labels"][fr]
            X[bi] = build_clip(self.cache[key], fr)
            y_state[bi] = STATE_TO_IDX[lbl]
            ev = float(self.soft_event[key][fr])
            y_event[bi, 0] = ev
            y_dead[bi, 0] = 1.0 if lbl == "Dead Cell" else 0.0
            ph, phw = phase_target(lbl)
            y_phase[bi] = ph
            sw_state[bi] = self.class_weights.get(lbl, 1.0)
            # exact/near events dominate sparse-event learning.
            if ev >= 0.99:
                sw_event[bi] = 10.0
            elif ev >= 0.5:
                sw_event[bi] = 5.0
            elif ev > 0:
                sw_event[bi] = 2.5
            else:
                sw_event[bi] = 1.0
            sw_dead[bi] = 2.5 if lbl == "Dead Cell" else 1.0
            sw_phase[bi] = phw

        y = {"state": y_state, "division": y_event, "dead": y_dead, "phase": y_phase}
        sw = {"state": sw_state, "division": sw_event, "dead": sw_dead, "phase": sw_phase}
        return X, y, sw

# =============================================================================
# MODEL
# =============================================================================
@tf.keras.utils.register_keras_serializable(package="AgingChipV6")
def focal_event_loss(y_true, logits):
    y_true = tf.cast(y_true, tf.float32)
    logits = tf.cast(logits, tf.float32)
    p = tf.nn.sigmoid(logits)
    ce = tf.nn.sigmoid_cross_entropy_with_logits(labels=y_true, logits=logits)
    pt = y_true * p + (1.0 - y_true) * (1.0 - p)
    alpha = y_true * EVENT_FOCAL_ALPHA + (1.0 - y_true) * (1.0 - EVENT_FOCAL_ALPHA)
    # Return one loss value per example so Keras sample weights work correctly.
    return tf.reduce_mean(alpha * tf.pow(1.0 - pt, EVENT_FOCAL_GAMMA) * ce, axis=-1)


@tf.keras.utils.register_keras_serializable(package="AgingChipV6")
def phase_cosine_loss(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.math.l2_normalize(tf.cast(y_pred, tf.float32), axis=-1)
    y_true_n = tf.math.l2_normalize(y_true + 1e-7, axis=-1)
    # Per-example loss; living-state mask is supplied through sample_weight.
    return 1.0 - tf.reduce_sum(y_true_n * y_pred, axis=-1)


def build_model():
    inp = layers.Input((CLIP_LEN, IMG_SIZE, IMG_SIZE, 3), dtype="uint8", name="long_context_clip")
    x = layers.Rescaling(1.0/255.0)(inp)

    frame_encoder = models.Sequential([
        layers.Input((IMG_SIZE, IMG_SIZE, 3)),
        layers.Conv2D(24, 5, strides=2, padding="same", use_bias=False),
        layers.BatchNormalization(), layers.Activation("swish"),
        layers.SeparableConv2D(48, 3, strides=2, padding="same", use_bias=False),
        layers.BatchNormalization(), layers.Activation("swish"),
        layers.SeparableConv2D(80, 3, strides=2, padding="same", use_bias=False),
        layers.BatchNormalization(), layers.Activation("swish"),
        layers.SeparableConv2D(128, 3, strides=2, padding="same", use_bias=False),
        layers.BatchNormalization(), layers.Activation("swish"),
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="swish"),
    ], name="microscopy_frame_encoder")

    seq = layers.TimeDistributed(frame_encoder, name="shared_frame_encoder")(x)
    seq = layers.Bidirectional(layers.GRU(96, return_sequences=True, dropout=0.10), name="bigru1")(seq)
    r = layers.Conv1D(192, 3, padding="same", activation="swish", name="temporal_conv1")(seq)
    r = layers.Dropout(0.15)(r)
    r = layers.Conv1D(192, 3, padding="same", dilation_rate=2, activation="swish", name="temporal_conv2")(r)
    seq = layers.Add(name="temporal_residual")([seq, r])
    seq = layers.Bidirectional(layers.GRU(64, return_sequences=True, dropout=0.10), name="bigru2")(seq)

    center = layers.Lambda(lambda z: z[:, CLIP_RADIUS, :], name="center_context")(seq)
    avg = layers.GlobalAveragePooling1D(name="clip_average")(seq)
    feat = layers.Concatenate(name="context_fusion")([center, avg])
    feat = layers.Dense(224, activation="swish", name="fusion_dense")(feat)
    feat = layers.Dropout(0.30)(feat)

    state = layers.Dense(len(STATE_CLASSES), dtype="float32", name="state")(feat)
    division = layers.Dense(1, dtype="float32", name="division")(feat)
    dead = layers.Dense(1, dtype="float32", name="dead")(feat)
    phase = layers.Dense(2, dtype="float32", name="phase")(feat)

    return models.Model(inp, {"state": state, "division": division, "dead": dead, "phase": phase},
                        name="aging_chip_long_context_counter")


def compile_model(model, lr=3e-4):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr, clipnorm=2.0),
        loss={
            "state": tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            "division": focal_event_loss,
            "dead": tf.keras.losses.BinaryCrossentropy(from_logits=True),
            "phase": phase_cosine_loss,
        },
        loss_weights={"state": LOSS_W_STATE, "division": LOSS_W_EVENT,
                      "dead": LOSS_W_DEAD, "phase": LOSS_W_PHASE},
        metrics={
            "state": ["accuracy"],
            "division": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
            "dead": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
        },
    )

# =============================================================================
# INFERENCE + EVENT MATCHING
# =============================================================================
def predict_traps(model, records, cache, keys):
    centers = build_centers(records, keys, training=False, rng=np.random.RandomState(0))
    seq = ClipSequence(records, cache, centers, BATCH_SIZE, training=False)
    out = model.predict(seq, verbose=0)
    # Keras dict output ordering remains names; normalize explicitly.
    if not isinstance(out, dict):
        names = model.output_names
        out = {n: arr for n, arr in zip(names, out)}
    state_prob = tf.nn.softmax(out["state"], axis=-1).numpy()
    div_prob = tf.nn.sigmoid(out["division"]).numpy().ravel()
    dead_prob = tf.nn.sigmoid(out["dead"]).numpy().ravel()
    phase_raw = out["phase"]
    result = {}
    cursor = 0
    by_key = defaultdict(list)
    for key, fr in centers:
        by_key[key].append((fr, cursor))
        cursor += 1
    for key in keys:
        items = sorted(by_key.get(key, []))
        T = records[key]["n_frames"]
        sp = np.zeros((T, len(STATE_CLASSES)), np.float32)
        dp = np.zeros(T, np.float32)
        deadp = np.zeros(T, np.float32)
        ph = np.zeros((T, 2), np.float32)
        mask = np.zeros(T, bool)
        for fr, ix in items:
            sp[fr] = state_prob[ix]
            dp[fr] = div_prob[ix]
            deadp[fr] = dead_prob[ix]
            ph[fr] = phase_raw[ix]
            mask[fr] = True
        result[key] = {"state": sp, "division": dp, "dead": deadp, "phase": ph, "mask": mask}
    return result


def local_maxima(p, threshold):
    cand = []
    for i, v in enumerate(p):
        if v < threshold:
            continue
        l = p[i-1] if i > 0 else -1.0
        r = p[i+1] if i+1 < len(p) else -1.0
        if v >= l and v >= r:
            cand.append(i)
    return cand


def logit(p):
    p = np.clip(p, 1e-5, 1-1e-5)
    return np.log(p) - np.log1p(-p)


def phase_wrap_probability(state_prob, t, lookback=3):
    late_i = STATE_TO_IDX["Late Bud"]
    m_i = STATE_TO_IDX["Mother"]
    e_i = STATE_TO_IDX["Early Bud"]
    if t <= 0:
        return 1e-4
    lo = max(0, t-lookback)
    before = float(np.max(state_prob[lo:t, late_i])) if t > lo else 0.0
    after = float(state_prob[t, m_i] + state_prob[t, e_i])
    return float(np.clip(math.sqrt(max(0.0, before*after)), 1e-4, 1-1e-4))


def learn_gap_prior(records, keys):
    gaps = []
    for key in keys:
        d = records[key]["rls"]["division_frames"]
        if len(d) >= 2:
            gaps.extend(np.diff(d).tolist())
    if not gaps:
        # conservative fallback
        min_gap, max_gap = 2, 60
        return min_gap, max_gap, np.zeros(max_gap+1, dtype=np.float64)
    qlo, qhi = np.percentile(gaps, [0.5, 99.5])
    min_gap = max(2, int(math.floor(qlo)))
    max_gap = max(min_gap+3, int(math.ceil(qhi)))
    max_gap = min(max_gap, 100)
    hist = np.ones(max_gap+1, dtype=np.float64)  # Laplace
    for g in gaps:
        if min_gap <= g <= max_gap:
            hist[int(g)] += 1.0
    p = hist / hist.sum()
    uniform = 1.0 / (max_gap-min_gap+1)
    lr = np.zeros_like(p)
    for g in range(min_gap, max_gap+1):
        lr[g] = np.log(max(p[g], 1e-12) / uniform)
    # small smoothing in gap space.
    sm = lr.copy()
    for g in range(min_gap, max_gap+1):
        a, b = max(min_gap, g-1), min(max_gap, g+1)
        sm[g] = lr[a:b+1].mean()
    return min_gap, max_gap, sm


def decode_renewal(pred, gap_prior, cfg):
    p = pred["division"]
    state = pred["state"]
    min_gap, max_gap, gap_lr = gap_prior
    candidates = local_maxima(p, cfg["candidate_threshold"])
    if not candidates:
        return []
    unary = {}
    for t in candidates:
        s = float(logit(p[t])) - cfg["event_penalty"]
        if cfg["phase_weight"] > 0:
            s += cfg["phase_weight"] * float(logit(phase_wrap_probability(state, t)))
        unary[t] = s

    dp = np.full(len(candidates), -np.inf, dtype=np.float64)
    prev = np.full(len(candidates), -1, dtype=np.int32)
    for j, tj in enumerate(candidates):
        best_prev_score = 0.0
        best_i = -1
        for i in range(j):
            gap = tj - candidates[i]
            if gap < min_gap or gap > max_gap:
                continue
            link = dp[i] + cfg["gap_weight"] * gap_lr[gap]
            if link > best_prev_score:
                best_prev_score = link
                best_i = i
        dp[j] = unary[tj] + best_prev_score
        prev[j] = best_i

    j = int(np.argmax(dp))
    if dp[j] <= 0:
        return []
    chosen = []
    while j >= 0:
        chosen.append(candidates[j])
        j = int(prev[j])
    return sorted(chosen)


def sustained_death(p, threshold, persistence):
    run = 0
    for i, v in enumerate(p):
        if v >= threshold:
            run += 1
            if run >= persistence:
                return True, i-persistence+1
        else:
            run = 0
    return False, None


def match_events(true_events, pred_events, tolerance=2):
    true_events = list(true_events)
    pred_events = list(pred_events)
    used = set()
    tp = 0
    for t in true_events:
        candidates = [(abs(t-p), j) for j,p in enumerate(pred_events) if j not in used and abs(t-p) <= tolerance]
        if candidates:
            _, j = min(candidates)
            used.add(j)
            tp += 1
    fp = len(pred_events)-tp
    fn = len(true_events)-tp
    return tp, fp, fn


def calibration_rank(metrics):
    return (metrics["mae"], -metrics["within1"], -metrics["exact"], abs(metrics["bias"]))


def evaluate_with_cfg(preds, records, keys, gap_prior, div_cfg, death_cfg):
    rows = []
    tp = fp = fn = 0
    for key in keys:
        true = records[key]["rls"]
        ev = decode_renewal(preds[key], gap_prior, div_cfg)
        pred_dead, death_fr = sustained_death(preds[key]["dead"], death_cfg["threshold"], death_cfg["persistence"])
        tpi, fpi, fni = match_events(true["division_frames"], ev, tolerance=2)
        tp += tpi; fp += fpi; fn += fni
        rows.append({
            "chip": key[0], "position": key[1], "trap_id": key[2],
            "true_rls": int(true["rls_count"]), "pred_rls": int(len(ev)),
            "signed_error": int(len(ev)-true["rls_count"]),
            "abs_error": int(abs(len(ev)-true["rls_count"])),
            "true_died": bool(true["died_on_chip"]), "pred_died": bool(pred_dead),
            "pred_death_frame": death_fr,
            "true_event_frames": ",".join(map(str, true["division_frames"])),
            "pred_event_frames": ",".join(map(str, ev)),
        })
    df = pd.DataFrame(rows)
    precision = tp/max(1,tp+fp)
    recall = tp/max(1,tp+fn)
    f1 = 2*precision*recall/max(1e-12,precision+recall)
    metrics = {
        "mae": float(df["abs_error"].mean()),
        "bias": float(df["signed_error"].mean()),
        "exact": float((df["abs_error"]==0).mean()),
        "within1": float((df["abs_error"]<=1).mean()),
        "death_agreement": float((df["true_died"]==df["pred_died"]).mean()),
        "event_precision_t2": float(precision), "event_recall_t2": float(recall), "event_f1_t2": float(f1),
        "n_traps": int(len(df)),
    }
    return df, metrics


def calibrate_decoder(preds, records, cal_keys, gap_prior):
    best = None
    # Calibrate death independently.
    best_death = None
    for thr in DEATH_THRESHOLDS:
        for pers in DEATH_PERSISTENCES:
            correct = 0
            for key in cal_keys:
                pdied, _ = sustained_death(preds[key]["dead"], thr, pers)
                correct += int(pdied == records[key]["rls"]["died_on_chip"])
            acc = correct/max(1,len(cal_keys))
            rank = (-acc, pers, -thr)
            if best_death is None or rank < best_death[0]:
                best_death = (rank, {"threshold": float(thr), "persistence": int(pers)})
    death_cfg = best_death[1]

    for ct in CANDIDATE_THRESHOLDS:
        for pen in EVENT_PENALTIES:
            for pw in PHASE_WEIGHTS:
                for gw in GAP_WEIGHTS:
                    cfg = {"candidate_threshold": float(ct), "event_penalty": float(pen),
                           "phase_weight": float(pw), "gap_weight": float(gw)}
                    _, m = evaluate_with_cfg(preds, records, cal_keys, gap_prior, cfg, death_cfg)
                    rank = calibration_rank(m)
                    if best is None or rank < best[0]:
                        best = (rank, cfg, m)
    return best[1], death_cfg, best[2]

# =============================================================================
# TRAP-LEVEL SPLITS
# =============================================================================
def make_balanced_folds(summary, n_folds, seed=42):
    """Greedy trap-level fold assignment balancing position, death and RLS bins."""
    rng = np.random.RandomState(seed)
    s = summary.copy()
    # Quantile bins collapse duplicates safely.
    try:
        s["rls_bin"] = pd.qcut(s["rls"], q=min(4, s["rls"].nunique()), duplicates="drop").astype(str)
    except Exception:
        s["rls_bin"] = "all"
    s["stratum"] = s["position"].astype(str) + "|" + s["died"].astype(int).astype(str) + "|" + s["rls_bin"].astype(str)
    fold_keys = [[] for _ in range(n_folds)]
    fold_n = np.zeros(n_folds, int)
    strata = defaultdict(list)
    for _, row in s.iterrows():
        strata[row["stratum"]].append(row["key"])
    for st, keys in sorted(strata.items(), key=lambda kv: -len(kv[1])):
        rng.shuffle(keys)
        for key in keys:
            f = int(np.argmin(fold_n))
            fold_keys[f].append(key)
            fold_n[f] += 1
    return fold_keys


def split_train_cal(train_pool, records, cal_fraction=0.20, seed=42):
    rng = np.random.RandomState(seed)
    # Sort by position/RLS then take a randomized approximately-stratified slice.
    buckets = defaultdict(list)
    for key in train_pool:
        r = records[key]
        rb = min(4, int(r["rls"]["rls_count"] // 10))
        buckets[(r["pos"], bool(r["rls"]["died_on_chip"]), rb)].append(key)
    cal = []
    train = []
    for _, keys in buckets.items():
        keys = list(keys); rng.shuffle(keys)
        ncal = max(1, int(round(len(keys)*cal_fraction))) if len(keys) >= 4 else (1 if len(keys)>=3 else 0)
        cal.extend(keys[:ncal]); train.extend(keys[ncal:])
    # Ensure reasonable sizes.
    if len(cal) < max(5, int(len(train_pool)*0.12)):
        remaining = [k for k in train if k not in cal]
        rng.shuffle(remaining)
        need = max(5, int(len(train_pool)*0.15)) - len(cal)
        move = remaining[:max(0,need)]
        cal.extend(move); train = [k for k in train if k not in set(move)]
    return train, cal

# =============================================================================
# ENDPOINT CALLBACK
# =============================================================================
class EndpointCallback(tf.keras.callbacks.Callback):
    def __init__(self, records, cache, cal_keys, gap_prior, checkpoint, stage="fold"):
        super().__init__()
        self.records = records; self.cache = cache; self.cal_keys = list(cal_keys)
        self.gap_prior = gap_prior; self.checkpoint = checkpoint; self.stage = stage
        self.best_rank = None; self.best_epoch = 0; self.best_div = None; self.best_death = None; self.best_metrics = None
        self.bad_checks = 0

    def on_epoch_end(self, epoch, logs=None):
        ep = epoch + 1
        if ep < MIN_EPOCHS or ep % ENDPOINT_EVERY != 0:
            return
        preds = predict_traps(self.model, self.records, self.cache, self.cal_keys)
        div_cfg, death_cfg, m = calibrate_decoder(preds, self.records, self.cal_keys, self.gap_prior)
        print(f"\n[{self.stage} endpoint] epoch {ep}: MAE={m['mae']:.2f} bias={m['bias']:+.2f} "
              f"exact={m['exact']*100:.1f}% within1={m['within1']*100:.1f}% "
              f"eventF1±2={m['event_f1_t2']:.3f} death={m['death_agreement']*100:.1f}% "
              f"| ct={div_cfg['candidate_threshold']:.2f} pen={div_cfg['event_penalty']:.2f} "
              f"phase={div_cfg['phase_weight']:.2f} gapW={div_cfg['gap_weight']:.2f}")
        rank = calibration_rank(m)
        if self.best_rank is None or rank < self.best_rank:
            self.best_rank = rank; self.best_epoch = ep; self.best_div = div_cfg; self.best_death = death_cfg; self.best_metrics = m
            self.model.save_weights(self.checkpoint)
            self.bad_checks = 0
            print(f"[{self.stage} endpoint] NEW BEST -> {self.checkpoint}")
        else:
            self.bad_checks += 1
            if self.bad_checks >= ENDPOINT_PATIENCE:
                print(f"[{self.stage} endpoint] no endpoint improvement for {self.bad_checks} checks; stopping.")
                self.model.stop_training = True

# =============================================================================
# TRAINING HELPERS
# =============================================================================
def train_one_fold(fold_id, records, cache, train_keys, cal_keys, test_keys):
    print("\n" + "="*80)
    print(f"FOLD {fold_id}: train={len(train_keys)} cal={len(cal_keys)} test={len(test_keys)}")
    print("="*80)
    rng = np.random.RandomState(RANDOM_SEED + fold_id)
    tr_centers = build_centers(records, train_keys, training=True, rng=rng)
    ca_centers = build_centers(records, cal_keys, training=False, rng=rng)
    print(f"--> centers: train={len(tr_centers)} cal_frames={len(ca_centers)}")
    train_seq = ClipSequence(records, cache, tr_centers, BATCH_SIZE, training=True, seed=RANDOM_SEED+fold_id)
    cal_seq = ClipSequence(records, cache, ca_centers, BATCH_SIZE, training=False, seed=RANDOM_SEED+fold_id)

    model = build_model()
    compile_model(model, 3e-4)
    gap_prior = learn_gap_prior(records, train_keys)
    checkpoint = f"fold{fold_id}_best.weights.h5"
    endpoint = EndpointCallback(records, cache, cal_keys, gap_prior, checkpoint, stage=f"FOLD{fold_id}")
    callbacks = [
        endpoint,
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1),
    ]
    model.fit(train_seq, validation_data=cal_seq, epochs=MAX_EPOCHS, callbacks=callbacks, verbose=1)

    if endpoint.best_rank is None:
        # If MAX_EPOCHS was set below MIN_EPOCHS, calibrate once.
        preds = predict_traps(model, records, cache, cal_keys)
        div_cfg, death_cfg, m = calibrate_decoder(preds, records, cal_keys, gap_prior)
        model.save_weights(checkpoint)
        endpoint.best_epoch = MAX_EPOCHS; endpoint.best_div = div_cfg; endpoint.best_death = death_cfg; endpoint.best_metrics = m
    else:
        model.load_weights(checkpoint)

    # IMPORTANT: decoder was calibrated on cal traps only; test is touched once here.
    test_preds = predict_traps(model, records, cache, test_keys)
    test_df, test_m = evaluate_with_cfg(test_preds, records, test_keys, gap_prior, endpoint.best_div, endpoint.best_death)
    test_df["fold"] = fold_id
    model_path = f"candidate_fold_{fold_id}.keras"
    model.save(model_path)
    print(f"\n[FOLD {fold_id} TEST] MAE={test_m['mae']:.2f} bias={test_m['bias']:+.2f} "
          f"exact={test_m['exact']*100:.1f}% within1={test_m['within1']*100:.1f}% "
          f"eventF1±2={test_m['event_f1_t2']:.3f} death={test_m['death_agreement']*100:.1f}%")
    return {
        "model_path": model_path, "best_epoch": int(endpoint.best_epoch),
        "div_cfg": endpoint.best_div, "death_cfg": endpoint.best_death,
        "gap_min": int(gap_prior[0]), "gap_max": int(gap_prior[1]),
        "test_df": test_df, "test_metrics": test_m,
    }


def aggregate_metrics(df):
    tp=fp=fn=0
    # Event F1 is not reconstructable from CSV string cheaply? Do it here.
    for _, row in df.iterrows():
        t = [int(x) for x in str(row["true_event_frames"]).split(",") if str(x).strip() and str(x) != "nan"]
        p = [int(x) for x in str(row["pred_event_frames"]).split(",") if str(x).strip() and str(x) != "nan"]
        a,b,c = match_events(t,p,2); tp+=a; fp+=b; fn+=c
    prec=tp/max(1,tp+fp); rec=tp/max(1,tp+fn); f1=2*prec*rec/max(1e-12,prec+rec)
    return {
        "mae": float(df["abs_error"].mean()),
        "bias": float(df["signed_error"].mean()),
        "exact": float((df["abs_error"]==0).mean()),
        "within1": float((df["abs_error"]<=1).mean()),
        "death_agreement": float((df["true_died"]==df["pred_died"]).mean()),
        "event_precision_t2": float(prec), "event_recall_t2": float(rec), "event_f1_t2": float(f1),
        "n_traps": int(len(df)),
    }


def median_cfg(fold_results, name):
    cfgs = [r[name] for r in fold_results]
    out = {}
    for k in cfgs[0]:
        vals = [c[k] for c in cfgs]
        out[k] = int(round(float(np.median(vals)))) if isinstance(vals[0], (int, np.integer)) else float(np.median(vals))
    return out

# =============================================================================
# FINAL FIT AFTER OOF SUCCESS
# =============================================================================
def fit_final_model(records, cache, all_keys, epochs):
    print("\n" + "="*80)
    print(f"FINAL FIT on all {len(all_keys)} endpoint traps for {epochs} epochs")
    print("="*80)
    rng = np.random.RandomState(RANDOM_SEED+999)
    centers = build_centers(records, all_keys, training=True, rng=rng)
    seq = ClipSequence(records, cache, centers, BATCH_SIZE, training=True, seed=RANDOM_SEED+999)
    model = build_model(); compile_model(model, 3e-4)
    # Fixed epoch count came from cross-validation; no training-set endpoint calibration.
    model.fit(seq, epochs=max(1,int(epochs)), verbose=1,
              callbacks=[tf.keras.callbacks.ReduceLROnPlateau(monitor="loss", factor=0.5, patience=3, min_lr=1e-6)])
    return model

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    source_sha256 = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    print("="*80)
    print("AGING CHIP RLS TRAINER v6 -- LONG-CONTEXT + RENEWAL DECODING")
    print(f"SOURCE FILE: {os.path.abspath(__file__)}")
    print(f"SOURCE SHA256: {source_sha256}")
    print("="*80)
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for g in gpus:
            try: tf.config.experimental.set_memory_growth(g, True)
            except Exception: pass
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
        print(f"--> GPU detected ({len(gpus)}); mixed_float16 enabled")
    else:
        print("--> WARNING: no GPU detected")

    if not os.path.isdir(TRAPS_DIR):
        sys.exit(f"FATAL: TRAPS_DIR does not exist: {TRAPS_DIR}\nSet AGING_TRAPS_DIR on Euler.")

    df = load_annotation_df()
    print(f"--> Labeled annotation rows after guard: {len(df)}")
    file_map = map_trap_files(TRAPS_DIR)
    print(f"--> TIFF stacks found: {len(file_map)}")
    records = build_trap_records(df, file_map)
    summary, human_gaps = summarize_dataset(records)
    endpoint_keys = summary["key"].tolist()
    if len(endpoint_keys) < max(18, N_FOLDS*5):
        sys.exit(f"FATAL: only {len(endpoint_keys)} endpoint traps; insufficient for {N_FOLDS}-fold training.")

    # One shared image cache; fold models never duplicate raw pixel memory.
    cache = prepare_image_cache(records, endpoint_keys)

    folds = make_balanced_folds(summary, N_FOLDS, RANDOM_SEED)
    print("--> Fold sizes: " + ", ".join(map(str, map(len, folds))))
    fold_results = []
    for fi in range(N_FOLDS):
        test_keys = folds[fi]
        train_pool = [k for fj,f in enumerate(folds) if fj != fi for k in f]
        train_keys, cal_keys = split_train_cal(train_pool, records, 0.20, RANDOM_SEED+fi)
        fold_results.append(train_one_fold(fi+1, records, cache, train_keys, cal_keys, test_keys))
        tf.keras.backend.clear_session()

    oof = pd.concat([r["test_df"] for r in fold_results], ignore_index=True)
    oof = oof.sort_values(["position","trap_id"]).reset_index(drop=True)
    oof.to_csv(OOF_CSV, index=False)
    m = aggregate_metrics(oof)

    print("\n" + "="*80)
    print("POOLED OUT-OF-FOLD REPORT -- EVERY TRAP WAS UNSEEN BY ITS MODEL")
    print("="*80)
    print(f"OOF traps:              {m['n_traps']}")
    print(f"RLS MAE:                {m['mae']:.2f} divisions")
    print(f"RLS bias:               {m['bias']:+.2f} divisions")
    print(f"Exact RLS match:        {m['exact']*100:.1f}%")
    print(f"Within +/-1 division:   {m['within1']*100:.1f}%")
    print(f"Event F1 (±2 frames):   {m['event_f1_t2']:.3f}")
    print(f"Death-call agreement:   {m['death_agreement']*100:.1f}%")
    print(f"Report:                  {OOF_CSV}")

    deploy_ok = (
        m["mae"] <= MAX_DEPLOY_OOF_MAE and
        m["within1"] >= MIN_DEPLOY_OOF_WITHIN1 and
        m["death_agreement"] >= MIN_DEPLOY_OOF_DEATH
    )

    avg_div_cfg = median_cfg(fold_results, "div_cfg")
    avg_death_cfg = median_cfg(fold_results, "death_cfg")
    best_epochs = [r["best_epoch"] for r in fold_results]
    final_epochs = max(1, int(round(float(np.median(best_epochs)))))

    meta = {
        "version": "long_context_renewal_v6",
        "model_input": {
            "clip_len": CLIP_LEN, "clip_radius": CLIP_RADIUS, "img_size": IMG_SIZE,
            "channels": ["normalized_gray", "abs_prev_difference", "anchor_heatmap"],
        },
        "state_classes": STATE_CLASSES,
        "rls_event_definition": "Late Bud -> Mother/Early Bud, bridging No Cell/Blurry",
        "decoder": {
            "type": "renewal_dynamic_programming",
            "division_config_median_from_folds": avg_div_cfg,
            "death_config_median_from_folds": avg_death_cfg,
            "gap_prior": "learn from deployment training annotations at startup/export",
        },
        "oof_metrics": m,
        "fold_best_epochs": best_epochs,
        "recommended_final_epochs": final_epochs,
        "deployment_gate": {
            "max_oof_mae": MAX_DEPLOY_OOF_MAE,
            "min_oof_within1": MIN_DEPLOY_OOF_WITHIN1,
            "min_oof_death": MIN_DEPLOY_OOF_DEATH,
            "passed": bool(deploy_ok),
        },
    }

    if not deploy_ok:
        with open(CANDIDATE_META_OUT, "w") as f:
            json.dump(meta, f, indent=2)
        print("\nDEPLOYMENT GATE: FAIL")
        print(f"Requires MAE<={MAX_DEPLOY_OOF_MAE:.2f}, within1>={MIN_DEPLOY_OOF_WITHIN1*100:.0f}%, "
              f"death>={MIN_DEPLOY_OOF_DEATH*100:.0f}%")
        print("No production model was written. Fold candidates + OOF concordance were retained.")
        sys.exit(2)

    print("\nDEPLOYMENT GATE: PASS -- fitting final production model on all eligible traps.")
    final_model = fit_final_model(records, cache, endpoint_keys, final_epochs)
    final_model.save(MODEL_OUT)
    with open(CLASS_LABELS_OUT, "w") as f:
        json.dump(STATE_CLASSES, f, indent=2)

    # Export a gap prior learned from all production-training traps.
    gmin, gmax, glr = learn_gap_prior(records, endpoint_keys)
    meta["decoder"]["gap_prior_export"] = {
        "min_gap": int(gmin), "max_gap": int(gmax), "log_ratio": glr.tolist(),
    }
    with open(META_OUT, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"--> Production model: {MODEL_OUT}")
    print(f"--> Labels:           {CLASS_LABELS_OUT}")
    print(f"--> Decoder metadata: {META_OUT}")
    print("DONE.")
