import os
import re
import cv2
import glob
import json
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

ORACLE_MODEL_PATH = "lifespan_oracle.keras"
ORACLE_META_PATH = "lifespan_oracle_meta.json"

SPATIAL_KEYS = ["Pillar_P1_X", "Pillar_P1_Y", "Pillar_P2_X", "Pillar_P2_Y", "Mother_X", "Mother_Y"]

ORACLE_FEATURE_VERSION = 2  # v2: dropped mean_conf/recent_conf (were trained as constant 1.0
                            # from human labels but served with real confidences ->
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
VITERBI_TEMPERATURE = 1.0  # fallback only. T>1 softens emissions (too high erases
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
    hm = np.exp(-(((x - cx) ** 2) + ((y - cy) ** 2)) / (2.0 * sigma**2))
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


def preprocess_frame_for_ai(raw_img, coords=None, prev_img=None, next_img=None):
    """Thin wrapper over the canonical input builder (kept for name stability).
    coords is the display-space tracking dict for the frame (or None)."""
    return build_model_input(raw_img, coords=coords, prev_img=prev_img, next_img=next_img)


def batch_predict_trap(model, stack, tracking_cache=None, transitions=None, temperature=None,
                       use_triplet=True):
    """Runs the frame classifier on a raw trap stack and Viterbi-smooths the
    per-frame probabilities with the transition prior so the on-screen
    'Classifier Counted Trap RLS' reflects the deployed (smoothed) pipeline.
    Returns (labels, probabilities, pred_indices)."""
    if model is None or len(stack) == 0:
        return [], [], []

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
        return predicted_labels, probabilities, pred_indices
    except Exception as e:
        print(f"Batch prediction error: {e}")
        return [], [], []


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
    """Wrapper that owns feature normalization and prospective quantile inference.
    Model is trained ONLY on prefixes from completed (observed-death) traps, so
    the target is true remaining RLS rather than 'time until observation ends'."""
    def __init__(self, model_path=ORACLE_MODEL_PATH, meta_path=ORACLE_META_PATH):
        self.model = None
        self.meta = None
        if not (os.path.exists(model_path) and os.path.exists(meta_path)):
            print("--> Oracle not found. Running without prospective lifespan predictions.")
            return
        try:
            with open(meta_path, "r") as f:
                self.meta = json.load(f)
            if self.meta.get("feature_version") != ORACLE_FEATURE_VERSION:
                print(f"--> Oracle metadata feature version mismatch "
                      f"(file={self.meta.get('feature_version')}, UI={ORACLE_FEATURE_VERSION}). "
                      f"Retrain with train_oracle_only.py. Oracle disabled.")
                self.meta = None
                return
            if list(self.meta.get("feature_names", [])) != list(ORACLE_FEATURE_NAMES):
                print("--> Oracle feature-name ordering mismatch. Retrain with "
                      "train_oracle_only.py. Oracle disabled.")
                self.meta = None
                return
            self.model = tf.keras.models.load_model(
                model_path, custom_objects={"pinball_loss_multi": pinball_loss_multi}
            )
            print(f"--> Loaded Prospective Lifespan Oracle: '{model_path}'")
        except Exception as e:
            print(f"--> Warning: Failed to load oracle ({e}). Oracle inactive.")
            self.model = None
            self.meta = None

    @property
    def active(self):
        return self.model is not None and self.meta is not None

    def predict_remaining_quantiles(self, feature_vector):
        if not self.active:
            return None
        x = np.asarray(feature_vector, dtype=np.float32)
        means = np.asarray(self.meta["feature_means"], dtype=np.float32)
        stds = np.asarray(self.meta["feature_stds"], dtype=np.float32)
        stds[stds < 1e-6] = 1.0
        x_norm = ((x - means) / stds)[None, :]
        pred = self.model.predict(x_norm, verbose=0)[0]
        pred = np.asarray(pred, dtype=float)
        # Quantile crossing is possible with an unconstrained output head; sorting
        # preserves a valid [q10 <= q50 <= q90] HUD interval at serving time.
        pred = np.sort(pred)
        return np.maximum(pred, 0.0)


