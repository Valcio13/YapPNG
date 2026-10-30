# 🏛️ YapPNG Architecture & Technical Specifications

**YapPNG** is an in-app DaVinci Resolve extension that automates voice-reactive sprite animation (PNGtuber style) directly on the editing timeline.

---

## 1. High-Level System Architecture

```text
+-----------------------------------------------------------------------------------+
|                            DaVinci Resolve Environment                            |
|                                                                                   |
|  [ Workspace > Scripts Menu ]                                                     |
|         │                                                                         |
|         ▼                                                                         |
|  +─────────────────────────────────────────────────────────────────────────────+  |
|  |                 YapPNG UI Engine (fusion.UIManager / Qt)                   |  |
|  |   - Character Manager   - Expression Auto-Scanner   - Layout Controls       |  |
|  |   - VAD Sliders         - Bounce / Dimming Toggles  - Marker Automation     |  |
|  +──────────────────────────────────────┬──────────────────────────────────────+  |
|                                         │ Triggers Splicing                       |
|                                         ▼                                         |
|  +─────────────────────────────────────────────────────────────────────────────+  |
|  |                 Single-Pass Audio Pipeline (FFmpeg + NumPy)                 |  |
|  |   1. Stream extraction via FFmpeg (-vn -sn -dn -threads 4)                  |  |
|  |   2. Vectorized Prefix-Sum RMS calculation (27ms for 5 mins of audio)       |  |
|  |   3. State Classification (Silence = 0, Talk = 1, Shout = 2)               |  |
|  |   4. Hysteresis Hold & Min-Duration Smoothing Filter                       |  |
|  +──────────────────────────────────────┬──────────────────────────────────────+  |
|                                         │ Generates Cut Lists                     |
|                                         ▼                                         |
|  +─────────────────────────────────────────────────────────────────────────────+  |
|  |                    Resolve Timeline Editing Dispatcher                      |  |
|  |   - Pre-caches MediaPoolItem references (Zero API re-query)                 |  |
|  |   - Batched clip lift/deletion on marked range                              |  |
|  |   - Places Base Track (Idle sprite @ Dimming Opacity)                       |  |
|  |   - Overlays Talk Track (Talk/Shout sprites @ 100% Opacity + Bounce Hop)    |  |
|  |   - Sets Pan, Tilt, Zoom, and FlipX clip properties                         |  |
|  +─────────────────────────────────────────────────────────────────────────────+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Voice Activity Detection (VAD) Algorithm

### Vectorized Prefix-Sum Energy Calculation
Instead of iterating through audio samples using standard Python loops, YapPNG computes Root Mean Square (RMS) decibels across video frame boundaries using cumulative sum squares:

1. Let audio samples be $x[n]$ for $n \in [0, N-1]$.
2. Compute cumulative sum of squares:
   $$S[k] = \sum_{i=0}^{k-1} x[i]^2, \quad S[0] = 0$$
3. For any video frame spanning audio sample indices $[s_{\text{start}}, s_{\text{end}})$:
   $$\text{RMS} = \sqrt{\frac{S[s_{\text{end}}] - S[s_{\text{start}}]}{s_{\text{end}} - s_{\text{start}}}}$$
4. Convert RMS to Decibels Full Scale ($\text{dBFS}$):
   $$\text{dB} = 20 \log_{10}\left(\frac{\text{RMS}}{32767} + 10^{-9}\right)$$

### Multi-Threshold State Machine
Each video frame is classified into one of three states:
* $\text{State } 2\ (\text{SHOUT})$ if $\text{dB} \ge \text{Threshold}_{\text{shout}}$
* $\text{State } 1\ (\text{TALK})$ if $\text{dB} \ge \text{Threshold}_{\text{speech}}$
* $\text{State } 0\ (\text{IDLE})$ otherwise

### Hysteresis Hold Smoothing
To prevent rapid mouth fluttering on consonants and micro-pauses (e.g. *p*, *t*, *k* stops), a countdown hold window ($H_{\text{frames}} = \lceil (\text{hold\_ms} / 1000) \times \text{FPS} \rceil$) extends active states across momentary drops below threshold.

---

## 3. Dual-Track Non-Destructive Overlay Model

YapPNG uses a non-destructive multi-track layering strategy:

```text
Video Track 3 (Talk):        [ Talk / Shout Cut ]       [ Talk / Shout Cut ]
Video Track 2 (Idle): [================== Continuous Idle Clip ==================]
Audio Track 1 (Voice):[~~~~ "Hello everyone!" ~~~~]     [~~~~ "Let's begin!" ~~~~]
```

### Advantages:
1. **Zero Gap Risk:** Because the Idle clip continuously spans underneath, there is never a single frame of black/empty screen between syllables.
2. **Effortless Trimming:** Editors can easily slip, slide, ripple, or delete cuts directly on the Edit timeline without disturbing character layout.
3. **Smooth Dimming:** In podcast/multi-speaker mode, the Idle clip sits at a resting listening opacity ($70\%$). When the speaker talks, Track 3 overlays at $100\%$ full brightness with the hop transform, then seamlessly reveals the resting state when talking stops.

---

## 4. Marker-Driven Expression Segmentation

When operating in **Marker-Driven Mode**:
1. All timeline markers are fetched via `timeline.GetMarkers()`.
2. Markers matching character expression names (e.g., `Happy`, `Angry`, `Neutral`) are sorted chronologically:
   $$\text{Marker}_1 (f_1, \text{Expr}_1), \quad \text{Marker}_2 (f_2, \text{Expr}_2), \quad \dots$$
3. The timeline is partitioned into continuous expression intervals:
   $$[f_{\text{start}}, f_1) \rightarrow \text{Default}, \quad [f_1, f_2) \rightarrow \text{Expr}_1, \quad [f_2, f_{\text{end}}) \rightarrow \text{Expr}_2$$
4. Pre-computed audio states are sliced in memory per interval, allowing long timelines (e.g., 60 minutes) to be processed in a single pass.
