import os
import re
import cv2
import glob
import json
import shutil
import numpy as np
import pandas as pd
import tifffile as tif
import tensorflow as tf

# ==============================================================================
# PATHS & MASTER CONFIGURATION
# ==============================================================================
OUTDIR = './annotation/'
os.makedirs(OUTDIR, exist_ok=True)

MASTER_EXCEL_PATH = os.path.join(OUTDIR, "master_human_annotations.xlsx")
MODEL_PATH = "aging_chip_classifier.keras"
CLASS_LABELS_PATH = "class_labels.json"
RLS_DETECTOR_PATH = "aging_chip_rls_detector.keras"
RLS_DETECTOR_META_PATH = "rls_detector_meta.json"

ORACLE_MODEL_PATH = "lifespan_oracle.keras"
ORACLE_META_PATH = "lifespan_oracle_meta.json"

# ------------------------------------------------------------------------------
# CHIP REGISTRY -- !! KEEP IN SYNC with DEFAULT_TRAPS_DIRS in train_classifier.py !!
# Every physical aging chip reuses the same position names (Pos0, Pos1, ...),
# so the Chip_ID column in master_human_annotations.xlsx is the ONLY thing
# keeping annotations of identically named positions on different chips apart.
# This mapping lets the startup prompts (a) auto-fill the correct extracted-
# traps directory for the chip being annotated and (b) refuse a Chip_ID /
# directory mixup, which would otherwise silently corrupt BOTH chips' records.
# ------------------------------------------------------------------------------
DEFAULT_CHIP_ID = "JM135_SixCondition_33"  # current default: six-condition chip (_33 acquisition)
KNOWN_CHIP_TRAPS_DIRS = {
    "JM135_CR_Mud1": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps",
    "JM135_CR_Mud1_Chip2_Intronless": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Aging Chip 2 includes intronless Mud1\_1\extracted_traps",
    "JM135_SixCondition_33": r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\Six condition chip\_33\extracted_traps",
}

SPATIAL_KEYS = ["Pillar_P1_X", "Pillar_P1_Y", "Pillar_P2_X", "Pillar_P2_Y", "Mother_X", "Mother_Y"]

ORACLE_FEATURE_VERSION = 2  # v2: dropped mean_conf/recent_conf (were trained as constant 1.0
                            # from human labels but served with real classifier confidences ->
                            # train/serve skew). Retrain with train_oracle_only.py.
ORACLE_FEATURE_NAMES = [
    "curr_rls", "frames_observed",
    "frac_mother", "frac_early", "frac_late", "frac_no_cell", "frac_blurry", "frac_dead",
    "is_curr_mother", "is_curr_early", "is_curr_late", "is_curr_no_cell", "is_curr_blurry", "is_curr_dead",
    "mean_idi", "std_idi", "recent_idi", "recent_3_mean_idi", "idi_slope", "idi_cv"
]

CLASS_CONFIG = {
    ord('1'): {"key_str": "[1]", "label": "Mother",                     "color": (255, 160, 0)},     
    ord('2'): {"key_str": "[2]", "label": "Early Bud",                   "color": (0, 180, 255)},    
    ord('3'): {"key_str": "[3]", "label": "Late Bud",                    "color": (0, 220, 100)},    
    ord('4'): {"key_str": "[4]", "label": "Dead Cell",                   "color": (0, 0, 230)},      
    ord('5'): {"key_str": "[5]", "label": "No Cell",                     "color": (150, 150, 150)},  
    ord('7'): {"key_str": "[7]", "label": "Mother Escaped (Ignore Rest)","color": (0, 255, 255)},    
    ord('8'): {"key_str": "[8]", "label": "Out of Focus / Blurry",       "color": (180, 50, 180)},    
    ord('x'): {"key_str": "[X]", "label": "Skipped / Bad Trap",          "color": (0, 100, 255)}
}

CLASS_CONFIG[ord('e')] = CLASS_CONFIG[ord('7')]
CLASS_CONFIG[ord('E')] = CLASS_CONFIG[ord('7')]
CLASS_CONFIG[ord('f')] = CLASS_CONFIG[ord('8')]
CLASS_CONFIG[ord('F')] = CLASS_CONFIG[ord('8')]

# Arrow keys via cv2.waitKeyEx (codes are platform-specific: Windows / Linux / macOS)
ARROW_RIGHT_CODES = {2555904, 65363, 63235}
ARROW_LEFT_CODES  = {2424832, 65361, 63234}
NAV_NEXT_FRAME_KEYS = ARROW_RIGHT_CODES
NAV_PREV_FRAME_KEYS = ARROW_LEFT_CODES
NAV_NEXT_TRAP_KEYS  = {ord('n'), ord('N')}
NAV_PREV_TRAP_KEYS  = {ord('p'), ord('P')}
NAV_QUIT_KEYS       = {ord('q'), ord('Q')}

KEY_TOGGLE_ORACLE_OVERLAY = {ord('o'), ord('O')}
KEY_RESET_CLICKS          = {ord('c'), ord('C')}
KEY_ZOOM_IN               = ord('=')
KEY_ZOOM_OUT              = ord('-')
KEY_BRIGHT_UP             = ord(']')
KEY_BRIGHT_DN             = ord('[')

CLASS_LABELS = []
SPATIAL_CLICKS = []  # Active manual clicks placed on the current frame


# ==============================================================================
# CANONICAL PIPELINE GEOMETRY, MODEL INPUT & TEMPORAL SMOOTHING
# !! KEEP THIS BLOCK IDENTICAL TO THE COPY IN train_classifier.py !!
#
# COORDINATE SPACES (Bug fix): all clicks / auto-tracked coordinates (and the
# values stored in master_human_annotations.xlsx) live in the 460x460 DISPLAY
# space. Raw extracted trap frames are ~100x100. Every consumer of stored
# coordinates must convert display -> raw via display_to_raw() (i.e. /4.6 for
# 100px traps) before touching pixels.
#
# INPUT STRUCTURE (leakage fix): every frame, regardless of class, gets the
# SAME input: a TEMPORAL grayscale triplet [t-1, t, t+1] resized to 128x128
# (channels 0-2, so the network sees motion), plus a Gaussian heatmap channel
# (3) whose anchor falls back Mother -> pillar gap -> frame center, so a
# heatmap is ALWAYS present and its presence carries no class information.
# ==============================================================================
DISPLAY_SPACE_SIZE = 460.0     # coordinate space of the annotation display & Excel coords
MODEL_IMG_SIZE = (128, 128)    # (w, h) of the classifier input
HEATMAP_SIGMA = 10.0           # Gaussian sigma in model-input (128px) space
GAP_SHIFT_RAW_PX = 25.0        # right-shift from pillar midline into trap pocket, raw px
HMM_TRANSITIONS_PATH = "hmm_transitions.json"  # written by train_classifier.py
VITERBI_TEMPERATURE = 0.0  # fallback only. T>1 softens emissions (too high erases
                           # short Mother/Early dwells -> divisions deleted); T<1
                           # SHARPENS soft emissions so genuine dwells survive
                           # smoothing; T<=0 disables smoothing (raw argmax). The
                           # trainer/sweep pick T on validation traps and store it
                           # in model_input_meta.json; the UI loads it automatically.
MODEL_INPUT_FORMAT = "temporal_triplet_v2"  # written to model_input_meta.json by the
                                            # trainer; the UI warns loudly on mismatch
SINGLE_FRAME_INPUT_FORMAT = "single_frame_v1"  # ablation alternative (USE_TEMPORAL_TRIPLET
                                               # = False in train_classifier.py); the UI
                                               # builds inputs to match the loaded model
HMM_MAX_SELF_TRANSITION = 0.98  # anti-absorption: no state may be stickier than this
HMM_MIN_TRANSITION = 1e-3       # every transition keeps a floor probability, so
                                # sustained contrary evidence can always pull the
                                # Viterbi path out of a state (e.g. a premature
                                # 'Dead Cell' lock-in that truncates the RLS count)

_HMM_DEFAULT_WEIGHTS = {
    # Relative (unnormalized) transition weights encoding valid biology.
    # Rows = from-state. Unlisted targets get 0.1; rows normalize to 1.
    "Mother":                {"Mother": 60, "Early Bud": 10, "Late Bud": 2,
                              "Dead Cell": 1, "No Cell": 0.5, "Out of Focus / Blurry": 2},
    "Early Bud":             {"Early Bud": 50, "Late Bud": 12, "Mother": 0.5,
                              "Dead Cell": 1, "No Cell": 0.3, "Out of Focus / Blurry": 2},
    "Late Bud":              {"Late Bud": 50, "Mother": 10, "Early Bud": 6,
                              "Dead Cell": 1, "No Cell": 0.5, "Out of Focus / Blurry": 2},
    "Dead Cell":             {"Dead Cell": 80, "Out of Focus / Blurry": 2, "No Cell": 1,
                              "Mother": 0.05, "Early Bud": 0.05, "Late Bud": 0.05},
    "No Cell":               {"No Cell": 70, "Mother": 1, "Early Bud": 0.5,
                              "Late Bud": 0.2, "Dead Cell": 0.2, "Out of Focus / Blurry": 2},
    "Out of Focus / Blurry": {"Out of Focus / Blurry": 30, "Mother": 8, "Early Bud": 8,
                              "Late Bud": 8, "Dead Cell": 4, "No Cell": 4},
}


def display_to_raw(x, y, raw_w, raw_h):
    """Convert a display-space (460x460) coordinate to raw trap-frame pixels."""
    try:
        x, y = float(x), float(y)
    except (TypeError, ValueError):
        return np.nan, np.nan
    if np.isnan(x) or np.isnan(y):
        return np.nan, np.nan
    return x * (raw_w / DISPLAY_SPACE_SIZE), y * (raw_h / DISPLAY_SPACE_SIZE)


def resolve_heatmap_anchor(coords, raw_w, raw_h):
    """Class-independent heatmap anchor in RAW pixels.
    Priority: Mother centroid -> pillar-gap point -> frame center.
    Always returns finite coordinates so every frame gets a heatmap."""
    coords = coords or {}
    mx, my = display_to_raw(coords.get("Mother_X", np.nan), coords.get("Mother_Y", np.nan), raw_w, raw_h)
    if not (np.isnan(mx) or np.isnan(my)):
        return mx, my
    p1x, p1y = display_to_raw(coords.get("Pillar_P1_X", np.nan), coords.get("Pillar_P1_Y", np.nan), raw_w, raw_h)
    p2x, p2y = display_to_raw(coords.get("Pillar_P2_X", np.nan), coords.get("Pillar_P2_Y", np.nan), raw_w, raw_h)
    if not any(np.isnan(v) for v in (p1x, p1y, p2x, p2y)):
        gap_x = min(raw_w - 1.0, (p1x + p2x) / 2.0 + GAP_SHIFT_RAW_PX)
        gap_y = (p1y + p2y) / 2.0
        return gap_x, gap_y
    return raw_w / 2.0, raw_h / 2.0


