# 📖 Panduan Alur Kerja YapPNG (Bahasa Indonesia)

Panduan langkah demi langkah menggunakan **YapPNG** di DaVinci Resolve: mulai dari persiapan gambar sprite karakter, setup podcast multi-karakter, hingga automasi ekspresi berbasis marker untuk video berdurasi panjang.

[English Guide](WORKFLOW_GUIDE.md) | **[Panduan Bahasa Indonesia](WORKFLOW_GUIDE_ID.md)**

---

## 🎨 1. Menyiapkan Folder & Gambar Sprite Karakter

YapPNG dapat mengenali semua ekspresi karakter Anda secara otomatis asalkan Anda mengikuti format penamaan file yang standar.

### Struktur Folder yang Disarankan:

```text
Proyek_PNGtuber/
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

### Kata Kunci Nama File yang Didukung:
* **Diam / Mulut Tertutup (Idle):** `_idle`, `_closed`, `_close`, `_mouth_closed`, `_shut`
* **Bicara / Mulut Terbuka (Talk):** `_talk`, `_talking`, `_open`, `_mouth_open`, `_speaking`
* **Berteriak / Mulut Sangat Lebar (Shout):** `_shout`, `_scream`, `_yell`, `_loud`, `_wide`

*(Anda juga bisa menggunakan subfolder per ekspresi, contoh: `Host/happy/idle.png` dan `Host/happy/talk.png`!)*

---

## 🎙️ 2. Setup untuk Satu Karakter

1. Buka DaVinci Resolve dan pastikan rekaman suara Anda berada di **Trek Audio 1 (A1)**.
2. Buka menu atas: **`Workspace` > `Scripts` > `Edit` > `YapPNG`**.
3. Di bagian **1. Character Profile**, pilih folder karakter Anda lalu klik tombol **`📂 Auto-Scan`**.
4. Atur posisi layar karakter di bagian **3. Placement, Dynamics & Dimming**:
   - Pilih preset (misal `Center Stage` atau `Left Side`).
   - Atau geser dan ubah ukuran klip karakter langsung di viewer DaVinci Resolve, lalu klik tombol **`📥 Fetch from Timeline Clip`**.
5. Tentukan rentang bagian video menggunakan tombol **`I` (Mark In)** dan **`O` (Mark Out)** di timeline Resolve.
6. Klik tombol **`🎙️ Auto-Calibrate`** untuk mengukur kebisingan ruangan dan mikrofon Anda secara otomatis.
7. Klik tombol **`▶ Splicing To Timeline`**!

---

## 👥 3. Setup Podcast / Kolaborasi Multi-Karakter

Jika Anda membuat video obrolan, podcast, atau gameplay berdua (contoh: Host di sebelah kiri, Tamu di sebelah kanan):

### Langkah A: Konfigurasi Karakter Host
1. Pilih **`Character_Host`** pada dropdown karakter.
2. Di bagian **Audio & Video Track Routing**:
   - Audio Track: **`Track 1`** (Mikrofon Host)
   - Idle Video Track: **`Track 2`**
   - Talk Video Track: **`Track 3`**
3. Di bagian **Placement**:
   - Layout Preset: **`Left Side`**
   - Flip Horizontal (Mirror): **Jangan dicentang** (menghadap ke kanan arah tamu)
4. Aktifkan **`🦘 Bounce Hop`** dan **`💡 Inactive Dim`** ($70\%$).

### Langkah B: Konfigurasi Karakter Tamu
1. Pilih **`Character_Guest`** (atau klik `+ New Char` untuk membuat baru).
2. Di bagian **Audio & Video Track Routing**:
   - Audio Track: **`Track 2`** (Mikrofon Tamu)
   - Idle Video Track: **`Track 4`**
   - Talk Video Track: **`Track 5`**
3. Di bagian **Placement**:
   - Layout Preset: **`Right Side`**
   - Flip Horizontal (Mirror): **Centang** (menghadap ke kiri arah host)
4. Aktifkan **`🦘 Bounce Hop`** dan **`💡 Inactive Dim`** ($70\%$).

### Langkah C: Eksekusi Pemotongan
1. Pilih **`Character_Host`** $\rightarrow$ Klik **`▶ Splicing To Timeline`**.
2. Pilih **`Character_Guest`** $\rightarrow$ Klik **`▶ Splicing To Timeline`**.
3. Kedua karakter sekarang berdampingan di video! Saat salah satu berbicara, karakternya akan melompat dan menyala terang $100\%$, sedangkan karakter yang sedang mendengarkan akan meredup $70\%$ secara natural.

---

## 🏷️ 4. Otomasi Ekspresi Berdasarkan Marker (Video Panjang)

Untuk video berdurasi 20–60 menit, Anda tidak perlu menandai Mark In / Out puluhan kali:

1. Dengarkan rekaman Anda sambil memutar timeline di DaVinci Resolve.
2. Setiap kali ekspresi karakter berubah, tekan tombol **`M`** untuk membuat penanda (marker):
   - Beri nama marker sesuai nama ekspresi: `Happy`, `Angry`, `Neutral`, `Smug`, dll.
3. Di jendela YapPNG, ubah **Placement Mode** menjadi:
   **`🏷️ Marker-Driven Expressions`**.
4. Klik tombol **`▶ Splicing To Timeline`**.
5. YapPNG akan membagi seluruh timeline Anda menjadi beberapa zona sesuai marker yang Anda buat, lalu menempatkan ekspresi yang tepat di sepanjang video dalam **sekali klik**!

---

## ⚙️ 5. Panduan Sensitivitas & Dinamika Suara

| Parameter | Rekomendasi | Penjelasan |
| :--- | :--- | :--- |
| **Threshold (dB)** | `-28 dB` s/d `-34 dB` | Batas volume deteksi suara bicara. Klik `Auto-Calibrate` agar terisi otomatis. |
| **Shouting Trigger (dB)**| `-10 dB` s/d `-14 dB` | Pemicu sekunder saat berteriak, tertawa keras, atau berseru. |
| **Mouth Hold (ms)** | `120 ms` s/d `150 ms` | Menahan mulut tetap terbuka di jeda antar suku kata agar tidak berkedip cepat. |
| **Bounce Height (px)** | `15 px` s/d `22 px` | Ketinggian lompatan animasi saat berbicara. Suara teriakan otomatis melompat $1.6\times$ lebih tinggi. |
| **Dim Opacity (%)** | `65%` s/d `75%` | Tingkat transparansi/keredupan saat karakter diam mendengarkan lawan bicara. |
