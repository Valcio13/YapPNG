# 📖 Panduan Lengkap Fitur & Alur Kerja YapPNG

Panduan lengkap dan santai buat makai semua fitur **YapPNG** di DaVinci Resolve (Free maupun Studio): dari persiapan gambar PNGtuber, alur multi-track podcast, penataan posisi visual, sampai tips video panjang 2 jam anti-freeze.

[English Guide](WORKFLOW_GUIDE.md) | **[Panduan Bahasa Indonesia](WORKFLOW_GUIDE_ID.md)**

---

## 📑 Daftar Isi
1. [Format Nama File & Auto-Scan](#1-format-nama-file--auto-scan)
2. [Mengenal 6 Bagian Utama UI YapPNG](#2-mengenal-6-bagian-utama-ui-yappng)
3. [Panduan Lengkap Marking (Tandai Timeline)](#3-panduan-lengkap-marking-tandai-timeline)
   - [A. Mark In & Mark Out (`I` & `O`)](#a-mark-in--mark-out-i--o)
   - [B. Entire Audio Track (Satu Timeline Penuh)](#b-entire-audio-track-satu-timeline-penuh)
   - [C. Marker-Driven Expressions (`M`)](#c-marker-driven-expressions-m)
4. [Routing Multi-Track Audio & File Eksternal](#4-routing-multi-track-audio--file-eksternal)
   - [Pakai Track Audio Lain di Timeline (Track 2, 3, dst.)](#pakai-track-audio-lain-di-timeline-track-2-3-dst)
   - [Import Langsung File Audio Mentah](#import-langsung-file-audio-mentah)
5. [Sensitivitas Suara, Auto-Calibrate & Teriak](#5-sensitivitas-suara-auto-calibrate--teriak)
6. [Penataan Posisi Layar, Bounce Hop & Dimming](#6-penataan-posisi-layar-bounce-hop--dimming)
   - [Ambil Posisi Visual ("Fetch from Timeline Clip")](#ambil-posisi-visual-fetch-from-timeline-clip)
   - [Animasi Lompat (Bounce Pop Physics)](#animasi-lompat-bounce-pop-physics)
   - [Mode Menyimak / Redup (Inactive Dimming)](#mode-menyimak--redup-inactive-dimming)
7. [Contoh Alur Kerja Nyata (Praktek Langsung)](#7-contoh-alur-kerja-nyata-praktek-langsung)
   - [Alur A: Video Gaming / Konten Solo](#alur-a-video-gaming--konten-solo)
   - [Alur B: Podcast / Collab Discord Berdua](#alur-b-podcast--collab-discord-berdua)
   - [Alur C: Optimasi Video Panjang 2 Jam](#alur-c-optimasi-video-panjang-2-jam)

---

## 🎨 1. Format Nama File & Auto-Scan

YapPNG sudah punya fitur cerdas untuk mengenali jenis mulut dan ekspresi secara otomatis, asalkan kamu memakai akhiran nama file standar berikut:

### Struktur Folder yang Rapi:
```text
Folder_Aset_Karakter/
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

### Kata Kunci Akhiran yang Dikenali:
* **Diem / Mingkem (Idle):** `_idle`, `_closed`, `_close`, `_mouth_closed`, `_shut`
* **Bicara / Mangap (Talk):** `_talk`, `_talking`, `_open`, `_mouth_open`, `_speaking`
* **Teriak / Mangap Lebar (Shout):** `_shout`, `_scream`, `_yell`, `_loud`, `_wide`

*(Bisa juga dipisah per subfolder, misal `Character_Host/happy/idle.png` dan `Character_Host/happy/talk.png`!)*

Cukup klik tombol **`📂 Auto-Scan`** di Bagian 1, dan semua ekspresi langsung terisi otomatis dalam 1 detik!

---

## 🖥️ 2. Mengenal 6 Bagian Utama UI YapPNG

Antarmuka YapPNG didesain menyerupai DaVinci Resolve Studio Inspector bertema gelap modern:

1. **Bagian 1: Character Profile (Pip Biru):**
   - Mengganti profil karakter (misal `Character_Host`, `Character_Guest`).
   - Buat karakter baru (`+ New Char`) atau hapus profil (`🗑 Del`).
   - Tentukan folder karakter dan jalankan `📂 Auto-Scan`.
2. **Bagian 2: Expression Sprites (Pip Ungu):**
   - Ganti ekspresi aktif (`Neutral`, `Happy`, `Angry`, dll.).
   - Menampilkan 3 sprite tiap ekspresi: **Idle (Mingkem)**, **Talk (Mangap)**, dan **Shout (Teriak)**.
3. **Bagian 3: Placement, Dynamics & Dimming (Pip Cyan):**
   - Preset posisi: `Left Side`, `Right Side`, `Center`, atau `Custom`.
   - `📥 Fetch from Timeline Clip`: Menyalin koordinat posisi Pan, Tilt, Zoom, dan Flip langsung dari viewer DaVinci Resolve!
   - `🦘 Bounce Hop`: Efek loncat vertikal saat bicara.
   - `💡 Inactive Dim`: Meredupkan karakter yang sedang diam mendengarkan co-host.
4. **Bagian 4: Audio & Track Routing (Pip Amber):**
   - Sumber audio: Dari track timeline Resolve atau file audio eksternal.
   - Penomoran video track untuk klip Idle (diam) dan klip Talk (ngomong).
5. **Bagian 5: Voice & Shouting Detection (Pip Hijau):**
   - Slider ambang batas suara (*noise gate*) dengan angka dB langsung.
   - `🎙️ Auto-Calibrate`: 1-klik untuk kalibrasi kebisingan ruangan secara otomatis.
   - Slider pemicu teriak (*shouting trigger*).
   - Slider tahan mulut (*mouth hold ms*).
6. **Bagian 6: Timeline Splicing Options (Pip Indigo):**
   - Mode jangkauan (In/Out Range, Entire Track, atau Marker-Driven).
   - Checkbox *Clean Overwrite* (menimpa hasil potongan sebelumnya secara rapi).
7. **Action Dock (Terkunci di Bawah):**
   - Lampu indikator status (🟢 Siap / 🔵 Memproses / 🔴 Error).
   - Progress bar dinamis dengan persentase dan estimasi waktu sisa (*ETA*).
   - Tombol `🔍 Preview Detection` dan tombol utama `⚡ SPLICING TO TIMELINE`.
   - Berubah menjadi tombol merah `🛑 Stop / Cancel` saat proses sedang berjalan.

---

## ✂️ 3. Panduan Lengkap Marking (Tandai Timeline)

### A. Mark In & Mark Out (`I` & `O`)
Gunakan cara ini kalau kamu cuma mau men-generate animasi PNGtuber di **bagian tertentu saja** (misal segmen highlight 3 menit dari video 2 jam):

1. Geser playhead (garis merah) ke detik awal $\rightarrow$ tekan **`I`** di keyboard (*Mark In*).
2. Geser playhead ke detik akhir $\rightarrow$ tekan **`O`** di keyboard (*Mark Out*).
3. Di YapPNG Bagian 6, pilih **Range Mode**: **`Mark In / Out Range`**.
4. Klik **`⚡ SPLICING TO TIMELINE`**.
5. *Untuk mereset/menghapus tanda In-Out di Resolve: tekan **`Alt + X`**.*

### B. Entire Audio Track (Satu Timeline Penuh)
Pilih mode ini kalau kamu mau YapPNG langsung memproses seluruh timeline dari frame 0 sampai video selesai tanpa perlu menandai In/Out manual.

### C. Marker-Driven Expressions (`M`)
Fitur keren untuk **mengganti ekspresi otomatis** di video panjang tanpa repot motong scene manual:
1. Putar timeline kamu di DaVinci Resolve.
2. Tiap kali karakter harus ganti emosi (misal momen lucu atau kaget), tekan tombol **`M`** untuk bikin marker di timeline.
3. Tekan **`M` sekali lagi** (atau double-click titik markernya) untuk buka kotak nama marker.
4. Di kolom **Name**, ketik nama ekspresi yang ada di YapPNG kamu: `Happy`, `Angry`, `Smug`, atau `Neutral`.
5. Di YapPNG Bagian 6, ubah **Range Mode** menjadi **`🏷️ Marker-Driven Expressions`**.
6. Klik **`⚡ SPLICING TO TIMELINE`**!
7. YapPNG otomatis membagi timeline mengikuti marker: bagian awal memakai sprite Neutral, begitu menyentuh marker Happy otomatis berganti memakai Happy, dst.

---

## 🎛️ 4. Routing Multi-Track Audio & File Eksternal

### Pakai Track Audio Lain di Timeline (Track 2, 3, dst.)
Kalau kamu punya audio teman mabar / co-host di track terpisah:
1. Taruh audio tersebut di **Audio Track 2** di DaVinci Resolve.
2. Di YapPNG Bagian 4 (**Audio & Track Routing**):
   - Set **Audio Source**: `Timeline Audio Track`.
   - Set **Audio Track**: `2`.
3. Pastikan **Talk Video Track** diset ke track video yang kosong (misal Video Track 4 & 5) agar tidak menimpa karakter pertama.

### Import Langsung File Audio Mentah
Kalau kamu punya file voiceover mentah (`.wav`, `.mp3`, `.m4a`, `.flac`) yang belum ditaruh di timeline:
1. Di Bagian 4, ganti **Audio Source** jadi **`Custom Audio File`**.
2. Klik tombol **`Browse...`** di samping kolom *Or Audio File* dan pilih filenya.
3. YapPNG langsung menganalisis file audio tersebut dengan decoding instan di RAM.

---

## 🎙️ 5. Sensitivitas Suara, Auto-Calibrate & Teriak

| Pengaturan | Nilai Rekomendasi | Penjelasan |
| :--- | :---: | :--- |
| **Threshold (dB)** | `-28 dB` s/d `-34 dB` | Pemicu suara bicara. Suara di atas volume ini akan membuka mulut. |
| **🎙️ Auto-Calibrate** | *Klik 1 Kali* | Menganalisis noise ruangan kamu dan menyetel threshold ideal secara otomatis. |
| **Shouting Trigger** | `-10 dB` s/d `-14 dB` | Mendeteksi teriakan atau tawa kencang dan otomatis memanggil sprite `_shout`. |
| **Mouth Hold (ms)** | `120 ms` s/d `150 ms` | Menahan mulut tetap terbuka antar suku kata agar tidak bergetar patah-patah (*flicker*). |

---

## 📐 6. Penataan Posisi Layar, Bounce Hop & Dimming

### Ambil Posisi Visual ("Fetch from Timeline Clip")
Daripada menebak-nebak angka koordinat X dan Y:
1. Tarik salah satu gambar PNG karakter kamu ke timeline DaVinci Resolve.
2. Posisikan, perbesar/perkecil (*zoom*), atau balik horizontal (*flip*) langsung di layar viewer DaVinci Resolve menggunakan kontrol Transform di tab Inspector kanan atas.
3. Klik klip tersebut di timeline agar terseleksi.
4. Di YapPNG Bagian 3, klik tombol **`📥 Fetch from Timeline Clip`**.
5. YapPNG langsung membaca dan menyalin angka Pos X, Pos Y, Zoom, dan Flip secara presisi! Klip pancingan tadi bisa langsung kamu hapus.

### Animasi Lompat (Bounce Pop Physics)
* Centang **`🦘 Bounce Hop`** dan atur **Hop (px)** (standar: `18 px`).
* Karakter akan otomatis memantul ke atas tiap kali ada tarikan suara bicara.
* Saat teriak (*shout*), tinggi pantulan otomatis dikalikan **$1.6\times$** lebih tinggi dengan efek zoom kartun!

### Mode Menyimak / Redup (Inactive Dimming)
* Centang **`💡 Inactive Dim`** dan atur **Dim (%)** (standar: `70%`).
* Saat berbicara, karakter menyala terang $100\%$.
* Saat diam mendengarkan co-host, karakter otomatis meredup ke $70\%$ transparansi, menciptakan hierarki fokus visual profesional seperti streamer papan atas.

---

## 🚀 7. Contoh Alur Kerja Nyata (Praktek Langsung)

### Alur A: Video Gaming / Konten Solo
1. Taruh audio suara di **Audio Track 1**.
2. Buka YapPNG (**Workspace > Scripts > Edit > YapPNG**).
3. Pilih karakter dan preset posisi (misal `Left Side`).
4. Klik tombol **`🎙️ Auto-Calibrate`**.
5. Tandai In (`I`) dan Out (`O`) di timeline.
6. Klik **`⚡ SPLICING TO TIMELINE`**. Selesai!

### Alur B: Podcast / Collab Discord Berdua
1. Audio Host di **Audio 1**, Audio Tamu di **Audio 2**.
2. **Setting Host:**
   - Profil: `Character_Host`.
   - Audio Track: `1`, Video Idle: `2`, Video Talk: `3`.
   - Preset: `Left Side` (Flip Horizontal: jangan dicentang).
   - Klik **`⚡ SPLICING TO TIMELINE`**.
3. **Setting Tamu:**
   - Profil: `Character_Guest`.
   - Audio Track: `2`, Video Idle: `4`, Video Talk: `5`.
   - Preset: `Right Side` (Flip Horizontal: dicentang agar saling berhadapan).
   - Klik **`⚡ SPLICING TO TIMELINE`**.
4. Kedua karakter akan saling bersahut-sahutan di layar secara otomatis!

### Alur C: Optimasi Video Panjang 2 Jam
1. YapPNG sudah otomatis memakai **Single-Pass Audio Grouping**, membaca file rekaman video gameplay besar (seperti MKV) hanya 1 kali dalam hitungan detik.
2. Proses pemotongan berjalan dalam **micro-batch 35 klip**, sehingga DaVinci Resolve dan YapPNG tetap responsif 60 FPS tanpa freeze atau *(Not Responding)*.
3. Jika sewaktu-waktu ingin membatalkan proses, cukup klik tombol merah **`🛑 Stop / Cancel`** di bagian bawah.