def gaussian_heatmap_uint8(width, height, cx, cy, sigma):
    x = np.arange(width, dtype=np.float32)
    y = np.arange(height, dtype=np.float32)[:, np.newaxis]
    hm = np.exp(-(((x - cx) ** 2) + ((y - cy) ** 2)) / (2.0 * sigma ** 2))
    return np.clip(hm * 255.0, 0, 255).astype(np.uint8)


def build_model_input(raw_img, coords=None, prev_img=None, next_img=None):
    """Canonical 4-channel classifier input, identical at train & inference time.
    Channels 0-2: temporal grayscale triplet [t-1, t, t+1], each independently
    percentile-normalized (motion context for bud-stage disambiguation).
    Channel 3: Gaussian anchor heatmap. Missing neighbors at sequence ends
    fall back to the current frame. coords: display-space dict."""
    def _norm_gray_128(img):
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        p_low, p_high = np.percentile(img, (0.5, 99.5))
        if p_high > p_low:
            out = np.clip((img.astype(np.float32) - p_low) * (255.0 / (p_high - p_low)), 0, 255).astype(np.uint8)
        else:
            out = img.astype(np.uint8)
        return cv2.resize(out, MODEL_IMG_SIZE)

    raw_h, raw_w = raw_img.shape[:2]
    curr = _norm_gray_128(raw_img)
    prev = _norm_gray_128(prev_img) if prev_img is not None else curr
    nxt  = _norm_gray_128(next_img) if next_img is not None else curr

    ax_raw, ay_raw = resolve_heatmap_anchor(coords, raw_w, raw_h)
    ax_model = ax_raw * (MODEL_IMG_SIZE[0] / float(raw_w))
    ay_model = ay_raw * (MODEL_IMG_SIZE[1] / float(raw_h))
    heatmap = gaussian_heatmap_uint8(MODEL_IMG_SIZE[0], MODEL_IMG_SIZE[1], ax_model, ay_model, HEATMAP_SIGMA)

    return np.dstack([prev, curr, nxt, heatmap])


def default_transition_matrix(class_names):
    """Row-stochastic transition matrix built from the biological prior above."""
    n = len(class_names)
    mat = np.full((n, n), 0.1, dtype=np.float64)
    for i, src in enumerate(class_names):
        row = _HMM_DEFAULT_WEIGHTS.get(src)
        if row is None:
            mat[i, :] = 1.0
        else:
            for j, dst in enumerate(class_names):
                mat[i, j] = row.get(dst, 0.1)
    mat /= mat.sum(axis=1, keepdims=True)
    return mat


def regularize_transition_matrix(mat):
    """Prevents absorbing states in Viterbi decoding. Empirical matrices make
    'Dead Cell' near-absorbing (humans never annotate Dead -> living), so a
    single premature entry into Dead would truncate all later divisions.
    Caps self-transitions at HMM_MAX_SELF_TRANSITION (redistributing the
    excess proportionally) and floors every transition at HMM_MIN_TRANSITION."""
    m = np.asarray(mat, dtype=np.float64).copy()
    n = m.shape[0]
    m /= m.sum(axis=1, keepdims=True)
    for i in range(n):
        if m[i, i] > HMM_MAX_SELF_TRANSITION:
            excess = m[i, i] - HMM_MAX_SELF_TRANSITION
            m[i, i] = HMM_MAX_SELF_TRANSITION
            off = [j for j in range(n) if j != i]
            off_sum = m[i, off].sum()
            for j in off:
                m[i, j] += excess * (m[i, j] / off_sum) if off_sum > 0 else excess / (n - 1)
        m[i] = np.maximum(m[i], HMM_MIN_TRANSITION)
        m[i] /= m[i].sum()
    return m


def load_transition_matrix(class_names, path=HMM_TRANSITIONS_PATH):
    """Prefer the empirical matrix written by train_classifier.py; fall back to
    the biological prior if missing or class ordering mismatches. Always
    returns an anti-absorption regularized matrix."""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if list(data.get("class_names", [])) == list(class_names):
                mat = np.asarray(data["matrix"], dtype=np.float64)
                if mat.shape == (len(class_names), len(class_names)):
                    print(f"--> Loaded empirical HMM transition matrix from {path}")
                    return regularize_transition_matrix(mat)
            print(f"--> Warning: {path} class ordering mismatch; using default transitions.")
        except Exception as e:
            print(f"--> Warning: could not read {path} ({e}); using default transitions.")
    return regularize_transition_matrix(default_transition_matrix(class_names))


def viterbi_smooth(prob_seq, transition_matrix):
    """Viterbi decoding of per-frame class probabilities under the transition
    prior. Removes single-frame flicker (e.g. Mother -> Late Bud -> Mother)
    that inflates RLS counts. Returns the smoothed state index path."""
    probs = np.asarray(prob_seq, dtype=np.float64)
    if probs.ndim != 2 or probs.shape[0] == 0:
        return []
    T, C = probs.shape
    log_em = np.log(probs + 1e-12)
    log_tr = np.log(np.asarray(transition_matrix, dtype=np.float64) + 1e-12)

    delta = np.zeros((T, C), dtype=np.float64)
    psi = np.zeros((T, C), dtype=np.int32)
    delta[0] = log_em[0]  # uniform initial prior
    for t in range(1, T):
        scores = delta[t - 1][:, np.newaxis] + log_tr
        psi[t] = np.argmax(scores, axis=0)
        delta[t] = scores[psi[t], np.arange(C)] + log_em[t]

    path = np.zeros(T, dtype=np.int32)
    path[-1] = int(np.argmax(delta[-1]))
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]
    return path.tolist()
# ============================ END CANONICAL BLOCK =============================


