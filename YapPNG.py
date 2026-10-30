#!/usr/bin/env python
"""
=============================================================================
YapPNG for DaVinci Resolve (v2.2 Ultra - Universal Free & Studio Edition)
- Universal Dark GUI (Works on both Free & Studio, bypasses UIManager lock)
- Vectorized VAD Engine (NumPy Prefix-Sum + Array Fallback)
- Single-Pass Audio Decoding & In-Memory Slicing
- Multi-Clip Timeline Audio Aggregation & Frame Sync
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
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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

if not resolve_app and bmd_module:
    try:
        resolve_app = bmd_module.scriptapp("Resolve")
    except Exception:
        pass

if not resolve_app:
    try:
        import DaVinciResolveScript as dvr_script
        resolve_app = dvr_script.scriptapp("Resolve")
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
    "overwrite_existing": True,
    "stay_on_top": True
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
    cache = {}
    valid_paths = [os.path.abspath(p) for p in file_paths if p and os.path.isfile(p)]
    if not valid_paths:
        return cache

    for clip in target_folder.GetClipList():
        p = os.path.abspath(clip.GetClipProperty().get("File Path", ""))
        if p in valid_paths:
            cache[p] = clip

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
# Universal Dark UI (Tkinter - Works in both Free & Studio)
# ---------------------------------------------------------------------------
def run_app():
    cfg = load_config()

    root = tk.Tk()
    root.title("YapPNG v2.2 - Voice-Activated PNGtuber Animator")
    root.geometry("620x820")
    root.minsize(580, 720)
    root.configure(bg="#1e1e1e")

    if cfg.get("stay_on_top", True):
        root.attributes("-topmost", True)

    # Dark Styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background="#1e1e1e", foreground="#dddddd", font=("Segoe UI", 9))
    style.configure("TLabel", background="#1e1e1e", foreground="#dddddd")
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#00aaff")
    style.configure("Section.TLabel", font=("Segoe UI", 9, "bold"), foreground="#ffffff")
    style.configure("TButton", background="#2d2d2d", foreground="#ffffff", borderwidth=1, padding=4)
    style.map("TButton", background=[("active", "#0e639c"), ("pressed", "#1177bb")])
    style.configure("Action.TButton", background="#0e639c", foreground="#ffffff", font=("Segoe UI", 9, "bold"))
    style.map("Action.TButton", background=[("active", "#1177bb")])
    style.configure("TEntry", fieldbackground="#2b2b2b", foreground="#ffffff", insertcolor="#ffffff")
    style.configure("TCombobox", fieldbackground="#2b2b2b", foreground="#ffffff")
    style.configure("TSpinbox", fieldbackground="#2b2b2b", foreground="#ffffff")
    style.configure("TCheckbutton", background="#1e1e1e", foreground="#dddddd")
    style.map("TCheckbutton", background=[("active", "#1e1e1e")])
    style.configure("Horizontal.TScale", background="#1e1e1e", troughcolor="#2b2b2b")

    # Main Scrollable Frame Container
    canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def _on_canvas_configure(e):
        canvas.itemconfig(canvas_window, width=e.width)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    root.bind_all("<MouseWheel>", _on_mousewheel)

    # UI Variables
    var_char_name = tk.StringVar(value=cfg.get("active_character", "Character_Host"))
    var_char_folder = tk.StringVar()
    var_expr_name = tk.StringVar(value="Neutral")
    var_idle_png = tk.StringVar()
    var_talk_png = tk.StringVar()
    var_shout_png = tk.StringVar()

    var_preset = tk.StringVar(value="Left Side")
    var_pos_x = tk.StringVar(value="-550.0")
    var_pos_y = tk.StringVar(value="-150.0")
    var_zoom = tk.StringVar(value="0.85")
    var_flip_x = tk.BooleanVar(value=False)
    var_bounce = tk.BooleanVar(value=True)
    var_bounce_px = tk.IntVar(value=18)
    var_dim = tk.BooleanVar(value=True)
    var_dim_pct = tk.IntVar(value=70)

    var_audio_src = tk.StringVar(value="Timeline Audio Track")
    var_audio_track = tk.IntVar(value=1)
    var_audio_file = tk.StringVar(value=cfg.get("custom_audio_file", ""))
    var_base_track = tk.IntVar(value=2)
    var_talk_track = tk.IntVar(value=3)

    var_thresh = tk.IntVar(value=30)
    var_shout_thresh = tk.IntVar(value=12)
    var_enable_shout = tk.BooleanVar(value=True)
    var_hold_ms = tk.IntVar(value=120)

    var_range_mode = tk.StringVar(value="Mark In / Out Range")
    var_overwrite = tk.BooleanVar(value=True)
    var_stay_on_top = tk.BooleanVar(value=bool(cfg.get("stay_on_top", True)))

    # --- Header ---
    perf_badge = "⚡ NumPy Accelerated" if HAVE_NUMPY else "Python Native"
    header_frame = ttk.Frame(scroll_frame)
    header_frame.pack(fill="x", padx=14, pady=(10, 6))
    ttk.Label(header_frame, text="🎙️ YapPNG v2.2", style="Header.TLabel").pack(side="left")
    ttk.Label(header_frame, text=perf_badge, foreground="#00aaff").pack(side="left", padx=10)

    def _toggle_on_top():
        root.attributes("-topmost", var_stay_on_top.get())
        cfg["stay_on_top"] = var_stay_on_top.get()
        save_config(cfg)
    ttk.Checkbutton(header_frame, text="Stay on Top", variable=var_stay_on_top, command=_toggle_on_top).pack(side="right")

    # Helper: Separator line
    def add_separator():
        sep = tk.Frame(scroll_frame, height=1, bg="#333333")
        sep.pack(fill="x", padx=14, pady=6)

    # ---------------- SECTION 1: CHARACTER PROFILE ----------------
    f1 = ttk.LabelFrame(scroll_frame, text=" 1. Character Profile ", padding=8)
    f1.pack(fill="x", padx=14, pady=4)

    r1 = ttk.Frame(f1)
    r1.pack(fill="x", pady=2)
    ttk.Label(r1, text="Character:").pack(side="left")
    char_combo = ttk.Combobox(r1, textvariable=var_char_name, state="readonly", width=22)
    char_combo.pack(side="left", padx=6)
    btn_new_char = ttk.Button(r1, text="+ New Char")
    btn_new_char.pack(side="left", padx=2)
    btn_del_char = ttk.Button(r1, text="🗑 Del")
    btn_del_char.pack(side="left", padx=2)

    r2 = ttk.Frame(f1)
    r2.pack(fill="x", pady=(6, 2))
    ttk.Label(r2, text="Folder:").pack(side="left")
    ttk.Entry(r2, textvariable=var_char_folder).pack(side="left", fill="x", expand=True, padx=6)
    def _browse_folder():
        d = filedialog.askdirectory(title="Select Character Folder")
        if d:
            var_char_folder.set(d)
            _scan_folder()
    ttk.Button(r2, text="Browse...", command=_browse_folder).pack(side="left", padx=2)
    btn_scan_folder = ttk.Button(r2, text="📂 Auto-Scan")
    btn_scan_folder.pack(side="left", padx=2)

    # ---------------- SECTION 2: EXPRESSION SPRITES ----------------
    f2 = ttk.LabelFrame(scroll_frame, text=" 2. Expression Sprites ", padding=8)
    f2.pack(fill="x", padx=14, pady=4)

    er1 = ttk.Frame(f2)
    er1.pack(fill="x", pady=2)
    ttk.Label(er1, text="Expression:").pack(side="left")
    expr_combo = ttk.Combobox(er1, textvariable=var_expr_name, state="readonly", width=22)
    expr_combo.pack(side="left", padx=6)
    btn_new_expr = ttk.Button(er1, text="+ New Expr")
    btn_new_expr.pack(side="left", padx=2)
    btn_del_expr = ttk.Button(er1, text="🗑 Del")
    btn_del_expr.pack(side="left", padx=2)

    # Sprite pickers
    def make_file_row(parent, label_text, str_var):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label_text, width=16, anchor="w").pack(side="left")
        ttk.Entry(row, textvariable=str_var).pack(side="left", fill="x", expand=True, padx=6)
        def _browse():
            f = filedialog.askopenfilename(
                title=f"Select {label_text}",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp"), ("All Files", "*.*")]
            )
            if f:
                str_var.set(f)
                save_ui_to_config()
        ttk.Button(row, text="Browse...", command=_browse).pack(side="left")

    make_file_row(f2, "Idle (Closed):", var_idle_png)
    make_file_row(f2, "Talk (Open):", var_talk_png)
    make_file_row(f2, "Shout (Scream):", var_shout_png)

    # ---------------- SECTION 3: PLACEMENT & DYNAMICS ----------------
    f3 = ttk.LabelFrame(scroll_frame, text=" 3. Placement, Dynamics & Dimming ", padding=8)
    f3.pack(fill="x", padx=14, pady=4)

    pr1 = ttk.Frame(f3)
    pr1.pack(fill="x", pady=2)
    ttk.Label(pr1, text="Preset:").pack(side="left")
    preset_combo = ttk.Combobox(pr1, textvariable=var_preset, values=list(PRESETS.keys()), state="readonly", width=14)
    preset_combo.pack(side="left", padx=6)
    btn_fetch = ttk.Button(pr1, text="📥 Fetch from Timeline Clip")
    btn_fetch.pack(side="left", padx=6)

    pr2 = ttk.Frame(f3)
    pr2.pack(fill="x", pady=4)
    ttk.Label(pr2, text="Pos X:").pack(side="left")
    ttk.Entry(pr2, textvariable=var_pos_x, width=8).pack(side="left", padx=4)
    ttk.Label(pr2, text="Pos Y:").pack(side="left", padx=(8, 0))
    ttk.Entry(pr2, textvariable=var_pos_y, width=8).pack(side="left", padx=4)
    ttk.Label(pr2, text="Zoom:").pack(side="left", padx=(8, 0))
    ttk.Entry(pr2, textvariable=var_zoom, width=8).pack(side="left", padx=4)
    ttk.Checkbutton(pr2, text="Flip Horizontal", variable=var_flip_x).pack(side="left", padx=(10, 0))

    pr3 = ttk.Frame(f3)
    pr3.pack(fill="x", pady=2)
    ttk.Checkbutton(pr3, text="🦘 Bounce Hop", variable=var_bounce).pack(side="left")
    ttk.Label(pr3, text="Hop (px):").pack(side="left", padx=(6, 2))
    ttk.Spinbox(pr3, from_=4, to=50, textvariable=var_bounce_px, width=5).pack(side="left")
    ttk.Checkbutton(pr3, text="💡 Inactive Dim", variable=var_dim).pack(side="left", padx=(14, 0))
    ttk.Label(pr3, text="Dim (%):").pack(side="left", padx=(6, 2))
    ttk.Spinbox(pr3, from_=30, to=95, textvariable=var_dim_pct, width=5).pack(side="left")

    # ---------------- SECTION 4: AUDIO & TRACK ROUTING ----------------
    f4 = ttk.LabelFrame(scroll_frame, text=" 4. Audio & Track Routing ", padding=8)
    f4.pack(fill="x", padx=14, pady=4)

    ar1 = ttk.Frame(f4)
    ar1.pack(fill="x", pady=2)
    ttk.Label(ar1, text="Audio Source:").pack(side="left")
    audio_src_combo = ttk.Combobox(ar1, textvariable=var_audio_src, values=["Timeline Audio Track", "Custom Audio File"], state="readonly", width=18)
    audio_src_combo.pack(side="left", padx=6)
    ttk.Label(ar1, text="Audio Track:").pack(side="left", padx=(8, 2))
    ttk.Spinbox(ar1, from_=1, to=16, textvariable=var_audio_track, width=5).pack(side="left")

    ar2 = ttk.Frame(f4)
    ar2.pack(fill="x", pady=2)
    ttk.Label(ar2, text="Or Audio File:", width=14, anchor="w").pack(side="left")
    ttk.Entry(ar2, textvariable=var_audio_file).pack(side="left", fill="x", expand=True, padx=6)
    def _browse_audio():
        f = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a;*.flac;*.aac;*.mp4;*.mov"), ("All Files", "*.*")]
        )
        if f:
            var_audio_file.set(f)
    ttk.Button(ar2, text="Browse...", command=_browse_audio).pack(side="left")

    ar3 = ttk.Frame(f4)
    ar3.pack(fill="x", pady=2)
    ttk.Label(ar3, text="Idle Video Track:").pack(side="left")
    ttk.Spinbox(ar3, from_=1, to=24, textvariable=var_base_track, width=5).pack(side="left", padx=6)
    ttk.Label(ar3, text="Talk Video Track:").pack(side="left", padx=(12, 0))
    ttk.Spinbox(ar3, from_=1, to=24, textvariable=var_talk_track, width=5).pack(side="left", padx=6)

    # ---------------- SECTION 5: SENSITIVITY & SHOUT DETECTION ----------------
    f5 = ttk.LabelFrame(scroll_frame, text=" 5. Voice & Shouting Detection ", padding=8)
    f5.pack(fill="x", padx=14, pady=4)

    sr1 = ttk.Frame(f5)
    sr1.pack(fill="x", pady=2)
    lbl_thresh_val = ttk.Label(sr1, text="-30 dB", width=8)
    ttk.Label(sr1, text="Threshold:").pack(side="left")
    scale_thresh = ttk.Scale(sr1, from_=10, to=60, variable=var_thresh, orient="horizontal")
    scale_thresh.pack(side="left", fill="x", expand=True, padx=8)
    lbl_thresh_val.pack(side="left")
    btn_calibrate = ttk.Button(sr1, text="🎙️ Auto-Calibrate")
    btn_calibrate.pack(side="left", padx=4)

    def _update_thresh_lbl(*args):
        lbl_thresh_val.config(text=f"-{var_thresh.get()} dB")
    var_thresh.trace_add("write", _update_thresh_lbl)

    sr2 = ttk.Frame(f5)
    sr2.pack(fill="x", pady=2)
    lbl_shout_val = ttk.Label(sr2, text="-12 dB", width=8)
    ttk.Checkbutton(sr2, text="📢 Shouting Trigger:", variable=var_enable_shout).pack(side="left")
    scale_shout = ttk.Scale(sr2, from_=6, to=24, variable=var_shout_thresh, orient="horizontal")
    scale_shout.pack(side="left", fill="x", expand=True, padx=8)
    lbl_shout_val.pack(side="left")

    def _update_shout_lbl(*args):
        lbl_shout_val.config(text=f"-{var_shout_thresh.get()} dB")
    var_shout_thresh.trace_add("write", _update_shout_lbl)

    sr3 = ttk.Frame(f5)
    sr3.pack(fill="x", pady=2)
    lbl_hold_val = ttk.Label(sr3, text="120 ms", width=8)
    ttk.Label(sr3, text="Mouth Hold:").pack(side="left")
    scale_hold = ttk.Scale(sr3, from_=30, to=350, variable=var_hold_ms, orient="horizontal")
    scale_hold.pack(side="left", fill="x", expand=True, padx=8)
    lbl_hold_val.pack(side="left")

    def _update_hold_lbl(*args):
        lbl_hold_val.config(text=f"{var_hold_ms.get()} ms")
    var_hold_ms.trace_add("write", _update_hold_lbl)

    # ---------------- SECTION 6: ACTIONS & STATUS ----------------
    f6 = ttk.LabelFrame(scroll_frame, text=" 6. Timeline Splicing ", padding=8)
    f6.pack(fill="x", padx=14, pady=4)

    act_r1 = ttk.Frame(f6)
    act_r1.pack(fill="x", pady=2)
    ttk.Label(act_r1, text="Mode:").pack(side="left")
    range_combo = ttk.Combobox(
        act_r1,
        textvariable=var_range_mode,
        values=["Mark In / Out Range", "Entire Audio Track", "🏷️ Marker-Driven Expressions"],
        state="readonly",
        width=26
    )
    range_combo.pack(side="left", padx=6)
    ttk.Checkbutton(act_r1, text="🧹 Clean Overwrite", variable=var_overwrite).pack(side="left", padx=8)

    act_r2 = ttk.Frame(f6)
    act_r2.pack(fill="x", pady=(8, 2))
    btn_preview = ttk.Button(act_r2, text="🔍 Test / Preview Detection")
    btn_preview.pack(side="left", fill="x", expand=True, padx=3)
    btn_generate = ttk.Button(act_r2, text="▶ Splicing To Timeline", style="Action.TButton")
    btn_generate.pack(side="left", fill="x", expand=True, padx=3)

    # Status Label
    lbl_status = tk.Label(
        scroll_frame,
        text="Ready. Select character, set In/Out marks on timeline, and click Splicing.",
        bg="#252526",
        fg="#aaaaaa",
        relief="groove",
        padx=10,
        pady=8,
        wraplength=540,
        justify="left"
    )
    lbl_status.pack(fill="x", padx=14, pady=(8, 14))

    def set_status(msg, color="#ffffff"):
        print(f"[YapPNG] {msg}")
        lbl_status.config(text=msg, fg=color)

    # --- Data Binding Logic ---
    def get_cur_char_data():
        cname = var_char_name.get()
        if "characters" not in cfg:
            cfg["characters"] = {}
        if cname not in cfg["characters"]:
            cfg["characters"][cname] = {
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
        return cfg["characters"][cname]

    def refresh_characters_ui():
        cnames = list(cfg.get("characters", {}).keys())
        char_combo["values"] = cnames
        cur = cfg.get("active_character", "Character_Host")
        if cur in cnames:
            var_char_name.set(cur)
        elif cnames:
            var_char_name.set(cnames[0])
        load_character_into_ui()

    def load_character_into_ui():
        cdata = get_cur_char_data()
        var_char_folder.set(cdata.get("folder", ""))
        var_audio_track.set(cdata.get("audio_track_index", 1))
        var_base_track.set(cdata.get("base_video_track", 2))
        var_talk_track.set(cdata.get("talk_video_track", 3))

        var_thresh.set(abs(cdata.get("threshold_db", -30)))
        var_shout_thresh.set(abs(cdata.get("shout_threshold_db", -12)))
        var_enable_shout.set(bool(cdata.get("enable_shout", True)))
        var_hold_ms.set(cdata.get("hold_ms", 120))

        var_bounce.set(bool(cdata.get("enable_bounce", True)))
        var_bounce_px.set(int(cdata.get("bounce_px", 18)))
        var_dim.set(bool(cdata.get("enable_dimming", True)))
        var_dim_pct.set(int(cdata.get("dim_opacity", 70)))

        var_preset.set(cdata.get("layout_preset", "Custom"))
        var_pos_x.set(str(cdata.get("pan", 0.0)))
        var_pos_y.set(str(cdata.get("tilt", 0.0)))
        var_zoom.set(str(cdata.get("zoom", 1.0)))
        var_flip_x.set(bool(cdata.get("flip_x", False)))

        refresh_expressions_ui()

    def refresh_expressions_ui():
        cdata = get_cur_char_data()
        enames = list(cdata.get("expressions", {}).keys())
        expr_combo["values"] = enames
        active = cdata.get("active_expression", "Neutral")
        if active in enames:
            var_expr_name.set(active)
        elif enames:
            var_expr_name.set(enames[0])
        load_expression_sprites()

    def load_expression_sprites():
        cdata = get_cur_char_data()
        cur_exp = var_expr_name.get()
        edata = cdata.get("expressions", {}).get(cur_exp, {})
        var_idle_png.set(edata.get("idle_png", ""))
        var_talk_png.set(edata.get("talk_png", ""))
        var_shout_png.set(edata.get("shout_png", ""))

    def save_ui_to_config():
        cname = var_char_name.get()
        cdata = get_cur_char_data()

        cfg["active_character"] = cname
        cdata["folder"] = var_char_folder.get().strip()
        cdata["audio_track_index"] = var_audio_track.get()
        cdata["base_video_track"] = var_base_track.get()
        cdata["talk_video_track"] = var_talk_track.get()
        cdata["threshold_db"] = -var_thresh.get()
        cdata["shout_threshold_db"] = -var_shout_thresh.get()
        cdata["enable_shout"] = var_enable_shout.get()
        cdata["hold_ms"] = var_hold_ms.get()

        cdata["enable_bounce"] = var_bounce.get()
        cdata["bounce_px"] = var_bounce_px.get()
        cdata["enable_dimming"] = var_dim.get()
        cdata["dim_opacity"] = var_dim_pct.get()

        cdata["layout_preset"] = var_preset.get()
        try:
            cdata["pan"] = float(var_pos_x.get())
        except ValueError:
            pass
        try:
            cdata["tilt"] = float(var_pos_y.get())
        except ValueError:
            pass
        try:
            cdata["zoom"] = float(var_zoom.get())
        except ValueError:
            pass
        cdata["flip_x"] = var_flip_x.get()

        cur_exp = var_expr_name.get()
        if cur_exp:
            cdata["active_expression"] = cur_exp
            if cur_exp in cdata.get("expressions", {}):
                cdata["expressions"][cur_exp]["idle_png"] = var_idle_png.get().strip()
                cdata["expressions"][cur_exp]["talk_png"] = var_talk_png.get().strip()
                cdata["expressions"][cur_exp]["shout_png"] = var_shout_png.get().strip()

        cfg["audio_source_type"] = 1 if var_audio_src.get() == "Custom Audio File" else 0
        cfg["custom_audio_file"] = var_audio_file.get().strip()

        rmode_map = {"Mark In / Out Range": 0, "Entire Audio Track": 1, "🏷️ Marker-Driven Expressions": 2}
        cfg["range_mode"] = rmode_map.get(var_range_mode.get(), 0)
        cfg["overwrite_existing"] = var_overwrite.get()
        save_config(cfg)

    # Event handlers
    def _on_char_change(event):
        save_ui_to_config()
        cfg["active_character"] = var_char_name.get()
        load_character_into_ui()
    char_combo.bind("<<ComboboxSelected>>", _on_char_change)

    def _on_expr_change(event):
        save_ui_to_config()
        cdata = get_cur_char_data()
        cdata["active_expression"] = var_expr_name.get()
        load_expression_sprites()
    expr_combo.bind("<<ComboboxSelected>>", _on_expr_change)

    def _on_preset_change(event):
        pname = var_preset.get()
        pvals = PRESETS.get(pname)
        if pvals:
            var_pos_x.set(str(pvals["pan"]))
            var_pos_y.set(str(pvals["tilt"]))
            var_zoom.set(str(pvals["zoom"]))
            var_flip_x.set(bool(pvals["flip_x"]))
            save_ui_to_config()
    preset_combo.bind("<<ComboboxSelected>>", _on_preset_change)

    def _new_char():
        save_ui_to_config()
        base = "Character_"
        i = 1
        while f"{base}{i}" in cfg["characters"]:
            i += 1
        nname = f"{base}{i}"
        cfg["characters"][nname] = {
            "folder": "",
            "active_expression": "Neutral",
            "expressions": {"Neutral": {"idle_png": "", "talk_png": "", "shout_png": ""}},
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
        cfg["active_character"] = nname
        save_config(cfg)
        refresh_characters_ui()
        set_status(f"Created new character: '{nname}'.", "#4CAF50")
    btn_new_char.config(command=_new_char)

    def _del_char():
        cname = var_char_name.get()
        if len(cfg["characters"]) <= 1:
            set_status("Cannot delete the only character.", "#FF9800")
            return
        if cname in cfg["characters"]:
            del cfg["characters"][cname]
            cfg["active_character"] = next(iter(cfg["characters"].keys()))
            save_config(cfg)
            refresh_characters_ui()
            set_status(f"Deleted character '{cname}'.", "#FF9800")
    btn_del_char.config(command=_del_char)

    def _new_expr():
        cdata = get_cur_char_data()
        base = "Expression_"
        i = 1
        while f"{base}{i}" in cdata["expressions"]:
            i += 1
        nname = f"{base}{i}"
        cdata["expressions"][nname] = {"idle_png": "", "talk_png": "", "shout_png": ""}
        cdata["active_expression"] = nname
        save_config(cfg)
        refresh_expressions_ui()
        set_status(f"Added expression '{nname}'.", "#4CAF50")
    btn_new_expr.config(command=_new_expr)

    def _del_expr():
        cdata = get_cur_char_data()
        ename = var_expr_name.get()
        if len(cdata["expressions"]) <= 1:
            set_status("Cannot delete the only expression.", "#FF9800")
            return
        if ename in cdata["expressions"]:
            del cdata["expressions"][ename]
            cdata["active_expression"] = next(iter(cdata["expressions"].keys()))
            save_config(cfg)
            refresh_expressions_ui()
            set_status(f"Deleted expression '{ename}'.", "#FF9800")
    btn_del_expr.config(command=_del_expr)

    def _scan_folder():
        fpath = var_char_folder.get().strip()
        if not fpath:
            set_status("Please select a character folder first.", "#FF9800")
            return
        scanned = scan_character_folder(fpath)
        if not scanned:
            set_status(f"No expression sprites found in '{fpath}'. Use names like neutral_idle.png / neutral_talk.png.", "#FF9800")
            return
        cdata = get_cur_char_data()
        cdata["folder"] = os.path.dirname(fpath) if os.path.isfile(fpath) else fpath
        cdata["expressions"] = scanned
        cdata["active_expression"] = next(iter(scanned.keys()))
        save_config(cfg)
        refresh_expressions_ui()
        set_status(f"Auto-scan found {len(scanned)} expressions: {', '.join(scanned.keys())}", "#4CAF50")
    btn_scan_folder.config(command=_scan_folder)

    def _fetch_layout():
        try:
            if not resolve_app:
                raise RuntimeError("DaVinci Resolve is not connected.")
            proj = resolve_app.GetProjectManager().GetCurrentProject()
            if not proj:
                raise RuntimeError("No active DaVinci Resolve project found.")
            tl = proj.GetCurrentTimeline()
            if not tl:
                raise RuntimeError("No active timeline found.")

            target_clip = tl.GetCurrentVideoItem()
            if not target_clip:
                clips = tl.GetItemListInTrack("video", var_base_track.get())
                if clips and len(clips) > 0:
                    target_clip = clips[-1]

            if not target_clip:
                raise RuntimeError("No video clip found under playhead. Select a clip on your timeline.")

            props = target_clip.GetProperty()
            pan = float(props.get("Pan", 0.0))
            tilt = float(props.get("Tilt", 0.0))
            zoom = float(props.get("ZoomX", 1.0))
            flip_x = bool(props.get("FlipX", False))

            var_pos_x.set(f"{pan:.1f}")
            var_pos_y.set(f"{tilt:.1f}")
            var_zoom.set(f"{zoom:.3f}")
            var_flip_x.set(flip_x)
            var_preset.set("Custom")
            save_ui_to_config()
            set_status(f"Fetched layout from '{target_clip.GetName()}': X={pan:.1f}, Y={tilt:.1f}, Zoom={zoom:.2f}, Flip={flip_x}!", "#4CAF50")
        except Exception as e:
            set_status(f"Fetch Error: {str(e)}", "#F44336")
    btn_fetch.config(command=_fetch_layout)

    # Timeline execution helpers
    def get_timeline_zones():
        if not resolve_app:
            raise RuntimeError("DaVinci Resolve connection not available.")
        proj = resolve_app.GetProjectManager().GetCurrentProject()
        if not proj:
            raise RuntimeError("No active DaVinci Resolve project found.")
        timeline = proj.GetCurrentTimeline()
        if not timeline:
            raise RuntimeError("No active Timeline opened in DaVinci Resolve.")

        tl_start = timeline.GetStartFrame()
        tl_end = timeline.GetEndFrame()
        rmode_str = var_range_mode.get()

        cdata = get_cur_char_data()
        avail_exprs = list(cdata.get("expressions", {}).keys())
        default_expr = var_expr_name.get() or "Neutral"

        if "Marker" in rmode_str:
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

        elif "Mark In" in rmode_str:
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

    def extract_full_audio_for_zones(zones):
        if not resolve_app:
            raise RuntimeError("DaVinci Resolve connection not detected.")
        proj = resolve_app.GetProjectManager().GetCurrentProject()
        if not proj:
            raise RuntimeError("No active DaVinci Resolve project found.")
        timeline = proj.GetCurrentTimeline()
        if not timeline:
            raise RuntimeError("No active timeline found in project.")
        fps = float(timeline.GetSetting("timelineFrameRate"))

        min_frame = min(z[0] for z in zones)
        max_frame = max(z[1] for z in zones)
        total_tl_frames = max(1, max_frame - min_frame)

        is_custom_file = (var_audio_src.get() == "Custom Audio File")
        thresh_db = -var_thresh.get()
        shout_thresh_db = -var_shout_thresh.get()
        enable_shout = var_enable_shout.get()

        all_states = [0] * total_tl_frames
        sample_pcm_for_noise = None

        if is_custom_file:
            file_path = var_audio_file.get().strip()
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Custom audio file does not exist: {file_path}")
            duration_sec = total_tl_frames / fps
            pcm_bytes = extract_pcm_from_file(file_path, start_sec=0.0, duration_sec=duration_sec)
            sample_pcm_for_noise = pcm_bytes
            db_array = compute_frame_db_vectorized(pcm_bytes, 16000, fps)
            clip_states = classify_frame_states(db_array, thresh_db, shout_thresh_db, enable_shout)
            n_copy = min(total_tl_frames, len(clip_states))
            all_states[:n_copy] = clip_states[:n_copy]
        else:
            track_idx = var_audio_track.get()
            items = timeline.GetItemListInTrack("audio", track_idx)
            if not items:
                raise RuntimeError(f"No audio clips found on Audio Track {track_idx}.")

            overlapping_clips = []
            for itm_clip in items:
                c_start = itm_clip.GetStart()
                c_end = itm_clip.GetEnd()
                if c_end > min_frame and c_start < max_frame:
                    overlapping_clips.append(itm_clip)

            if not overlapping_clips:
                raise RuntimeError(f"No audio clips found in range {min_frame}-{max_frame} on Audio Track {track_idx}.")

            for itm_clip in overlapping_clips:
                c_start = itm_clip.GetStart()
                c_end = itm_clip.GetEnd()
                source_start = itm_clip.GetSourceStartFrame()
                media_pool_item = itm_clip.GetMediaPoolItem()
                if not media_pool_item:
                    continue
                file_path = media_pool_item.GetClipProperty("File Path")
                if not file_path or not os.path.isfile(file_path):
                    continue

                overlap_start = max(min_frame, c_start)
                overlap_end = min(max_frame, c_end)
                if overlap_end <= overlap_start:
                    continue

                source_offset_frame = source_start + (overlap_start - c_start)
                start_sec = source_offset_frame / fps
                dur_sec = (overlap_end - overlap_start) / fps

                pcm_bytes = extract_pcm_from_file(file_path, start_sec=start_sec, duration_sec=dur_sec)
                if sample_pcm_for_noise is None and len(pcm_bytes) > 0:
                    sample_pcm_for_noise = pcm_bytes

                db_array = compute_frame_db_vectorized(pcm_bytes, 16000, fps)
                clip_states = classify_frame_states(db_array, thresh_db, shout_thresh_db, enable_shout)

                dest_start = max(0, overlap_start - min_frame)
                dest_end = min(total_tl_frames, overlap_end - min_frame)
                slice_len = dest_end - dest_start
                if slice_len > 0 and len(clip_states) > 0:
                    all_states[dest_start:dest_end] = clip_states[:slice_len]

        return {
            "fps": fps,
            "min_frame": min_frame,
            "max_frame": max_frame,
            "all_states": all_states,
            "sample_pcm": sample_pcm_for_noise
        }

    def _calibrate():
        try:
            set_status("Sampling background audio noise...", "#00aaff")
            zones = get_timeline_zones()
            full_audio = extract_full_audio_for_zones(zones)
            pcm = full_audio.get("sample_pcm")
            if not pcm or len(pcm) == 0:
                raise RuntimeError("No audio samples available to calibrate.")
            noise_db, target_thresh = calibrate_noise_floor(pcm, sample_rate=16000)
            abs_val = abs(target_thresh)
            var_thresh.set(abs_val)
            get_cur_char_data()["threshold_db"] = target_thresh
            save_ui_to_config()
            set_status(f"Calibrated! Background noise: {noise_db:.1f} dB. Threshold set to: {target_thresh} dB.", "#4CAF50")
        except Exception as e:
            set_status(f"Calibration Error: {str(e)}", "#F44336")
    btn_calibrate.config(command=_calibrate)

    def _preview():
        try:
            save_ui_to_config()
            set_status("Analyzing audio detection...", "#00aaff")
            zones = get_timeline_zones()
            full_audio = extract_full_audio_for_zones(zones)

            all_states = full_audio["all_states"]
            fps = full_audio["fps"]
            min_frame = full_audio["min_frame"]
            hold = var_hold_ms.get()

            total_talk = 0
            total_shout = 0
            total_dur_sec = (full_audio["max_frame"] - full_audio["min_frame"]) / fps

            for z_start, z_end, _ in zones:
                idx_start = max(0, z_start - min_frame)
                idx_end = min(len(all_states), z_end - min_frame)
                zone_states = all_states[idx_start:idx_end]
                segs = extract_segments_from_states(zone_states, fps, hold_ms=hold)
                total_talk += sum(1 for label, _, _ in segs if label == 'TALK')
                total_shout += sum(1 for label, _, _ in segs if label == 'SHOUT')

            set_status(
                f"Preview ({len(zones)} zones): Found {total_talk} Talk + {total_shout} Shout bursts "
                f"across {total_dur_sec:.1f}s total. Ready to splice!",
                "#4CAF50"
            )
        except Exception as e:
            set_status(f"Preview Error: {str(e)}", "#F44336")
    btn_preview.config(command=_preview)

    def _generate():
        try:
            save_ui_to_config()
            set_status("Timeline audio decode & media pre-caching...", "#00aaff")

            if not resolve_app:
                raise RuntimeError("DaVinci Resolve connection not detected.")
            proj = resolve_app.GetProjectManager().GetCurrentProject()
            if not proj:
                raise RuntimeError("No active DaVinci Resolve project found.")
            timeline = proj.GetCurrentTimeline()
            if not timeline:
                raise RuntimeError("No active timeline found in project.")
            media_pool = proj.GetMediaPool()

            zones = get_timeline_zones()
            char_name = var_char_name.get()
            cdata = get_cur_char_data()

            base_track = var_base_track.get()
            talk_track = var_talk_track.get()
            ensure_video_tracks(timeline, max(base_track, talk_track))

            pan = float(cdata.get("pan", 0.0))
            tilt = float(cdata.get("tilt", 0.0))
            zoom = float(cdata.get("zoom", 1.0))
            flip_x = bool(cdata.get("flip_x", False))

            enable_bounce = var_bounce.get()
            bounce_px = float(var_bounce_px.get())

            enable_dim = var_dim.get()
            dim_opacity = float(var_dim_pct.get())
            idle_opacity = dim_opacity if enable_dim else 100.0

            # 1. Pre-Cache all Media Pool items
            folder = get_media_folder(media_pool, f"PNGtuber - {char_name}")
            all_paths = []
            for z_exp in cdata.get("expressions", {}).values():
                for k in ("idle_png", "talk_png", "shout_png"):
                    if z_exp.get(k):
                        all_paths.append(z_exp[k])
            media_cache = build_media_cache(media_pool, folder, all_paths)

            # 2. Extract full audio aligned to timeline frames
            full_audio = extract_full_audio_for_zones(zones)
            all_states = full_audio["all_states"]
            fps = full_audio["fps"]
            min_frame = full_audio["min_frame"]
            max_frame = full_audio["max_frame"]
            hold = var_hold_ms.get()

            # 3. Batched timeline overwrite
            if var_overwrite.get():
                clear_tracks_in_range_batched(timeline, [base_track, talk_track], min_frame, max_frame)

            total_cuts_made = 0

            # 4. Splicing loop
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
                speech_segments = extract_segments_from_states(zone_states, fps, hold_ms=hold)

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
                f"Done! Fast-spliced {len(zones)} zones with {total_cuts_made} cuts in one pass.",
                "#4CAF50"
            )
        except Exception as e:
            set_status(f"Generation Error: {str(e)}", "#F44336")
    btn_generate.config(command=_generate)

    # Window close handler
    def _on_close():
        save_ui_to_config()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", _on_close)

    # Initial load
    refresh_characters_ui()

    root.mainloop()

if __name__ == "__main__" or "resolve" in globals() or "fusion" in globals() or "fu" in globals():
    try:
        run_app()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"[YapPNG Fatal Error]\n{err_msg}")
        try:
            import tkinter as tk
            from tkinter import messagebox
            err_root = tk.Tk()
            err_root.withdraw()
            messagebox.showerror("YapPNG Launch Error", f"Failed to start YapPNG:\n\n{err_msg}")
            err_root.destroy()
        except Exception:
            pass
