"""
train_rls_supermodel_v7.py
==========================

Positive-sum RLS supertrainer for Jordan's microfluidic aging-chip trap movies.

This trainer is deliberately NOT a replacement for the working
human_classifier_ui.py state model.  It trains a second, specialized RLS expert
and leaves the current UI classifier untouched.

Design
------
1) Gold-standard audit.  Uses JM135.xlsx manual trap-level RLS counts as an
   independent high-level target.  Frame annotations that disagree strongly
   with the manual count are excluded from supervised event training rather
   than poisoning the model, but their images remain useful for self-supervision.
2) Trap-native self-supervised pretraining.  A masked-patch autoencoder learns
   the morphology/PDMS/illumination domain from ALL extracted trap frames,
   including unlabeled ones.
3) BudFinder-style event expert.  Eleven aligned frames are encoded by the
   pretrained morphology encoder and a temporal Transformer predicts a division
   event directly at the center frame.  Auxiliary state/death heads retain the
   useful human labels already collected.
4) Microfluidic advantages.  Frames are translated so the tracked mother/pillar
   anchor is in a canonical location; the model therefore learns the unique
   mother-in-trap movie rather than generic yeast imagery.
5) Gold-count calibrator.  A heavily regularized ridge model combines several
   independently useful summaries of the event timeline to predict the observed
   RLS count.  Exact manual JM135 counts supervise this layer directly.
6) Position-grouped OOF validation.  Whole positions are held out.  No frame from
   an outer-test position is used for supervised event fitting or count fitting.
7) Existing working system is preserved.  No existing production model is ever
   overwritten.  New artifacts are promoted only if the manual-gold OOF gate is
   cleared.

Research basis
--------------
* Nguyen et al., BudFinder, PLOS Computational Biology 2026: masked-autoencoder
  pretraining on unlabeled yeast crops + an 11-frame temporal Transformer for
  direct budding-event detection.
* Leger et al., MIDL 2026: full sequence models outperform single/fixed-window
  approaches for label-free cell-cycle inference.
* Kraus et al., CVPR 2024: masked autoencoders are scalable learners of
  microscopy representations.

Environment variables
---------------------
AGING_ANNOTATION_PATH  default annotation/master_human_annotations.xlsx
AGING_GOLD_RLS_PATH    default JM135.xlsx
AGING_TRAPS_DIR        extracted Pos*_trap_*.tif directory
AGING_SSL_EPOCHS       default 24
AGING_EVENT_EPOCHS     default 28
AGING_FOLDS            default 3
AGING_BATCH_SIZE       event-model batch size, default 16
AGING_SSL_BATCH_SIZE   default 64
AGING_SEED             default 42
AGING_SKIP_SSL         1 -> skip SSL and load ssl_trap_encoder.keras

Outputs
-------
Always:
  v7_run_manifest.json
  v7_gold_annotation_audit.csv
  v7_gold_oof_concordance.csv
  candidate_v7_fold_*.keras
  ssl_trap_encoder.keras

Only if strict gold OOF gate passes:
  aging_chip_bud_event_transformer.keras
  aging_chip_rls_count_calibrator.joblib
  aging_chip_rls_supermodel_meta.json

The current aging_chip_classifier.keras / human_classifier_ui.py artifacts are
NEVER modified by this file.
"""

import os
import re
import sys
import json
import math
import time
import glob
import random
import hashlib
from collections import defaultdict, OrderedDict

import cv2
import joblib
import numpy as np
import pandas as pd
import tifffile as tif
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

# =============================================================================
# CONFIG
# =============================================================================
SEED = int(os.environ.get("AGING_SEED", 42))
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

ANNOTATION_PATH = os.environ.get(
    "AGING_ANNOTATION_PATH", os.path.join("annotation", "master_human_annotations.xlsx")
)
GOLD_RLS_PATH = os.environ.get("AGING_GOLD_RLS_PATH", "JM135.xlsx")
TRAPS_DIR = os.environ.get(
    "AGING_TRAPS_DIR",
    r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps",
)

IMG_SIZE = 96
WINDOW_RADIUS = 5
WINDOW_LEN = 2 * WINDOW_RADIUS + 1
DISPLAY_SPACE_SIZE = 460.0
GAP_SHIFT_RAW_PX = 25.0

N_FOLDS = int(os.environ.get("AGING_FOLDS", 3))
EVENT_EPOCHS = int(os.environ.get("AGING_EVENT_EPOCHS", 28))
SSL_EPOCHS = int(os.environ.get("AGING_SSL_EPOCHS", 24))
EVENT_BATCH = int(os.environ.get("AGING_BATCH_SIZE", 16))
SSL_BATCH = int(os.environ.get("AGING_SSL_BATCH_SIZE", 64))
SSL_STEPS = int(os.environ.get("AGING_SSL_STEPS", 180))
SSL_VAL_STEPS = int(os.environ.get("AGING_SSL_VAL_STEPS", 30))
SKIP_SSL = os.environ.get("AGING_SKIP_SSL", "0") == "1"

# Strong annotation-vs-manual disagreement means the frame labels are not safe
# event supervision.  Images remain in SSL.
MAX_GOLD_FRAME_DISAGREE = 2

# BudFinder-like contiguous-positive collapse.  Threshold is calibrated using
# training-side gold counts within every outer fold.
EVENT_THRESHOLDS = np.round(np.arange(0.10, 0.91, 0.05), 2)
DEATH_THRESHOLDS = (0.50, 0.60, 0.70, 0.80, 0.90)
DEATH_PERSISTENCES = (2, 3, 5, 7)

# Supervised sample balancing.
EVENT_POS_RADIUS = 1
TRANSITION_KEEP_RADIUS = 3
MAX_BACKGROUND_PER_TRAP = 110
LATE_LIFE_EVENT_BOOST = 1.6

# Strict candidate gate.  This is intentionally harder than the earlier v6 gate.
# It is a *candidate* for superhuman performance, not proof of superhumanity.
MAX_GOLD_OOF_MAE = float(os.environ.get("AGING_DEPLOY_MAE", 0.75))
MIN_GOLD_OOF_WITHIN1 = float(os.environ.get("AGING_DEPLOY_WITHIN1", 0.95))
MIN_GOLD_OOF_EXACT = float(os.environ.get("AGING_DEPLOY_EXACT", 0.70))
MIN_GOLD_OOF_DEATH = float(os.environ.get("AGING_DEPLOY_DEATH", 0.93))