# ==============================================================================
# CLASSIFIER INFERENCE ENGINE (4-CHANNEL COMPATIBLE)
# ==============================================================================
def load_keras_classifier(model_path):
    global CLASS_LABELS
    if os.path.exists(CLASS_LABELS_PATH):
        try:
            with open(CLASS_LABELS_PATH, "r") as f:
                CLASS_LABELS = json.load(f)
            print(f"--> Loaded class label ordering from JSON: {CLASS_LABELS}")
        except Exception as e:
            print(f"--> Warning: Could not read {CLASS_LABELS_PATH}: {e}")

    if os.path.exists(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            print(f"--> Successfully loaded Keras classifier: '{model_path}'")
            return model
        except Exception as e:
            print(f"--> Warning: Failed to load '{model_path}': {e}")
    else:
        print(f"--> Warning: Model file '{model_path}' not found. UI running without predictions.")
    return None


def load_rls_detector(model_path=RLS_DETECTOR_PATH, meta_path=RLS_DETECTOR_META_PATH):
    """Loads the calibrated direct division-event detector exported by
    train_classifier.py, plus its decoding parameters. Both files must exist;
    otherwise the UI keeps showing the state-argmax RLS line only."""
    if not (os.path.exists(model_path) and os.path.exists(meta_path)):
        print(f"--> RLS detector not deployed ('{model_path}'): showing state-argmax RLS only.")
        return None, None
    try:
        detector = tf.keras.models.load_model(model_path, compile=False)
        with open(meta_path, "r") as f:
            meta = json.load(f)
        div_cfg = meta.get("division_decoder", {})
        dead_cfg = meta.get("death_decoder", {})
        if ("threshold" not in div_cfg or "min_gap" not in div_cfg
                or "threshold" not in dead_cfg or "persistence" not in dead_cfg):
            print(f"--> Warning: '{meta_path}' missing decoder parameters; detector disabled.")
            return None, None
        esc_cfg = meta.get("escape_decoder", {})
        esc_note = ""
        if isinstance(esc_cfg, dict) and "threshold" in esc_cfg and "persistence" in esc_cfg:
            esc_note = (f" | esc_thr={esc_cfg['threshold']:.2f},"
                        f" epersist={esc_cfg['persistence']}")
        print(f"--> Loaded calibrated RLS detector: '{model_path}' "
              f"(div_thr={div_cfg['threshold']:.2f}, gap={div_cfg['min_gap']} | "
              f"dead_thr={dead_cfg['threshold']:.2f}, persist={dead_cfg['persistence']}"
              f"{esc_note})")
        return detector, meta
    except Exception as e:
        print(f"--> Warning: Failed to load RLS detector: {e}")
        return None, None


def pick_division_events(prob_seq, threshold, min_gap):
    """Ported VERBATIM from train_classifier.py: local maxima + nonmaximum
    suppression; returns one pulse (frame index) per detected division."""
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
    """Ported VERBATIM from train_classifier.py: death is called at the first
    run of `persistence` consecutive frames at/above `threshold`."""
    run = 0
    for i, v in enumerate(prob_seq):
        if v >= threshold:
            run += 1
            if run >= persistence:
                return True, i - persistence + 1
        else:
            run = 0
    return False, None


def detector_predict_trap(detector, detector_meta, proc_stack):
    """Runs the direct division/death/escape detector over the SAME preprocessed
    input stack already built for the state classifier, then decodes it with
    the calibrated parameters from rls_detector_meta.json. Escape censors the
    trap exactly like the human 'Mother Escaped (Ignore Rest)' rule: divisions
    at/after the escape frame are discarded and death is invalidated. Handles
    both the legacy 2-output detector and the 3-output escape-aware one."""
    if detector is None or detector_meta is None or proc_stack is None or len(proc_stack) == 0:
        return None
    try:
        outs = detector.predict(proc_stack, verbose=0)
        if not isinstance(outs, (list, tuple)):
            outs = [outs]
        div_logits, dead_logits = outs[0], outs[1]
        esc_logits = outs[2] if len(outs) >= 3 else None
        div_p = tf.math.sigmoid(div_logits).numpy().ravel()
        dead_p = tf.math.sigmoid(dead_logits).numpy().ravel()
        div_cfg = detector_meta["division_decoder"]
        dead_cfg = detector_meta["death_decoder"]
        esc_cfg = detector_meta.get("escape_decoder")
        events = pick_division_events(div_p, div_cfg["threshold"], div_cfg["min_gap"])
        died, death_frame = sustained_death(dead_p, dead_cfg["threshold"], dead_cfg["persistence"])
        escaped, escape_frame = False, None
        esc_p = None
        if (esc_logits is not None and isinstance(esc_cfg, dict)
                and "threshold" in esc_cfg and "persistence" in esc_cfg):
            esc_p = tf.math.sigmoid(esc_logits).numpy().ravel()
            escaped, escape_frame = sustained_death(
                esc_p, esc_cfg["threshold"], esc_cfg["persistence"])
        if escaped:
            events = [e for e in events if e < escape_frame]
            if death_frame is None or death_frame >= escape_frame:
                died, death_frame = False, None
        return {
            "rls_count": int(len(events)),
            "division_frames": [int(i) for i in events],
            "died_on_chip": bool(died),
            "death_frame": (int(death_frame) if death_frame is not None else None),
            "escaped": bool(escaped),
            "escape_frame": (int(escape_frame) if escape_frame is not None else None),
            "division_probs": div_p,
            "dead_probs": dead_p,
            "escape_probs": esc_p,
        }
    except Exception as e:
        print(f"Detector prediction error: {e}")
        return None

def preprocess_frame_for_ai(raw_img, coords=None, prev_img=None, next_img=None):
    """Thin wrapper over the canonical input builder (kept for name stability).
    coords is the display-space tracking dict for the frame (or None)."""
    return build_model_input(raw_img, coords=coords, prev_img=prev_img, next_img=next_img)


def batch_predict_trap(model, stack, tracking_cache=None, transitions=None, temperature=None,
                       use_triplet=True):
    """Runs the frame classifier on a raw trap stack and Viterbi-smooths the
    per-frame probabilities with the transition prior so the on-screen
    'Classifier Counted Trap RLS' reflects the deployed (smoothed) pipeline.
    Returns (labels, probabilities, pred_indices, proc_stack); proc_stack is
    the built model-input array, reused by the calibrated RLS detector."""
    if model is None or len(stack) == 0:
        return [], [], [], None

    try:
        proc_frames = []
        for idx, img in enumerate(stack):
            coords = tracking_cache.get(idx) if tracking_cache else None
            prev_img = stack[idx - 1] if (use_triplet and idx > 0) else None
            next_img = stack[idx + 1] if (use_triplet and idx < len(stack) - 1) else None
            proc_frames.append(preprocess_frame_for_ai(img, coords=coords,
                                                       prev_img=prev_img, next_img=next_img))

        proc_stack = np.array(proc_frames, dtype=np.float32)
        logits = model.predict(proc_stack, verbose=0)
        probabilities = tf.nn.softmax(logits).numpy()
        temp = VITERBI_TEMPERATURE if temperature is None else float(temperature)

        if (temp > 0 and transitions is not None and CLASS_LABELS
                and probabilities.shape[1] == len(CLASS_LABELS)):
            smooth_probs = tf.nn.softmax(logits / temp).numpy()
            pred_indices = viterbi_smooth(smooth_probs, transitions)
        else:
            pred_indices = np.argmax(probabilities, axis=1).tolist()

        predicted_labels = [
            CLASS_LABELS[idx] if (CLASS_LABELS and idx < len(CLASS_LABELS)) else f"Class {idx}"
            for idx in pred_indices
        ]
        return predicted_labels, probabilities, pred_indices, proc_stack
    except Exception as e:
        print(f"Batch prediction error: {e}")
        return [], [], [], None


# ==============================================================================
# CANONICAL RLS & FEATURE EXTRACTION ENGINE
# ==============================================================================
def find_division_frames(frame_labels):
    """Frame indices at which a completed division is registered.
    A division = Late Bud -> (Mother | Early Bud), optionally across a run of
    'No Cell' or 'Out of Focus / Blurry' frames: both are treated as missing
    observations that do not break the transition. NOTE: a long gap can hide
    additional divisions, which are inherently uncountable.
    !! KEEP IDENTICAL to the copies in train_classifier.py / train_oracle_only.py !!"""
    GAP_STATES = ("No Cell", "Out of Focus / Blurry")
    div_frames = []
    for i in range(1, len(frame_labels)):
        curr = frame_labels[i]
        if curr is None:
            continue
        prev = frame_labels[i - 1]
        if prev is None:
            continue

        if prev == "Late Bud" and curr in ("Mother", "Early Bud"):
            div_frames.append(i)
        elif curr in ("Mother", "Early Bud"):
            lookback_idx = i - 1
            while lookback_idx >= 0 and frame_labels[lookback_idx] in GAP_STATES:
                lookback_idx -= 1
            if 0 <= lookback_idx < i - 1 and frame_labels[lookback_idx] in ("Early Bud", "Late Bud"):
                div_frames.append(i)
    return div_frames


def calculate_trap_rls(frame_labels):
    """Trap-level RLS metrics. CENSORING POLICY: blurry frames do NOT censor
    the trap (every trap has some) -- blur only invalidates that frame's
    spatial data. Only 'Mother Escaped' and 'Skipped / Bad Trap' censor.
    Death detection bridges blurry/unlabeled runs (living -> [blur...] -> Dead
    still counts as an observed on-chip death)."""
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

    is_censored = False
    censor_reasons = []
    max_check_idx = death_frame_idx if (died_on_chip and death_frame_idx is not None) else len(frame_labels) - 1

    for i in range(max_check_idx + 1):
        curr = frame_labels[i]
        if curr is None:
            continue

        if curr == "Mother Escaped (Ignore Rest)":
            is_censored = True
            if "Mother Escaped" not in censor_reasons:
                censor_reasons.append("Mother Escaped")
        elif curr == "Skipped / Bad Trap":
            is_censored = True
            if "Skipped Trap" not in censor_reasons:
                censor_reasons.append("Skipped Trap")

    return {
        "rls_count": rls_count,
        "is_censored": is_censored,
        "censor_reasons": censor_reasons,
        "died_on_chip": died_on_chip,
        "death_frame": death_frame_idx
    }


def extract_prefix_features(frame_labels):
    """Oracle feature vector (v2). Division/IDI features come from the shared
    find_division_frames() so they can never diverge from the RLS counter.
    !! KEEP IDENTICAL to the copy in train_oracle_only.py !!"""
    n_obs = len(frame_labels)
    if n_obs == 0:
        return np.zeros(len(ORACLE_FEATURE_NAMES), dtype=np.float32)

    rls_data = calculate_trap_rls(frame_labels)
    curr_rls = float(rls_data["rls_count"])

    c_mother = sum(1 for x in frame_labels if x == "Mother")
    c_early  = sum(1 for x in frame_labels if x == "Early Bud")
    c_late   = sum(1 for x in frame_labels if x == "Late Bud")
    c_nocell = sum(1 for x in frame_labels if x == "No Cell")
    c_blur   = sum(1 for x in frame_labels if x == "Out of Focus / Blurry")
    c_dead   = sum(1 for x in frame_labels if x == "Dead Cell")

    frac_mother = c_mother / n_obs
    frac_early  = c_early / n_obs
    frac_late   = c_late / n_obs
    frac_nocell = c_nocell / n_obs
    frac_blur   = c_blur / n_obs
    frac_dead   = c_dead / n_obs

    curr_label = frame_labels[-1]
    is_curr_mother = 1.0 if curr_label == "Mother" else 0.0
    is_curr_early  = 1.0 if curr_label == "Early Bud" else 0.0
    is_curr_late   = 1.0 if curr_label == "Late Bud" else 0.0
    is_curr_nocell = 1.0 if curr_label == "No Cell" else 0.0
    is_curr_blur   = 1.0 if curr_label == "Out of Focus / Blurry" else 0.0
    is_curr_dead   = 1.0 if curr_label == "Dead Cell" else 0.0

    div_frames = find_division_frames(frame_labels)

    k_divs = len(div_frames)
    if k_divs >= 2:
        idis = [div_frames[j] - div_frames[j - 1] for j in range(1, k_divs)]
    elif k_divs == 1:
        idis = [div_frames[0]]
    else:
        idis = []

    mean_idi = float(np.mean(idis)) if len(idis) > 0 else 0.0
    std_idi  = float(np.std(idis)) if len(idis) > 1 else 0.0
    recent_idi = float(idis[-1]) if len(idis) > 0 else 0.0
    recent_3_mean = float(np.mean(idis[-3:])) if len(idis) > 0 else 0.0

    if len(idis) >= 3:
        try:
            idi_slope = float(np.polyfit(range(len(idis)), idis, 1)[0])
        except Exception:
            idi_slope = 0.0
    else:
        idi_slope = 0.0

    idi_cv = (std_idi / (mean_idi + 1e-5)) if len(idis) > 1 else 0.0

    return np.array([
        curr_rls, float(n_obs),
        frac_mother, frac_early, frac_late, frac_nocell, frac_blur, frac_dead,
        is_curr_mother, is_curr_early, is_curr_late, is_curr_nocell, is_curr_blur, is_curr_dead,
        mean_idi, std_idi, recent_idi, recent_3_mean, idi_slope, idi_cv
    ], dtype=np.float32)


# ==============================================================================
# PROSPECTIVE LIFESPAN QUANTILE ORACLE
# ==============================================================================
@tf.keras.utils.register_keras_serializable(package="Custom")
def pinball_loss_multi(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_true = tf.reshape(y_true, (-1, 1))  # Force shape to (batch, 1) for broadcasting
    err = y_true - y_pred
    q = tf.constant([[0.1, 0.5, 0.9]], dtype=tf.float32)
    loss = tf.maximum(q * err, (q - 1.0) * err)
    return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))


class RemainingRLSOracle:
    def __init__(self, model_path=ORACLE_MODEL_PATH, meta_path=ORACLE_META_PATH):
        self.model = None
        self.metadata = {}
        self.is_loaded = False
        
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                print(f"--> Loaded Oracle metadata from {meta_path}")
            except Exception as e:
                print(f"--> Warning: Could not read Oracle metadata: {e}")

        meta_version = self.metadata.get("feature_version", 1)
        meta_means = self.metadata.get("feature_means", [])
        version_ok = (meta_version == ORACLE_FEATURE_VERSION
                      and len(meta_means) == len(ORACLE_FEATURE_NAMES))

        if os.path.exists(model_path) and not version_ok:
            print(f"--> Warning: Oracle metadata is feature-version {meta_version} "
                  f"({len(meta_means)} features) but this UI expects version "
                  f"{ORACLE_FEATURE_VERSION} ({len(ORACLE_FEATURE_NAMES)} features). "
                  f"Oracle DISABLED - retrain with train_oracle_only.py.")
        elif os.path.exists(model_path):
            try:
                self.model = tf.keras.models.load_model(
                    model_path, 
                    custom_objects={"pinball_loss_multi": pinball_loss_multi}, 
                    compile=False
                )
                self.is_loaded = True
                print(f"--> Successfully loaded Prospective Lifespan Oracle: '{model_path}'")
            except Exception as e:
                print(f"--> Warning: Failed to load Oracle model '{model_path}': {e}")
        else:
            print(f"--> Info: Oracle model '{model_path}' not found. Overlay will report inactive status.")

    def predict_remaining(self, prefix_labels):
        if len(prefix_labels) == 0 or not self.is_loaded:
            return 0.0, 0.0, 0.0, 0.0

        try:
            past_metrics = calculate_trap_rls(prefix_labels)
            last_state = prefix_labels[-1]

            if past_metrics["died_on_chip"] or last_state in ("Dead Cell", "Mother Escaped (Ignore Rest)", "Skipped / Bad Trap"):
                return 0.0, 0.0, 0.0, 0.0

            feat = extract_prefix_features(prefix_labels)
            means = np.array(self.metadata.get("feature_means", np.zeros_like(feat)), dtype=np.float32)
            stds = np.array(self.metadata.get("feature_stds", np.ones_like(feat)), dtype=np.float32)
            stds[stds < 1e-6] = 1.0

            feat_norm = (feat - means) / stds
            preds = self.model.predict(feat_norm.reshape(1, -1), verbose=0)[0]

            q10 = max(0.0, float(preds[0]))
            q50 = max(q10, float(preds[1]))
            q90 = max(q50, float(preds[2]))
            
            half_range = (q90 - q10) / 2.0
            return q50, half_range, q10, q90
        except Exception:
            return 0.0, 0.0, 0.0, 0.0


