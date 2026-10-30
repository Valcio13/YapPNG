# 📖 YapPNG Complete Workflow Guide

A step-by-step tutorial covering everything from preparing your sprite art to multi-character podcast editing and marker-driven expression automation in DaVinci Resolve.

---

## 🎨 1. Sprite Art Organization

YapPNG automatically recognizes your sprites if you follow standard naming conventions.

### Recommended Folder Structure:

```text
My_PNGtuber_Project/
├── Characters/
│   ├── Host/
│   │   ├── neutral_idle.png
│   │   ├── neutral_talk.png
│   │   ├── neutral_shout.png
│   │   ├── happy_idle.png
│   │   ├── happy_talk.png
│   │   ├── angry_idle.png
│   │   ├── angry_talk.png
│   │   └── angry_shout.png
│   └── Guest/
│       ├── neutral_idle.png
│       ├── neutral_talk.png
│       ├── smug_idle.png
│       ├── smug_talk.png
│       ├── surprised_idle.png
│       ├── surprised_talk.png
│       └── surprised_shout.png
```

### Supported Suffixes:
* **Idle (Closed Mouth):** `_idle`, `_closed`, `_close`, `_mouth_closed`, `_shut`
* **Talking (Open Mouth):** `_talk`, `_talking`, `_open`, `_mouth_open`, `_speaking`
* **Shouting (Screaming / Loud):** `_shout`, `_scream`, `_yell`, `_loud`, `_wide`

*(Subfolder organization like `Host/happy/idle.png` & `Host/happy/talk.png` is also supported!)*

---

## 🎙️ 2. Single-Character Setup

1. Open your DaVinci Resolve project. Ensure your voice track is placed on **Audio Track 1**.
2. Go to: **`Workspace` > `Scripts` > `Edit` > `PNG_Voice_Animator`**.
3. Under **Character Profile**, browse your character's folder and click **`📂 Auto-Scan`**.
4. Set your character's screen position:
   - Pick a preset (e.g. `Center Stage` or `Left Side`).
   - Or drag the sprite clip in Resolve's viewer and click **`📥 Fetch from Timeline Clip`**.
5. Set In (`I`) and Out (`O`) on your timeline.
6. Click **`🎙️ Auto-Calibrate`** next to the Threshold slider to adapt to your room noise.
7. Click **`▶ Splicing To Timeline`**!

---

## 👥 3. Multi-Character Podcasting Setup

To set up two characters talking to each other (e.g. Host on the left, Guest on the right):

### Step A: Configure Host
1. Select **`Character_Host`** in the character dropdown.
2. Under **Audio & Video Routing**:
   - Audio Track: **`Track 1`**
   - Idle Video Track: **`Track 2`**
   - Talk Video Track: **`Track 3`**
3. Under **Placement**:
   - Layout Preset: **`Left Side`**
   - Flip Horizontal: **Unchecked** (facing right toward the guest)
4. Enable **`🦘 Bounce Hop`** and **`💡 Inactive Dim`** ($70\%$).

### Step B: Configure Guest
1. Select **`Character_Guest`** (or click `+ New Char`).
2. Under **Audio & Video Routing**:
   - Audio Track: **`Track 2`** (Guest's microphone)
   - Idle Video Track: **`Track 4`**
   - Talk Video Track: **`Track 5`**
3. Under **Placement**:
   - Layout Preset: **`Right Side`**
   - Flip Horizontal: **Checked** (facing left toward the host)
4. Enable **`🦘 Bounce Hop`** and **`💡 Inactive Dim`** ($70\%$).

### Step C: Splicing Both
1. Select **`Character_Host`** $\rightarrow$ Click **`▶ Splicing To Timeline`**.
2. Select **`Character_Guest`** $\rightarrow$ Click **`▶ Splicing To Timeline`**.
3. Both characters will now converse side-by-side! Whenever one speaks, they hop and brighten to $100\%$, while the other stays at $70\%$ resting opacity listening.

---

## 🏷️ 4. Marker-Driven Expression Switching (Long Videos)

When editing a 20+ minute video, you don't need to manually slice scene by scene:

1. Play through your timeline in DaVinci Resolve.
2. Whenever the character's emotion changes, press **`M`** to drop a timeline marker:
   - Type the expression name: `Happy`, `Angry`, `Neutral`, `Smug`, etc.
3. In YapPNG, change **Placement Mode** to:
   **`🏷️ Marker-Driven Expressions`**.
4. Click **`▶ Splicing To Timeline`**.
5. YapPNG automatically partitions your entire timeline by markers and applies the matching expressions across all sections in a single pass!

---

## ⚙️ 5. Sensitivity & Dynamics Reference

| Parameter | Recommended | Explanation |
| :--- | :--- | :--- |
| **Threshold (dB)** | `-28 dB` to `-34 dB` | Speech volume trigger. Click `Auto-Calibrate` to set automatically. |
| **Shouting Trigger (dB)**| `-10 dB` to `-14 dB` | Secondary trigger for screaming/yelling/loud laughter. |
| **Mouth Hold (ms)** | `120 ms` to `150 ms` | Keeps mouth open across syllables so it doesn't flicker on consonants. |
| **Bounce Height (px)** | `15 px` to `22 px` | Vertical hop distance on speech. Shouts automatically hop $1.6\times$ higher. |
| **Dim Opacity (%)** | `65%` to `75%` | Inactive resting brightness when listening to co-hosts. |
