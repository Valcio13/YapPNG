# 🎙️ YapPNG

> **Plugin animator sprite PNG (PNGtuber) berbasis suara yang berjalan langsung di DaVinci Resolve Free & Studio.**

[English](README.md) | **[Bahasa Indonesia](README_ID.md)**

[![Resolve](https://img.shields.io/badge/DaVinci%20Resolve-Free%20%26%20Studio%20(18%2C%2019%2C%2021%2B)-black?logo=davinci-resolve)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/Python-3.8%20--%203.12-blue?logo=python)](https://python.org)
[![NumPy](https://img.shields.io/badge/Akselerasi-NumPy%20Vectorized%20VAD-green?logo=numpy)](https://numpy.org)
[![License](https://img.shields.io/badge/Lisensi-MIT-purple.svg)](LICENSE)

**YapPNG** mengubah rekaman suara atau mikrofon Anda menjadi animasi karakter PNGtuber secara otomatis langsung di timeline Edit DaVinci Resolve. Plugin ini mendeteksi aktivitas suara secara instan tanpa perlu API cloud atau transkripsi yang lambat, lalu memotong dan menempatkan sprite Diam (Idle), Bicara (Talk), dan Berteriak (Shout) dengan animasi pantulan (bounce), penempatan posisi layar yang presisi, serta efek peredupan (dimming) otomatis bergaya podcast.

---

## ✨ Fitur Utama

* 🎛️ **Berjalan Langsung di Dalam Resolve:** Dibuka langsung dari menu `Workspace > Scripts > Edit > YapPNG` menggunakan antarmuka Qt `UIManager` bawaan Resolve. Kompatibel dengan **DaVinci Resolve Free & Studio**.
* ⚡ **Deteksi Suara VAD Super Cepat:** Menganalisis rekaman suara 5 menit hanya dalam waktu **~27 milidetik** menggunakan akselerasi prefix-sum NumPy (dengan fallback otomatis ke Python murni).
* 👥 **Dukungan Multi-Karakter (Podcast / Collab):** Rute trek audio & video terpisah untuk tiap karakter (contoh: Host di A1/V2/V3, Tamu di A2/V4/V5).
* 📂 **Pemindai Folder Otomatis:** Cukup pilih folder karakter dan klik **`📂 Auto-Scan`** untuk mengenali seluruh ekspresi (`idle`, `talk`, `shout`) secara otomatis.
* 🏷️ **Otomasi Ekspresi Berdasarkan Marker:** Tekan `M` pada timeline saat mendengarkan audio untuk membuat penanda ekspresi (`Happy`, `Angry`, `Neutral`). YapPNG akan memotong dan mengganti ekspresi sepanjang video 60+ menit hanya dengan **sekali klik**!
* 🦘 **Efek Pantulan "PNGtuber Bounce":** Menambahkan animasi loncatan vertikal dan denyut skala halus saat karakter berbicara, dengan lompatan $+60\%$ lebih tinggi saat berteriak.
* 📢 **Deteksi Suara Keras / Berteriak (Shout Trigger):** Mendeteksi teriakan, tawa keras, atau lonjakan volume ($>-12\text{ dB}$) untuk otomatis berganti ke sprite mulut berteriak/terbuka lebar.
* 💡 **Peredupan Karakter Pasif (Inactive Dimming):** Karakter yang sedang diam/mendengarkan akan otomatis meredup ($70\%$ opacity), dan langsung menyala terang $100\%$ begitu mulai berbicara.
* 📐 **Pengaturan Tata Letak & Ambil Posisi Layar:** Dilengkapi preset (*Kiri*, *Kanan*, *Tengah Bawah*) serta tombol **`📥 Fetch from Timeline Clip`** untuk menyalin posisi dan ukuran langsung dari viewer DaVinci Resolve.
* 🎙️ **Kalibrasi Kebisingan Sekali Klik:** Mengukur kebisingan ruangan (noise floor) dan menyesuaikan sensitivitas ambang batas suara secara otomatis.
* 🧹 **Mode Timpa Bersih (Clean Overwrite):** Mengganti potongan klip lama pada rentang In/Out secara rapi tanpa merusak susunan klip lainnya di timeline.

---

## 🎬 Mekanisme Pemotongan Timeline (Dual-Track Overlay)

YapPNG menggunakan sistem penumpukan dua trek video yang non-destruktif:

```text
Trek Video 3 (Bicara):        [ Klip Bicara / Teriak ]       [ Klip Bicara / Teriak ]
Trek Video 2 (Diam)  : [================== Klip Diam Menyambung ==================]
Trek Audio 1 (Suara) : [~~~~ "Halo semuanya!" ~~~~]          [~~~~ "Ayo mulai!" ~~~~]
```

* **Saat Hening / Mendengarkan:** Klip sprite Diam (Idle) tampil di bawah dengan opacity santai ($70\%$).
* **Saat Berbicara:** Potongan klip Bicara (Talk/Shout) menimpa di atasnya dengan opacity terang $100\%$ dan efek animasi pantulan.
* **100% Dapat Diedit:** Klip hasil pemotongan adalah klip video timeline biasa, sehingga Anda bebas memotong, menggeser, atau menghapusnya menggunakan alat bawaan Resolve.

---

## 🚀 Panduan Memulai Cepat

### 1. Instalasi
Jalankan skrip instalasi:
* **Windows:** Klik ganda file `install_plugin.bat`.
* **Manual / macOS / Linux:** Salin file `YapPNG.py` ke folder skrip DaVinci Resolve:
  * **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`
  * **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/`
  * **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/`

### 2. Buka di DaVinci Resolve
Buka proyek apa pun di DaVinci Resolve, lalu buka menu:
> **`Workspace` > `Scripts` > `Edit` > `YapPNG`**

### 3. Memotong Karakter Pertama Anda
1. Pada jendela YapPNG, pilih folder karakter Anda pada bagian **Character Folder** (atau gunakan contoh bawaan di [`test_assets/Character_Host`](test_assets/Character_Host)).
2. Klik tombol **`📂 Auto-Scan`**.
3. Tentukan titik Mark In (`I`) dan Mark Out (`O`) pada timeline Anda.
4. Klik tombol **`🎙️ Auto-Calibrate`** untuk mengkalibrasi sensitivitas mikrofon Anda.
5. Klik tombol **`▶ Splicing To Timeline`**!

---

## 📁 Struktur Repositori

```text
YapPNG/
├── YapPNG.py                   # Skrip utama plugin DaVinci Resolve (v2.2 Ultra)
├── install_plugin.bat          # Skrip installer otomatis untuk Windows
├── docs/
│   ├── ARCHITECTURE.md         # Dokumentasi teknis & algoritma VAD (Bahasa Inggris)
│   ├── WORKFLOW_GUIDE.md       # Panduan alur kerja lengkap (Bahasa Inggris)
│   └── WORKFLOW_GUIDE_ID.md    # Panduan alur kerja lengkap (Bahasa Indonesia)
├── test_assets/                # Aset sampel karakter siap pakai
│   ├── Character_Host/         # Karakter Host (Sprite Neutral, Happy, Angry)
│   ├── Character_Guest/        # Karakter Tamu (Sprite Neutral, Smug, Surprised)
│   └── test_voice.wav          # Rekaman suara sampel untuk pengujian
├── .gitignore
├── LICENSE
├── README.md                   # Dokumentasi Bahasa Inggris
└── README_ID.md                # Dokumentasi Bahasa Indonesia
```

---

## 📚 Panduan Lengkap

* 📖 **[Panduan Alur Kerja Lengkap (Bahasa Indonesia)](docs/WORKFLOW_GUIDE_ID.md)**: Pelajari cara setup multi-karakter podcast, automasi marker, dan konvensi penamaan gambar.
* 🏛️ **[Arsitektur Teknis & Matematika VAD](docs/ARCHITECTURE.md)**: Penjelasan mendalam tentang algoritma prefix-sum energy, smoothing histeresis, dan API Resolve.

---

## ⚙️ Persyaratan Sistem

* **DaVinci Resolve:** Versi 18, 19, atau 21+ (Edisi Free maupun Studio).
* **Python:** Python 3.8+ (DaVinci Resolve akan menggunakan instalasi Python yang ada di komputer Anda).
* **FFmpeg:** Terpasang di sistem PATH Anda (digunakan untuk membaca stream audio dengan cepat).
* **NumPy (Opsional):** Untuk akselerasi pemrosesan audio di bawah 30 milidetik.

---

## 📄 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat file [LICENSE](LICENSE) untuk informasi lebih lanjut.