def calculate_prefix_prospective_rls(prefix_labels, oracle_engine):
    """Strict prospective inference: features are built ONLY from prefix_labels
    (never future frames / full-lifespan outcomes). Returns Q10/Q50/Q90 remaining
    RLS plus a projected total (observed divisions + median remaining)."""
    prefix_info = calculate_trap_rls(prefix_labels)
    observed_rls = prefix_info["rls_count"]

    out = {
        "oracle_active": False,
        "remaining_rls_median": np.nan,
        "remaining_rls_half_range": np.nan,
        "projected_total_rls": np.nan,
        "q10": np.nan, "q50": np.nan, "q90": np.nan
    }
    if oracle_engine is None or not oracle_engine.active:
        return out

    if prefix_info["died_on_chip"]:
        # If the prefix already contains observed death, remaining RLS is exactly 0.
        out.update({
            "oracle_active": True,
            "remaining_rls_median": 0.0,
            "remaining_rls_half_range": 0.0,
            "projected_total_rls": float(observed_rls),
            "q10": 0.0, "q50": 0.0, "q90": 0.0
        })
        return out

    features = extract_prefix_features(prefix_labels)
    quantiles = oracle_engine.predict_remaining_quantiles(features)
    if quantiles is None:
        return out

    q10, q50, q90 = map(float, quantiles)
    half_range = (q90 - q10) / 2.0
    out.update({
        "oracle_active": True,
        "remaining_rls_median": q50,
        "remaining_rls_half_range": half_range,
        "projected_total_rls": float(observed_rls) + q50,
        "q10": q10, "q50": q50, "q90": q90
    })
    return out


# ==============================================================================
# STAGE / TRAP SPATIAL TRACKING ENGINE (PILLARS + MOTHER CENTROID)
# ==============================================================================
def normalize_to_uint8(img):
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.float32)
    lo, hi = np.percentile(img, (0.5, 99.5))
    if hi > lo:
        img = (img - lo) * (255.0 / (hi - lo))
    return np.clip(img, 0, 255).astype(np.uint8)


def _translate_points(points, dx, dy):
    """Applies a single global stage translation. Relative trap geometry is
    invariant, so pillar 1, pillar 2 and the mother centroid all move together."""
    return [(float(x) + dx, float(y) + dy) for x, y in points]


def _estimate_translation_phasecorr(img_ref, img_new, hann_window=None):
    """Fast translation estimate. Returns the shift that maps REF coordinates
    into NEW-frame coordinates, plus the phase-correlation response."""
    ref = img_ref.astype(np.float32)
    new = img_new.astype(np.float32)
    shift_new_to_ref, response = cv2.phaseCorrelate(new, ref, hann_window)
    # cv2.phaseCorrelate(src1=new, src2=ref) returns the shift that moves
    # new -> ref; tracked REF points require the opposite sign to land in new.
    dx, dy = -float(shift_new_to_ref[0]), -float(shift_new_to_ref[1])
    return dx, dy, float(response)


def _estimate_translation_ecc(img_ref, img_new):
    """Translation-only ECC fallback. The returned warp maps NEW -> REF;
    negate it to move reference-frame points into the new frame."""
    ref = img_ref.astype(np.float32) / 255.0
    new = img_new.astype(np.float32) / 255.0
    warp = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-5)
    try:
        _, warp = cv2.findTransformECC(ref, new, warp, cv2.MOTION_TRANSLATION, criteria)
        return -float(warp[0, 2]), -float(warp[1, 2]), True
    except cv2.error:
        return 0.0, 0.0, False


def _shift_reasonable(dx, dy, max_shift_px):
    return np.isfinite(dx) and np.isfinite(dy) and abs(dx) <= max_shift_px and abs(dy) <= max_shift_px


