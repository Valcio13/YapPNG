#!/usr/bin/env python
"""
=============================================================================
YapPNG for DaVinci Resolve (v2.2 Ultra-Optimized Edition)
- Vectorized VAD Engine (NumPy Prefix-Sum + Array Fallback)
- Single-Pass Audio Decoding & In-Memory Slicing
- Pre-Cached Media Pool Item Resolution
- Batched Timeline Lift & Splice Operations
- Multi-Character Profiles & Track Routing
- Character Folder Auto-Scanner (Idle, Talk, Shout)
- Visual Screen Layout & "Fetch from Selected Clip"
- PNGtuber Voice Bounce / Pop Effect
- High-Volume "Shout / Scream" Detection
- One-Click Background Noise Auto-Calibration
- Clean Overwrite / Replace in Range
- 🏷️ Marker-Driven Expression Auto-Switching
- 💡 Inactive Speaker Dimming / Listening Mode (Opacity)
=============================================================================
Compatible with: DaVinci Resolve Free & Studio (18, 19, 21+)
Author: Pair Programming with Antigravity
"""

import os
import sys
import json
import math
import struct
import subprocess
import array

# High-performance NumPy acceleration if available
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

# ---------------------------------------------------------------------------
# Resolve / Fusion Context Detection
# ---------------------------------------------------------------------------
resolve_app = globals().get('resolve')
fusion_app = globals().get('fusion') or globals().get('fu')
bmd_module = globals().get('bmd')

if not bmd_module:
    try:
        import bmd
        bmd_module = bmd
    except ImportError:
        pass

if not fusion_app and bmd_module:
    try:
        fusion_app = bmd_module.scriptapp("Fusion")
    except Exception:
        pass

if not resolve_app and bmd_module:
    try:
        resolve_app = bmd_module.scriptapp("Resolve")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Configuration Persistence
# ---------------------------------------------------------------------------
CONFIG_DIR = os.path.join(
    os.getenv('APPDATA', os.path.expanduser('~')),
    'Blackmagic Design', 'DaVinci Resolve', 'Support'
)
CONFIG_FILE = os.path.join(CONFIG_DIR, 'YapPNG_config.json')

DEFAULT_CONFIG = {
    "active_character": "Character_Host",
    "characters": {
        "Character_Host": {
            "folder": r"F:\Plugin\test_assets\Character_Host",
            "active_expression": "Neutral",
            "expressions": {
                "Neutral": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Host\neutral_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Host\neutral_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Host\neutral_shout.png"
                },
                "Happy": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Host\happy_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Host\happy_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Host\neutral_shout.png"
                },
                "Angry": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Host\angry_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Host\angry_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Host\angry_shout.png"
                }
            },
            "audio_track_index": 1,
            "base_video_track": 2,
            "talk_video_track": 3,
            "threshold_db": -30,
            "shout_threshold_db": -12,
            "enable_shout": True,
            "hold_ms": 120,
            "min_speech_ms": 50,
            "enable_bounce": True,
            "bounce_px": 18,
            "enable_dimming": True,
            "dim_opacity": 70,
            "layout_preset": "Left Side",
            "pan": -550.0,
            "tilt": -150.0,
            "zoom": 0.85,
            "flip_x": False
        },
        "Character_Guest": {
            "folder": r"F:\Plugin\test_assets\Character_Guest",
            "active_expression": "Neutral",
            "expressions": {
                "Neutral": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Guest\neutral_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Guest\neutral_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Guest\neutral_shout.png"
                },
                "Smug": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Guest\smug_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Guest\smug_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Guest\neutral_shout.png"
                },
                "Surprised": {
                    "idle_png": r"F:\Plugin\test_assets\Character_Guest\surprised_idle.png",
                    "talk_png": r"F:\Plugin\test_assets\Character_Guest\surprised_talk.png",
                    "shout_png": r"F:\Plugin\test_assets\Character_Guest\surprised_shout.png"
                }
            },
            "audio_track_index": 2,
            "base_video_track": 4,
            "talk_video_track": 5,
            "threshold_db": -30,
            "shout_threshold_db": -12,
            "enable_shout": True,
            "hold_ms": 120,
            "min_speech_ms": 50,
            "enable_bounce": True,
            "bounce_px": 18,
            "enable_dimming": True,
            "dim_opacity": 70,
            "layout_preset": "Right Side",
            "pan": 550.0,
            "tilt": -150.0,
            "zoom": 0.85,
            "flip_x": True
        }
    },
    "audio_source_type": 0,
    "custom_audio_file": r"F:\Plugin\test_assets\test_voice.wav",
    "range_mode": 0,
    "overwrite_existing": True
}

PRESETS = {
    "Left Side": {"pan": -550.0, "tilt": -150.0, "zoom": 0.85, "flip_x": False},
    "Right Side": {"pan": 550.0, "tilt": -150.0, "zoom": 0.85, "flip_x": True},
    "Center Bottom": {"pan": 0.0, "tilt": -180.0, "zoom": 1.0, "flip_x": False},
    "Center Stage": {"pan": 0.0, "tilt": 0.0, "zoom": 1.0, "flip_x": False},
    "Custom": None
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cfg = dict(DEFAULT_CONFIG)
                cfg.update(data)
                return cfg
        except Exception as e:
            print(f"[YapPNG] Error loading config: {e}")
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"[YapPNG] Error saving config: {e}")

