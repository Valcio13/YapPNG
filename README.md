# 🎙️ YapPNG

> **Voice-activated PNG sprite animator (PNGtuber) plugin built natively for DaVinci Resolve Free & Studio.**

[![Resolve](https://img.shields.io/badge/DaVinci%20Resolve-Free%20%26%20Studio%20(18%2C%2019%2C%2021%2B)-black?logo=davinci-resolve)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/Python-3.8%20--%203.12-blue?logo=python)](https://python.org)
[![NumPy](https://img.shields.io/badge/Acceleration-NumPy%20Vectorized%20VAD-green?logo=numpy)](https://numpy.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**YapPNG** transforms your voiceover or microphone tracks into animated PNGtuber characters right on your DaVinci Resolve Edit timeline. It detects voice activity in real time without slow cloud APIs or transcription delays, dynamically splicing Idle, Talking, and Shouting sprites with physics bounce, screen positioning, and podcast-style speaker dimming.

---

## ✨ Features at a Glance

* 🎛️ **Runs Natively Inside Resolve:** Launches right from `Workspace > Scripts > Edit > PNG_Voice_Animator` using Resolve's built-in Qt `UIManager`. Compatible with **DaVinci Resolve Free & Studio**.
* ⚡ **Ultra-Fast Vectorized VAD:** Analyzes 5 minutes of speech in **~27 milliseconds** using NumPy prefix-sum energy calculation (with pure-Python fallback).
* 👥 **Multi-Character Podcasting:** Independent audio & video track routing per character (e.g. Host on A1/V2/V3, Guest on A2/V4/V5).
* 📂 **Folder Auto-Scanner:** Point to your character's folder and click **`📂 Auto-Scan`** to automatically discover all expressions (`idle`, `talk`, `shout`).
* 🏷️ **Marker-Driven Expression Automation:** Press `M` while listening to your timeline to drop markers (`Happy`, `Angry`, `Neutral`). YapPNG automates expression switching across 60+ minute videos in **one click**!
* 🦘 **The "PNGtuber Bounce" Effect:** Adds an energetic vertical hop and scale pulse on speech, with $+60\%$ extra hop on shouting peaks.
* 📢 **High-Volume Shouting / Scream Trigger:** Detects yells and screams ($>-12\text{ dB}$) and switches to wide-open screaming sprites.
* 💡 **Inactive Speaker Dimming:** Automatically dims listening speakers ($70\%$ opacity) and pops active speakers to $100\%$ full brightness.
* 📐 **Screen Layouts & Visual Fetch:** Built-in presets (*Left*, *Right*, *Center*) plus an **`📥 Fetch from Timeline Clip`** button to visually copy coordinates directly from Resolve's viewer.
* 🎙️ **One-Click Noise Calibrator:** Measures room noise and auto-calibrates sensitivity.
* 🧹 **Clean Overwrite Mode:** Lifts previous cuts in the marked range cleanly without shifting downstream edits.

---

## 🎬 Timeline Splicing Mechanics

YapPNG uses a non-destructive dual-track layering model:

```text
Video Track 3 (Talk):        [ Talk / Shout Cut ]       [ Talk / Shout Cut ]
Video Track 2 (Idle): [================== Continuous Idle Clip ==================]
Audio Track 1 (Voice):[~~~~ "Hello everyone!" ~~~~]     [~~~~ "Let's begin!" ~~~~]
```

* **Silent / Listening:** Continuous Idle sprite shows at resting opacity ($70\%$).
* **Speaking:** Talk / Shout cuts overlay at $100\%$ brightness with the vertical hop transform.
* **100% Editable:** Because these are standard timeline clips, you can trim, ripple, or delete cuts with Resolve's standard tools.

---

## 🚀 Quick Start

### 1. Installation
Run the installer script:
* **Windows:** Double-click `install_plugin.bat`.
* **Manual / macOS / Linux:** Copy `PNG_Voice_Animator.py` to your DaVinci Resolve scripts directory:
  * **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`
  * **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/`
  * **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/`

### 2. Launch in DaVinci Resolve
Open any project in DaVinci Resolve, then go to:
> **`Workspace` > `Scripts` > `Edit` > `PNG_Voice_Animator`**

### 3. Splicing Your First Character
1. In the panel, point **Character Folder** to your sprite art (or use the pre-packaged [`test_assets/Character_Host`](test_assets/Character_Host)).
2. Click **`📂 Auto-Scan`**.
3. Set In (`I`) and Out (`O`) on your timeline.
4. Click **`🎙️ Auto-Calibrate`** to calibrate to your room's noise floor.
5. Click **`▶ Splicing To Timeline`**!

---

## 📁 Repository Structure

```text
YapPNG/
├── PNG_Voice_Animator.py       # Main DaVinci Resolve Plugin script (v2.2 Ultra)
├── install_plugin.bat          # One-click Windows installer
├── docs/
│   ├── ARCHITECTURE.md         # Technical architecture & VAD math
│   └── WORKFLOW_GUIDE.md       # Complete step-by-step user guide
├── test_assets/                # Ready-to-use sample character art
│   ├── Character_Host/         # Host (Neutral, Happy, Angry sprites)
│   ├── Character_Guest/        # Guest (Neutral, Smug, Surprised sprites)
│   └── test_voice.wav          # Sample voice track for testing
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📚 In-Depth Documentation

* 📖 **[Workflow & Tutorial Guide](docs/WORKFLOW_GUIDE.md)**: Full guide on multi-character podcasting, marker-driven automation, and sprite conventions.
* 🏛️ **[Technical Architecture & VAD Math](docs/ARCHITECTURE.md)**: Deep dive into prefix-sum energy calculation, hysteresis smoothing, and Resolve API dispatching.

---

## ⚙️ Requirements

* **DaVinci Resolve:** Version 18, 19, or 21+ (Free or Studio).
* **Python:** Python 3.8+ (Resolve uses your system's installed Python).
* **FFmpeg:** Installed on your system path (for audio stream decoding).
* **NumPy (Optional):** Optional acceleration for sub-30ms audio processing.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
