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

### 6. Emphasis, animasi dan bahasa
Ambil intent dan beat dari [editorial-intelligence](../editorial-intelligence/SKILL.md).
Gunakan word timestamps yang telah diperiksa untuk menonjolkan kata aktual saat
terdengar. Biarkan frasa utama stabil; ubah warna, bobot atau skala satu bagian
yang membantu makna. Jangan mengganti kata, negasi atau urutan untuk komedi.
Jangan menampilkan kata punchline sebelum reveal.

Entrance/exit singkat boleh memperjelas onset/emphasis. Hentikan animasi selama
penonton membaca. Movement hanya saat mengikuti perubahan komposisi atau gag
yang terbukti; caption tidak perlu bounce atau bergerak sepanjang waktu.
Uji posisi awal, tengah gerak dan akhir terhadap mata, mulut, HUD dan UI platform.
Untuk satu kata yang benar-benar penting, sinkronkan visual emphasis dengan
`word_ids` terverifikasi. Jika SFX ikut dipakai, letakkan event terpisah dalam
`audio-design.json`; jangan mengandalkan warna subtitle sebagai bukti bahwa kata
tersebut sudah diverifikasi atau menambahkan pop pada setiap kata.

Bedakan `dialogue`, `translation`, `reading-aid`, `emphasis` dan `information`.
Caption informasi editor harus jelas bukan kutipan dan didukung bukti. V2
menyimpan word_ids, emphasis_word_ids, bahasa, animasi beserta alasan dan posisi.
Dialogue/emphasis harus cocok dengan kata terverifikasi; terjemahan tidak bisa
dibuktikan lewat kecocokan kata dan memerlukan receipt review bahasa sendiri.

Untuk multilingual, pertahankan code-switching dan ejaan asli. Uji font fallback,
glyph, shaping dan line breaks pada render. Prioritaskan satu lapisan bahasa;
jangan menumpuk dialog, romaji dan terjemahan menjadi paragraf kecil. Dua speaker
overlap dapat memakai dua baris terpisah. Untuk tiga atau lebih suara, prioritaskan
ucapan yang dapat dipahami, labeli bagian tidak jelas dan sertakan transcript
lengkap bila relevan. Jangan menciptakan urutan dialog baru.

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