def calculate_prefix_prospective_rls(prefix_labels, oracle_predictor):
    try:
        past_metrics = calculate_trap_rls(prefix_labels)
        current_age = past_metrics["rls_count"]
        
        q50, half_range, q10, q90 = oracle_predictor.predict_remaining(prefix_labels)
        projected_total = current_age + q50

        return {
            "current_age": current_age,
            "remaining_rls_median": q50,
            "remaining_rls_half_range": half_range,
            "q10": q10,
            "q90": q90,
            "projected_total_rls": projected_total,
            "is_censored": past_metrics["is_censored"],
            "died_on_chip": past_metrics["died_on_chip"],
            "oracle_active": oracle_predictor.is_loaded
        }
    except Exception:
        return {
            "current_age": 0, "remaining_rls_median": 0.0, "remaining_rls_half_range": 0.0,
            "q10": 0.0, "q90": 0.0, "projected_total_rls": 0.0, "is_censored": False,
            "died_on_chip": False, "oracle_active": False
        }


# ==============================================================================
# COMPUTER VISION RIGID STAGE TRACKER & SPATIAL INTERACTION
# ==============================================================================
def normalize_to_uint8(img):
    if img is None or img.size == 0:
        return np.zeros((460, 460), dtype=np.uint8)
    
    img_resized = cv2.resize(img, (460, 460))
    img_f = img_resized.astype(np.float32)
    p_low, p_high = np.percentile(img_f, (0.5, 99.5))
    
    if p_high > p_low:
        img_norm = np.clip((img_f - p_low) * (255.0 / (p_high - p_low)), 0, 255)
    else:
        img_norm = np.zeros_like(img_f)
        
    return img_norm.astype(np.uint8)


