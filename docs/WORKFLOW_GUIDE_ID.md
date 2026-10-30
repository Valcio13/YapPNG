# 📖 Panduan Alur Kerja YapPNG

Panduan santai cara pake **YapPNG** di DaVinci Resolve: dari nyiapin gambar karakter, bikin podcast berdua, sampai motong ekspresi otomatis pake marker di video panjang.

[English Guide](WORKFLOW_GUIDE.md) | **[Panduan Bahasa Indonesia](WORKFLOW_GUIDE_ID.md)**

---

## 🎨 1. Aturan Penamaan Gambar Karakter

YapPNG udah pinter buat ngenalin ekspresi karakter lu secara otomatis, asal format nama filenya bener.

### Contoh Susunan Folder yang Rapi:

```text
Project_PNGtuber/
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
│   └── Tamu/
│       ├── neutral_idle.png
│       ├── neutral_talk.png
│       ├── smug_idle.png
│       ├── smug_talk.png
│       ├── surprised_idle.png
│       ├── surprised_talk.png
│       └── surprised_shout.png
```

### Kata Kunci Nama File:
* **Diem / Mingkem (Idle):** `_idle`, `_closed`, `_close`, `_mouth_closed`, `_shut`
* **Ngomong / Mangap (Talk):** `_talk`, `_talking`, `_open`, `_mouth_open`, `_speaking`
* **Teriak / Mangap Lebar (Shout):** `_shout`, `_scream`, `_yell`, `_loud`, `_wide`

*(Kalo mau dipisah pake subfolder juga bisa banget, misal: `Host/happy/idle.png` dan `Host/happy/talk.png`!)*

---

## 🎙️ 2. Setup Buat Satu Karakter

1. Buka project DaVinci Resolve lu, pastiin audio suara ada di **Track Audio 1 (A1)**.
2. Buka menu: **`Workspace` > `Scripts` > `Edit` > `YapPNG`**.
3. Di bagian **1. Character Profile**, pilih folder karakter lu terus klik tombol **`📂 Auto-Scan`**.
4. Atur posisi layar karakter di bagian **3. Placement, Dynamics & Dimming**:
   - Bisa pilih preset kayak `Left Side` atau `Center Stage`.
   - Atau geser langsung gambar karakter di viewer DaVinci Resolve, terus klik tombol **`📥 Fetch from Timeline Clip`**. YapPNG bakal langsung ngerekam koordinat posisinya!
5. Tandai bagian audio yang mau dipotong pake **`I` (Mark In)** dan **`O` (Mark Out)** di timeline.
6. Klik tombol **`🎙️ Auto-Calibrate`** biar sensitivitasnya pas sama kebisingan mic lu.
7. Klik **`▶ Splicing To Timeline`**, dan selesai!

---

## 👥 3. Setup Podcast / Collab Berdua (Host vs Tamu)

Kalo lagi bikin konten ngobrol berdua kayak podcast Discord (misal: Host di kiri, Tamu di kanan):

### Langkah A: Setting Karakter Host
1. Pilih **`Character_Host`** di dropdown karakter.
2. Di bagian **Audio & Video Track Routing**:
   - Audio Track: **`Track 1`** (Mic si Host)
   - Idle Video Track: **`Track 2`**
   - Talk Video Track: **`Track 3`**
3. Di bagian **Placement**:
   - Layout Preset: **`Left Side`**
   - Flip Horizontal (Mirror): **Gak usah dicentang** (biar ngadep kanan ke arah tamu)
4. Aktifkan **`🦘 Bounce Hop`** dan **`💡 Inactive Dim`** ($70\%$).

### Langkah B: Setting Karakter Tamu
1. Pilih **`Character_Guest`** (atau klik `+ New Char` kalo mau nambah baru).
2. Di bagian **Audio & Video Track Routing**:
   - Audio Track: **`Track 2`** (Mic si Tamu)
   - Idle Video Track: **`Track 4`**
   - Talk Video Track: **`Track 5`**
3. Di bagian **Placement**:
   - Layout Preset: **`Right Side`**
   - Flip Horizontal (Mirror): **Centang** (biar ngadep kiri ke arah host)
4. Aktifkan **`🦘 Bounce Hop`** dan **`💡 Inactive Dim`** ($70\%$).

### Langkah C: Eksekusi
1. Pilih **`Character_Host`** $\rightarrow$ Klik **`▶ Splicing To Timeline`**.
2. Pilih **`Character_Guest`** $\rightarrow$ Klik **`▶ Splicing To Timeline`**.
3. Hasilnya: kedua karakter bakal mejeng barengan di timeline! Pas Host ngomong, karakternya bakal lompat dan terang $100\%$, sementara Tamu otomatis agak redup nyimak. Pas Tamu bales ngomong, gantian Tamu yang terang dan lompat!

---

## 🏷️ 4. Ganti Ekspresi Pake Marker Timeline (Buat Video Panjang)

Kalo video lu panjang (15–60 menit), nentuin In/Out puluhan kali pasti pegel banget. Pake cara ini biar sat-set:

1. Sambil dengerin timeline di Resolve, lu pencet tombol **`M`** di keyboard tiap kali mau ganti ekspresi:
   - Kasih nama markernya sesuai ekspresi: misal `Happy`, `Angry`, `Neutral`, `Smug`.
2. Di jendela YapPNG, ganti **Placement Mode** jadi:
   **`🏷️ Marker-Driven Expressions`**.
3. Klik tombol **`▶ Splicing To Timeline`**.
4. YapPNG bakal ngebagi timeline lu sesuai marker-marker tadi, terus otomatis masang ekspresi yang bener di sepanjang video dalam **sekali klik**!

---

## ⚙️ 5. Contekan Setelan Slider

| Setting | Rekomendasi | Penjelasan |
| :--- | :--- | :--- |
| **Threshold (dB)** | `-28 dB` s/d `-34 dB` | Batas minimal suara biar mulut kebuka. Klik `Auto-Calibrate` biar otomatis pas. |
| **Shouting Trigger (dB)**| `-10 dB` s/d `-14 dB` | Batas suara teriak / ketawa ngakak biar mangap lebar. |
| **Mouth Hold (ms)** | `120 ms` s/d `150 ms` | Nahan mulut tetep kebuka di antara suku kata biar gak kedip-kedip heboh. |
| **Bounce Height (px)** | `15 px` s/d `22 px` | Tinggi lompatan pas ngomong. Pas teriak otomatis $1.6\times$ lebih tinggi. |
| **Dim Opacity (%)** | `65%` s/d `75%` | Tingkat redup pas karakter lagi diem ngedengerin lawan bicara. |