# ---------------------------------------------------------------------------
# Folder Scanner for Expressions
# ---------------------------------------------------------------------------
def scan_character_folder(folder_path):
    if os.path.isfile(folder_path):
        folder_path = os.path.dirname(folder_path)

    if not os.path.isdir(folder_path):
        return {}

    expressions = {}
    valid_exts = ('.png', '.jpg', '.jpeg', '.webp')

    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except Exception:
        return {}

    idle_keywords = ['_idle', '_closed', '_close', '_mouth_closed', '_shut', '_off']
    talk_keywords = ['_talk', '_talking', '_open', '_mouth_open', '_speaking', '_on']
    shout_keywords = ['_shout', '_scream', '_yell', '_loud', '_wide']

    for f in files:
        name_lower, ext = os.path.splitext(f.lower())
        if ext not in valid_exts:
            continue

        for kw in idle_keywords:
            if kw in name_lower:
                expr_name = name_lower.split(kw)[0].strip('_ -').title() or 'Default'
                if expr_name not in expressions:
                    expressions[expr_name] = {'idle_png': '', 'talk_png': '', 'shout_png': ''}
                expressions[expr_name]['idle_png'] = os.path.join(folder_path, f)
                break

        for kw in talk_keywords:
            if kw in name_lower:
                expr_name = name_lower.split(kw)[0].strip('_ -').title() or 'Default'
                if expr_name not in expressions:
                    expressions[expr_name] = {'idle_png': '', 'talk_png': '', 'shout_png': ''}
                expressions[expr_name]['talk_png'] = os.path.join(folder_path, f)
                break

        for kw in shout_keywords:
            if kw in name_lower:
                expr_name = name_lower.split(kw)[0].strip('_ -').title() or 'Default'
                if expr_name not in expressions:
                    expressions[expr_name] = {'idle_png': '', 'talk_png': '', 'shout_png': ''}
                expressions[expr_name]['shout_png'] = os.path.join(folder_path, f)
                break

    try:
        subdirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    except Exception:
        subdirs = []

    for d in subdirs:
        sub_path = os.path.join(folder_path, d)
        expr_name = d.strip().title()
        try:
            sub_files = [sf for sf in os.listdir(sub_path) if os.path.isfile(os.path.join(sub_path, sf))]
        except Exception:
            sub_files = []

        idle_file, talk_file, shout_file = '', '', ''
        for sf in sub_files:
            s_lower, ext = os.path.splitext(sf.lower())
            if ext not in valid_exts:
                continue
            if any(k in s_lower for k in ['idle', 'closed', 'close', 'off']):
                idle_file = os.path.join(sub_path, sf)
            elif any(k in s_lower for k in ['shout', 'scream', 'yell', 'loud', 'wide']):
                shout_file = os.path.join(sub_path, sf)
            elif any(k in s_lower for k in ['talk', 'talking', 'open', 'mouth', 'on']):
                talk_file = os.path.join(sub_path, sf)

        if idle_file or talk_file:
            if expr_name not in expressions:
                expressions[expr_name] = {'idle_png': '', 'talk_png': '', 'shout_png': ''}
            if idle_file:
                expressions[expr_name]['idle_png'] = idle_file
            if talk_file:
                expressions[expr_name]['talk_png'] = talk_file
            if shout_file:
                expressions[expr_name]['shout_png'] = shout_file

    return expressions

