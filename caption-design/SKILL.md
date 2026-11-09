---
name: caption-design
description: Designs readable, synchronized, speaker-coded captions and subtitles for VTuber vertical clips, including Indonesian/Japanese/English dialogue, emphasis words, and safe placement around faces and HUD.
---

# Caption Design

## Tujuan
Membuat ucapan mudah dibaca di ponsel tanpa menutupi wajah, gameplay, HUD, atau punchline. Caption harus setia pada ucapan dan gaya visual klip.

## Aturan wajib
1. Hanya gunakan teks VERIFIED atau USER_CONFIRMED.
2. Jangan menerjemahkan jika pengguna meminta verbatim; jangan menambahkan reading/furigana kecuali diminta atau memang diperlukan untuk referensi.
3. Jangan menulis ulang dialog agar lebih lucu.
4. Gunakan satu mapping warna per speaker yang stabil. Speaker unknown memakai neutral.
5. Maksimal dua baris sebagai default; pecah kalimat berdasarkan frasa alami.
6. Jangan menutupi mata, mulut, HUD, score, crosshair, atau teks penting.
7. Safe-zone koordinat adalah guardrail awal, bukan pengganti inspeksi visual.

## Langkah kerja

### 1. Tentukan jenis teks
- Verbatim caption: kata yang benar-benar diucapkan.
- Translation subtitle: terjemahan yang dibedakan jelas dari ucapan asli.
- Reading aid: furigana/romaji untuk bantuan baca.
- Editorial emphasis: kata yang sama dari ucapan, hanya ditonjolkan secara visual.
Jangan mencampur jenis teks tanpa label yang jelas.

### 2. Pecah frasa
- Tampilkan frasa yang dapat dibaca dalam satu glance.
- Pertahankan negasi, nama, dan kata kunci.
- Hindari satu kata per caption kecuali timing komedi memang membutuhkannya.
- Hindari paragraf panjang.
- Pertahankan jeda dan timing reaksi.

### 3. Hierarki visual
- Font sans-serif tebal, rounded bila cocok dengan referensi.
- Kontras teks tinggi dengan outline/shadow secukupnya.
- Ukuran awal 64–82 px pada canvas 1080×1920; uji keterbacaan pada layar HP.
- Satu atau dua baris; gunakan warna speaker yang kontras.
- Warna harus tetap terbaca pada background terang/gelap.

### 4. Posisi
- Mulai dari lower-middle, lalu pindahkan bila wajah/HUD berada di sana.
- Sisakan ruang dari tepi dan area UI platform.
- Periksa setiap shot, bukan hanya satu posisi global.
- Hindari menaruh caption tepat pada mulut speaker.

### 5. Timing
- Caption masuk mengikuti awal frasa yang terdengar.
- Caption keluar setelah kata terakhir selesai, dengan sedikit ruang baca.
- Jangan memotong kata pada pergantian shot.
- Untuk overlap, atur dua baris speaker secara terpisah tanpa mengubah urutan waktu.

## Potongan FFmpeg
Burn-in ASS subtitle (path perlu di-escape sesuai OS):

~~~~bash
ffmpeg -i INPUT.mp4 -vf "subtitles=captions.ass" -c:v libx264 -preset medium -crf 18 -c:a copy OUTPUT.mp4
~~~~

## Checklist QA
- [ ] Teks sama dengan transcript terverifikasi.
- [ ] Ejaan nama dan istilah benar.
- [ ] Warna speaker konsisten.
- [ ] Maksimal dua baris pada mayoritas caption.
- [ ] Tidak menutup mata/mulut/HUD.
- [ ] Timing tidak mendahului atau tertinggal dari ucapan.
- [ ] Kontras terbaca pada frame terang dan gelap.
- [ ] Japanese script/reading/translation tidak tercampur.

## Kesalahan umum
- Caption seluruh kalimat panjang sekaligus.
- Menggunakan font kecil agar semua kata muat.
- Menempatkan semua caption pada satu koordinat.
- Memberi warna speaker yang belum teridentifikasi.
- Menganggap outline tebal selalu menyelesaikan masalah kontras.

## Batas kemampuan AI
AI dapat mengatur timing dan style dari transcript, tetapi harus melihat preview final untuk mendeteksi overlap wajah, HUD, atau UI platform.