SSL_ENCODER_OUT = "ssl_trap_encoder.keras"
FINAL_EVENT_OUT = "aging_chip_bud_event_transformer.keras"
FINAL_COUNT_OUT = "aging_chip_rls_count_calibrator.joblib"
FINAL_META_OUT = "aging_chip_rls_supermodel_meta.json"
OOF_OUT = "v7_gold_oof_concordance.csv"
AUDIT_OUT = "v7_gold_annotation_audit.csv"
MANIFEST_OUT = "v7_run_manifest.json"

EXCLUDE_CLASSES = {
    "Mother Escaped (Ignore Rest)", "Mother Escaped", "Skipped / Bad Trap",
    "2 Cells", "2 Cells (Right)"
}
STATE_CLASSES = [
    "Dead Cell", "Early Bud", "Late Bud", "Mother", "No Cell", "Out of Focus / Blurry"
]
STATE_TO_IDX = {c: i for i, c in enumerate(STATE_CLASSES)}
LIVING = {"Mother", "Early Bud", "Late Bud"}
GAPS = {"No Cell", "Out of Focus / Blurry"}

# =============================================================================
# FINGERPRINTS / GPU
# =============================================================================
def sha256_file(path, block=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def setup_gpu():
    gpus = tf.config.list_physical_devices("GPU")
    for g in gpus:
        try:
            tf.config.experimental.set_memory_growth(g, True)
        except Exception:
            pass
    if gpus:
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
    print(f"--> GPU count: {len(gpus)} | mixed precision: {'ON' if gpus else 'OFF'}")

# =============================================================================
# CANONICAL RLS RULE
# =============================================================================
def find_division_frames(labels):
    out = []
    for i in range(1, len(labels)):
        cur, prev = labels[i], labels[i - 1]
        if cur is None or prev is None:
            continue
        if prev == "Late Bud" and cur in ("Mother", "Early Bud"):
            out.append(i)
        elif cur in ("Mother", "Early Bud"):
            lb = i - 1
            while lb >= 0 and labels[lb] in GAPS:
                lb -= 1
            if 0 <= lb < i - 1 and labels[lb] in ("Early Bud", "Late Bud"):
                out.append(i)
    return out


def death_from_labels(labels):
    for i in range(1, len(labels)):
        if labels[i] != "Dead Cell":
            continue
        lb = i - 1
        while lb >= 0 and labels[lb] in ("Out of Focus / Blurry", None):
            lb -= 1
        if lb >= 0 and labels[lb] in LIVING:
            return True, i
    return False, None

# =============================================================================
# DATA LOADING / AUDIT
# =============================================================================
def norm_pos(v):
    m = re.search(r"(\d+)", str(v))
    return int(m.group(1)) if m else None


def map_trap_files(root):
    files = glob.glob(os.path.join(root, "*.tif")) + glob.glob(
        os.path.join(root, "**", "*.tif"), recursive=True
    )
    out = {}
    for fp in files:
        pm = re.search(r"pos_?(\d+)", fp, re.I)
        tm = re.search(r"trap_?(\d+)\.tif$", fp, re.I)
        if pm and tm:
            out[(int(pm.group(1)), int(tm.group(1)))] = fp
    return out


def read_annotations(path):
    df = pd.read_excel(path, sheet_name="Frame_Annotations")
    df = df.dropna(subset=["Class"]).copy()
    df["Class"] = df["Class"].astype(str).str.strip()
    df = df[df["Class"].str.lower() != "nan"].copy()
    df["Position_int"] = df["Position"].map(norm_pos)
    df = df[df["Position_int"].notna()].copy()
    df["Position_int"] = df["Position_int"].astype(int)
    df["Trap_ID"] = df["Trap_ID"].astype(int)
    df["Frame"] = df["Frame"].astype(int)
    return df


def read_gold(path):
    df = pd.read_excel(path)
    tcol = "TRAP Number (For Annotation File)"
    rcol = "Replicative Lifespan"
    dcol = "Dies on chip \n(1 = yes 0 = no)"
    df = df[df[tcol].notna() & df["Position"].notna() & df[rcol].notna()].copy()
    df["Position_int"] = df["Position"].astype(int)
    df["Trap_ID"] = df[tcol].astype(int)
    df["Gold_RLS"] = df[rcol].astype(float)
    df["Gold_Died"] = df[dcol].fillna(0).astype(int)
    # Duplicate mappings are dangerous; keep only unambiguous keys.
    dup = df.duplicated(["Position_int", "Trap_ID"], keep=False)
    if dup.any():
        print(f"--> WARNING: dropping {int(dup.sum())} duplicate gold mappings.")
        df = df[~dup].copy()
    return df


def build_records(ann, file_map, gold):
    gold_map = {
        (int(r.Position_int), int(r.Trap_ID)): {
            "gold_rls": float(r.Gold_RLS), "gold_died": int(r.Gold_Died)
        }
        for _, r in gold.iterrows()
    }
    by = defaultdict(list)
    for _, r in ann.iterrows():
        by[(int(r.Position_int), int(r.Trap_ID))].append(r)

    records = {}
    audit = []
    for key, fp in sorted(file_map.items()):
        try:
            with tif.TiffFile(fp) as tfp:
                n_frames = len(tfp.pages)
        except Exception:
            continue
        labels = [None] * n_frames
        coords = [None] * n_frames
        for r in by.get(key, []):
            fr = int(r.Frame)
            if not (0 <= fr < n_frames):
                continue
            cls = str(r.Class).strip()
            labels[fr] = cls
            coords[fr] = {
                "Pillar_P1_X": r.get("Pillar_P1_X", np.nan),
                "Pillar_P1_Y": r.get("Pillar_P1_Y", np.nan),
                "Pillar_P2_X": r.get("Pillar_P2_X", np.nan),
                "Pillar_P2_Y": r.get("Pillar_P2_Y", np.nan),
                "Mother_X": r.get("Mother_X", np.nan),
                "Mother_Y": r.get("Mother_Y", np.nan),
            }
        divs = find_division_frames(labels)
        human_died, human_death = death_from_labels(labels)
        g = gold_map.get(key)
        disagreement = None if g is None else len(divs) - g["gold_rls"]
        contaminated = bool(g is not None and abs(disagreement) > MAX_GOLD_FRAME_DISAGREE)
        # Excluded lifecycle labels also make this trap unsafe as dense event truth.
        excluded = any(x in EXCLUDE_CLASSES for x in labels if x is not None)
        clean_supervision = (not contaminated) and (not excluded) and sum(x is not None for x in labels) >= 30

        records[key] = {
            "key": key, "position": key[0], "trap": key[1], "path": fp,
            "n_frames": n_frames, "labels": labels, "coords": coords,
            "divisions": divs, "human_died": human_died, "human_death": human_death,
            "gold": g, "clean_supervision": clean_supervision,
        }
        audit.append({
            "position": key[0], "trap_id": key[1], "n_frames": n_frames,
            "labeled_frames": int(sum(x is not None for x in labels)),
            "frame_RLS": int(len(divs)),
            "gold_RLS": np.nan if g is None else g["gold_rls"],
            "gold_died": np.nan if g is None else g["gold_died"],
            "frame_minus_gold": np.nan if disagreement is None else disagreement,
            "clean_event_supervision": clean_supervision,
        })
    return records, pd.DataFrame(audit)

# =============================================================================
# TRAP-NATIVE IMAGE ALIGNMENT
# =============================================================================
def display_to_raw(x, y, raw_w, raw_h):
    try:
        x, y = float(x), float(y)
    except Exception:
        return np.nan, np.nan
    if np.isnan(x) or np.isnan(y):
        return np.nan, np.nan
    return x * raw_w / DISPLAY_SPACE_SIZE, y * raw_h / DISPLAY_SPACE_SIZE


def anchor_from_coords(coords, raw_w, raw_h):
    coords = coords or {}
    mx, my = display_to_raw(coords.get("Mother_X", np.nan), coords.get("Mother_Y", np.nan), raw_w, raw_h)
    if not (np.isnan(mx) or np.isnan(my)):
        return mx, my
    p1x, p1y = display_to_raw(coords.get("Pillar_P1_X", np.nan), coords.get("Pillar_P1_Y", np.nan), raw_w, raw_h)
    p2x, p2y = display_to_raw(coords.get("Pillar_P2_X", np.nan), coords.get("Pillar_P2_Y", np.nan), raw_w, raw_h)
    if not any(np.isnan(v) for v in (p1x, p1y, p2x, p2y)):
        return min(raw_w - 1.0, (p1x + p2x) / 2.0 + GAP_SHIFT_RAW_PX), (p1y + p2y) / 2.0
    return raw_w / 2.0, raw_h / 2.0


def normalize_gray(img):
    img = np.squeeze(img)
    if img.ndim > 2:
        img = img[0]
    lo, hi = np.percentile(img, (0.5, 99.5))
    if hi > lo:
        x = np.clip((img.astype(np.float32) - lo) / (hi - lo), 0, 1)
    else:
        x = img.astype(np.float32)
        m = max(float(x.max()), 1.0)
        x /= m
    return x.astype(np.float32)


def aligned_frame(raw, coords=None):
    x = normalize_gray(raw)
    h, w = x.shape[:2]
    ax, ay = anchor_from_coords(coords, w, h)
    # Keep mother at the middle-left of the canonical crop, leaving room on the
    # daughter/bud side while retaining trap pillars.
    tx, ty = IMG_SIZE * 0.44, IMG_SIZE * 0.50
    sx = IMG_SIZE / float(w)
    sy = IMG_SIZE / float(h)
    resized = cv2.resize(x, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_CUBIC)
    ax2, ay2 = ax * sx, ay * sy
    M = np.float32([[1, 0, tx - ax2], [0, 1, ty - ay2]])
    out = cv2.warpAffine(resized, M, (IMG_SIZE, IMG_SIZE), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REFLECT_101)
    return out[..., None]


class StackCache:
    def __init__(self, max_items=10):
        self.max_items = max_items
        self.cache = OrderedDict()

    def get(self, path):
        if path in self.cache:
            self.cache.move_to_end(path)
            return self.cache[path]
        with tif.TiffFile(path) as tfp:
            arr = [p.asarray() for p in tfp.pages]
        self.cache[path] = arr
        self.cache.move_to_end(path)
        while len(self.cache) > self.max_items:
            self.cache.popitem(last=False)
        return arr

# =============================================================================
# MASKED-PATCH SELF-SUPERVISION
# =============================================================================
def conv_block(x, filters, stride=2, name="cb"):
    x = layers.Conv2D(filters, 3, strides=stride, padding="same", use_bias=False,
                      name=name + "_conv")(x)
    x = layers.BatchNormalization(name=name + "_bn")(x)
    return layers.Activation("swish", name=name + "_act")(x)


def build_ssl_models():
    inp = layers.Input((IMG_SIZE, IMG_SIZE, 1), name="masked_trap_frame")
    x = conv_block(inp, 32, 2, "enc1")
    x = conv_block(x, 64, 2, "enc2")
    x = conv_block(x, 128, 2, "enc3")
    x = conv_block(x, 192, 2, "enc4")  # 6x6
    x = layers.Conv2D(192, 3, padding="same", activation="swish", name="enc_context")(x)
    emb = layers.GlobalAveragePooling2D(name="trap_embedding")(x)
    emb = layers.Dense(192, activation="swish", name="trap_embedding_dense")(emb)
    encoder = models.Model(inp, emb, name="ssl_trap_encoder")

    y = layers.Conv2DTranspose(128, 4, strides=2, padding="same", activation="swish")(x)
    y = layers.Conv2DTranspose(64, 4, strides=2, padding="same", activation="swish")(y)
    y = layers.Conv2DTranspose(32, 4, strides=2, padding="same", activation="swish")(y)
    y = layers.Conv2DTranspose(16, 4, strides=2, padding="same", activation="swish")(y)
    recon = layers.Conv2D(1, 3, padding="same", activation="sigmoid", dtype="float32", name="reconstruction")(y)
    auto = models.Model(inp, recon, name="masked_patch_autoencoder")
    return encoder, auto


def random_patch_mask(rng, patch=8, ratio=0.75):
    gh = IMG_SIZE // patch
    gw = IMG_SIZE // patch
    n = gh * gw
    k = int(round(n * ratio))
    ids = rng.choice(n, size=k, replace=False)
    small = np.zeros((gh, gw), np.float32)
    small.flat[ids] = 1.0
    mask = np.repeat(np.repeat(small, patch, 0), patch, 1)
    return mask[:IMG_SIZE, :IMG_SIZE, None]


class SSLSequence(tf.keras.utils.Sequence):
    def __init__(self, records, steps, batch, seed, shuffle_source=True, **kwargs):
        super().__init__(**kwargs)
        self.records = [r for r in records.values() if r["n_frames"] > 0]
        self.steps = steps
        self.batch = batch
        self.rng = np.random.RandomState(seed)
        self.cache = StackCache(max_items=7)
        self.shuffle_source = shuffle_source

    def __len__(self):
        return self.steps

    def __getitem__(self, idx):
        masked = np.zeros((self.batch, IMG_SIZE, IMG_SIZE, 1), np.float32)
        target = np.zeros_like(masked)
        weights = np.zeros((self.batch, IMG_SIZE, IMG_SIZE), np.float32)
        for i in range(self.batch):
            r = self.records[self.rng.randint(len(self.records))]
            stack = self.cache.get(r["path"])
            fr = self.rng.randint(len(stack))
            coords = r["coords"][fr] if fr < len(r["coords"]) else None
            img = aligned_frame(stack[fr], coords)
            mask = random_patch_mask(self.rng)
            # Replace masked regions with per-frame median rather than black, so
            # the pretext task cannot solve itself via mask-edge artifacts.
            med = float(np.median(img))
            x = img.copy()
            x[mask > 0] = med
            masked[i], target[i], weights[i] = x, img, mask[..., 0]
        return masked, target, weights

# =============================================================================
# 11-FRAME TEMPORAL EVENT MODEL
# =============================================================================
def transformer_block(x, dim, heads, ff_mult=2, dropout=0.15, name="tr"):
    n1 = layers.LayerNormalization(name=name + "_ln1")(x)
    a = layers.MultiHeadAttention(num_heads=heads, key_dim=dim // heads,
                                  dropout=dropout, name=name + "_mha")(n1, n1)
    x = layers.Add(name=name + "_add1")([x, a])
    n2 = layers.LayerNormalization(name=name + "_ln2")(x)
    y = layers.Dense(dim * ff_mult, activation="gelu", name=name + "_ff1")(n2)
    y = layers.Dropout(dropout)(y)
    y = layers.Dense(dim, name=name + "_ff2")(y)
    return layers.Add(name=name + "_add2")([x, y])


def build_event_model(ssl_encoder):
    clip = layers.Input((WINDOW_LEN, IMG_SIZE, IMG_SIZE, 1), name="aligned_11frame_clip")
    emb = layers.TimeDistributed(ssl_encoder, name="frame_encoder")(clip)
    dim = int(ssl_encoder.output_shape[-1])
    # Learned temporal positions using a standard Embedding layer; no custom
    # serialization layer is required.
    positions = tf.range(WINDOW_LEN)
    pos_layer = layers.Embedding(WINDOW_LEN, dim, name="temporal_position_embedding")
    pos = pos_layer(positions)
    x = emb + pos
    x = transformer_block(x, dim, 4, name="temporal1")
    x = transformer_block(x, dim, 4, name="temporal2")
    center = layers.Lambda(lambda z: z[:, WINDOW_RADIUS, :], name="center_token")(x)
    mean = layers.GlobalAveragePooling1D(name="temporal_mean")(x)
    fused = layers.Concatenate(name="event_fusion")([center, mean])
    fused = layers.Dense(256, activation="swish", name="event_dense")(fused)
    fused = layers.Dropout(0.30)(fused)
    event = layers.Dense(1, dtype="float32", name="division")(fused)
    dead = layers.Dense(1, dtype="float32", name="dead")(fused)
    state = layers.Dense(len(STATE_CLASSES), dtype="float32", name="state")(fused)
    return models.Model(clip, {"division": event, "dead": dead, "state": state},
                        name="trap_budding_temporal_transformer")


def event_loss(y_true, logits):
    y = tf.cast(y_true, tf.float32)
    x = tf.cast(logits, tf.float32)
    ce = tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=x)
    p = tf.sigmoid(x)
    pt = y * p + (1 - y) * (1 - p)
    alpha = y * 0.70 + (1 - y) * 0.30
    return tf.squeeze(alpha * tf.pow(1 - pt, 2.0) * ce, axis=-1)


