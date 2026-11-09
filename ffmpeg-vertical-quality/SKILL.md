---
name: ffmpeg-vertical-quality
description: Converts VTuber landscape footage into deliberate 9:16 vertical video using subject-aware crop, keyframed reframing, blur-fit, stacked layouts, scaling, encoding, and platform-compatible export settings.
---

# FFmpeg Vertical Quality

## Tujuan
Menghasilkan master vertikal yang menjaga subjek dan informasi penting. Resolusi output tinggi tidak dapat memperbaiki crop yang salah.

## Aturan wajib
1. Inspeksi frame sebelum menentukan crop.
2. Jangan center-crop otomatis.
3. Jangan menambahkan sharpen, denoise, atau deblock tanpa bukti artefak.
4. Jangan mengubah FPS sumber tanpa alasan.
5. Output default proyek: 1080×1920, H.264, yuv420p, square pixels, AAC 48 kHz.
6. CRF/bitrate adalah keputusan encoding, bukan jaminan kualitas platform.
7. Semua command yang belum dijalankan harus ditandai belum diuji.

## Langkah kerja

### 1. Pilih layout
- Subject-aware crop bila subjek berada pada area yang dapat dipertahankan.
- Keyframed pan/crop bila subjek bergerak.
- Blur-fit bila seluruh frame landscape perlu terlihat.
- Stacked/side-by-side bila dua area sama penting dan penggunaannya masuk akal.
- Full-bleed bila source memang portrait atau crop aman.

Aturan specialist membatasi pilihan ini. Untuk beat conversation, gunakan
speaker-follow solo atau satu shared two-shot yang relevan. Stacked, side-by-side,
avatar-inset dan blur-fit bukan fallback otomatis untuk conversation. Simpan
instruksi pengguna yang eksplisit bila komposisi tersebut diminta.

Ambil keputusan dari [editorial-intelligence](../editorial-intelligence/SKILL.md)
dan [panduan motion](../editorial-intelligence/references/camera-and-effects.md).
FFmpeg tidak memilih speaker, memahami humor, atau menyediakan tracking AI
otomatis. Implementasikan koordinat/keyframes yang sudah diperiksa. Easing
adalah maksud interpolasi, bukan nama parameter yang pasti tersedia.

Pada source 1920×1080, crop 9:16 dari tengah hanya sekitar 608×1080. Mengisi 1080×1920 berarti upscale sekitar 1,78×; detail yang hilang tidak dapat dipulihkan.

### 2. Scaling dan detail
Lanczos adalah pilihan awal untuk scaling. Uji bicubic/spline bila hasil lebih cocok. Sharpen luma ringan sekitar 0,15–0,35 hanya bila diperlukan. Periksa halo, noise, rambut, outline avatar, teks kecil, dan HUD pada 100%.

### 3. Encoding
Titik awal master:
- x264 CRF 16–18, preset medium.
- CRF 19–22 bila ukuran file lebih penting.
- FPS sesuai source.
- yuv420p dan setsar=1.
- AAC 48 kHz.

YouTube memberi rekomendasi upload encoding H.264, frame rate sama dengan source, dan AAC/48 kHz. CRF di atas adalah rekomendasi kerja, bukan persyaratan resmi.

### 4. Render dan periksa
Probe output, ambil keyframes, periksa frame awal/tengah/akhir, dan dengarkan audio. Bandingkan source dan output untuk memastikan detail tidak hilang.

Untuk motion, periksa frame di antara keyframe. Untuk freeze/speed ramp, gunakan
time_map source/output, remap caption dan tentukan perlakuan audio secara
eksplisit. Periksa filter melalui `ffmpeg -h filter=NAME` pada build terpasang.
Tidak semua build menyediakan libass, encoder atau filter yang sama. Jika
treatment tidak dapat dijalankan/ditinjau, gunakan alternatif sederhana dan
catat batasnya. Synthetic smoke test hanya membuktikan jalur teknis yang diuji.

## Potongan FFmpeg
Blur-fit fallback:

~~~~bash
ffmpeg -i INPUT.mp4 -filter_complex "[0:v]split=2[bg0][fg0];[bg0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=22:2[bg];[fg0]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]" -map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -ar 48000 OUTPUT.mp4
~~~~

Contoh belum diuji; blur-fit hanya fallback bila crop merusak konteks.

## Checklist QA
- [ ] Layout dipilih dari bukti visual.
- [ ] Avatar/gameplay/HUD yang penting dipertahankan.
- [ ] Tidak ada halo atau sharpen berlebihan.
- [ ] Resolusi, pixel format, FPS, dan audio sesuai target.
- [ ] Keyframes dilihat pada ukuran aktual.
- [ ] Ukuran file dan durasi masuk akal.

## Kesalahan umum
- Menganggap 1080p output sama dengan detail 1080p source.
- Sharpen untuk memperbaiki crop yang salah.
- Denoise semua video secara default.
- Memaksa 30 fps pada source 60 fps.
- Menggunakan blur-fit untuk semua tipe footage.

## Batas kemampuan AI
Metrik numerik tidak dapat memutuskan komposisi terbaik atau detail yang penting bagi penonton. Inspeksi visual tetap diperlukan.

## Production integration

The [bounded EDL preview renderer](../scripts/render_edl.py) executes supported cuts, crops and fixed-size pans. Read its [support matrix](../docs/production-tools.md) before routing. It rejects unimplemented zoom, effects, retiming and mix changes instead of silently ignoring them.
