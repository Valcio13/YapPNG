# 📖 YapPNG Complete Feature & Workflow Guide

A comprehensive, step-by-step tutorial covering every feature of **YapPNG** for DaVinci Resolve (Free & Studio): from sprite art preparation and audio routing to multi-character podcasting and 2-hour long video optimization.

**[English Guide](WORKFLOW_GUIDE.md)** | **[Panduan Bahasa Indonesia](WORKFLOW_GUIDE_ID.md)**

---

## 📑 Table of Contents
1. [Sprite Art Organization & Auto-Scanner](#1-sprite-art-organization--auto-scanner)
2. [Interface Overview (The 6 Cards)](#2-interface-overview-the-6-cards)
3. [Marking Modes Explained](#3-marking-modes-explained)
   - [A. Mark In & Mark Out (`I` & `O`)](#a-mark-in--mark-out-i--o)
   - [B. Entire Audio Track](#b-entire-audio-track)
   - [C. Marker-Driven Expressions (`M`)](#c-marker-driven-expressions-m)
4. [Audio & Multi-Track Routing](#4-audio--multi-track-routing)
   - [Using Another Timeline Audio Track](#using-another-timeline-audio-track)
   - [Importing a Custom Audio File Directly](#importing-a-custom-audio-file-directly)
5. [Sensitivity, Auto-Calibration & Shouting](#5-sensitivity-auto-calibration--shouting)
6. [Placement, Bounce Hop & Inactive Dimming](#6-placement-bounce-hop--inactive-dimming)
   - [Visual Layout with "Fetch from Timeline Clip"](#visual-layout-with-fetch-from-timeline-clip)
   - [Bounce Pop Physics](#bounce-pop-physics)
   - [Inactive Speaker Dimming (Listening Mode)](#inactive-speaker-dimming-listening-mode)
7. [Step-by-Step Workflows](#7-step-by-step-workflows)
   - [Workflow A: Solo Gaming / Commentary](#workflow-a-solo-gaming--commentary)
   - [Workflow B: 2-Person Podcast / Discord Collab](#workflow-b-2-person-podcast--discord-collab)
   - [Workflow C: Long 2-Hour Video Optimization](#workflow-c-long-2-hour-video-optimization)

---

## 🎨 1. Sprite Art Organization & Auto-Scanner

YapPNG automatically recognizes expressions and mouth states if you follow standard naming conventions.

### Recommended Folder Structure:
```text
My_PNGtuber_Assets/
└── Character_Host/
    ├── neutral_idle.png
    ├── neutral_talk.png
    ├── neutral_shout.png
    ├── happy_idle.png
    ├── happy_talk.png
    ├── angry_idle.png
    ├── angry_talk.png
    └── angry_shout.png
```

### Recognized Keywords:
* **Idle (Mouth Closed):** `_idle`, `_closed`, `_close`, `_mouth_closed`, `_shut`
* **Talking (Mouth Open):** `_talk`, `_talking`, `_open`, `_mouth_open`, `_speaking`
* **Shouting (Screaming / Loud Laugh):** `_shout`, `_scream`, `_yell`, `_loud`, `_wide`

*(Subfolder organization such as `Character_Host/happy/idle.png` & `Character_Host/happy/talk.png` is also fully recognized!)*

Clicking **`📂 Auto-Scan`** in Card 1 will automatically parse all matching PNGs and populate your expressions in seconds.

---

## 🖥️ 2. Interface Overview (The 6 Cards)

The YapPNG interface is styled after DaVinci Resolve's native dark inspector:

1. **Card 1: Character Profile (Blue Pip):**
   - Switch between character profiles (e.g. `Character_Host`, `Character_Guest`).
   - Create new characters (`+ New Char`) or delete profiles (`🗑 Del`).
   - Browse character folder and run `📂 Auto-Scan`.
2. **Card 2: Expression Sprites (Purple Pip):**
   - Switch active expression (`Neutral`, `Happy`, `Angry`, etc.).
   - Displays the 3 sprites for each expression: **Idle**, **Talk**, and **Shout**.
3. **Card 3: Placement, Dynamics & Dimming (Cyan Pip):**
   - Position presets: `Left Side`, `Right Side`, `Center`, or `Custom`.
   - `📥 Fetch from Timeline Clip`: Reads exact Pan, Tilt, Zoom, and Flip from the selected clip in Resolve's viewer!
   - `🦘 Bounce Hop`: Vertical pop when speaking.
   - `💡 Inactive Dim`: Dims resting speaker opacity when listening.
4. **Card 4: Audio & Track Routing (Amber Pip):**
   - Audio source selection: Timeline track or external audio file.
   - Video track assignments for Idle base clip and Talk clips.
5. **Card 5: Voice & Shouting Detection (Green Pip):**
   - Voice threshold slider with dynamic dB readout pill.
   - `🎙️ Auto-Calibrate`: 1-click ambient room noise auto-tuning.
   - Shouting trigger threshold slider.
   - Mouth hold time slider (ms).
6. **Card 6: Timeline Splicing Options (Indigo Pip):**
   - Range mode selector (In/Out Range, Entire Track, Markers).
   - Clean overwrite checkbox.
7. **Action Dock (Pinned at Bottom):**
   - Live status indicator (🟢 Ready / 🔵 Processing / 🔴 Error).
   - Animated progress bar with percentage and estimated time remaining (ETA).
   - `🔍 Preview Detection` and `⚡ SPLICING TO TIMELINE` buttons.
   - Becomes `🛑 Stop / Cancel` during generation.

---

## ✂️ 3. Marking Modes Explained

### A. Mark In & Mark Out (`I` & `O`)
Use this when you want to generate PNGtuber animations for a **specific section** of your timeline (e.g. a 3-minute highlight from a 2-hour stream).

1. Move playhead to start point $\rightarrow$ press **`I`** (*Mark In*).
2. Move playhead to end point $\rightarrow$ press **`O`** (*Mark Out*).
3. In YapPNG Card 6, select **Range Mode**: **`Mark In / Out Range`**.
4. Click **`⚡ SPLICING TO TIMELINE`**.
5. *To reset/clear marks in Resolve: press **`Alt + X`**.*

### B. Entire Audio Track
Use this when you want YapPNG to process your timeline from frame 0 to the very last frame automatically without setting any in/out points.

### C. Marker-Driven Expressions (`M`)
Use this to **automate emotional changes** throughout long videos without manual scene slicing:
1. Play through your timeline in DaVinci Resolve.
2. Whenever the character's emotion should change, press **`M`** to drop a marker.
3. Press **`M` again** (or double-click the marker) to open its dialog.
4. In the **Name** field, type the expression name: `Happy`, `Angry`, `Smug`, or `Neutral`.
5. In YapPNG Card 6, set **Range Mode** to **`🏷️ Marker-Driven Expressions`**.
6. Click **`⚡ SPLICING TO TIMELINE`**!
7. YapPNG automatically segments the timeline by markers, placing Neutral clips until the `Happy` marker, then switching to Happy sprites, etc.

---

## 🎛️ 4. Audio & Multi-Track Routing

### Using Another Timeline Audio Track
If you have a co-host, guest, or game audio on another track:
1. Place their audio on **Audio Track 2** in DaVinci Resolve.
2. In YapPNG Card 4 (**Audio & Track Routing**):
   - Set **Audio Source**: `Timeline Audio Track`.
   - Set **Audio Track**: `2`.
3. Set **Talk Video Track** to an unused video track (e.g. Track 4 or 5) so it doesn't overwrite your primary host.

### Importing a Custom Audio File Directly
If you have a raw `.wav`, `.mp3`, `.m4a`, or `.flac` voiceover file:
1. In Card 4, change **Audio Source** to **`Custom Audio File`**.
2. Click **`Browse...`** next to *Or Audio File* and select your file.
3. YapPNG decodes and analyzes this audio file directly in high-speed memory.

---

## 🎙️ 5. Sensitivity, Auto-Calibration & Shouting

| Control | Recommended Setting | Description |
| :--- | :---: | :--- |
| **Threshold (dB)** | `-28 dB` to `-34 dB` | Voice detection gate. Sounds above this level open the mouth. |
| **🎙️ Auto-Calibrate** | *Click Once* | Samples background noise on your timeline and sets optimal threshold automatically. |
| **Shouting Trigger** | `-10 dB` to `-14 dB` | Detects loud laughter or yelling and switches to the `_shout` sprite with extra bounce. |
| **Mouth Hold (ms)** | `120 ms` to `150 ms` | Keeps mouth open across rapid syllables so it doesn't flicker on consonants. |

---

## 📐 6. Placement, Bounce Hop & Inactive Dimming

### Visual Layout with "Fetch from Timeline Clip"
Instead of guessing coordinate numbers:
1. Drag any sprite from your media pool onto the timeline.
2. Position, scale, and flip it visually in Resolve's preview viewer (using Resolve's Transform controls in the top-right Inspector).
3. Select that clip on your timeline.
4. In YapPNG Card 3, click **`📥 Fetch from Timeline Clip`**.
5. YapPNG instantly reads the exact Pan, Tilt, Zoom, and Flip values! Delete the temporary clip and you are ready.

### Bounce Pop Physics
* Check **`🦘 Bounce Hop`** and set **Hop (px)** (default: `18 px`).
* When speaking, the character pops upward on every speech burst.
* During loud shouts, the bounce automatically scales to **$1.6\times$ height** with a slight scale pop for cartoon emphasis!

### Inactive Speaker Dimming (Listening Mode)
* Check **`💡 Inactive Dim`** and set **Dim (%)** (default: `70%`).
* While speaking, the character shines at $100\%$ full opacity.
* When quiet and listening to a co-host, the character smoothly dims to $70\%$ resting opacity, giving professional podcast visual hierarchy!

---

## 🚀 7. Step-by-Step Workflows

### Workflow A: Solo Gaming / Commentary
1. Ensure your voice track is on **Audio Track 1**.
2. Open YapPNG (**Workspace > Scripts > Edit > YapPNG**).
3. Select character, pick **Left Side** or **Right Side** preset.
4. Click **`🎙️ Auto-Calibrate`**.
5. Set In (`I`) and Out (`O`) on your timeline.
6. Click **`⚡ SPLICING TO TIMELINE`**.

### Workflow B: 2-Person Podcast / Discord Collab
1. Put Host audio on **Audio 1**, Guest audio on **Audio 2**.
2. **Host Setup:**
   - Select `Character_Host`.
   - Audio Track: `1`, Idle Video: `2`, Talk Video: `3`.
   - Preset: `Left Side` (Flip Horizontal: unchecked).
   - Click **`⚡ SPLICING TO TIMELINE`**.
3. **Guest Setup:**
   - Select `Character_Guest`.
   - Audio Track: `2`, Idle Video: `4`, Talk Video: `5`.
   - Preset: `Right Side` (Flip Horizontal: checked).
   - Click **`⚡ SPLICING TO TIMELINE`**.
4. Both characters will now converse side-by-side with automatic listening dimming and bounce hops!

### Workflow C: Long 2-Hour Video Optimization
1. YapPNG's engine automatically uses **Single-Pass Audio Grouping** to decode multi-hour MKV/MP4 recordings once in seconds.
2. Splicing runs in **35-clip micro-batches** with a non-blocking Windows event pump, so your UI never freezes or says *(Not Responding)*.
3. If you ever need to stop, click the red **`🛑 Stop / Cancel`** button in the bottom dock to safely cancel.