def compile_event_model(model, lr):
    model.compile(
        optimizer=tf.keras.optimizers.AdamW(lr, weight_decay=1e-5, clipnorm=1.0),
        loss={
            "division": event_loss,
            "dead": tf.keras.losses.BinaryCrossentropy(from_logits=True),
            "state": tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        },
        loss_weights={"division": 3.0, "dead": 0.55, "state": 0.45},
        metrics={
            "division": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
            "dead": [tf.keras.metrics.AUC(name="auc", from_logits=True)],
            "state": ["accuracy"],
        },
    )


def build_supervised_index(records, allowed_positions, training=True):
    rng = np.random.RandomState(SEED + (1 if training else 99))
    samples = []
    for key, r in records.items():
        if r["position"] not in allowed_positions or not r["clean_supervision"]:
            continue
        labels = r["labels"]
        events = set(r["divisions"])
        positives = set()
        for e in events:
            for d in range(-EVENT_POS_RADIUS, EVENT_POS_RADIUS + 1):
                if 0 <= e + d < r["n_frames"]:
                    positives.add(e + d)
        keep = set(positives)
        # Keep difficult state-transition neighborhoods.
        for i in range(1, len(labels)):
            if labels[i] is not None and labels[i - 1] is not None and labels[i] != labels[i - 1]:
                for d in range(-TRANSITION_KEEP_RADIUS, TRANSITION_KEEP_RADIUS + 1):
                    if 0 <= i + d < r["n_frames"]:
                        keep.add(i + d)
        neg_pool = [i for i, x in enumerate(labels) if x is not None and i not in keep]
        if training and len(neg_pool) > MAX_BACKGROUND_PER_TRAP:
            neg_pool = rng.choice(neg_pool, MAX_BACKGROUND_PER_TRAP, replace=False).tolist()
        keep.update(neg_pool)

        # Age estimate from human event history is used ONLY for sample weighting,
        # never as an inference feature.
        ev_sorted = sorted(events)
        for c in sorted(keep):
            cls = labels[c]
            if cls is None or cls in EXCLUDE_CLASSES or cls not in STATE_TO_IDX:
                continue
            is_event = 1.0 if c in positives else 0.0
            dead = 1.0 if cls == "Dead Cell" else 0.0
            prior_divs = sum(e <= c for e in ev_sorted)
            late = prior_divs >= max(12, int(0.65 * max(len(ev_sorted), 1)))
            weight = 1.0
            if is_event:
                weight *= 2.5
                if late:
                    weight *= LATE_LIFE_EVENT_BOOST
            samples.append((key, c, is_event, dead, STATE_TO_IDX[cls], weight))
    return samples


