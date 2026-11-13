---
name: qa-and-self-review
description: Performs technical and editorial quality assurance for VTuber short clips and render packages, including format, duration, A/V timing, loudness, black frames, caption safety, keyframes, and source exclusion.
---

# QA & Self-Review

## Tujuan
Memastikan file benar-benar siap ditonton dan diserahkan, bukan sekadar berhasil diekspor.

## Aturan wajib
1. Jangan menyebut PASS jika pemeriksaan belum dijalankan.
2. Exit code FFmpeg bukan bukti hasil berkualitas.
3. Audio harus didengar manusia sebelum final.
4. Sharpness proxy tidak membuktikan gambar tajam.
5. REVIEW dan SKIP bukan PASS.
6. Setiap FAIL harus diperbaiki atau dijelaskan sebagai exception yang disetujui pengguna.

## Langkah kerja

### 1. Pemeriksaan teknis
Probe:
- resolusi dan aspect ratio;
- codec, pixel format, FPS;
- durasi;
- audio codec, sample rate, channels;
- video/audio stream start time dan durasi;
- ukuran file.

Threshold internal awal:
- output 1080×1920, H.264, yuv420p;
- AAC 48 kHz;
- start delta stream ≤80 ms dan durasi delta ≤120 ms;
- loudness proyek -16…-14 LUFS dan true peak ≤-1 dBTP;
- tidak ada black segment tidak sengaja ≥0,20 detik.

Threshold tersebut adalah guardrail proyek, bukan ketentuan resmi platform dan bukan bukti lip-sync sempurna.

### 2. Pemeriksaan visual
Periksa frame awal, 1–2 detik pertama, tiap perubahan layout, caption, overlay, payoff, dan frame akhir. Pastikan mata/mulut, avatar, HUD, score, reticle, chat penting, dan game objective tidak tertutup.

### 3. Pemeriksaan caption
- Hanya VERIFIED/USER_CONFIRMED.
- Maksimal dua baris sebagai default.
- Ejaan dan speaker mapping konsisten.
- Safe-zone diperiksa secara otomatis bila tersedia dan manual pada preview.

### 4. Pemeriksaan audio
Dengarkan dengan earphone dan speaker HP pada volume rendah serta normal. Periksa voice clarity, BGM ducking, game cue, clipping, pumping, audio cut, dan setiap SFX. Cocokkan event ID/timestamp dengan sumbernya; pastikan kata penting, plosive, tawa, serta jeda tetap jelas. Sidechain pada mixed source bukan voice isolation.

### 5. Pemeriksaan paket
Jika ZIP dibuat, pastikan source video tidak ada di dalamnya. Jalankan script dengan path berspasi bila memungkinkan. Catat versi FFmpeg dan status test.

### 6. Editorial quality assessment
Gunakan intent dan bukti [editorial-intelligence](../editorial-intelligence/SKILL.md).
Nilai 0–4 dengan [rubric berindikator](references/editorial-rubric.md) untuk
storytelling clarity, hook effectiveness, timing precision, humor/emotional
delivery, visual composition, caption readability, audio comfort, editing
naturalness, effect restraint dan overall coherence.

Simpan [editorial review JSON](../schemas/editorial-review.schema.json) terpisah
dari technical checks. Catat mode automated, agent-audiovisual atau human.
Automated checks tidak memberi skor editorial. NOT_RUN/REVIEW/SKIP memakai
score null; jangan mengisi nilai rata-rata atau default. Setiap skor perlu bukti
dan setiap kekurangan perlu tindakan spesifik beserta timestamp.

Bandingkan treatment sederhana dengan treatment ekspresif pada beat yang sama.
Periksa apakah efek membantu makna/timing, apakah silence berguna terjaga, dan
apakah ending menyelesaikan adegan. Nilai tinggi tidak membuktikan profesional,
viral, atau cocok untuk semua penonton. Pertahankan REVIEW jika bukti kurang.

### 7. Perbaiki dan periksa kembali
Revisi masalah utama sebelum dekorasi tambahan. Setelah retime/crop berubah,
periksa ulang caption, gerak, audio dan batas shot yang terdampak. Rekam issue,
aksi, status dan artifact recheck. Jangan mengganti FAIL menjadi PASS hanya
karena alasan perubahan sudah ditulis. Human review tetap terpisah dan nyata.

## Potongan FFmpeg
Deteksi black segment:

~~~~bash
ffmpeg -hide_banner -i OUTPUT.mp4 -vf "blackdetect=d=0.20:pix_th=0.10" -an -f null -
~~~~

## Checklist QA
- [ ] Format dan codec sesuai.
- [ ] Durasi sesuai brief/platform.
- [ ] Stream timing diperiksa.
- [ ] Loudness/true peak diperiksa.
- [ ] Black frame tidak sengaja diperiksa.
- [ ] Keyframes dilihat.
- [ ] Caption diverifikasi dan aman.
- [ ] Audio didengar manusia.
- [ ] Setiap SFX punya evidence, timing, source/license/hash dan fungsi yang jelas.
- [ ] Tidak ada SFX yang menutupi kata atau menyiratkan kejadian palsu.
- [ ] Audio mix receipt menyatakan batas sidechain dan human-listening status.
- [ ] Setiap SFX punya evidence, timing, source/license/hash dan fungsi yang jelas.
- [ ] Tidak ada SFX yang menutupi kata atau menyiratkan kejadian palsu.
- [ ] Audio mix receipt menyatakan batas sidechain dan human-listening status.
- [ ] ZIP tidak berisi source video.
- [ ] Semua FAIL/REVIEW/SKIP dilaporkan.

## Kesalahan umum
- Menganggap stream timing delta sebagai bukti lip-sync.
- Menganggap edge-energy tinggi sebagai ketajaman.
- Menganggap safe-zone checker mendeteksi wajah/HUD.
- Menyembunyikan FAIL agar hasil tampak selesai.
- Tidak melihat hasil render setelah proses export.

## Batas kemampuan AI
QA otomatis hanya mengukur hal yang dapat dihitung. Komposisi, humor, naturalness, keterbacaan, dan kenyamanan audio memerlukan review manusia.

## Production integration

Use [verify_evidence.py](../scripts/verify_evidence.py) to check actual source metadata/hash and inspection-file hashes. Follow the [production guide](../docs/production-tools.md). File integrity PASS is distinct from audiovisual evidence verification, editorial quality and human listening.