# ---------------------------------------------------------------------------
# High-Performance Audio Processing & VAD
# ---------------------------------------------------------------------------
def extract_pcm_from_file(file_path, start_sec=0.0, duration_sec=None):
    """
    Optimized single-pass FFmpeg extractor skipping video, subtitles, and metadata.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Media file not found: {file_path}")

    cmd = ["ffmpeg", "-y", "-sn", "-dn", "-threads", "4"]
    if start_sec > 0.001:
        cmd.extend(["-ss", f"{start_sec:.4f}"])
    if duration_sec is not None and duration_sec > 0:
        cmd.extend(["-t", f"{duration_sec:.4f}"])
    cmd.extend([
        "-i", file_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-f", "s16le", "-"
    ])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    raw_pcm, _ = proc.communicate()
    if proc.returncode != 0 and len(raw_pcm) == 0:
        raise RuntimeError("ffmpeg failed to extract audio.")
    return raw_pcm

def compute_frame_db_vectorized(pcm_data, sample_rate, target_fps):
    """
    Computes per-frame decibel energy values with ultra-fast vectorized prefix sums.
    """
    if HAVE_NUMPY:
        samples = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)
        total_samples = len(samples)
        if total_samples == 0:
            return np.array([], dtype=np.float32)

        spf = sample_rate / target_fps
        total_frames = int(math.ceil(total_samples / spf))
        frame_starts = (np.arange(total_frames) * spf).astype(np.int64)
        frame_ends = np.minimum(total_samples, (np.arange(1, total_frames + 1) * spf).astype(np.int64))

        sq = samples ** 2
        cumsum = np.insert(np.cumsum(sq), 0, 0.0)
        chunk_sums = cumsum[frame_ends] - cumsum[frame_starts]
        chunk_lens = np.maximum(1, frame_ends - frame_starts)
        rms = np.sqrt(chunk_sums / chunk_lens)
        db_levels = 20.0 * np.log10((rms / 32767.0) + 1e-9)
        return db_levels
    else:
        # Standard library array fallback
        samples = array.array('h')
        samples.frombytes(pcm_data)
        total_samples = len(samples)
        if total_samples == 0:
            return []

        spf = sample_rate / target_fps
        total_frames = int(math.ceil(total_samples / spf))
        db_levels = [0.0] * total_frames

        for f in range(total_frames):
            s_start = int(f * spf)
            s_end = min(total_samples, int((f + 1) * spf))
            if s_end <= s_start:
                continue
            chunk = samples[s_start:s_end]
            sum_sq = sum(s * s for s in chunk)
            rms = math.sqrt(sum_sq / len(chunk))
            db_levels[f] = 20.0 * math.log10((rms / 32767.0) + 1e-9)
        return db_levels

def calibrate_noise_floor(pcm_bytes, sample_rate=16000, window_ms=250):
    if HAVE_NUMPY:
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        total_samples = len(samples)
        if total_samples == 0:
            return -50.0, -32
        window_samples = int(sample_rate * (window_ms / 1000.0))
        step = int(sample_rate * 0.08)
        if window_samples <= 0 or total_samples < window_samples:
            return -50.0, -32

        sq = samples ** 2
        cumsum = np.insert(np.cumsum(sq), 0, 0.0)
        starts = np.arange(0, total_samples - window_samples, step, dtype=np.int64)
        ends = starts + window_samples
        w_sums = cumsum[ends] - cumsum[starts]
        rms_vals = np.sqrt(w_sums / window_samples)
        min_rms = float(np.min(rms_vals))
        noise_db = 20.0 * math.log10((max(1.0, min_rms) / 32767.0) + 1e-9)
        target_thresh = int(round(max(-48.0, min(-20.0, noise_db + 14.0))))
        return noise_db, target_thresh
    else:
        total_samples = len(pcm_bytes) // 2
        if total_samples == 0:
            return -50.0, -32
        samples = struct.unpack(f"<{total_samples}h", pcm_bytes)
        window_samples = int(sample_rate * (window_ms / 1000.0))
        min_rms = float("inf")
        step = int(sample_rate * 0.08)
        for start in range(0, total_samples - window_samples, step):
            chunk = samples[start:start + window_samples]
            sum_sq = sum(s * s for s in chunk)
            rms = math.sqrt(sum_sq / len(chunk))
            if rms < min_rms:
                min_rms = rms
        noise_db = 20.0 * math.log10((max(1.0, min_rms) / 32767.0) + 1e-9)
        target_thresh = int(round(max(-48.0, min(-20.0, noise_db + 14.0))))
        return noise_db, target_thresh

def classify_frame_states(db_array, threshold_db=-30.0, shout_threshold_db=-12.0, enable_shout=True):
    """
    Converts frame decibel levels into integer states (0: silence, 1: talk, 2: shout).
    """
    total_frames = len(db_array)
    states = [0] * total_frames
    for i in range(total_frames):
        db = db_array[i]
        if enable_shout and db >= shout_threshold_db:
            states[i] = 2
        elif db >= threshold_db:
            states[i] = 1
    return states

def extract_segments_from_states(states, target_fps, hold_ms=120, min_speech_ms=50):
    """
    Applies hold hysteresis and extracts contiguous [TALK / SHOUT] speech intervals.
    """
    total_frames = len(states)
    if total_frames == 0:
        return []

    hold_frames = int(math.ceil((hold_ms / 1000.0) * target_fps))
    held_states = list(states)
    countdown = 0
    cur_held = 0

    for i in range(total_frames):
        st = states[i]
        if st > 0:
            countdown = hold_frames
            cur_held = st
        elif countdown > 0:
            held_states[i] = cur_held
            countdown -= 1
        else:
            cur_held = 0

    min_frames = int(math.ceil((min_speech_ms / 1000.0) * target_fps))
    segments = []
    in_state = 0
    seg_start = 0

    for i, st in enumerate(held_states):
        if st != in_state:
            if in_state > 0 and (i - seg_start) >= min_frames:
                label = 'SHOUT' if in_state == 2 else 'TALK'
                segments.append((label, seg_start, i))
            in_state = st
            seg_start = i

    if in_state > 0 and (total_frames - seg_start) >= min_frames:
        label = 'SHOUT' if in_state == 2 else 'TALK'
        segments.append((label, seg_start, total_frames))

    return segments

# ---------------------------------------------------------------------------
# Resolve Timeline Operations (Batched & Cached)
# ---------------------------------------------------------------------------
def get_media_folder(media_pool, folder_name="PNGtuber Sprites"):
    root_folder = media_pool.GetRootFolder()
    for sub in root_folder.GetSubFolderList():
        if sub.GetName() == folder_name:
            return sub
    new_sub = media_pool.AddSubFolder(root_folder, folder_name)
    return new_sub or root_folder

def build_media_cache(media_pool, target_folder, file_paths):
    """
    Pre-caches MediaPoolItem objects to eliminate repetitive lookups.
    """
    cache = {}
    valid_paths = [os.path.abspath(p) for p in file_paths if p and os.path.isfile(p)]
    if not valid_paths:
        return cache

    # Existing clips in folder
    for clip in target_folder.GetClipList():
        p = os.path.abspath(clip.GetClipProperty().get("File Path", ""))
        if p in valid_paths:
            cache[p] = clip

    # Import missing
    missing = [p for p in valid_paths if p not in cache]
    if missing:
        media_pool.SetCurrentFolder(target_folder)
        imported = media_pool.ImportMedia(missing)
        for clip in target_folder.GetClipList():
            p = os.path.abspath(clip.GetClipProperty().get("File Path", ""))
            if p in valid_paths:
                cache[p] = clip
    return cache

def ensure_video_tracks(timeline, required_max_track):
    current_count = timeline.GetTrackCount("video")
    while current_count < required_max_track:
        timeline.AddTrack("video")
        current_count += 1

def clear_tracks_in_range_batched(timeline, track_indices, min_frame, max_frame):
    """
    Batches deletion across all tracks in a single atomic pass.
    """
    to_delete = []
    for trk in track_indices:
        items = timeline.GetItemListInTrack("video", trk)
        if not items:
            continue
        for itm in items:
            if itm.GetStart() < max_frame and itm.GetEnd() > min_frame:
                to_delete.append(itm)
    if to_delete:
        timeline.DeleteClips(to_delete, False)

def apply_clip_transform(clip, pan=0.0, tilt=0.0, zoom=1.0, flip_x=False, opacity=100.0):
    try:
        clip.SetProperty("Pan", float(pan))
        clip.SetProperty("Tilt", float(tilt))
        clip.SetProperty("ZoomX", float(zoom))
        clip.SetProperty("ZoomY", float(zoom))
        clip.SetProperty("ZoomGang", True)
        clip.SetProperty("FlipX", bool(flip_x))
        clip.SetProperty("Opacity", float(opacity))
    except Exception as e:
        print(f"[YapPNG] Warning applying clip transform: {e}")

# ---------------------------------------------------------------------------
# Main GUI Window (UIManager)
# ---------------------------------------------------------------------------
def run_app():
    if not fusion_app:
        print("[YapPNG] Could not access Fusion. Please run inside DaVinci Resolve (Workspace > Scripts).")
        return

    ui = fusion_app.UIManager
    disp = bmd_module.UIDispatcher(ui)
    cfg = load_config()

    perf_badge = "⚡ NumPy Accelerated" if HAVE_NUMPY else "Python Native"

    win = disp.AddWindow({
        "WindowTitle": "YapPNG - Voice-Activated PNGtuber Animator",
        "ID": "YapPNGWin",
        "Geometry": [180, 40, 620, 940],
    }, [
        ui.VGroup({"Spacing": 6, "Margin": 10}, [
            # Header
            ui.Label({
                "Text": f"<b>🎙️ YapPNG v2.2</b> &nbsp; <small style='color:#03A9F4;'>{perf_badge}</small>",
                "Weight": 0,
                "StyleSheet": "font-size: 14px;"
            }),

            # ---------------- 1. CHARACTER SELECTOR ----------------
            ui.Label({"Text": "<b>1. Character Profile:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.ComboBox({"ID": "CharCombo", "Weight": 0.65}),
                ui.Button({"ID": "NewCharBtn", "Text": "+ New Char", "Weight": 0.2}),
                ui.Button({"ID": "DelCharBtn", "Text": "🗑 Del", "Weight": 0.15})
            ]),

            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Character Folder:", "Weight": 0.28}),
                ui.FileControl({"ID": "CharFolderCtrl", "Weight": 0.52}),
                ui.Button({"ID": "ScanFolderBtn", "Text": "📂 Auto-Scan", "Weight": 0.2})
            ]),

            # ---------------- 2. EXPRESSIONS & SHOUT SPRITES ----------------
            ui.Label({"Text": "<b>2. Expression Sprites:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.ComboBox({"ID": "ExprCombo", "Weight": 0.65}),
                ui.Button({"ID": "NewExprBtn", "Text": "+ New Expr", "Weight": 0.2}),
                ui.Button({"ID": "DelExprBtn", "Text": "🗑 Del", "Weight": 0.15})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Idle PNG (Closed):", "Weight": 0.3}),
                ui.FileControl({"ID": "IdleFileCtrl", "Weight": 0.7})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Talk PNG (Open):", "Weight": 0.3}),
                ui.FileControl({"ID": "TalkFileCtrl", "Weight": 0.7})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Shout PNG (Scream):", "Weight": 0.3}),
                ui.FileControl({"ID": "ShoutFileCtrl", "Weight": 0.7})
            ]),

            # ---------------- 3. SCREEN PLACEMENT, BOUNCE & DIMMING ----------------
            ui.Label({"Text": "<b>3. Placement, Dynamics & Dimming:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Layout Preset:", "Weight": 0.25}),
                ui.ComboBox({"ID": "PresetCombo", "Weight": 0.35}),
                ui.Button({"ID": "FetchLayoutBtn", "Text": "📥 Fetch from Timeline Clip", "Weight": 0.4})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Pos X (Pan):", "Weight": 0.2}),
                ui.LineEdit({"ID": "PosXEdit", "Text": "-550", "Weight": 0.25}),
                ui.Label({"Text": "Pos Y (Tilt):", "Weight": 0.2}),
                ui.LineEdit({"ID": "PosYEdit", "Text": "-150", "Weight": 0.25})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Zoom / Scale:", "Weight": 0.25}),
                ui.LineEdit({"ID": "ZoomEdit", "Text": "0.85", "Weight": 0.25}),
                ui.CheckBox({"ID": "FlipXCheck", "Text": "Flip Horizontal (Mirror)", "Checked": False, "Weight": 0.5})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.CheckBox({"ID": "BounceCheck", "Text": "🦘 Bounce Hop", "Checked": True, "Weight": 0.4}),
                ui.Label({"Text": "Hop (px):", "Weight": 0.18}),
                ui.SpinBox({"ID": "BounceSpin", "Minimum": 4, "Maximum": 50, "Value": 18, "Weight": 0.15}),
                ui.CheckBox({"ID": "DimCheck", "Text": "💡 Inactive Dim", "Checked": True, "Weight": 0.4}),
                ui.Label({"Text": "Dim (%):", "Weight": 0.18}),
                ui.SpinBox({"ID": "DimSpin", "Minimum": 30, "Maximum": 95, "Value": 70, "Weight": 0.15})
            ]),

            # ---------------- 4. AUDIO & TRACK ROUTING ----------------
            ui.Label({"Text": "<b>4. Audio & Video Track Routing:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.ComboBox({"ID": "AudioSourceCombo", "Weight": 0.5}),
                ui.Label({"Text": "Audio Track:", "Weight": 0.25}),
                ui.SpinBox({"ID": "AudioTrackSpin", "Minimum": 1, "Maximum": 16, "Value": 1, "Weight": 0.25})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Or Audio File:", "Weight": 0.3}),
                ui.FileControl({"ID": "CustomAudioCtrl", "Weight": 0.7})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Idle Video Track:", "Weight": 0.25}),
                ui.SpinBox({"ID": "BaseTrackSpin", "Minimum": 1, "Maximum": 16, "Value": 2, "Weight": 0.25}),
                ui.Label({"Text": "Talk Video Track:", "Weight": 0.25}),
                ui.SpinBox({"ID": "TalkTrackSpin", "Minimum": 1, "Maximum": 16, "Value": 3, "Weight": 0.25})
            ]),

            # ---------------- 5. SENSITIVITY & SHOUT DETECTION ----------------
            ui.Label({"Text": "<b>5. Voice & Shouting Detection:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Threshold (dB):", "Weight": 0.3}),
                ui.Slider({"ID": "ThreshSlider", "Minimum": 10, "Maximum": 60, "Value": 30, "Weight": 0.35}),
                ui.Label({"ID": "ThreshLabel", "Text": "-30 dB", "Weight": 0.12}),
                ui.Button({"ID": "CalibrateBtn", "Text": "🎙️ Auto-Calibrate", "Weight": 0.23})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.CheckBox({"ID": "ShoutCheck", "Text": "📢 Shouting / Scream Trigger:", "Checked": True, "Weight": 0.45}),
                ui.Slider({"ID": "ShoutSlider", "Minimum": 6, "Maximum": 24, "Value": 12, "Weight": 0.4}),
                ui.Label({"ID": "ShoutLabel", "Text": "-12 dB", "Weight": 0.15})
            ]),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Mouth Hold (ms):", "Weight": 0.3}),
                ui.Slider({"ID": "HoldSlider", "Minimum": 30, "Maximum": 350, "Value": 120, "Weight": 0.5}),
                ui.Label({"ID": "HoldLabel", "Text": "120 ms", "Weight": 0.2})
            ]),

            # ---------------- 6. TIMELINE ACTIONS ----------------
            ui.Label({"Text": "<b>6. Timeline Placement Mode:</b>", "Weight": 0}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Label({"Text": "Placement Mode:", "Weight": 0.28}),
                ui.ComboBox({"ID": "RangeCombo", "Weight": 0.42}),
                ui.CheckBox({"ID": "OverwriteCheck", "Text": "🧹 Clean Overwrite", "Checked": True, "Weight": 0.3})
            ]),

            ui.VGap({"Weight": 0.05}),
            ui.HGroup({"Weight": 0, "Spacing": 6}, [
                ui.Button({"ID": "PreviewBtn", "Text": "🔍 Test / Preview Detection", "Weight": 0.45}),
                ui.Button({"ID": "GenerateBtn", "Text": "▶ Splicing To Timeline", "Weight": 0.55})
            ]),

            # ---------------- STATUS BOX ----------------
            ui.VGap({"Weight": 0.05}),
            ui.Label({
                "ID": "StatusLabel",
                "Text": "Ready. Choose range or Marker-Driven mode and click Splicing.",
                "WordWrap": True,
                "StyleSheet": "background-color: #1e1e1e; border: 1px solid #333; padding: 6px; border-radius: 4px; color: #aaa;",
                "Weight": 0.3
            })
        ])
    ])

    itm = win.GetItems()

    def get_cur_char_name():
        return itm["CharCombo"].CurrentText or cfg.get("active_character", "Character_Host")

    def get_cur_char_data():
        char_name = get_cur_char_name()
        if "characters" not in cfg:
            cfg["characters"] = {}
        if char_name not in cfg["characters"]:
            cfg["characters"][char_name] = {
                "folder": "",
                "active_expression": "Neutral",
                "expressions": {"Neutral": {"idle_png": "", "talk_png": "", "shout_png": ""}},
                "audio_track_index": 1,
                "base_video_track": 2,
                "talk_video_track": 3,
                "threshold_db": -30,
                "shout_threshold_db": -12,
                "enable_shout": True,
                "hold_ms": 120,
                "min_speech_ms": 50,
                "enable_bounce": True,
                "bounce_px": 18,
                "enable_dimming": True,
                "dim_opacity": 70,
                "layout_preset": "Custom",
                "pan": 0.0,
                "tilt": 0.0,
                "zoom": 1.0,
                "flip_x": False
            }
        return cfg["characters"][char_name]

    def refresh_characters_combo():
        itm["CharCombo"].Clear()
        char_names = list(cfg.get("characters", {}).keys())
        for cname in char_names:
            itm["CharCombo"].AddItem(cname)
        active = cfg.get("active_character", "Character_Host")
        if active in char_names:
            itm["CharCombo"].CurrentIndex = char_names.index(active)
        load_character_data_into_ui()

    def load_character_data_into_ui():
        cdata = get_cur_char_data()
        itm["CharFolderCtrl"].Text = cdata.get("folder", "")
        itm["AudioTrackSpin"].Value = cdata.get("audio_track_index", 1)
        itm["BaseTrackSpin"].Value = cdata.get("base_video_track", 2)
        itm["TalkTrackSpin"].Value = cdata.get("talk_video_track", 3)

        thresh = abs(cdata.get("threshold_db", -30))
        itm["ThreshSlider"].Value = thresh
        itm["ThreshLabel"].Text = f"-{thresh} dB"

        shout_thresh = abs(cdata.get("shout_threshold_db", -12))
        itm["ShoutSlider"].Value = shout_thresh
        itm["ShoutLabel"].Text = f"-{shout_thresh} dB"
        itm["ShoutCheck"].Checked = bool(cdata.get("enable_shout", True))

        hold = cdata.get("hold_ms", 120)
        itm["HoldSlider"].Value = hold
        itm["HoldLabel"].Text = f"{hold} ms"

        # Bounce & Dimming
        itm["BounceCheck"].Checked = bool(cdata.get("enable_bounce", True))
        itm["BounceSpin"].Value = int(cdata.get("bounce_px", 18))
        itm["DimCheck"].Checked = bool(cdata.get("enable_dimming", True))
        itm["DimSpin"].Value = int(cdata.get("dim_opacity", 70))

        # Layout
        preset_name = cdata.get("layout_preset", "Custom")
        preset_list = list(PRESETS.keys())
        if preset_name in preset_list:
            itm["PresetCombo"].CurrentIndex = preset_list.index(preset_name)

        itm["PosXEdit"].Text = str(cdata.get("pan", 0.0))
        itm["PosYEdit"].Text = str(cdata.get("tilt", 0.0))
        itm["ZoomEdit"].Text = str(cdata.get("zoom", 1.0))
        itm["FlipXCheck"].Checked = bool(cdata.get("flip_x", False))

        refresh_expressions_combo()

    def refresh_expressions_combo():
        cdata = get_cur_char_data()
        itm["ExprCombo"].Clear()
        expr_list = list(cdata.get("expressions", {}).keys())
        for exp in expr_list:
            itm["ExprCombo"].AddItem(exp)
        active_expr = cdata.get("active_expression", "Neutral")
        if active_expr in expr_list:
            itm["ExprCombo"].CurrentIndex = expr_list.index(active_expr)
        load_current_expression_sprites()

    def load_current_expression_sprites():
        cdata = get_cur_char_data()
        cur_expr = itm["ExprCombo"].CurrentText
        if not cur_expr:
            return
        expr_data = cdata.get("expressions", {}).get(cur_expr, {})
        itm["IdleFileCtrl"].Text = expr_data.get("idle_png", "")
        itm["TalkFileCtrl"].Text = expr_data.get("talk_png", "")
        itm["ShoutFileCtrl"].Text = expr_data.get("shout_png", "")

    for p in PRESETS.keys():
        itm["PresetCombo"].AddItem(p)

    itm["AudioSourceCombo"].AddItem("Timeline Audio Track")
    itm["AudioSourceCombo"].AddItem("Custom Audio File")
    itm["AudioSourceCombo"].CurrentIndex = cfg.get("audio_source_type", 0)
    itm["CustomAudioCtrl"].Text = cfg.get("custom_audio_file", "")

    itm["RangeCombo"].AddItem("Mark In / Out Range")
    itm["RangeCombo"].AddItem("Entire Audio Track")
    itm["RangeCombo"].AddItem("🏷️ Marker-Driven Expressions")
    itm["RangeCombo"].CurrentIndex = cfg.get("range_mode", 0)
    itm["OverwriteCheck"].Checked = bool(cfg.get("overwrite_existing", True))

    refresh_characters_combo()

    def set_status(msg, color="#ddd"):
        print(f"[YapPNG] {msg}")
        itm["StatusLabel"].Text = f"<span style='color:{color};'>{msg}</span>"

    def save_current_ui_to_config():
        char_name = get_cur_char_name()
        cdata = get_cur_char_data()

        cfg["active_character"] = char_name
        cdata["folder"] = itm["CharFolderCtrl"].Text.strip()
        cdata["audio_track_index"] = int(itm["AudioTrackSpin"].Value)
        cdata["base_video_track"] = int(itm["BaseTrackSpin"].Value)
        cdata["talk_video_track"] = int(itm["TalkTrackSpin"].Value)
        cdata["threshold_db"] = -int(itm["ThreshSlider"].Value)
        cdata["shout_threshold_db"] = -int(itm["ShoutSlider"].Value)
        cdata["enable_shout"] = bool(itm["ShoutCheck"].Checked)
        cdata["hold_ms"] = int(itm["HoldSlider"].Value)

        cdata["enable_bounce"] = bool(itm["BounceCheck"].Checked)
        cdata["bounce_px"] = int(itm["BounceSpin"].Value)
        cdata["enable_dimming"] = bool(itm["DimCheck"].Checked)
        cdata["dim_opacity"] = int(itm["DimSpin"].Value)

        cdata["layout_preset"] = itm["PresetCombo"].CurrentText
        try:
            cdata["pan"] = float(itm["PosXEdit"].Text)
        except ValueError:
            pass
        try:
            cdata["tilt"] = float(itm["PosYEdit"].Text)
        except ValueError:
            pass
        try:
            cdata["zoom"] = float(itm["ZoomEdit"].Text)
        except ValueError:
            pass
        cdata["flip_x"] = bool(itm["FlipXCheck"].Checked)

        cur_expr = itm["ExprCombo"].CurrentText
        if cur_expr:
            cdata["active_expression"] = cur_expr
            if cur_expr in cdata.get("expressions", {}):
                cdata["expressions"][cur_expr]["idle_png"] = itm["IdleFileCtrl"].Text.strip()
                cdata["expressions"][cur_expr]["talk_png"] = itm["TalkFileCtrl"].Text.strip()
                cdata["expressions"][cur_expr]["shout_png"] = itm["ShoutFileCtrl"].Text.strip()

        cfg["audio_source_type"] = itm["AudioSourceCombo"].CurrentIndex
        cfg["custom_audio_file"] = itm["CustomAudioCtrl"].Text.strip()
        cfg["range_mode"] = itm["RangeCombo"].CurrentIndex
        cfg["overwrite_existing"] = bool(itm["OverwriteCheck"].Checked)
        save_config(cfg)

    # --- Events ---
    def _close(ev):
        save_current_ui_to_config()
        disp.ExitLoop()
    win.On.YapPNGWin.Close = _close

    def _char_changed(ev):
        save_current_ui_to_config()
        cfg["active_character"] = itm["CharCombo"].CurrentText
        load_character_data_into_ui()
    win.On.CharCombo.CurrentIndexChanged = _char_changed

    def _add_char(ev):
        save_current_ui_to_config()
        base = "Character_"
        i = 1
        while f"{base}{i}" in cfg["characters"]:
            i += 1
        new_name = f"{base}{i}"
        cfg["characters"][new_name] = {
            "folder": "",
            "active_expression": "Neutral",
            "expressions": {
                "Neutral": {"idle_png": "", "talk_png": "", "shout_png": ""}
            },
            "audio_track_index": 2,
            "base_video_track": 4,
            "talk_video_track": 5,
            "threshold_db": -30,
            "shout_threshold_db": -12,
            "enable_shout": True,
            "hold_ms": 120,
            "min_speech_ms": 50,
            "enable_bounce": True,
            "bounce_px": 18,
            "enable_dimming": True,
            "dim_opacity": 70,
            "layout_preset": "Right Side",
            "pan": 550.0,
            "tilt": -150.0,
            "zoom": 0.85,
            "flip_x": True
        }
        cfg["active_character"] = new_name
        save_config(cfg)
        refresh_characters_combo()
        set_status(f"Created new character: <b>{new_name}</b>.", "#4CAF50")
    win.On.NewCharBtn.Clicked = _add_char

    def _del_char(ev):
        cname = get_cur_char_name()
        if len(cfg["characters"]) <= 1:
            set_status("Cannot delete the only character.", "#FF9800")
            return
        if cname in cfg["characters"]:
            del cfg["characters"][cname]
            cfg["active_character"] = next(iter(cfg["characters"].keys()))
            save_config(cfg)
            refresh_characters_combo()
            set_status(f"Deleted character '{cname}'.", "#FF9800")
    win.On.DelCharBtn.Clicked = _del_char

    def _scan_folder(ev):
        folder_input = itm["CharFolderCtrl"].Text.strip()
        if not folder_input:
            set_status("Please browse or enter a Character Folder first.", "#FF9800")
            return

        cdata = get_cur_char_data()
        scanned = scan_character_folder(folder_input)
        if not scanned:
            set_status(f"No sprites found in '{folder_input}'. Use neutral_idle.png, neutral_talk.png, neutral_shout.png.", "#FF9800")
            return

        cdata["folder"] = os.path.dirname(folder_input) if os.path.isfile(folder_input) else folder_input
        cdata["expressions"] = scanned
        cdata["active_expression"] = next(iter(scanned.keys()))
        save_config(cfg)
        refresh_expressions_combo()
        set_status(f"Auto-scan complete! Found <b>{len(scanned)}</b> expressions: {', '.join(scanned.keys())}", "#4CAF50")
    win.On.ScanFolderBtn.Clicked = _scan_folder

    def _preset_changed(ev):
        pname = itm["PresetCombo"].CurrentText
        pvals = PRESETS.get(pname)
        if pvals:
            itm["PosXEdit"].Text = str(pvals["pan"])
            itm["PosYEdit"].Text = str(pvals["tilt"])
            itm["ZoomEdit"].Text = str(pvals["zoom"])
            itm["FlipXCheck"].Checked = bool(pvals["flip_x"])
            save_current_ui_to_config()
    win.On.PresetCombo.CurrentIndexChanged = _preset_changed

    def _fetch_layout_clicked(ev):
        try:
            if not resolve_app:
                raise RuntimeError("DaVinci Resolve connection not available.")
            proj = resolve_app.GetProjectManager().GetCurrentProject()
            if not proj:
                raise RuntimeError("No active DaVinci Resolve project found.")
            timeline = proj.GetCurrentTimeline()
            if not timeline:
                raise RuntimeError("No active Timeline found.")

            target_clip = timeline.GetCurrentVideoItem()
            if not target_clip:
                base_track = int(itm["BaseTrackSpin"].Value)
                clips = timeline.GetItemListInTrack("video", base_track)
                if clips and len(clips) > 0:
                    target_clip = clips[-1]

            if not target_clip:
                raise RuntimeError("No clip found to fetch position from. Select a clip on your timeline.")

            props = target_clip.GetProperty()
            pan = float(props.get("Pan", 0.0))
            tilt = float(props.get("Tilt", 0.0))
            zoom = float(props.get("ZoomX", 1.0))
            flip_x = bool(props.get("FlipX", False))

            itm["PosXEdit"].Text = f"{pan:.1f}"
            itm["PosYEdit"].Text = f"{tilt:.1f}"
            itm["ZoomEdit"].Text = f"{zoom:.3f}"
            itm["FlipXCheck"].Checked = flip_x
            itm["PresetCombo"].CurrentIndex = list(PRESETS.keys()).index("Custom")

            save_current_ui_to_config()
            set_status(f"Fetched layout from '{target_clip.GetName()}': X={pan:.1f}, Y={tilt:.1f}, Zoom={zoom:.2f}, Flip={flip_x}!", "#4CAF50")
        except Exception as e:
            set_status(f"Fetch Error: {str(e)}", "#F44336")
    win.On.FetchLayoutBtn.Clicked = _fetch_layout_clicked

    def _expr_changed(ev):
        cdata = get_cur_char_data()
        cdata["active_expression"] = itm["ExprCombo"].CurrentText
        load_current_expression_sprites()
    win.On.ExprCombo.CurrentIndexChanged = _expr_changed

    def _idle_changed(ev):
        cdata = get_cur_char_data()
        cur_expr = itm["ExprCombo"].CurrentText
        if cur_expr in cdata.get("expressions", {}):
            cdata["expressions"][cur_expr]["idle_png"] = itm["IdleFileCtrl"].Text
            save_config(cfg)
    win.On.IdleFileCtrl.EditingFinished = _idle_changed

    def _talk_changed(ev):
        cdata = get_cur_char_data()
        cur_expr = itm["ExprCombo"].CurrentText
        if cur_expr in cdata.get("expressions", {}):
            cdata["expressions"][cur_expr]["talk_png"] = itm["TalkFileCtrl"].Text
            save_config(cfg)
    win.On.TalkFileCtrl.EditingFinished = _talk_changed

    def _shout_changed(ev):
        cdata = get_cur_char_data()
        cur_expr = itm["ExprCombo"].CurrentText
        if cur_expr in cdata.get("expressions", {}):
            cdata["expressions"][cur_expr]["shout_png"] = itm["ShoutFileCtrl"].Text
            save_config(cfg)
    win.On.ShoutFileCtrl.EditingFinished = _shout_changed

    def _thresh_changed(ev):
        val = -int(ev["Value"])
        itm["ThreshLabel"].Text = f"{val} dB"
        get_cur_char_data()["threshold_db"] = val
    win.On.ThreshSlider.ValueChanged = _thresh_changed

    def _shout_slider_changed(ev):
        val = -int(ev["Value"])
        itm["ShoutLabel"].Text = f"{val} dB"
        get_cur_char_data()["shout_threshold_db"] = val
    win.On.ShoutSlider.ValueChanged = _shout_slider_changed

    def _hold_changed(ev):
        val = int(ev["Value"])
        itm["HoldLabel"].Text = f"{val} ms"
        get_cur_char_data()["hold_ms"] = val
    win.On.HoldSlider.ValueChanged = _hold_changed

    def get_timeline_zones():
        proj = resolve_app.GetProjectManager().GetCurrentProject()
        timeline = proj.GetCurrentTimeline()
        tl_start = timeline.GetStartFrame()
        tl_end = timeline.GetEndFrame()
        range_mode = itm["RangeCombo"].CurrentIndex

        cdata = get_cur_char_data()
        avail_exprs = list(cdata.get("expressions", {}).keys())
        default_expr = itm["ExprCombo"].CurrentText or "Neutral"

        if range_mode == 2:
            markers = timeline.GetMarkers()
            if not markers:
                raise RuntimeError("No timeline markers found! Press 'M' to add markers named after expressions (e.g. 'Happy', 'Angry').")

            sorted_marks = sorted([(int(float(f)), m.get('name', '').strip()) for f, m in markers.items()])
            zones = []
            cur_expr = default_expr
            prev_frame = tl_start

            for f, name in sorted_marks:
                matched = None
                for exp in avail_exprs:
                    if exp.lower() in name.lower():
                        matched = exp
                        break
                if f > prev_frame:
                    zones.append((prev_frame, f, cur_expr))
                if matched:
                    cur_expr = matched
                prev_frame = f

            if prev_frame < tl_end:
                zones.append((prev_frame, tl_end, cur_expr))
            return zones

        elif range_mode == 0:
            target_start = tl_start
            target_end = tl_end
            marks = timeline.GetMarkInOut()
            v_mark = marks.get("video") if isinstance(marks, dict) else None
            if not v_mark and isinstance(marks, dict):
                v_mark = marks.get("audio")
            if v_mark and isinstance(v_mark, dict) and "in" in v_mark and "out" in v_mark:
                if v_mark["out"] > v_mark["in"]:
                    target_start = int(v_mark["in"])
                    target_end = int(v_mark["out"])
            return [(target_start, target_end, default_expr)]

        else:
            return [(tl_start, tl_end, default_expr)]

    # Single-pass optimized audio extraction for all zones combined
    def extract_full_audio_for_zones(zones):
        proj = resolve_app.GetProjectManager().GetCurrentProject()
        timeline = proj.GetCurrentTimeline()
        fps = float(timeline.GetSetting("timelineFrameRate"))

        min_frame = min(z[0] for z in zones)
        max_frame = max(z[1] for z in zones)

        audio_src_type = itm["AudioSourceCombo"].CurrentIndex
        pcm_bytes = None

        if audio_src_type == 1:
            file_path = itm["CustomAudioCtrl"].Text.strip()
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Custom audio file does not exist: {file_path}")
            duration_sec = (max_frame - min_frame) / fps
            pcm_bytes = extract_pcm_from_file(file_path, start_sec=0.0, duration_sec=duration_sec)
        else:
            track_idx = int(itm["AudioTrackSpin"].Value)
            items = timeline.GetItemListInTrack("audio", track_idx)
            if not items:
                raise RuntimeError(f"No audio clips found on Audio Track {track_idx}.")

            chosen_item = None
            for itm_clip in items:
                c_start = itm_clip.GetStart()
                c_end = itm_clip.GetEnd()
                if c_end > min_frame and c_start < max_frame:
                    chosen_item = itm_clip
                    break

            if not chosen_item:
                raise RuntimeError(f"No audio clip spans the target range on Audio Track {track_idx}.")

            clip_start = chosen_item.GetStart()
            clip_end = chosen_item.GetEnd()
            source_start = chosen_item.GetSourceStartFrame()
            media_pool_item = chosen_item.GetMediaPoolItem()
            file_path = media_pool_item.GetClipProperty("File Path")

            overlap_start = max(min_frame, clip_start)
            overlap_end = min(max_frame, clip_end)
            source_offset_frame = source_start + (overlap_start - clip_start)

            start_sec = source_offset_frame / fps
            dur_sec = (overlap_end - overlap_start) / fps

            pcm_bytes = extract_pcm_from_file(file_path, start_sec=start_sec, duration_sec=dur_sec)

        db_array = compute_frame_db_vectorized(pcm_bytes, 16000, fps)
        return {
            "fps": fps,
            "min_frame": min_frame,
            "max_frame": max_frame,
            "db_array": db_array,
            "pcm_bytes": pcm_bytes
        }

    def _calibrate_clicked(ev):
        try:
            set_status("Sampling background audio noise...", "#03A9F4")
            zones = get_timeline_zones()
            full_audio = extract_full_audio_for_zones(zones)
            pcm = full_audio["pcm_bytes"]
            noise_db, target_thresh = calibrate_noise_floor(pcm, sample_rate=16000)
            abs_val = abs(target_thresh)
            itm["ThreshSlider"].Value = abs_val
            itm["ThreshLabel"].Text = f"{target_thresh} dB"
            get_cur_char_data()["threshold_db"] = target_thresh
            save_current_ui_to_config()
            set_status(f"Calibrated! Noise: <b>{noise_db:.1f} dB</b>. Threshold set to: <b>{target_thresh} dB</b>.", "#4CAF50")
        except Exception as e:
            set_status(f"Calibration Error: {str(e)}", "#F44336")
    win.On.CalibrateBtn.Clicked = _calibrate_clicked

    def _preview_clicked(ev):
        try:
            save_current_ui_to_config()
            set_status("Analyzing audio detection...", "#03A9F4")
            zones = get_timeline_zones()
            full_audio = extract_full_audio_for_zones(zones)

            db_array = full_audio["db_array"]
            fps = full_audio["fps"]
            min_frame = full_audio["min_frame"]

            thresh_db = -int(itm["ThreshSlider"].Value)
            shout_thresh_db = -int(itm["ShoutSlider"].Value)
            enable_shout = bool(itm["ShoutCheck"].Checked)
            hold_ms = int(itm["HoldSlider"].Value)

            # Vectorized state classification
            all_states = classify_frame_states(db_array, thresh_db, shout_thresh_db, enable_shout)

            total_talk = 0
            total_shout = 0
            total_dur_sec = (full_audio["max_frame"] - full_audio["min_frame"]) / fps

            for z_start, z_end, _ in zones:
                idx_start = max(0, z_start - min_frame)
                idx_end = min(len(all_states), z_end - min_frame)
                zone_states = all_states[idx_start:idx_end]
                segs = extract_segments_from_states(zone_states, fps, hold_ms=hold_ms)
                total_talk += sum(1 for label, _, _ in segs if label == 'TALK')
                total_shout += sum(1 for label, _, _ in segs if label == 'SHOUT')

            set_status(
                f"Preview ({len(zones)} zones): Found <b>{total_talk}</b> Talk + <b>{total_shout}</b> Shout bursts "
                f"across {total_dur_sec:.1f}s total.",
                "#4CAF50"
            )
        except Exception as e:
            set_status(f"Preview Error: {str(e)}", "#F44336")
    win.On.PreviewBtn.Clicked = _preview_clicked

    def _generate_clicked(ev):
        try:
            save_current_ui_to_config()
            set_status("Single-pass audio decode & media pre-caching...", "#03A9F4")

            proj = resolve_app.GetProjectManager().GetCurrentProject()
            timeline = proj.GetCurrentTimeline()
            media_pool = proj.GetMediaPool()

            zones = get_timeline_zones()
            char_name = get_cur_char_name()
            cdata = get_cur_char_data()

            base_track = int(itm["BaseTrackSpin"].Value)
            talk_track = int(itm["TalkTrackSpin"].Value)
            ensure_video_tracks(timeline, max(base_track, talk_track))

            # Transform & Physics Parameters
            pan = float(cdata.get("pan", 0.0))
            tilt = float(cdata.get("tilt", 0.0))
            zoom = float(cdata.get("zoom", 1.0))
            flip_x = bool(cdata.get("flip_x", False))

            enable_bounce = bool(cdata.get("enable_bounce", True))
            bounce_px = float(cdata.get("bounce_px", 18))

            enable_dim = bool(cdata.get("enable_dimming", True))
            dim_opacity = float(cdata.get("dim_opacity", 70))
            idle_opacity = dim_opacity if enable_dim else 100.0

            # 1. Pre-Cache all Media Pool items in one shot
            folder = get_media_folder(media_pool, f"PNGtuber - {char_name}")
            all_paths = []
            for z_exp in cdata.get("expressions", {}).values():
                for k in ("idle_png", "talk_png", "shout_png"):
                    if z_exp.get(k):
                        all_paths.append(z_exp[k])
            media_cache = build_media_cache(media_pool, folder, all_paths)

            # 2. Extract full audio in single pass
            full_audio = extract_full_audio_for_zones(zones)
            db_array = full_audio["db_array"]
            fps = full_audio["fps"]
            min_frame = full_audio["min_frame"]
            max_frame = full_audio["max_frame"]

            thresh_db = -int(itm["ThreshSlider"].Value)
            shout_thresh_db = -int(itm["ShoutSlider"].Value)
            enable_shout = bool(itm["ShoutCheck"].Checked)
            hold_ms = int(itm["HoldSlider"].Value)

            all_states = classify_frame_states(db_array, thresh_db, shout_thresh_db, enable_shout)

            # 3. Batched timeline overwrite
            if itm["OverwriteCheck"].Checked:
                clear_tracks_in_range_batched(timeline, [base_track, talk_track], min_frame, max_frame)

            total_cuts_made = 0

            # 4. Splicing loop (pure in-memory slicing)
            for z_idx, (z_start, z_end, z_expr) in enumerate(zones):
                expr_dict = cdata.get("expressions", {}).get(z_expr, {})
                idle_path = os.path.abspath(expr_dict.get("idle_png", ""))
                talk_path = os.path.abspath(expr_dict.get("talk_png", ""))
                shout_path = os.path.abspath(expr_dict.get("shout_png", "")) or talk_path

                idle_item = media_cache.get(idle_path)
                talk_item = media_cache.get(talk_path)
                shout_item = media_cache.get(shout_path) or talk_item

                if not idle_item or not talk_item:
                    continue

                zone_span = z_end - z_start
                if zone_span <= 0:
                    continue

                # Place Base Idle Clip
                idle_subclip = {
                    "mediaPoolItem": idle_item,
                    "startFrame": 0,
                    "endFrame": zone_span,
                    "trackIndex": base_track,
                    "recordFrame": z_start,
                    "mediaType": 1
                }
                new_idle = media_pool.AppendToTimeline([idle_subclip])
                if new_idle:
                    for c in new_idle:
                        apply_clip_transform(c, pan=pan, tilt=tilt, zoom=zoom, flip_x=flip_x, opacity=idle_opacity)

                # Slice speech segments from precomputed states
                idx_start = max(0, z_start - min_frame)
                idx_end = min(len(all_states), z_end - min_frame)
                zone_states = all_states[idx_start:idx_end]
                speech_segments = extract_segments_from_states(zone_states, fps, hold_ms=hold_ms)

                if speech_segments:
                    talk_clips = []
                    seg_labels = []
                    for label, s_start, s_end in speech_segments:
                        dur = s_end - s_start
                        rec = z_start + s_start
                        use_item = shout_item if (label == 'SHOUT' and shout_item) else talk_item
                        talk_clips.append({
                            "mediaPoolItem": use_item,
                            "startFrame": 0,
                            "endFrame": dur,
                            "trackIndex": talk_track,
                            "recordFrame": rec,
                            "mediaType": 1
                        })
                        seg_labels.append(label)

                    new_talk = media_pool.AppendToTimeline(talk_clips)
                    if new_talk:
                        for i, c in enumerate(new_talk):
                            lbl = seg_labels[i] if i < len(seg_labels) else 'TALK'
                            c_tilt = tilt
                            c_zoom = zoom
                            if enable_bounce:
                                if lbl == 'SHOUT':
                                    c_tilt = tilt + (bounce_px * 1.6)
                                    c_zoom = zoom * 1.05
                                else:
                                    c_tilt = tilt + bounce_px
                                    c_zoom = zoom * 1.025
                            apply_clip_transform(c, pan=pan, tilt=c_tilt, zoom=c_zoom, flip_x=flip_x, opacity=100.0)
                        total_cuts_made += len(new_talk)

            set_status(
                f"Done! Fast-spliced <b>{len(zones)} zones</b> with {total_cuts_made} cuts in one pass.",
                "#4CAF50"
            )
        except Exception as e:
            set_status(f"Generation Error: {str(e)}", "#F44336")
    win.On.GenerateBtn.Clicked = _generate_clicked

    # Show window
    win.Show()
    disp.RunLoop()
    win.Hide()

if __name__ == "__main__":
    run_app()