class ClipSequence(tf.keras.utils.Sequence):
    def __init__(self, records, samples, batch, shuffle, seed, **kwargs):
        super().__init__(**kwargs)
        self.records = records
        self.samples = list(samples)
        self.batch = batch
        self.shuffle = shuffle
        self.rng = np.random.RandomState(seed)
        self.cache = StackCache(max_items=8)
        self.indices = np.arange(len(self.samples))
        self.on_epoch_end()

    def __len__(self):
        return int(math.ceil(len(self.samples) / self.batch))

    def on_epoch_end(self):
        if self.shuffle:
            self.rng.shuffle(self.indices)

    def __getitem__(self, bi):
        ids = self.indices[bi * self.batch:(bi + 1) * self.batch]
        B = len(ids)
        X = np.zeros((B, WINDOW_LEN, IMG_SIZE, IMG_SIZE, 1), np.float32)
        y_event = np.zeros((B, 1), np.float32)
        y_dead = np.zeros((B, 1), np.float32)
        y_state = np.zeros((B,), np.int32)
        sw_event = np.ones((B,), np.float32)
        for j, si in enumerate(ids):
            key, center, ev, dead, state, w = self.samples[si]
            r = self.records[key]
            stack = self.cache.get(r["path"])
            for k, off in enumerate(range(-WINDOW_RADIUS, WINDOW_RADIUS + 1)):
                fr = min(max(center + off, 0), len(stack) - 1)
                coords = r["coords"][fr] if fr < len(r["coords"]) else None
                X[j, k] = aligned_frame(stack[fr], coords)
            y_event[j, 0], y_dead[j, 0], y_state[j], sw_event[j] = ev, dead, state, w
        y = {"division": y_event, "dead": y_dead, "state": y_state}
        sw = {"division": sw_event, "dead": np.ones(B, np.float32), "state": np.ones(B, np.float32)}
        return X, y, sw

