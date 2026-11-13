---
name: render-package-for-user
description: Packages VTuber clip edits into portable ZIP deliverables with FFmpeg scripts, ASS captions, assets, README, and mobile-friendly Google Colab instructions. Use when the user wants to render on their own PC or phone.
---

# Render Package for User

## Tujuan
Membuat paket yang bisa dijalankan pengguna di PC atau Colab tanpa memasukkan video sumber ke dalam ZIP.

## Aturan wajib
1. Jangan pernah memasukkan video sumber pengguna ke ZIP.
2. FFmpeg/FFprobe adalah dependensi render dasar; catat versi, encoder dan filter yang benar-benar dipakai. Jangan mengklaim semua build 6–8 sudah diuji.
3. Python/NumPy/WhisperX/model ASR hanya opsional dan dijelaskan terpisah.
4. Script menerima input path dan output path; jangan hard-code path komputer pembuat.
5. Jangan memakai filter_complex_script.
6. Jangan menyertakan token, cache model, file sementara, atau aset berhak cipta tanpa izin.
7. Script yang belum dijalankan harus ditandai belum diuji.

## Langkah kerja

### 1. Susun paket
Struktur yang disarankan:

~~~~text
clip-package/
├── BACA_DULU.txt
├── render.sh
├── render.bat
├── edit-plan.json
├── audio-design.json       # only when SFX are used
├── audio-assets/           # only permitted, hash-recorded assets
├── captions/
│   └── captions.ass
├── assets/
└── qa/
    ├── qa-report.json
    └── keyframes/
~~~~

Folder kosong tidak perlu dibuat.

### 2. Siapkan script
- Path input/output harus berupa argumen.
- Quote path yang mengandung spasi.
- Windows batch memakai %% untuk persen literal dan ^ untuk line continuation.
- Hindari command line CMD melebihi 8191 karakter.
- Filter graph tetap inline.
- Semua font, musik, dan SFX harus punya sumber/lisensi dan hash.
- Jika SFX digunakan, sertakan `audio-design.json`, `render_audio_events.py`, dan aset yang benar-benar dirujuk. Jalankan audio pass setelah base render; jangan menyertakan aset yang tidak dipakai.

### 3. Uji paket
- Smoke test render beberapa detik.
- Jalankan script dengan path yang mengandung spasi.
- Probe hasil.
- Pastikan tidak ada source video di ZIP.
- Periksa ukuran ZIP dan file MP4.

Sertakan decision brief dari [editorial-intelligence](../editorial-intelligence/SKILL.md)
dalam edit plan, source checksum/metadata, clock mapping, versi tool, command,
font/aset/lisensi, dan status review. Jangan mengemas data placeholder sebagai
hasil yang sudah diverifikasi. Jalankan validator artifact dengan stage final
untuk master final; paket draft harus melaporkan REVIEW/NOT_RUN secara jelas.
Dependensi Python/jsonschema untuk validasi developer terpisah dari render dasar.

### 4. Instruksi HP/Colab
1. Buka Google Colab melalui Chrome; gunakan mode desktop bila perlu.
2. Upload ZIP melalui panel Files atau mount Drive.
3. Upload video sumber secara terpisah.
4. Extract ZIP.
5. Jalankan script dengan path video.
6. Simpan hasil ke Drive sebelum runtime berakhir.
7. Unduh MP4 hasil render, bukan source video dari ZIP.

## Potongan FFmpeg
Contoh command Colab:

~~~~bash
!unzip -oq CLIP_PACKAGE.zip -d /content/clip-package
!bash /content/clip-package/render.sh "/content/SOURCE VIDEO.mp4" "/content/OUTPUT.mp4"
~~~~

Contoh belum diuji pada runtime pengguna.

## Checklist QA
- [ ] ZIP tidak berisi source video.
- [ ] Script menerima input/output path.
- [ ] Hanya FFmpeg wajib untuk render dasar.
- [ ] Tidak ada filter_complex_script.
- [ ] Script PC dan Windows tersedia bila diminta.
- [ ] Semua asset punya sumber/lisensi dan hash.
- [ ] Audio design plan dan SFX pass disertakan bila efek suara digunakan.
- [ ] Audio final didengar manusia, bukan hanya lolos limiter.
- [ ] Instruksi Colab dapat disalin dari HP.
- [ ] Smoke test dan QA report tersedia bila environment memungkinkan.

## Kesalahan umum
- Membundel VOD berukuran besar.
- Hard-code path lokal.
- Menyertakan font/musik tanpa lisensi.
- Membuat filter graph terlalu panjang untuk CMD.
- Menganggap ZIP berhasil berarti render script pasti berjalan.

## Batas kemampuan AI
AI dapat membuat paket dan script, tetapi kompatibilitas akhir harus diuji di perangkat/runtime pengguna.

## Production integration

The [production tools](../docs/production-tools.md) generate private working directories, not ready-to-ship ZIPs. Exclude inspection PNG/audio bundles, raw source media, models and unlicensed fonts from delivery. Include only the reviewed output and explicitly permitted reproducibility assets.