def auto_track_entire_stack(stack_uint8, ref_frame_idx, initial_clicks):
    num_frames = len(stack_uint8)
    if len(initial_clicks) < 2 or num_frames == 0:
        return {}

    p1_init, p2_init = initial_clicks[0], initial_clicks[1]
    has_mother = len(initial_clicks) >= 3 and initial_clicks[2] is not None and not any(np.isnan(initial_clicks[2]))
    m_init = initial_clicks[2] if has_mother else (np.nan, np.nan)
    
    w, h = 460, 460

    px1 = min(p1_init[0], p2_init[0])
    px2 = max(p1_init[0], p2_init[0])
    py1 = min(p1_init[1], p2_init[1])
    py2 = max(p1_init[1], p2_init[1])

    pad_x, pad_y = 20, 15
    t_x1 = max(0, int(round(px1 - pad_x)))
    t_x2 = min(w, int(round(px2 + pad_x)))
    t_y1 = max(0, int(round(py1 - pad_y)))
    t_y2 = min(h, int(round(py2 + pad_y)))

    if (t_x2 - t_x1) < 20:
        t_x1 = max(0, t_x1 - 10)
        t_x2 = min(w, t_x2 + 10)
    if (t_y2 - t_y1) < 20:
        t_y1 = max(0, t_y1 - 10)
        t_y2 = min(h, t_y2 + 10)

    ref_img = stack_uint8[ref_frame_idx]
    ref_template = ref_img[t_y1:t_y2, t_x1:t_x2]

    tracked_coords = {}
    tracked_coords[ref_frame_idx] = {
        "Pillar_P1_X": float(p1_init[0]), "Pillar_P1_Y": float(p1_init[1]),
        "Pillar_P2_X": float(p2_init[0]), "Pillar_P2_Y": float(p2_init[1]),
        "Mother_X":    float(m_init[0]) if has_mother else np.nan, 
        "Mother_Y":    float(m_init[1]) if has_mother else np.nan
    }

    if ref_template.size == 0 or ref_template.shape[0] < 5 or ref_template.shape[1] < 5:
        for f in range(num_frames):
            tracked_coords[f] = tracked_coords[ref_frame_idx]
        return tracked_coords

    search_pad = 35

    # 1. Forward Tracking
    curr_t_x1, curr_t_y1 = t_x1, t_y1
    prev_p1, prev_p2, prev_m = p1_init, p2_init, m_init

    for f in range(ref_frame_idx + 1, num_frames):
        curr_img = stack_uint8[f]
        sx1 = max(0, curr_t_x1 - search_pad)
        sy1 = max(0, curr_t_y1 - search_pad)
        sx2 = min(w, curr_t_x1 + ref_template.shape[1] + search_pad)
        sy2 = min(h, curr_t_y1 + ref_template.shape[0] + search_pad)

        search_region = curr_img[sy1:sy2, sx1:sx2]
        if search_region.shape[0] >= ref_template.shape[0] and search_region.shape[1] >= ref_template.shape[1]:
            res = cv2.matchTemplate(search_region, ref_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.3:
                matched_x = sx1 + max_loc[0]
                matched_y = sy1 + max_loc[1]
                dx = matched_x - curr_t_x1
                dy = matched_y - curr_t_y1
                curr_t_x1, curr_t_y1 = matched_x, matched_y
            else:
                dx, dy = 0, 0
        else:
            dx, dy = 0, 0

        curr_p1 = (prev_p1[0] + dx, prev_p1[1] + dy)
        curr_p2 = (prev_p2[0] + dx, prev_p2[1] + dy)
        curr_m  = (prev_m[0] + dx,  prev_m[1] + dy) if has_mother else (np.nan, np.nan)

        tracked_coords[f] = {
            "Pillar_P1_X": float(curr_p1[0]), "Pillar_P1_Y": float(curr_p1[1]),
            "Pillar_P2_X": float(curr_p2[0]), "Pillar_P2_Y": float(curr_p2[1]),
            "Mother_X":    float(curr_m[0]) if has_mother else np.nan,  
            "Mother_Y":    float(curr_m[1]) if has_mother else np.nan
        }
        prev_p1, prev_p2, prev_m = curr_p1, curr_p2, curr_m

    # 2. Backward Tracking
    curr_t_x1, curr_t_y1 = t_x1, t_y1
    prev_p1, prev_p2, prev_m = p1_init, p2_init, m_init

    for f in range(ref_frame_idx - 1, -1, -1):
        curr_img = stack_uint8[f]
        sx1 = max(0, curr_t_x1 - search_pad)
        sy1 = max(0, curr_t_y1 - search_pad)
        sx2 = min(w, curr_t_x1 + ref_template.shape[1] + search_pad)
        sy2 = min(h, curr_t_y1 + ref_template.shape[0] + search_pad)

        search_region = curr_img[sy1:sy2, sx1:sx2]
        if search_region.shape[0] >= ref_template.shape[0] and search_region.shape[1] >= ref_template.shape[1]:
            res = cv2.matchTemplate(search_region, ref_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.3:
                matched_x = sx1 + max_loc[0]
                matched_y = sy1 + max_loc[1]
                dx = matched_x - curr_t_x1
                dy = matched_y - curr_t_y1
                curr_t_x1, curr_t_y1 = matched_x, matched_y
            else:
                dx, dy = 0, 0
        else:
            dx, dy = 0, 0

        curr_p1 = (prev_p1[0] + dx, prev_p1[1] + dy)
        curr_p2 = (prev_p2[0] + dx, prev_p2[1] + dy)
        curr_m  = (prev_m[0] + dx,  prev_m[1] + dy) if has_mother else (np.nan, np.nan)

        tracked_coords[f] = {
            "Pillar_P1_X": float(curr_p1[0]), "Pillar_P1_Y": float(curr_p1[1]),
            "Pillar_P2_X": float(curr_p2[0]), "Pillar_P2_Y": float(curr_p2[1]),
            "Mother_X":    float(curr_m[0]) if has_mother else np.nan,  
            "Mother_Y":    float(curr_m[1]) if has_mother else np.nan
        }
        prev_p1, prev_p2, prev_m = curr_p1, curr_p2, curr_m

    return tracked_coords


def handle_mouse_clicks(event, x, y, flags, param):
    """Records clicks in UNZOOMED 460x460 display space. `param` is the shared
    ui_state dict carrying the live zoom factor, so clicks placed while zoomed
    are inverse-transformed back to the canonical display space that tracking
    and the Excel database use."""
    global SPATIAL_CLICKS
    if event == cv2.EVENT_LBUTTONDOWN:
        if 20 <= x <= 480 and 65 <= y <= 525:
            zoom = 1.0
            if isinstance(param, dict):
                zoom = float(param.get("zoom", 1.0)) or 1.0

            panel_x, panel_y = x - 20, y - 65
            if zoom > 1.0:
                cx, cy = 230.0, 230.0
                norm_x = (panel_x - cx) / zoom + cx
                norm_y = (panel_y - cy) / zoom + cy
            else:
                norm_x, norm_y = float(panel_x), float(panel_y)

            norm_x = min(459.0, max(0.0, norm_x))
            norm_y = min(459.0, max(0.0, norm_y))

            if len(SPATIAL_CLICKS) < 3:
                SPATIAL_CLICKS.append((int(round(norm_x)), int(round(norm_y))))


def apply_dynamic_mask_overlay(canvas, overlay_clicks, zoom_factor=1.0):
    try:
        def transform_pt(pt_x, pt_y):
            if zoom_factor > 1.0:
                cx, cy = 230, 230
                disp_x = int(round((pt_x - cx) * zoom_factor + cx + 20))
                disp_y = int(round((pt_y - cy) * zoom_factor + cy + 65))
            else:
                disp_x = int(round(pt_x + 20))
                disp_y = int(round(pt_y + 65))
            return disp_x, disp_y

        if len(overlay_clicks) >= 1:
            p1 = transform_pt(overlay_clicks[0][0], overlay_clicks[0][1])
            if 20 <= p1[0] <= 480 and 65 <= p1[1] <= 525:
                cv2.circle(canvas, p1, 4, (0, 255, 255), -1)

        if len(overlay_clicks) >= 2:
            p1 = transform_pt(overlay_clicks[0][0], overlay_clicks[0][1])
            p2 = transform_pt(overlay_clicks[1][0], overlay_clicks[1][1])
            if 20 <= p1[0] <= 480 and 65 <= p1[1] <= 525:
                cv2.circle(canvas, p2, 4, (0, 255, 255), -1)
                cv2.line(canvas, p1, p2, (0, 255, 255), 2)

        if len(overlay_clicks) == 3:
            m = transform_pt(overlay_clicks[2][0], overlay_clicks[2][1])
            if 20 <= m[0] <= 480 and 65 <= m[1] <= 525:
                cv2.circle(canvas, m, int(18 * zoom_factor), (0, 255, 0), 2)
                cv2.circle(canvas, m, 3, (0, 255, 0), -1)
                cv2.putText(canvas, "Mother (Tracked)", (m[0] + 8, m[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    except Exception:
        pass


# ==============================================================================
# DATA PERSISTENCE & POSITION FILTERING
# ==============================================================================
def load_master_annotations():
    """Loads only frames carrying a real human class label. Rows without a
    Class are skipped entirely (tracking coordinates for unlabeled frames are
    regenerated on the fly), so no phantom records enter the session.
    Blurry frames keep their label but their coordinate data is nulled (blur
    censors that frame's spatial data only, never the whole trap); Mother
    coords stay NaN for No Cell / Skipped by semantics."""
    annotation_dict = {}
    skipped_unlabeled = 0
    if os.path.exists(MASTER_EXCEL_PATH):
        try:
            excel_file = pd.ExcelFile(MASTER_EXCEL_PATH)
            sheet_name = "Frame_Annotations" if "Frame_Annotations" in excel_file.sheet_names else 0
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Rolling session-start backup: the master file now carries EVERY
            # chip's annotations, so a known-good snapshot is kept before this
            # session writes anything back.
            try:
                backup_path = os.path.join(OUTDIR, "master_human_annotations.session_backup.xlsx")
                shutil.copy2(MASTER_EXCEL_PATH, backup_path)
                print(f"--> Session-start backup written: {backup_path}")
            except Exception as backup_err:
                print(f"--> Warning: could not write session-start backup ({backup_err}).")
            
            for _, row in df.iterrows():
                cls_raw = row.get("Class")
                cls_str = str(cls_raw).strip() if pd.notna(cls_raw) else None
                if not cls_str or cls_str.lower() == "nan":
                    skipped_unlabeled += 1
                    continue

                chip = str(row.get("Chip_ID", "JM135_CR_Mud1")).strip()
                pos = str(row.get("Position", "Pos18")).strip()
                trap = int(row["Trap_ID"])
                frame = int(row["Frame"])
                
                is_blurry = (cls_str == "Out of Focus / Blurry")
                is_no_cell = (cls_str in ["No Cell", "Skipped / Bad Trap"])
                key = (chip, pos, trap, frame)
                
                annotation_dict[key] = {
                    "Class": cls_str,
                    "Pillar_P1_X": np.nan if is_blurry else row.get("Pillar_P1_X", np.nan),
                    "Pillar_P1_Y": np.nan if is_blurry else row.get("Pillar_P1_Y", np.nan),
                    "Pillar_P2_X": np.nan if is_blurry else row.get("Pillar_P2_X", np.nan),
                    "Pillar_P2_Y": np.nan if is_blurry else row.get("Pillar_P2_Y", np.nan),
                    "Mother_X":    np.nan if (is_blurry or is_no_cell) else row.get("Mother_X", np.nan),
                    "Mother_Y":    np.nan if (is_blurry or is_no_cell) else row.get("Mother_Y", np.nan)
                }
            print(f"--> Loaded {len(annotation_dict)} labeled frame records from Master Database."
                  + (f" (Skipped {skipped_unlabeled} unlabeled rows.)" if skipped_unlabeled else ""))
        except Exception as e:
            # HARD STOP: the master database EXISTS but could not be read. The
            # old fallback ("start fresh") meant the very next save would have
            # overwritten every previously annotated chip with only this
            # session's records. With multiple chips sharing one Excel file
            # that is unrecoverable loss, so the UI refuses to continue.
            raise SystemExit(
                f"\n[!] FATAL: {MASTER_EXCEL_PATH} exists but could not be read ({e}).\n"
                f"    Refusing to start an empty session: the next save would overwrite\n"
                f"    ALL existing annotations (every chip) with only this session's data.\n"
                f"    Close/repair the file (or restore master_human_annotations.session_backup.xlsx)\n"
                f"    and run again."
            )
    return annotation_dict


def get_record_label(rec):
    """Returns the human class label of an in-memory record, or None if the
    record only carries tracking coordinates (never counts as annotated)."""
    if rec is None:
        return None
    if isinstance(rec, dict):
        lbl = rec.get("Class", None)
    else:
        lbl = str(rec)
    if lbl is None:
        return None
    lbl = str(lbl).strip()
    return lbl if lbl and lbl.lower() != "nan" else None


def save_master_annotations(annotation_dict):
    """Writes ONLY frames a human actually labeled. Records that exist purely
    to carry tracking coordinates (Class is None) are NOT written - this is
    the fix for the phantom-'Mother' bug where unlabeled tracked frames were
    silently saved as ground truth."""
    try:
        records = []
        trap_groups = {}

        for (chip_id, position, trap_id, frame_idx), data in sorted(annotation_dict.items()):
            cls_val = get_record_label(data)
            if cls_val is None:
                continue  # unlabeled tracking-only record: never persisted as ground truth

            rec = {
                "Chip_ID": chip_id,
                "Position": position,
                "Trap_ID": trap_id,
                "Frame": frame_idx,
                "Class": cls_val
            }
            
            is_blurry = (cls_val == "Out of Focus / Blurry")
            is_no_cell = (cls_val in ["No Cell", "Skipped / Bad Trap"])
            
            if isinstance(data, dict) and not is_blurry:
                for spat_key in SPATIAL_KEYS:
                    if spat_key in data:
                        if is_no_cell and spat_key in ["Mother_X", "Mother_Y"]:
                            rec[spat_key] = np.nan
                        else:
                            rec[spat_key] = data[spat_key]
            else:
                for spat_key in SPATIAL_KEYS:
                    rec[spat_key] = np.nan

            records.append(rec)
            trap_key = (chip_id, position, trap_id)
            if trap_key not in trap_groups:
                trap_groups[trap_key] = {}
            trap_groups[trap_key][frame_idx] = rec["Class"]

        df_frames = pd.DataFrame(records)

        summary_records = []
        for (chip_id, position, trap_id), frames in sorted(trap_groups.items()):
            sorted_frames = [frames[f] for f in sorted(frames.keys())]
            rls_data = calculate_trap_rls(sorted_frames)

            summary_records.append({
                "Chip_ID": chip_id,
                "Position": position,
                "Trap_ID": trap_id,
                "Observed_RLS": rls_data["rls_count"],
                "Is_Censored": rls_data["is_censored"],
                "Censor_Reasons": ", ".join(rls_data["censor_reasons"]) if rls_data["censor_reasons"] else "None",
                "Died_On_Chip": rls_data["died_on_chip"],
                "Death_Frame": rls_data["death_frame"] + 1 if rls_data["death_frame"] is not None else "N/A",
                "Total_Annotated_Frames": len(sorted_frames)
            })

        df_summary = pd.DataFrame(summary_records)

        with pd.ExcelWriter(MASTER_EXCEL_PATH, engine='openpyxl') as writer:
            df_frames.to_excel(writer, sheet_name="Frame_Annotations", index=False)
            df_summary.to_excel(writer, sheet_name="Trap_RLS_Summary", index=False)
    except PermissionError:
        print("\n[!] WARNING: Could not save to Excel because master_human_annotations.xlsx is open! Close it to save.\n")
    except Exception as e:
        print(f"\n[!] WARNING: Excel save failed ({e}). Continuing script...\n")


def fetch_position_traps(traps_dir, position):
    pos_clean = position.strip().lower()
    search_patterns = [
        os.path.join(traps_dir, "*.tif"),
        os.path.join(traps_dir, "**", "*.tif")
    ]
    
    all_files = []
    for pat in search_patterns:
        all_files.extend(glob.glob(pat, recursive=True))
    all_files = sorted(list(set(all_files)))

    if not all_files:
        print(f"\n[!] ERROR: Directory is empty or contains no TIFF traps:\n    {traps_dir}\n")
        return []

    # Strict boundary-aware position pattern matching to prevent Pos1 matching Pos10..Pos19
    if pos_clean.isdigit():
        pos_pattern = re.compile(rf'(?:pos_?|\b){pos_clean}(?!\d)', re.IGNORECASE)
    else:
        pos_pattern = re.compile(rf'\b{re.escape(pos_clean)}(?!\d)', re.IGNORECASE)

    matched_files = [f for f in all_files if pos_pattern.search(os.path.relpath(f, traps_dir))]

    if not matched_files:
        rel_files = [os.path.relpath(f, traps_dir) for f in all_files]
        detected_positions = set(re.findall(r'pos_?\d+', " ".join(rel_files), re.IGNORECASE))
        print("\n" + "!" * 75)
        print(f"[!] ERROR: Extracted traps for '{position}' were NOT found in:\n    {traps_dir}")
        if detected_positions:
            print(f"\n    Available positions detected: {', '.join(sorted(detected_positions))}")
        print("!" * 75 + "\n")
        return []

    valid_traps = []
    for f in matched_files:
        match = re.search(r'trap_?(\d+)\.tif', f, re.IGNORECASE)
        if match:
            trap_id = int(match.group(1))
            valid_traps.append((trap_id, f))

    valid_traps.sort(key=lambda x: x[0])
    return [f for _, f in valid_traps]


def get_trap_status(chip_id, position, trap_id, total_frames, annotations):
    annotated_count = sum(
        1 for f_idx in range(total_frames)
        if get_record_label(annotations.get((chip_id, position, trap_id, f_idx))) is not None
    )
    is_complete = (annotated_count == total_frames)
    return annotated_count, is_complete


def find_resume_position(trap_files, chip_id, position, annotations, trap_frame_counts):
    annotated_traps = {}
    chip_clean = chip_id.strip().lower()
    pos_clean = position.strip().lower()

    for (c, p, t_id, f_idx), rec in annotations.items():
        if get_record_label(rec) is None:
            continue  # tracking-only record: does not advance the resume cursor
        if str(c).strip().lower() == chip_clean and str(p).strip().lower() == pos_clean:
            if t_id not in annotated_traps:
                annotated_traps[t_id] = []
            annotated_traps[t_id].append(f_idx)

    if not annotated_traps:
        return 0, 0

    file_trap_ids = {}
    for t_idx, trap_file in enumerate(trap_files):
        match = re.search(r'trap_?(\d+)\.tif', trap_file, re.IGNORECASE)
        if match:
            file_trap_ids[int(match.group(1))] = t_idx

    valid_annotated_trap_ids = [t_id for t_id in annotated_traps if t_id in file_trap_ids]

    if not valid_annotated_trap_ids:
        return 0, 0

    max_trap_id = max(valid_annotated_trap_ids)
    max_frame_idx = max(annotated_traps[max_trap_id])
    target_trap_idx = file_trap_ids[max_trap_id]

    return target_trap_idx, max_frame_idx


def preprocess_trap_image(img, contrast_gain=1.0, zoom_factor=1.0):
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    p_low, p_high = np.percentile(img, (0.5, 99.5))
    if p_high > p_low:
        img_norm = np.clip((img - p_low) * (255.0 / (p_high - p_low)), 0, 255).astype(np.uint8)
    else:
        img_norm = img.astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_norm)

    if contrast_gain != 1.0:
        enhanced = cv2.convertScaleAbs(enhanced, alpha=contrast_gain, beta=0)

    bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    h, w = bgr.shape[:2]
    if zoom_factor > 1.0:
        crop_h, crop_w = int(h / zoom_factor), int(w / zoom_factor)
        start_y, start_x = (h - crop_h) // 2, (w - crop_w) // 2
        cropped = bgr[start_y:start_y + crop_h, start_x:start_x + crop_w]
        return cv2.resize(cropped, (460, 460), interpolation=cv2.INTER_CUBIC)

    return cv2.resize(bgr, (460, 460), interpolation=cv2.INTER_CUBIC)


# ==============================================================================
# DASHBOARD UI WITH ORACLE HUD, CLASSIFIER RLS & SPATIAL TRACKING
# ==============================================================================
def build_dashboard_ui(trap_img, chip_id, position, trap_id, current_frame, total_frames, 
                       current_class, gain, zoom, is_trap_complete, pos_completed_traps, 
                       total_pos_traps, human_curr_rls, oracle_prefix_rls, model_pred_str, 
                       model_pred_col, oracle_overlay_enabled, classifier_rls=None, 
                       detector_rls=None, active_clicks=None, tracked_info=None):
    
    canvas = np.zeros((660, 900, 3), dtype=np.uint8)
    canvas[:] = (24, 24, 24)

    # Header section
    cv2.rectangle(canvas, (0, 0), (900, 50), (12, 12, 12), -1)
    header_title = f"{chip_id} | {position} | Trap #{trap_id:02d}"
    if is_trap_complete:
        header_title += " [REVIEW MODE]"
    header_col = (0, 255, 128) if is_trap_complete else (255, 255, 255)
    cv2.putText(canvas, header_title, (20, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.62, header_col, 2)
    
    progress_str = f"Frame {current_frame + 1}/{total_frames} | Pos Traps: {pos_completed_traps}/{total_pos_traps}"
    cv2.putText(canvas, progress_str, (470, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 255), 1)

    # Main image view
    processed_view = preprocess_trap_image(trap_img, contrast_gain=gain, zoom_factor=zoom)
    canvas[65:525, 20:480] = processed_view
    border_col = (0, 255, 128) if is_trap_complete else (100, 100, 100)
    cv2.rectangle(canvas, (20, 65), (480, 525), border_col, 2)

    # Overlay dynamic spatial tracking clicks / centroids
    overlay_clicks = []
    if active_clicks and len(active_clicks) > 0:
        overlay_clicks = active_clicks
    elif tracked_info and not np.isnan(tracked_info.get("Pillar_P1_X", np.nan)):
        p1 = (int(round(tracked_info["Pillar_P1_X"])), int(round(tracked_info["Pillar_P1_Y"])))
        p2 = (int(round(tracked_info["Pillar_P2_X"])), int(round(tracked_info["Pillar_P2_Y"])))
        overlay_clicks = [p1, p2]

        mx = tracked_info.get("Mother_X", np.nan)
        my = tracked_info.get("Mother_Y", np.nan)
        if not (np.isnan(mx) or np.isnan(my)):
            m = (int(round(mx)), int(round(my)))
            overlay_clicks.append(m)

    apply_dynamic_mask_overlay(canvas, overlay_clicks, zoom_factor=zoom)

    # Right side panel
    cv2.rectangle(canvas, (500, 65), (880, 525), (35, 35, 35), -1)
    cv2.rectangle(canvas, (500, 65), (880, 525), (70, 70, 70), 2)

    # Upper Model AI Box
    cv2.rectangle(canvas, (510, 75), (870, 115), (20, 20, 20), -1)
    cv2.rectangle(canvas, (510, 75), (870, 115), model_pred_col, 1)
    cv2.putText(canvas, "KERAS AI PREDICTION:", (520, 93), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)
    cv2.putText(canvas, model_pred_str, (520, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.48, model_pred_col, 2)

    cv2.putText(canvas, "STATE CLASSIFICATION KEYS", (520, 138), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
    cv2.line(canvas, (520, 146), (860, 146), (80, 80, 80), 1)

    y_pos = 168
    displayed_keys = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('7'), ord('8'), ord('x')]
    
    for k_code in displayed_keys:
        info = CLASS_CONFIG[k_code]
        key_str = info["key_str"]
        label = info["label"]
        color = info["color"]

        is_selected = (current_class is not None and label == current_class)
        bg_color = (80, 80, 80) if is_selected else (50, 50, 50)
        border_color = color if is_selected else (70, 70, 70)

        cv2.rectangle(canvas, (520, y_pos - 14), (860, y_pos + 11), bg_color, -1)
        cv2.rectangle(canvas, (520, y_pos - 14), (860, y_pos + 11), border_color, 2 if is_selected else 1)
        cv2.rectangle(canvas, (530, y_pos - 7), (545, y_pos + 4), color, -1)
        
        txt_col = (255, 255, 255) if is_selected else (210, 210, 210)
        display_line = f"{key_str}  {label}"
        cv2.putText(canvas, display_line, (555, y_pos + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.41, txt_col, 2 if is_selected else 1)
        
        y_pos += 31

    oracle_status_txt = "ON" if oracle_overlay_enabled else "OFF"
    oracle_status_col = (0, 255, 128) if oracle_overlay_enabled else (120, 120, 120)

    cv2.line(canvas, (520, 422), (860, 422), (80, 80, 80), 1)
    cv2.putText(canvas, "Click tracked trap: re-pin Mother (fwd only) | [C]: new 3-click set | [Enter]: track 2", (520, 437), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    cv2.putText(canvas, "[<-]/[->]: Prev/Next Frame | [P]: Prev Trap | [N]: Next Trap", (520, 453), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)
    cv2.putText(canvas, f"[O]: Oracle Overlay [{oracle_status_txt}] | [C]: Clear Clicks", (520, 469), cv2.FONT_HERSHEY_SIMPLEX, 0.35, oracle_status_col, 1)
    cv2.putText(canvas, "[7]: Escaped | [X]: Mark Bad Trap", (520, 485), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 220, 255), 1)
    cv2.putText(canvas, "[+]/[-] Zoom | [[/]] Brightness | [Q]: Quit", (520, 501), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (140, 140, 140), 1)

    # Bottom Dashboard Panel
    cv2.rectangle(canvas, (20, 532), (880, 652), (15, 25, 35), -1)
    cv2.rectangle(canvas, (20, 532), (880, 652), (0, 180, 255) if oracle_overlay_enabled else (70, 70, 70), 1)

    # Human Ground-Truth Line
    h_cen = ">=" if human_curr_rls["is_censored"] else ""
    h_str = f"Observed Ground-Truth Age (f_0..{current_frame + 1}): {h_cen}{human_curr_rls['rls_count']} Buds"
    cv2.putText(canvas, h_str, (35, 555), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 255, 255), 2)

    # Separate Classifier Counted Trap RLS Line
    if classifier_rls is not None and len(classifier_rls) > 0:
        c_cen = ">=" if classifier_rls.get("is_censored", False) else ""
        c_rls_val = classifier_rls.get("rls_count", 0)
        c_str = f"Classifier Counted Trap RLS: {c_cen}{c_rls_val} Buds"
    else:
        c_str = "Classifier Counted Trap RLS: N/A"
    cv2.putText(canvas, c_str, (35, 575), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 220, 255), 1)

    # Calibrated direct division-event detector (shown only when deployed)
    if detector_rls is not None:
        if detector_rls.get("escaped"):
            d_death = f"escaped @ f={detector_rls.get('escape_frame')} (censored)"
        elif detector_rls.get("died_on_chip"):
            d_death = f"dies @ f={detector_rls['death_frame']}"
        else:
            d_death = "no on-chip death"
        d_str = f"Detector RLS (calibrated): {detector_rls['rls_count']} div | {d_death}"
        cv2.putText(canvas, d_str, (450, 575), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 140), 1)

    # Prospective Oracle Lines
    if oracle_overlay_enabled:
        if oracle_prefix_rls["oracle_active"]:
            cv2.putText(canvas, "PROSPECTIVE LIFESPAN ORACLE [QUANTILE HUD]", (450, 555), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1)

            rem_m = oracle_prefix_rls["remaining_rls_median"]
            rem_h = oracle_prefix_rls["remaining_rls_half_range"]
            proj_tot = oracle_prefix_rls["projected_total_rls"]

            o_rem_str = f"Pred Remaining RLS: {rem_m:.1f} +/- {rem_h:.1f} Buds [Q10={oracle_prefix_rls['q10']:.1f}, Q90={oracle_prefix_rls['q90']:.1f}]"
            o_tot_str = f"Projected Lifespan: {proj_tot:.1f} +/- {rem_h:.1f} Buds"

            cv2.putText(canvas, o_rem_str, (35, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 2)
            cv2.putText(canvas, o_tot_str, (35, 624), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 128), 2)
            cv2.putText(canvas, "*Strictly 20-feature prefix prediction. No heuristic fallback applied.", (35, 644), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (140, 140, 140), 1)
        else:
            cv2.putText(canvas, "Oracle Model Inactive (lifespan_oracle.keras not found)", (35, 605), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 100, 255), 1)
    else:
        cv2.putText(canvas, "Press [O] to enable Prospective Quantile Oracle HUD Overlay.", (35, 610), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (130, 130, 130), 1)

    return canvas


def merge_tracked_coordinates(annotations, tracking_cache, chip_id, position, trap_id,
                              tracked_seq, assign_frame=None, assign_label=None,
                              start_frame=None, overwrite=True):
    """Merges auto-tracked coordinates into the session state.
    start_frame: only frames >= start_frame are touched, so a mid-stack
    correction NEVER rewrites frames the annotator has already reviewed.
    overwrite=False (session reload): only fills frames that lack pillar
    coordinates, preserving everything loaded from the Excel database.
    NEVER invents a class label: frames without a human label keep Class=None
    (in memory only; save_master_annotations will not persist them).
    Mother coords are nulled for frames labeled No Cell / Skipped (no mother
    exists there); frames labeled blurry get ALL coords nulled (blur censors
    that frame's spatial data). The heatmap anchor then falls back to the
    frame center, so a heatmap is still always present."""
    for f_i, spat_coords in tracked_seq.items():
        if start_frame is not None and f_i < start_frame:
            continue  # never rewrite frames before the correction point
        rec = annotations.get((chip_id, position, trap_id, f_i), {})
        if not isinstance(rec, dict):
            rec = {"Class": str(rec)}
        if not overwrite and not np.isnan(rec.get("Pillar_P1_X", np.nan)):
            tracking_cache[f_i] = {k: rec.get(k, np.nan) for k in SPATIAL_KEYS}
            continue  # reload mode: keep existing (saved / human-corrected) coords

        if assign_frame is not None and f_i == assign_frame:
            rec["Class"] = assign_label

        cls_i = get_record_label(rec)
        frame_coords = dict(spat_coords)
        if cls_i == "Out of Focus / Blurry":
            for sk in SPATIAL_KEYS:
                frame_coords[sk] = np.nan
        # NOTE: the tracked mother is kept even on frames labeled 'No Cell' --
        # an explicit human click outranks a (possibly stale) class label. The
        # 'No Cell => Mother NaN' semantic is still enforced at save/load time,
        # so the persisted database stays clean.

        tracking_cache[f_i] = frame_coords
        rec.update(frame_coords)
        annotations[(chip_id, position, trap_id, f_i)] = rec


# ==============================================================================
# MAIN EVENT LOOP
# ==============================================================================
def main():
    global SPATIAL_CLICKS
    print("=" * 75)
    print("  YEAST ANNOTATOR STUDIO - SPATIAL TRACKER & LIFESPAN ORACLE HUD")
    print("=" * 75)

    # Case-insensitive registry lookups. Canonical spelling matters because the
    # trainer refuses two Chip_ID spellings that resolve to one directory.
    chip_canonical_names = {k.strip().lower(): k for k in KNOWN_CHIP_TRAPS_DIRS}
    dir_registered_owner = {os.path.normcase(os.path.normpath(v)): k
                            for k, v in KNOWN_CHIP_TRAPS_DIRS.items()}

    print("\n[Configuration Setup]")
    chip_id = input(f"Enter Aging Chip / Experiment ID [Default: {DEFAULT_CHIP_ID}]: ").strip() or DEFAULT_CHIP_ID
    canonical = chip_canonical_names.get(chip_id.strip().lower())
    if canonical is not None and canonical != chip_id:
        print(f"--> Chip_ID normalized to registered spelling: '{canonical}'")
        chip_id = canonical

    position = input("Enter Position ID [Default: Pos0]: ").strip() or "Pos0"

    # The traps-directory default follows the CHOSEN chip, so pressing Enter
    # through the prompts can never pair a Chip_ID with another chip's stacks.
    default_traps_dir = KNOWN_CHIP_TRAPS_DIRS.get(chip_id, KNOWN_CHIP_TRAPS_DIRS[DEFAULT_CHIP_ID])
    traps_dir_input = input(f"Enter path to extracted traps directory\n[Default: {default_traps_dir}]: ").strip()
    traps_dir = traps_dir_input if traps_dir_input else default_traps_dir

    # Multi-chip safety cross-check: every chip reuses Pos0/Pos1/..., so
    # annotating one chip's stacks under another chip's Chip_ID silently
    # corrupts BOTH chips' records (and their RLS numbers) in the master
    # database. Refuse the mixup unless it is explicitly confirmed.
    registered_owner = dir_registered_owner.get(os.path.normcase(os.path.normpath(traps_dir)))
    if registered_owner is not None and registered_owner.strip().lower() != chip_id.strip().lower():
        print("\n" + "!" * 75)
        print(f"[!] CHIP / DIRECTORY MISMATCH:")
        print(f"    Directory is registered to Chip_ID '{registered_owner}':")
        print(f"      {traps_dir}")
        print(f"    but you entered Chip_ID '{chip_id}'. Position/Trap numbers repeat")
        print(f"    across chips, so annotating under the wrong Chip_ID would silently")
        print(f"    corrupt both chips' annotations and lifespan counts.")
        print("!" * 75)
        confirm = input("Type YES to continue anyway (anything else aborts safely): ").strip()
        if confirm != "YES":
            print("Aborted. No annotations were touched.")
            return
    elif registered_owner is None:
        print(f"--> Note: this directory is not in KNOWN_CHIP_TRAPS_DIRS. Continuing with "
              f"Chip_ID '{chip_id}'; before training, add the mapping to DEFAULT_TRAPS_DIRS "
              f"in train_classifier.py (and to KNOWN_CHIP_TRAPS_DIRS here).")

    trap_files = fetch_position_traps(traps_dir, position)
    if not trap_files:
        return

    print("--> Pre-caching trap metadata...")
    trap_frame_counts = {}
    for tf_path in trap_files:
        match = re.search(r'trap_?(\d+)\.tif', tf_path, re.IGNORECASE)
        if match:
            t_id = int(match.group(1))
            with tif.TiffFile(tf_path) as check_tf:
                trap_frame_counts[t_id] = len(check_tf.pages)

    classifier_model = load_keras_classifier(MODEL_PATH)
    rls_detector_model, rls_detector_meta = load_rls_detector()
    viterbi_temp = VITERBI_TEMPERATURE
    use_triplet_inputs = True
    if classifier_model is not None:
        model_fmt = None
        if os.path.exists("model_input_meta.json"):
            try:
                with open("model_input_meta.json", "r") as f:
                    _meta = json.load(f)
                model_fmt = _meta.get("model_input_format")
                viterbi_temp = float(_meta.get("viterbi_temperature", VITERBI_TEMPERATURE))
            except Exception:
                pass
        use_triplet_inputs = (model_fmt != SINGLE_FRAME_INPUT_FORMAT)
        print(f"--> Viterbi smoothing temperature: T={viterbi_temp} | "
              f"input format: {'temporal triplet' if use_triplet_inputs else 'single frame'}")
        if model_fmt not in (MODEL_INPUT_FORMAT, SINGLE_FRAME_INPUT_FORMAT):
            print("!" * 74)
            print(f"!! WARNING: input-format mismatch. This UI builds '{MODEL_INPUT_FORMAT}'")
            print(f"!! inputs but the loaded model reports '{model_fmt}'.")
            print("!! AI predictions & Classifier Counted RLS will be unreliable and")
            print("!! typically biased toward 'Dead Cell' (static frames look in-")
            print("!! distribution, moving/living frames do not).")
            print("!! FIX: retrain with the current train_classifier.py.")
            print("!" * 74)
    oracle_engine = RemainingRLSOracle(ORACLE_MODEL_PATH, ORACLE_META_PATH)
    hmm_transitions = load_transition_matrix(CLASS_LABELS) if CLASS_LABELS else None

    annotations = load_master_annotations()
    start_trap_idx, start_frame_idx = find_resume_position(trap_files, chip_id, position, annotations, trap_frame_counts)
    
    print(f"\n--> Active Position: '{position}' on Chip '{chip_id}'")
    print(f"--> Found {len(trap_files)} trap files for {position}.")
    print(f"--> Resuming at Trap Index {start_trap_idx}, Frame {start_frame_idx + 1}")

    ui_state = {"zoom": 1.0}  # shared with the mouse callback for zoom-aware clicks
    cv2.namedWindow("Yeast Cell Annotator Studio", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("Yeast Cell Annotator Studio", handle_mouse_clicks, ui_state)

    contrast_gain = 1.0
    zoom_factor = 1.0
    oracle_overlay_enabled = False
    trap_index = start_trap_idx
    first_load = True

    while 0 <= trap_index < len(trap_files):
        trap_file = trap_files[trap_index]
        trap_id = int(re.search(r'trap_?(\d+)\.tif', trap_file, re.IGNORECASE).group(1))

        try:
            with tif.TiffFile(trap_file) as tf:
                raw_stack = [page.asarray() for page in tf.pages]
        except Exception as e:
            print(f"--> Error loading TIFF file {trap_file}: {e}. Skipping trap...")
            trap_index += 1
            continue

        total_frames = len(raw_stack)
        stack_uint8_460 = [normalize_to_uint8(img) for img in raw_stack]

        # Build / Load spatial tracking cache before AI inference
        trap_tracking_cache = {}
        ref_f_found, ref_clicks = None, None

        for f in range(total_frames):
            entry = annotations.get((chip_id, position, trap_id, f), {})
            if isinstance(entry, dict):
                cls_val = get_record_label(entry)

                if cls_val in ("No Cell", "Skipped / Bad Trap"):
                    entry["Mother_X"] = np.nan
                    entry["Mother_Y"] = np.nan

                p1x, p1y = entry.get("Pillar_P1_X", np.nan), entry.get("Pillar_P1_Y", np.nan)
                p2x, p2y = entry.get("Pillar_P2_X", np.nan), entry.get("Pillar_P2_Y", np.nan)
                mx, my   = entry.get("Mother_X", np.nan),    entry.get("Mother_Y", np.nan)

                if not any(np.isnan([p1x, p1y, p2x, p2y])):
                    trap_tracking_cache[f] = {
                        "Pillar_P1_X": p1x, "Pillar_P1_Y": p1y,
                        "Pillar_P2_X": p2x, "Pillar_P2_Y": p2y,
                        "Mother_X": mx,     "Mother_Y": my
                    }
                    if ref_f_found is None:
                        ref_clicks = [(p1x, p1y), (p2x, p2y)]
                        if not (np.isnan(mx) or np.isnan(my)):
                            ref_clicks.append((mx, my))
                        ref_f_found = f

        # Auto-track rest of trap if prior reference clicks exist
        if ref_f_found is not None and ref_clicks is not None:
            tracked_seq = auto_track_entire_stack(stack_uint8_460, ref_f_found, ref_clicks)
            merge_tracked_coordinates(annotations, trap_tracking_cache,
                                      chip_id, position, trap_id, tracked_seq,
                                      overwrite=False)

        ai_predicted_labels, ai_probabilities, ai_pred_indices, ai_proc_stack = batch_predict_trap(
            classifier_model, raw_stack, tracking_cache=trap_tracking_cache,
            transitions=hmm_transitions, temperature=viterbi_temp,
            use_triplet=use_triplet_inputs
        )
        classifier_rls = calculate_trap_rls(ai_predicted_labels) if ai_predicted_labels else None
        detector_rls = detector_predict_trap(rls_detector_model, rls_detector_meta, ai_proc_stack)

        if first_load:
            frame_idx = start_frame_idx
            first_load = False
        else:
            frame_idx = 0

        SPATIAL_CLICKS.clear()
        fresh_click_set = False  # armed by [C]: next 3 clicks build a full new pillar set

        while 0 <= frame_idx < total_frames:
            current_frame_img = raw_stack[frame_idx]
            entry = annotations.get((chip_id, position, trap_id, frame_idx), {})
            current_class = entry.get("Class", None) if isinstance(entry, dict) else str(entry)

            # CLICK GESTURES:
            #  * ONE click on an already-tracked trap = re-pin the MOTHER at the
            #    clicked spot; tracking updates from THIS frame FORWARD ONLY,
            #    frames already reviewed are never rewritten.
            #  * THREE clicks (pillar, pillar, mother) = full tracking set,
            #    also applied forward-only from this frame.
            #  * [C] arms a fresh pillar set on a tracked trap (suppresses the
            #    one-click mother shortcut until the 3-click set completes).
            _tracked_now = trap_tracking_cache.get(frame_idx, {})
            _has_pillars = (isinstance(_tracked_now, dict)
                            and not np.isnan(_tracked_now.get("Pillar_P1_X", np.nan))
                            and not np.isnan(_tracked_now.get("Pillar_P2_X", np.nan)))

            if (len(SPATIAL_CLICKS) == 1 and _has_pillars and not fresh_click_set
                    and current_class != "Out of Focus / Blurry"):
                new_m = SPATIAL_CLICKS[0]
                repin_clicks = [
                    (float(_tracked_now["Pillar_P1_X"]), float(_tracked_now["Pillar_P1_Y"])),
                    (float(_tracked_now["Pillar_P2_X"]), float(_tracked_now["Pillar_P2_Y"])),
                    (float(new_m[0]), float(new_m[1]))
                ]
                tracked_seq = auto_track_entire_stack(stack_uint8_460, frame_idx, repin_clicks)
                merge_tracked_coordinates(annotations, trap_tracking_cache,
                                          chip_id, position, trap_id, tracked_seq,
                                          start_frame=frame_idx)
                SPATIAL_CLICKS.clear()
                print(f"[{position}] Mother re-pinned at frame {frame_idx + 1}; "
                      f"tracking updated from here forward (earlier frames untouched).")

            elif len(SPATIAL_CLICKS) == 3 and current_class != "Out of Focus / Blurry":
                tracked_seq = auto_track_entire_stack(stack_uint8_460, frame_idx, SPATIAL_CLICKS)
                merge_tracked_coordinates(annotations, trap_tracking_cache,
                                          chip_id, position, trap_id, tracked_seq,
                                          start_frame=frame_idx)
                SPATIAL_CLICKS.clear()
                fresh_click_set = False
                print(f"[{position}] Full tracking set placed at frame {frame_idx + 1}; "
                      f"applied from here forward.")

            if len(ai_predicted_labels) > frame_idx and len(ai_probabilities) > frame_idx:
                pred_name = ai_predicted_labels[frame_idx]
                # Confidence of the SMOOTHED class (may differ from raw argmax)
                if len(ai_pred_indices) > frame_idx:
                    conf = float(ai_probabilities[frame_idx][ai_pred_indices[frame_idx]]) * 100.0
                else:
                    conf = float(np.max(ai_probabilities[frame_idx])) * 100.0
                model_pred_str = f"{pred_name} ({conf:.1f}%)"
                model_pred_col = (0, 255, 128)
            else:
                model_pred_str = "Model Inactive"
                model_pred_col = (120, 120, 120)

            annotated_cnt, is_complete = get_trap_status(chip_id, position, trap_id, total_frames, annotations)

            # Extract prefix human labels for ground-truth & Oracle features
            prefix_human_labels = []
            for f_i in range(frame_idx + 1):
                f_rec = annotations.get((chip_id, position, trap_id, f_i), None)
                prefix_human_labels.append(get_record_label(f_rec))

            human_curr_rls = calculate_trap_rls(prefix_human_labels)
            oracle_prefix_rls = calculate_prefix_prospective_rls(prefix_human_labels, oracle_engine)

            pos_completed_traps = sum(
                1 for t_id, num_f in trap_frame_counts.items()
                if get_trap_status(chip_id, position, t_id, num_f, annotations)[1]
            )

            tracked_info = trap_tracking_cache.get(frame_idx, None)
            ui_state["zoom"] = zoom_factor  # keep mouse callback zoom-aware

            gui_canvas = build_dashboard_ui(
                current_frame_img, chip_id, position, trap_id, frame_idx, total_frames, 
                current_class, contrast_gain, zoom_factor, 
                is_complete, pos_completed_traps, len(trap_files), 
                human_curr_rls, oracle_prefix_rls, model_pred_str, model_pred_col,
                oracle_overlay_enabled, classifier_rls=classifier_rls, detector_rls=detector_rls,
                active_clicks=SPATIAL_CLICKS, tracked_info=tracked_info
            )
            cv2.imshow("Yeast Cell Annotator Studio", gui_canvas)

            key = cv2.waitKeyEx(30)  # waitKeyEx: full key codes so arrow keys work

            if key in NAV_QUIT_KEYS:
                save_master_annotations(annotations)
                cv2.destroyAllWindows()
                print(f"\nSaved master annotations database ({len(annotations)} total frames). Exiting.")
                return

            elif key in KEY_RESET_CLICKS:
                SPATIAL_CLICKS.clear()
                fresh_click_set = True
                print(f"[{position}] Clicks cleared. Fresh pillar set armed: next clicks are "
                      f"pillar, pillar, mother (one-click mother re-pin suspended until then).")

            elif key in KEY_TOGGLE_ORACLE_OVERLAY:
                oracle_overlay_enabled = not oracle_overlay_enabled
                print(f"[{position}] Prospective Oracle Overlay: {'ENABLED' if oracle_overlay_enabled else 'DISABLED'}")

            elif key == 13:  # ENTER: run stage tracking with the clicks placed so far
                if len(SPATIAL_CLICKS) in (2, 3) and current_class != "Out of Focus / Blurry":
                    n_clicks = len(SPATIAL_CLICKS)
                    tracked_seq = auto_track_entire_stack(stack_uint8_460, frame_idx, SPATIAL_CLICKS)
                    merge_tracked_coordinates(annotations, trap_tracking_cache,
                                              chip_id, position, trap_id, tracked_seq,
                                              start_frame=frame_idx)
                    SPATIAL_CLICKS.clear()
                    fresh_click_set = False
                    print(f"[{position}] Tracking run with {n_clicks} clicks "
                          f"({'pillars + mother' if n_clicks == 3 else 'pillars only'}).")
                else:
                    print(f"[{position}] Place 2 clicks (pillars) or 3 (pillars + mother) before pressing Enter.")

            elif key in (ord('7'), ord('&')):
                escaped_label = CLASS_CONFIG[ord('7')]["label"]
                print(f"[{position}] Mother escaped Trap #{trap_id:02d} at frame {frame_idx + 1}. Auto-filling rest...")
                for f_i in range(frame_idx, total_frames):
                    rec = annotations.get((chip_id, position, trap_id, f_i), {})
                    if not isinstance(rec, dict):
                        rec = {}
                    rec["Class"] = escaped_label
                    annotations[(chip_id, position, trap_id, f_i)] = rec
                save_master_annotations(annotations)
                break

            elif key in (ord('x'), ord('X')):
                print(f"[{position}] Skipping Trap #{trap_id:02d} entirely...")
                for f_i in range(total_frames):
                    rec = annotations.get((chip_id, position, trap_id, f_i), {})
                    if not isinstance(rec, dict):
                        rec = {}
                    rec["Class"] = "Skipped / Bad Trap"
                    rec["Mother_X"] = np.nan
                    rec["Mother_Y"] = np.nan
                    annotations[(chip_id, position, trap_id, f_i)] = rec
                save_master_annotations(annotations)
                break

            elif key in CLASS_CONFIG:
                assigned_label = CLASS_CONFIG[key]["label"]

                if len(SPATIAL_CLICKS) in (2, 3) and assigned_label != "Out of Focus / Blurry":
                    tracked_seq = auto_track_entire_stack(stack_uint8_460, frame_idx, SPATIAL_CLICKS)
                    # Assign the human label ONLY to the current frame; other
                    # frames keep whatever label they already have (or None).
                    merge_tracked_coordinates(annotations, trap_tracking_cache,
                                              chip_id, position, trap_id, tracked_seq,
                                              assign_frame=frame_idx, assign_label=assigned_label,
                                              start_frame=frame_idx)
                    SPATIAL_CLICKS.clear()
                    fresh_click_set = False
                else:
                    rec = annotations.get((chip_id, position, trap_id, frame_idx), {})
                    if not isinstance(rec, dict):
                        rec = {}
                    rec["Class"] = assigned_label
                    if assigned_label == "Out of Focus / Blurry":
                        for sk in SPATIAL_KEYS:
                            rec[sk] = np.nan
                        trap_tracking_cache.pop(frame_idx, None)
                    # ('No Cell' no longer wipes the tracked mother from the live
                    #  cache; the save/load layer still nulls it in the database.)
                    annotations[(chip_id, position, trap_id, frame_idx)] = rec

                frame_idx += 1

            elif key in NAV_NEXT_FRAME_KEYS:
                frame_idx = min(total_frames - 1, frame_idx + 1)

            elif key in NAV_PREV_FRAME_KEYS:
                frame_idx = max(0, frame_idx - 1)

            elif key in NAV_NEXT_TRAP_KEYS:
                save_master_annotations(annotations)
                SPATIAL_CLICKS.clear()
                if trap_index + 1 >= len(trap_files):
                    print(f"[{position}] Already at the last trap (Trap #{trap_id:02d}). Cannot advance further.")
                else:
                    print(f"[{position}] Advancing to next trap from frame {frame_idx + 1}/{total_frames}...")
                    break

            elif key in NAV_PREV_TRAP_KEYS:
                save_master_annotations(annotations)
                SPATIAL_CLICKS.clear()
                if trap_index <= 0:
                    print(f"[{position}] Already at the first trap. Cannot go back.")
                else:
                    print(f"[{position}] Going back to previous trap...")
                    trap_index = max(0, trap_index - 1)
                    break

            elif key == KEY_ZOOM_IN:
                zoom_factor = min(3.0, zoom_factor + 0.2)
            elif key == KEY_ZOOM_OUT:
                zoom_factor = max(1.0, zoom_factor - 0.2)
            elif key == KEY_BRIGHT_UP:
                contrast_gain = min(3.0, contrast_gain + 0.1)
            elif key == KEY_BRIGHT_DN:
                contrast_gain = max(0.5, contrast_gain - 0.1)

        if key not in NAV_PREV_TRAP_KEYS:
            if key in NAV_NEXT_TRAP_KEYS and trap_index + 1 >= len(trap_files):
                pass
            else:
                trap_index += 1

    cv2.destroyAllWindows()
    save_master_annotations(annotations)
    print(f"\nAll traps completed for {position}! Master database saved to: {MASTER_EXCEL_PATH}")


if __name__ == "__main__":
    main()