# =============================================================================
# FULL-TRAP INFERENCE / DECODING
# =============================================================================
def predict_trap(model, rec, batch=32):
    cache = StackCache(max_items=1)
    stack = cache.get(rec["path"])
    n = len(stack)
    div = np.zeros(n, np.float32)
    dead = np.zeros(n, np.float32)
    state = np.zeros((n, len(STATE_CLASSES)), np.float32)
    for start in range(0, n, batch):
        centers = list(range(start, min(n, start + batch)))
        X = np.zeros((len(centers), WINDOW_LEN, IMG_SIZE, IMG_SIZE, 1), np.float32)
        for j, c in enumerate(centers):
            for k, off in enumerate(range(-WINDOW_RADIUS, WINDOW_RADIUS + 1)):
                fr = min(max(c + off, 0), n - 1)
                coords = rec["coords"][fr] if fr < len(rec["coords"]) else None
                X[j, k] = aligned_frame(stack[fr], coords)
        p = model.predict(X, verbose=0)
        div[start:start + len(centers)] = tf.sigmoid(p["division"]).numpy().ravel()
        dead[start:start + len(centers)] = tf.sigmoid(p["dead"]).numpy().ravel()
        state[start:start + len(centers)] = tf.nn.softmax(p["state"], axis=1).numpy()
    return {"division": div, "dead": dead, "state": state}


def collapse_positive_runs(probs, threshold, cutoff=None):
    n = len(probs) if cutoff is None else min(len(probs), int(cutoff))
    mask = np.asarray(probs[:n]) >= float(threshold)
    events = []
    i = 0
    while i < n:
        if not mask[i]:
            i += 1
            continue
        j = i + 1
        while j < n and mask[j]:
            j += 1
        local = i + int(np.argmax(probs[i:j]))
        events.append(local)
        i = j
    return events


def death_call(probs, threshold=0.8, persistence=3):
    x = np.asarray(probs) >= threshold
    if persistence <= 1:
        ids = np.where(x)[0]
        return (len(ids) > 0, int(ids[0]) if len(ids) else None)
    run = 0
    for i, v in enumerate(x):
        run = run + 1 if v else 0
        if run >= persistence:
            return True, i - persistence + 1
    return False, None


