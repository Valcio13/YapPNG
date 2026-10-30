# 🎙️ YapPNG

> **Plugin PNGtuber otomatis buat DaVinci Resolve — deteksi suara langsung dari timeline, gak pake ribet!**

[English](README.md) | **[Bahasa Indonesia](README_ID.md)**

[![Resolve](https://img.shields.io/badge/DaVinci%20Resolve-Free%20%26%20Studio%20(18%2C%2019%2C%2021%2B)-black?logo=davinci-resolve)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/Python-3.8%20--%203.12-blue?logo=python)](https://python.org)
[![NumPy](https://img.shields.io/badge/Akselerasi-NumPy%20Vectorized%20VAD-green?logo=numpy)](https://numpy.org)
[![License](https://img.shields.io/badge/Lisensi-MIT-purple.svg)](LICENSE)

**YapPNG** adalah tool buat para konten kreator, podcaster, dan vtuber/pngtuber yang ngedit di DaVinci Resolve. Tool ini bakal ngebaca suara lu di timeline, terus otomatis motong dan masang sprite karakter pas lagi diem (Idle), ngomong (Talk), sampai teriak (Shout) — lengkap sama efek mantul (*bounce*), posisi layar yang pas, dan efek redup (*dimming*) ala podcast Discord.

Gak perlu API cloud, gak perlu nunggu transkripsi teks yang lemot, semuanya diproses lokal dalam hitungan milidetik!

---

## ✨ Fitur Keren

* 🎛️ **Langsung di Dalem Resolve:** Tinggal buka dari menu `Workspace > Scripts > Edit > YapPNG`. Support **DaVinci Resolve Free maupun Studio**.
* ⚡ **Deteksi Suara Ngebut:** Berkat akselerasi NumPy, audio 5 menit bisa di-scan cuma dalam waktu **~27 milidetik**!
* 👥 **Bisa Banyak Karakter Sekaligus:** Mau bikin video podcast atau collab? Tinggal atur track audio dan video masing-masing (misal: Host di A1/V2/V3, Bintang Tamu di A2/V4/V5).
* 📂 **Auto-Scan Folder:** Cukup pilih folder karakter lu, klik **`📂 Auto-Scan`**, semua ekspresi (`idle`, `talk`, `shout`) langsung kebaca otomatis.
* 🏷️ **Ganti Ekspresi Pake Marker Timeline:** Buat video panjang 20–60 menit, tinggal pencet `M` di timeline terus kasih nama ekspresi (misal: `Happy`, `Angry`, `Neutral`). Klik sekali, YapPNG bakal motong dan nyesuaiin ekspresi di sepanjang video!
* 🦘 **Efek Mantul (PNGtuber Bounce):** Biar gak kayak gambar mati, karakternya bakal otomatis lompat kecil dan nge-pulse pas lagi ngomong (dan lompat lebih heboh pas teriak!).
* 📢 **Deteksi Teriak / Ngakak (Shout Trigger):** Pas volume audio lu tiba-tiba melonjak ($>-12\text{ dB}$), karakternya bakal otomatis ganti ke sprite mangap lebar/teriak.
* 💡 **Efek Redup Karakter Pasif (Dimming):** Pas karakter lu lagi diem ngedengerin lawan bicara, dia bakal otomatis agak redup ($70\%$ opacity). Pas mulai ngomong lagi, langsung cling terang $100\%$.
* 📐 **Atur Posisi Layar Gampang:** Ada preset (*Kiri*, *Kanan*, *Tengah*), plus tombol **`📥 Fetch from Timeline Clip`** — tinggal geser gambar di viewer Resolve sesuka hati, klik tombol ini, posisinya langsung kesimpen!
* 🎙️ **Auto-Calibrate Noise Sekali Klik:** Gak usah nebak-nebak slider dB, klik tombol ini buat ngukur noise ruangan lu secara otomatis.
* 🧹 **Clean Overwrite:** Kalo mau re-do atau ganti ekspresi di area yang sama, klip lama bakal otomatis diganti secara bersih tanpa numpuk-numpuk.

---

## 🎬 Cara Kerjanya di Timeline

YapPNG pake sistem 2 track video yang aman banget dan gak ngerusak timeline:

```text
Video Track 3 (Bicara):        [ Klip Ngomong / Teriak ]       [ Klip Ngomong / Teriak ]
Video Track 2 (Diem)  : [================== Klip Diem Nyambung Terus ==================]
Audio Track 1 (Suara) : [~~~~ "Halo ges balik lagi!" ~~~~]     [~~~~ "Gokil banget!" ~~~~]
```

* **Pas lagi diem / nyimak:** Gambar karakter yang mingkem (Idle) selalu ada di Track 2 dengan opacity santai ($70\%$).
* **Pas lagi ngomong:** Klip karakter yang mangap (Talk/Shout) otomatis numpuk di Track 3 dengan opacity $100\%$ plus efek mantul.
* **Gampang Diutak-atik:** Karena ini klip timeline biasa, lu bebas nge-trim, nge-geser, atau ngapus potongannya pake tool Resolve biasa.

---

## 🚀 Gas Coba (Quick Start)

### 1. Pasang Plugin
* **Windows:** Tinggal klik 2x file `install_plugin.bat`.
* **Manual / Mac / Linux:** Copy file `YapPNG.py` ke folder script Resolve:
  * **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`
  * **Mac:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/`
  * **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/`

### 2. Buka di DaVinci Resolve
Buka project Resolve lu, terus pilih menu:
> **`Workspace` > `Scripts` > `Edit` > `YapPNG`**

### 3. Eksekusi Karakter Pertama
1. Di panel YapPNG, pilih folder karakter lu di bagian **Character Folder** (bisa coba pake folder contoh di [`test_assets/Character_Host`](test_assets/Character_Host)).
2. Klik tombol **`📂 Auto-Scan`**.
3. Tandai area timeline pake **`I` (Mark In)** dan **`O` (Mark Out)**.
4. Klik **`🎙️ Auto-Calibrate`** biar pas sama suara mic lu.
5. Klik **`▶ Splicing To Timeline`** dan liat hasilnya!

---

## 📁 Struktur File Repositori

```text
YapPNG/
├── YapPNG.py                   # Script utama plugin DaVinci Resolve (v2.2 Ultra)
├── install_plugin.bat          # Installer otomatis buat Windows
├── docs/
│   ├── ARCHITECTURE.md         # Penjelasan teknis & matematika VAD (English)
│   ├── WORKFLOW_GUIDE.md       # Panduan lengkap alur kerja (English)
│   └── WORKFLOW_GUIDE_ID.md    # Panduan lengkap alur kerja (Bahasa Indonesia)
├── test_assets/                # Karakter sampel siap tes
│   ├── Character_Host/         # Karakter Host (Neutral, Happy, Angry)
│   ├── Character_Guest/        # Karakter Bintang Tamu (Neutral, Smug, Surprised)
│   └── test_voice.wav          # Audio contoh buat ngetes
├── .gitignore
├── LICENSE
├── README.md                   # README English
└── README_ID.md                # README Bahasa Indonesia
```

---

## 📚 Bacaan Lebih Lanjut

* 📖 **[Panduan Alur Kerja Lengkap](docs/WORKFLOW_GUIDE_ID.md)**: Tutorial lengkap cara bikin video podcast 2 orang, automasi marker, dan aturan penamaan gambar.
* 🏛️ **[Dokumentasi Arsitektur & VAD](docs/ARCHITECTURE.md)**: Buat yang penasaran sama jeroan teknis algoritma prefix-sum energy & API Resolve.

---

## ⚙️ Syarat Penggunaan

* **DaVinci Resolve:** Versi 18, 19, atau 21+ (Free maupun Studio).
* **Python:** Python 3.8+ (Resolve otomatis pake Python yang keinstall di PC lu).
* **FFmpeg:** Udah terpasang di path sistem (buat convert stream audio).
* **NumPy (Opsional):** Buat ngebutin scan audio di bawah 30 milidetik.

---

## 📄 Lisensi

Proyek ini open-source di bawah [Lisensi MIT](LICENSE). Bebas lu pake dan modifikasi!