def auto_track_entire_stack(stack_uint8_460, ref_frame_idx, ref_clicks):
    """Tracks STAGE/TRAP TRANSLATION frame-to-frame and propagates all 2 or 3
    reference points together. Designed for hundreds of frames: phase correlation
    is the primary estimator; translation-only ECC is a conservative fallback.

    IMPORTANT biological convention:
      - Pillar clicks define the rigid trap and are always propagated.
      - The third click (Mother centroid) is *not* independently object-tracked;
        it follows the rigid trap translation only. This intentionally avoids
        following the newly produced daughter out of the trap after cytokinesis.
      - Any per-frame mother correction should come from a human click, and that
        corrected reference is then propagated forward/backward until another
        correction is made.

    Returned coordinates remain in the 460x460 display space used by the UI and
    annotation workbook."""
    if not ref_clicks or len(stack_uint8_460) == 0:
        return {}
    if len(ref_clicks) not in (2, 3):
        raise ValueError("auto_track_entire_stack expects exactly 2 (pillars) or 3 (pillars+mother) clicks")

    n = len(stack_uint8_460)
    ref_frame_idx = int(np.clip(ref_frame_idx, 0, n - 1))
    ref_points = [(float(x), float(y)) for x, y in ref_clicks]

    # Convert the 460px display images to a smaller registration view.  Translation
    # is estimated in this reduced space for speed, then scaled back.
    REG_SIZE = 160
    REG_SCALE = 460.0 / REG_SIZE
    MAX_SHIFT_DISPLAY = 40.0  # reject wild registration jumps (> ~9 raw px)
    MAX_SHIFT_REG = MAX_SHIFT_DISPLAY / REG_SCALE

    reg_stack = [cv2.resize(img, (REG_SIZE, REG_SIZE), interpolation=cv2.INTER_AREA)
                 for img in stack_uint8_460]
    hann = cv2.createHanningWindow((REG_SIZE, REG_SIZE), cv2.CV_32F)

    cumulative = {ref_frame_idx: (0.0, 0.0)}

    def walk(start, stop, step):
        prev_i = start
        cum_dx, cum_dy = cumulative[start]
        i = start + step
        while (i <= stop if step > 0 else i >= stop):
            prev_img, curr_img = reg_stack[prev_i], reg_stack[i]
            dx_r, dy_r, resp = _estimate_translation_phasecorr(prev_img, curr_img, hann)
            if (resp < 0.05) or not _shift_reasonable(dx_r, dy_r, MAX_SHIFT_REG):
                dx_r, dy_r, ok = _estimate_translation_ecc(prev_img, curr_img)
                if not ok or not _shift_reasonable(dx_r, dy_r, MAX_SHIFT_REG):
                    dx_r, dy_r = 0.0, 0.0
            cum_dx += dx_r * REG_SCALE
            cum_dy += dy_r * REG_SCALE
            cumulative[i] = (cum_dx, cum_dy)
            prev_i = i
            i += step

    if ref_frame_idx < n - 1:
        walk(ref_frame_idx, n - 1, +1)
    if ref_frame_idx > 0:
        walk(ref_frame_idx, 0, -1)

    tracked = {}
    for f_idx in range(n):
        dx, dy = cumulative.get(f_idx, (0.0, 0.0))
        pts = _translate_points(ref_points, dx, dy)
        frame_coords = {
            "Pillar_P1_X": pts[0][0], "Pillar_P1_Y": pts[0][1],
            "Pillar_P2_X": pts[1][0], "Pillar_P2_Y": pts[1][1],
            "Mother_X": np.nan, "Mother_Y": np.nan
        }
        if len(pts) == 3:
            frame_coords["Mother_X"], frame_coords["Mother_Y"] = pts[2]
        tracked[f_idx] = frame_coords
    return tracked