def timeline_features(pred, threshold):
    divp, deadp, sp = pred["division"], pred["dead"], pred["state"]
    events = collapse_positive_runs(divp, threshold)
    feats = []
    for t in np.arange(0.10, 0.91, 0.10):
        feats.append(float(len(collapse_positive_runs(divp, t))))
    feats.extend([
        float(np.sum(divp)), float(np.mean(divp)), float(np.std(divp)),
        float(np.quantile(divp, 0.90)), float(np.quantile(divp, 0.95)), float(np.max(divp)),
        float(len(events)), float(len(divp)),
        float(np.mean(divp[:max(1, len(divp)//3)])),
        float(np.mean(divp[len(divp)//3:2*len(divp)//3])) if len(divp) >= 3 else float(np.mean(divp)),
        float(np.mean(divp[2*len(divp)//3:])) if len(divp) >= 3 else float(np.mean(divp)),
        float(np.max(deadp)), float(np.mean(deadp[-max(1, len(deadp)//5):])),
    ])
    # Soft state-transition evidence: Late(t-1) * [Mother+Early](t)
    late_i = STATE_TO_IDX["Late Bud"]
    mother_i = STATE_TO_IDX["Mother"]
    early_i = STATE_TO_IDX["Early Bud"]
    if len(sp) >= 2:
        trans = sp[:-1, late_i] * (sp[1:, mother_i] + sp[1:, early_i])
        feats += [float(np.sum(trans)), float(np.max(trans)), float(np.mean(trans))]
    else:
        feats += [0.0, 0.0, 0.0]
    if len(events) >= 2:
        gaps = np.diff(events)
        feats += [float(np.mean(gaps)), float(np.std(gaps)), float(np.median(gaps)), float(np.min(gaps))]
    else:
        feats += [0.0, 0.0, 0.0, 0.0]
    return np.asarray(feats, np.float32)


def calibrate_threshold(pred_by_key, gold_keys, records):
    best = None
    for th in EVENT_THRESHOLDS:
        errs = []
        for k in gold_keys:
            g = records[k]["gold"]
            if g is None:
                continue
            # Use detected death as a soft cutoff only for on-chip deaths.  For
            # censored cells, count through the movie; count calibrator learns the
            # residual from the gold observed count.
            dcall, dfr = death_call(pred_by_key[k]["dead"], 0.8, 3)
            cutoff = dfr if (g["gold_died"] == 1 and dcall and dfr is not None) else None
            c = len(collapse_positive_runs(pred_by_key[k]["division"], th, cutoff=cutoff))
            errs.append(abs(c - g["gold_rls"]))
        if not errs:
            continue
        score = float(np.mean(errs))
        if best is None or score < best[0]:
            best = (score, float(th))
    return 0.5 if best is None else best[1]


def calibrate_death(pred_by_key, gold_keys, records):
    best = None
    for th in DEATH_THRESHOLDS:
        for pers in DEATH_PERSISTENCES:
            ok = []
            for k in gold_keys:
                g = records[k]["gold"]
                if g is None:
                    continue
                call, _ = death_call(pred_by_key[k]["dead"], th, pers)
                ok.append(int(call == bool(g["gold_died"])))
            if not ok:
                continue
            acc = float(np.mean(ok))
            if best is None or acc > best[0]:
                best = (acc, float(th), int(pers))
    return {"threshold": 0.8, "persistence": 3} if best is None else {
        "threshold": best[1], "persistence": best[2]
    }


def fit_count_calibrator(pred_by_key, gold_keys, records, threshold):
    X, y = [], []
    for k in gold_keys:
        if records[k]["gold"] is None:
            continue
        X.append(timeline_features(pred_by_key[k], threshold))
        y.append(records[k]["gold"]["gold_rls"])
    if len(X) < 8:
        return None
    X = np.asarray(X, np.float32)
    y = np.asarray(y, np.float32)
    # Strong regularization is intentional: only ~100 manually mapped traps
    # exist, so the calibrator may correct systematic biases but cannot memorize.
    mdl = Ridge(alpha=25.0)
    mdl.fit(X, y)
    return mdl


def predict_count(pred, threshold, count_model=None):
    raw = len(collapse_positive_runs(pred["division"], threshold))
    if count_model is None:
        return int(raw)
    x = timeline_features(pred, threshold).reshape(1, -1)
    val = float(count_model.predict(x)[0])
    return int(np.clip(np.rint(val), 0, 70))

# =============================================================================
# OUTER POSITION-GROUPED CV
# =============================================================================
def choose_outer_splits(gold_keys, records, n_folds):
    keys = np.array(gold_keys, dtype=object)
    groups = np.array([records[k]["position"] for k in gold_keys])
    unique = np.unique(groups)
    folds = min(max(2, n_folds), len(unique))
    gkf = GroupKFold(n_splits=folds)
    dummy = np.zeros(len(keys))
    for tr, te in gkf.split(dummy, groups=groups):
        yield [gold_keys[i] for i in tr], [gold_keys[i] for i in te]


def train_one_fold(fold, ssl_encoder, records, train_gold_keys, test_gold_keys):
    test_positions = {records[k]["position"] for k in test_gold_keys}
    train_positions = {r["position"] for r in records.values()} - test_positions
    # Position-level internal validation: choose one train position, rotating by fold.
    pos_sorted = sorted(train_positions)
    val_pos = {pos_sorted[(fold - 1) % len(pos_sorted)]} if len(pos_sorted) > 1 else set()
    fit_pos = train_positions - val_pos if val_pos else train_positions

    enc = tf.keras.models.clone_model(ssl_encoder)
    enc.set_weights(ssl_encoder.get_weights())
    enc.trainable = False
    model = build_event_model(enc)
    compile_event_model(model, 4e-4)

    tr_samples = build_supervised_index(records, fit_pos, training=True)
    va_samples = build_supervised_index(records, val_pos, training=False) if val_pos else []
    if len(tr_samples) < 100:
        raise RuntimeError(f"Fold {fold}: only {len(tr_samples)} supervised clips.")
    tr_seq = ClipSequence(records, tr_samples, EVENT_BATCH, True, SEED + fold)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_division_auc" if va_samples else "division_auc",
            mode="max", patience=5, restore_best_weights=True, min_delta=0.002
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss" if va_samples else "loss", patience=2, factor=0.5,
            min_lr=2e-6
        ),
    ]
    fit_kwargs = dict(epochs=EVENT_EPOCHS, verbose=2, callbacks=callbacks)
    if va_samples:
        fit_kwargs["validation_data"] = ClipSequence(records, va_samples, EVENT_BATCH, False, SEED + 100 + fold)
    print(f"\n[FOLD {fold}] supervised train positions={sorted(fit_pos)} val={sorted(val_pos)} test={sorted(test_positions)}")
    print(f"[FOLD {fold}] train clips={len(tr_samples)} val clips={len(va_samples)}")
    model.fit(tr_seq, **fit_kwargs)

    # Gentle end-to-end adaptation of the morphology encoder.
    enc.trainable = True
    for layer in enc.layers[:-6]:
        layer.trainable = False
    compile_event_model(model, 2e-5)
    model.fit(tr_seq, validation_data=fit_kwargs.get("validation_data"), epochs=6,
              verbose=2, callbacks=[tf.keras.callbacks.EarlyStopping(
                  monitor="val_loss" if va_samples else "loss", patience=2,
                  restore_best_weights=True)])

    model.save(f"candidate_v7_fold_{fold}.keras")

    # Predictions for all gold training/test traps are required to calibrate the
    # threshold and the gold-count residual model without touching test labels.
    relevant = sorted(set(train_gold_keys) | set(test_gold_keys))
    pred = {}
    for j, k in enumerate(relevant, 1):
        pred[k] = predict_trap(model, records[k])
        if j % 10 == 0:
            print(f"[FOLD {fold}] inferred {j}/{len(relevant)} gold-mapped traps")

    threshold = calibrate_threshold(pred, train_gold_keys, records)
    death_cfg = calibrate_death(pred, train_gold_keys, records)
    count_model = fit_count_calibrator(pred, train_gold_keys, records, threshold)

    rows = []
    for k in test_gold_keys:
        g = records[k]["gold"]
        p = pred[k]
        pred_rls = predict_count(p, threshold, count_model)
        dcall, dfr = death_call(p["dead"], death_cfg["threshold"], death_cfg["persistence"])
        raw_count = len(collapse_positive_runs(p["division"], threshold))
        rows.append({
            "fold": fold, "position": k[0], "trap_id": k[1],
            "gold_rls": g["gold_rls"], "pred_rls": pred_rls,
            "raw_event_count": raw_count, "error": pred_rls - g["gold_rls"],
            "gold_died": g["gold_died"], "pred_died": int(dcall),
            "event_threshold": threshold,
            "death_threshold": death_cfg["threshold"],
            "death_persistence": death_cfg["persistence"],
        })
    return rows

# =============================================================================
# FINAL FIT
# =============================================================================
def fit_final_model(ssl_encoder, records, gold_keys, median_threshold):
    positions = {r["position"] for r in records.values()}
    enc = tf.keras.models.clone_model(ssl_encoder)
    enc.set_weights(ssl_encoder.get_weights())
    enc.trainable = False
    model = build_event_model(enc)
    compile_event_model(model, 4e-4)
    samples = build_supervised_index(records, positions, training=True)
    seq = ClipSequence(records, samples, EVENT_BATCH, True, SEED + 900)
    model.fit(seq, epochs=max(10, int(EVENT_EPOCHS * 0.75)), verbose=2,
              callbacks=[tf.keras.callbacks.ReduceLROnPlateau(
                  monitor="loss", patience=2, factor=0.5, min_lr=2e-6)])
    enc.trainable = True
    for layer in enc.layers[:-6]:
        layer.trainable = False
    compile_event_model(model, 2e-5)
    model.fit(seq, epochs=5, verbose=2)

    pred = {k: predict_trap(model, records[k]) for k in gold_keys}
    threshold = calibrate_threshold(pred, gold_keys, records)
    death_cfg = calibrate_death(pred, gold_keys, records)
    count_model = fit_count_calibrator(pred, gold_keys, records, threshold)
    model.save(FINAL_EVENT_OUT)
    joblib.dump(count_model, FINAL_COUNT_OUT)
    return model, count_model, threshold, death_cfg

# =============================================================================
# MAIN
# =============================================================================
def main():
    setup_gpu()
    source_path = os.path.abspath(__file__)
    source_sha = sha256_file(source_path)
    print("=" * 88)
    print("AGING CHIP RLS SUPERTRAINER v7 -- MASKED MORPHOLOGY + 11-FRAME EVENT TRANSFORMER")
    print("Existing human_classifier_ui.py production model: PRESERVED / NOT OVERWRITTEN")
    print(f"SOURCE: {source_path}")
    print(f"SOURCE SHA256: {source_sha}")
    print("=" * 88)

    for p, name in [(ANNOTATION_PATH, "annotations"), (GOLD_RLS_PATH, "JM135 gold RLS")]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing {name}: {p}")
    if not os.path.isdir(TRAPS_DIR):
        raise FileNotFoundError(f"Missing trap directory: {TRAPS_DIR}")

    ann = read_annotations(ANNOTATION_PATH)
    gold = read_gold(GOLD_RLS_PATH)
    file_map = map_trap_files(TRAPS_DIR)
    if not file_map:
        raise RuntimeError(f"No Pos*_trap_*.tif files found in {TRAPS_DIR}")
    records, audit = build_records(ann, file_map, gold)
    audit.to_csv(AUDIT_OUT, index=False)

    gold_keys = [k for k, r in records.items() if r["gold"] is not None]
    gold_positions = sorted({records[k]["position"] for k in gold_keys})
    clean_records = sum(r["clean_supervision"] for r in records.values())
    print(f"--> TIFF traps: {len(records)} | clean dense-label traps: {clean_records}")
    print(f"--> Gold-mapped TIFF traps: {len(gold_keys)} across positions {gold_positions}")

    # The manual RLS sheet is also a powerful annotation quality-control layer.
    ov = audit[audit["gold_RLS"].notna()].copy()
    ov["abs_disagree"] = (ov["frame_RLS"] - ov["gold_RLS"]).abs()
    print("\n=== MANUAL GOLD vs FRAME-ANNOTATION CONSISTENCY ===")
    print(f"Overlap traps: {len(ov)}")
    if len(ov):
        print(f"Raw MAE: {ov['abs_disagree'].mean():.3f} divisions")
        print(f"Exact: {(ov['abs_disagree'] == 0).mean()*100:.1f}% | within1: {(ov['abs_disagree'] <= 1).mean()*100:.1f}%")
        print(f"Excluded from event supervision for |difference|>{MAX_GOLD_FRAME_DISAGREE}: {(ov['abs_disagree'] > MAX_GOLD_FRAME_DISAGREE).sum()}")

    manifest = {
        "trainer_version": "v7",
        "source_sha256": source_sha,
        "annotation_path": os.path.abspath(ANNOTATION_PATH),
        "annotation_sha256": sha256_file(ANNOTATION_PATH),
        "gold_rls_path": os.path.abspath(GOLD_RLS_PATH),
        "gold_rls_sha256": sha256_file(GOLD_RLS_PATH),
        "traps_dir": os.path.abspath(TRAPS_DIR),
        "n_tiff_traps": len(records),
        "n_gold_mapped_traps": len(gold_keys),
        "gold_positions": gold_positions,
        "timestamp_unix": time.time(),
    }
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2)

    # -------------------------------------------------------------------------
    # SSL pretraining on ALL trap images.  This is label-free domain adaptation;
    # it deliberately uses images that may later be held out in the supervised
    # CV because no RLS/state/event label is exposed during this stage.
    # -------------------------------------------------------------------------
    if SKIP_SSL and os.path.exists(SSL_ENCODER_OUT):
        print(f"\n--> Loading existing SSL encoder: {SSL_ENCODER_OUT}")
        ssl_encoder = tf.keras.models.load_model(SSL_ENCODER_OUT, compile=False)
    else:
        print("\n================ SELF-SUPERVISED MASKED-PATCH PRETRAINING ================")
        ssl_encoder, auto = build_ssl_models()
        auto.compile(optimizer=tf.keras.optimizers.AdamW(3e-4, weight_decay=1e-5), loss="mse")
        train_ssl = SSLSequence(records, SSL_STEPS, SSL_BATCH, SEED + 11)
        val_ssl = SSLSequence(records, SSL_VAL_STEPS, SSL_BATCH, SEED + 22)
        auto.fit(
            train_ssl, validation_data=val_ssl, epochs=SSL_EPOCHS, verbose=2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5,
                                                 restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=2,
                                                     factor=0.5, min_lr=1e-6),
            ],
        )
        ssl_encoder.save(SSL_ENCODER_OUT)
        print(f"--> Saved {SSL_ENCODER_OUT}")

    # -------------------------------------------------------------------------
    # Outer OOF by POSITION against manual gold RLS.
    # -------------------------------------------------------------------------
    print("\n================ POSITION-GROUPED GOLD OOF ================")
    all_rows = []
    for fold, (tr_gold, te_gold) in enumerate(choose_outer_splits(gold_keys, records, N_FOLDS), 1):
        print("\n" + "=" * 88)
        print(f"FOLD {fold}: train gold={len(tr_gold)} test gold={len(te_gold)} | test positions={sorted({records[k]['position'] for k in te_gold})}")
        print("=" * 88)
        rows = train_one_fold(fold, ssl_encoder, records, tr_gold, te_gold)
        all_rows.extend(rows)
        tmp = pd.DataFrame(all_rows)
        tmp.to_csv(OOF_OUT, index=False)

    oof = pd.DataFrame(all_rows)
    oof.to_csv(OOF_OUT, index=False)
    ae = np.abs(oof["error"].to_numpy(float))
    mae = float(ae.mean())
    exact = float((ae == 0).mean())
    within1 = float((ae <= 1).mean())
    death = float((oof["gold_died"].astype(int) == oof["pred_died"].astype(int)).mean())
    bias = float(oof["error"].mean())

    print("\n" + "=" * 88)
    print("MANUAL-GOLD OUT-OF-FOLD REPORT -- WHOLE POSITIONS UNSEEN BY SUPERVISED FIT")
    print("=" * 88)
    print(f"Gold OOF traps:          {len(oof)}")
    print(f"RLS MAE:                 {mae:.3f} divisions")
    print(f"RLS bias:                {bias:+.3f}")
    print(f"Exact RLS:               {exact*100:.1f}%")
    print(f"Within +/-1 division:    {within1*100:.1f}%")
    print(f"Death agreement:         {death*100:.1f}%")
    print(f"Report:                  {OOF_OUT}")

    passed = (
        mae <= MAX_GOLD_OOF_MAE and within1 >= MIN_GOLD_OOF_WITHIN1
        and exact >= MIN_GOLD_OOF_EXACT and death >= MIN_GOLD_OOF_DEATH
    )
    print("\nSUPERHUMAN-CANDIDATE GATE: " + ("PASS" if passed else "FAIL"))
    print(f"Requires MAE<={MAX_GOLD_OOF_MAE:.2f}, within1>={MIN_GOLD_OOF_WITHIN1*100:.0f}%, "
          f"exact>={MIN_GOLD_OOF_EXACT*100:.0f}%, death>={MIN_GOLD_OOF_DEATH*100:.0f}%")
    print("NOTE: Passing this gate is evidence of exceptional agreement with the manual gold sheet; "
          "true 'better than the best human' requires an independent repeat/second-human benchmark.")

    if not passed:
        print("\nCandidate fold models and diagnostics retained. Existing production classifier was untouched.")
        print("Do NOT promote v7 automatically.")
        return

    print("\n================ FINAL FIT ON ALL CLEAN SUPERVISION ================")
    med_th = float(np.median(oof["event_threshold"])) if len(oof) else 0.5
    _, count_model, th, death_cfg = fit_final_model(ssl_encoder, records, gold_keys, med_th)
    meta = {
        "version": "v7",
        "input": {
            "window_length": WINDOW_LEN, "img_size": IMG_SIZE,
            "alignment": "mother_or_pillar_anchor_to_canonical_trap_location",
        },
        "event_threshold": th,
        "death_threshold": death_cfg["threshold"],
        "death_persistence": death_cfg["persistence"],
        "count_calibrator": FINAL_COUNT_OUT,
        "event_model": FINAL_EVENT_OUT,
        "ssl_encoder": SSL_ENCODER_OUT,
        "gold_oof": {
            "n": len(oof), "mae": mae, "bias": bias, "exact": exact,
            "within1": within1, "death_agreement": death,
        },
        "preserves_existing_ui_classifier": True,
        "source_sha256": source_sha,
    }
    with open(FINAL_META_OUT, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"--> PROMOTED: {FINAL_EVENT_OUT}")
    print(f"--> PROMOTED: {FINAL_COUNT_OUT}")
    print(f"--> PROMOTED: {FINAL_META_OUT}")
    print("--> Existing aging_chip_classifier.keras remains unchanged for human_classifier_ui.py.")


if __name__ == "__main__":
    main()
