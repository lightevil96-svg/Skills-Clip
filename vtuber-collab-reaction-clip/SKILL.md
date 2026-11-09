---
name: vtuber-collab-reaction-clip
description: Edits multi-person VTuber collaborations, group reactions, overlapping dialogue, call-ins, and reaction chains into short-form clips while preserving speaker attribution and conversational timing.
---

# VTuber Collab & Reaction Clip

## Tujuan
Membuat interaksi banyak VTuber tetap mudah diikuti. Penonton harus memahami siapa yang bicara, siapa yang bereaksi, dan bagaimana satu reaksi memicu reaksi berikutnya.

## Aturan wajib
1. Jangan menebak identitas talent dari warna rambut, posisi, atau desain avatar.
2. Speaker diarization dan pemetaan avatar adalah dua hal berbeda; jangan menyamakan S1 otomatis dengan avatar tertentu.
3. Jangan memotong overlap yang menjadi inti lelucon atau reaksi.
4. Jangan tampilkan semua avatar dengan ukuran sama sepanjang klip bila hanya satu yang relevan.
5. Jangan mengubah urutan sebab-akibat untuk menciptakan reaksi palsu.
6. Subtitle harus membedakan speaker secara konsisten; speaker tidak dikenal memakai style netral.
7. Jangan menaruh caption di atas mata, mulut, atau ekspresi yang menjadi payoff.

## Langkah kerja

### 1. Buat speaker ledger
Untuk setiap speaker, catat:
- speaker_id sementara;
- display name hanya jika dikonfirmasi;
- avatar reference;
- bukti pemetaan (lip flap, giliran bicara, visual cue, user confirmation);
- status UNKNOWN, CANDIDATE, VERIFIED, atau USER_CONFIRMED.

Jangan mengunci pemetaan berdasarkan satu frame. Cari minimal dua atau lebih giliran bicara yang konsisten atau minta konfirmasi.

### 2. Identifikasi pola interaksi
- **Turn-taking:** speaker bergantian; gunakan solo shot sesuai giliran.
- **Overlap:** dua atau lebih suara bertumpuk; pertahankan overlap dan gunakan shared shot bila visualnya mendukung.
- **Reaction chain:** satu orang memicu, orang lain bereaksi, lalu reaksi ketiga memperbesar komedi.
- **Group laugh:** beberapa avatar tertawa; tampilkan grup hanya selama reaksi bersama.
- **Call-in:** orang yang sedang bicara dapat tidak terlihat; gunakan layout yang menjaga konteks tanpa mengarang posisi.

### 3. Pilih kamera
- Solo shot untuk speaker aktif.
- Shared two-shot/three-shot untuk interaksi simultan yang relevan.
- Reaction cutaway hanya ketika ekspresi pendengar menambah informasi.
- Kembali ke speaker utama setelah reaction cutaway.
- Hindari persistent split-screen atau grid avatar sebagai default.
- Jika sumber tidak memiliki layout yang dapat dicrop dengan baik, pilih blur-fit atau komposisi lain yang mempertahankan semua bukti.

### 4. Bangun alur
Gunakan urutan pemicu → respons pertama → eskalasi → reaksi grup → payoff. Jangan memindahkan reaksi sebelum pemicunya. Sisakan sedikit ruang untuk tawa dan overlap alami.

### 5. Caption dan audio
- Gunakan warna speaker yang kontras dan stabil.
- Untuk speaker unknown, gunakan warna netral.
- Jika dua speaker overlap, pecah caption menjadi baris terpisah dengan timestamp yang benar; jangan mengurutkan ulang.
- Jangan menurunkan suara orang lain sampai hilang jika overlap itu penting.

## Potongan FFmpeg
Contoh dua crop yang disambung secara editorial harus menggunakan timestamp shot yang jelas. Hindari membangun split-screen permanen hanya karena lebih mudah dirender.

~~~~bash
ffmpeg -i INPUT.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k OUTPUT.mp4
~~~~

Ini hanya fallback fit sederhana, belum diuji pada source; gunakan layout shot-specific bila perlu.

## Checklist QA
- [ ] Speaker ledger tersedia.
- [ ] Identitas talent tidak ditebak.
- [ ] Giliran bicara dan overlap tetap benar.
- [ ] Reaction chain tidak terbalik.
- [ ] Layout berubah mengikuti kepentingan beat.
- [ ] Warna subtitle konsisten dan terbaca.
- [ ] Ekspresi penting tidak tertutup.
- [ ] Audio overlap masih dapat dipahami.

## Kesalahan umum
- Memberi warna subtitle berdasarkan posisi avatar saja.
- Memaksa semua avatar masuk dalam satu frame.
- Memotong suara kedua saat overlap.
- Mengubah reaction cutaway menjadi shot utama terlalu lama.
- Menganggap diarization otomatis sebagai identitas talent.

## Batas kemampuan AI
Diarization dapat salah pada tawa, teriakan, suara mirip, dan overlap. Pemetaan speaker-avatar harus diverifikasi dari visual/audio atau dikonfirmasi pengguna.