# ==============================================================================
# MOUSE INTERACTION & DYNAMIC MASK OVERLAY
# ==============================================================================
def handle_mouse_clicks(event, x, y, flags, param):
    """Records clicks inside the 460x460 image panel and inverse-maps them
    through the current center zoom so tracking always receives unzoomed display
    coordinates. No automatic clearing: the main loop interprets 1 click on an
    already-tracked trap as a mother re-pin, or 3 as a full pillar+mother set."""
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    img_x, img_y = x - 20, y - 65
    if not (0 <= img_x < 460 and 0 <= img_y < 460):
        return

    zoom = 1.0
    if isinstance(param, dict):
        try:
            zoom = max(1.0, float(param.get("zoom", 1.0)))
        except (TypeError, ValueError):
            zoom = 1.0

    if zoom > 1.0:
        # preprocess_trap_image crops the center to 460/zoom before resizing to 460.
        crop = 460.0 / zoom
        start = (460.0 - crop) / 2.0
        img_x = start + (img_x / 460.0) * crop
        img_y = start + (img_y / 460.0) * crop

    SPATIAL_CLICKS.append((int(round(img_x)), int(round(img_y))))
    if len(SPATIAL_CLICKS) == 1:
        print(f"[Spatial] Click 1 at ({SPATIAL_CLICKS[-1][0]}, {SPATIAL_CLICKS[-1][1]}). "
              f"On an already-tracked trap this re-pins MOTHER from the current frame forward; "
              f"otherwise continue with pillar 2 and mother.")
    elif len(SPATIAL_CLICKS) == 2:
        print(f"[Spatial] Click 2 (pillar) at ({SPATIAL_CLICKS[-1][0]}, {SPATIAL_CLICKS[-1][1]}). "
              f"Press Enter to track pillars only, or click mother for a 3-point set.")
    elif len(SPATIAL_CLICKS) == 3:
        print(f"[Spatial] Click 3 (mother) at ({SPATIAL_CLICKS[-1][0]}, {SPATIAL_CLICKS[-1][1]}). Tracking will run automatically.")
    elif len(SPATIAL_CLICKS) > 3:
        # Keep the latest three so accidental extra clicks never leave a stale set.
        del SPATIAL_CLICKS[:-3]
        print("[Spatial] >3 clicks: retaining the latest three as pillar1, pillar2, mother.")


def apply_dynamic_mask_overlay(canvas, active_clicks, zoom_factor=1.0):
    """Projects stored 460-space tracking coordinates into the currently shown
    center-zoomed image and masks the pillar-to-mother region."""
    if len(active_clicks) < 2:
        return

    z = max(1.0, float(zoom_factor))
    crop = 460.0 / z
    start = (460.0 - crop) / 2.0

    def to_view(pt):
        x, y = float(pt[0]), float(pt[1])
        if z > 1.0:
            x = (x - start) * (460.0 / crop)
            y = (y - start) * (460.0 / crop)
        return (int(round(x)) + 20, int(round(y)) + 65)

    pts = [to_view(p) for p in active_clicks]
    line_y = int((pts[0][1] + pts[1][1]) / 2)
    p1_x, p2_x = pts[0][0], pts[1][0]
    cv2.line(canvas, (p1_x, line_y), (p2_x, line_y), (255, 255, 0), 1)

    for i, (px, py) in enumerate(pts):
        col = (0, 255, 255) if i < 2 else (0, 255, 128)
        cv2.circle(canvas, (px, py), 5, col, 2)

    if len(pts) >= 3:
        mx, my = pts[2]
        cv2.line(canvas, (int((p1_x + p2_x)/2), line_y), (mx, my), (0, 255, 128), 1)


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
            print(f"Warning: Could not read master Excel ({e}). Starting fresh.")
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
                       active_clicks=None, tracked_info=None):
    
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

    default_traps_dir = r"Y:\Jordan\JM135 CR Mud1 zeropointonepercentglucose\_1\extracted_traps"
    
    print("\n[Configuration Setup]")
    chip_id = input("Enter Aging Chip / Experiment ID [Default: JM135_CR_Mud1]: ").strip() or "JM135_CR_Mud1"
    position = input("Enter Position ID [Default: Pos18]: ").strip() or "Pos18"
    traps_dir_input = input(f"Enter path to extracted traps directory\n[Default: {default_traps_dir}]: ").strip()
    traps_dir = traps_dir_input if traps_dir_input else default_traps_dir

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

        ai_predicted_labels, ai_probabilities, ai_pred_indices = batch_predict_trap(
            classifier_model, raw_stack, tracking_cache=trap_tracking_cache,
            transitions=hmm_transitions, temperature=viterbi_temp,
            use_triplet=use_triplet_inputs
        )
        classifier_rls = calculate_trap_rls(ai_predicted_labels) if ai_predicted_labels else None

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
                oracle_overlay_enabled, classifier_rls=classifier_rls,
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
