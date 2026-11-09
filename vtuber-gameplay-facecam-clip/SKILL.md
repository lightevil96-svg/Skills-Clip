---
name: vtuber-gameplay-facecam-clip
description: Edits VTuber gameplay clips where game footage, HUD, avatar or facecam, and live reactions must remain understandable in a vertical short. Use for gameplay highlights, clutch, fail, horror, competitive, or game-stream moments.
---

# VTuber Gameplay + Facecam Clip

## Tujuan
Mengubah momen gameplay menjadi short vertikal yang tetap memperlihatkan hubungan antara aksi game dan reaksi VTuber. Gameplay dan HUD bukan dekorasi: keduanya sering menjadi bukti mengapa reaksi terjadi.

## Aturan wajib
1. Jangan crop sebelum mengetahui lokasi avatar, gameplay target, score, reticle, health, objective, chat, dan event penting.
2. Jangan menghilangkan informasi game yang dibutuhkan untuk memahami aksi atau hasil.
3. Jangan memperbesar avatar sampai gameplay hanya menjadi latar yang tidak terbaca.
4. Jangan menambahkan SFX seolah-olah ada hit, kill, scare, atau kemenangan yang tidak terjadi.
5. Pertahankan build-up yang penting, terutama pada horror, clutch, dan komedi yang bergantung pada timing.
6. Facecam tidak wajib selalu terlihat besar. Ukuran dan posisi mengikuti kepentingan beat.
7. Jangan menggunakan crop tengah secara otomatis.

## Langkah kerja

### 1. Klasifikasikan gameplay
- **Gameplay dominan:** aksi dan HUD menjadi fokus; avatar menjadi inset yang cukup terbaca.
- **Reaction dominan:** reaksi avatar menjadi payoff; gameplay tetap terlihat sebagai konteks.
- **Competitive/clutch:** score, target, crosshair, kill feed, dan hasil harus dipertahankan.
- **Horror:** ambience dan jeda dapat menjadi bagian dari ketegangan; jangan menghapusnya otomatis.
- **Fail/funny moment:** pertahankan tindakan penyebab, hasil, dan reaksi.
- **Tutorial/strategy:** informasi visual yang menjelaskan langkah harus tetap terbaca.

### 2. Pilih komposisi
- Full-bleed crop bila target berada dalam area portrait yang aman.
- Gameplay full-frame dengan avatar inset bila keduanya penting.
- Blur-fit bila keseluruhan layar harus dipertahankan.
- Stacked/side-by-side hanya bila kedua area memang sama-sama penting dan layout tidak merusak konteks.
- Keyframed crop bila target bergerak; gunakan gerakan kamera halus, bukan pan yang jitter.

Angka awal untuk eksperimen: avatar inset sekitar 18–30% lebar canvas; avatar reaction close-up dapat diperbesar sementara sekitar 35–60% tinggi canvas. Ini bukan standar wajib. Ukur pada footage nyata.

### 3. Bentuk struktur beat
1. Hook: aksi/reaksi yang menarik tanpa membocorkan hasil.
2. Setup: informasi minimum tentang situasi game.
3. Build-up: keputusan, gerakan, ancaman, atau ekspektasi.
4. Payoff: hasil yang benar-benar terlihat/terdengar.
5. Reaction: beri ruang pada reaksi bila menambah makna.
6. Exit: potong setelah beat selesai.

### 4. Atur pacing
- Direct cut adalah default.
- Zoom hanya saat fokus berubah atau reaksi menjadi payoff.
- Jangan memotong loading, aiming, atau silence jika bagian tersebut membangun ketegangan.
- Jangan mempercepat semua shot dengan durasi yang sama.
- Gunakan slow motion hanya bila gerakan sumber cukup jelas dan tujuannya dapat dijelaskan.

### 5. Caption
Caption membantu reaksi atau informasi penting, bukan menyalin seluruh percakapan tanpa seleksi. Ikuti transcript verification dan caption design skill.

## Potongan FFmpeg
Contoh crop terarah; koordinat wajib ditentukan dari inspeksi source:

~~~~bash
ffmpeg -i INPUT.mp4 -vf "crop=608:1080:X:0,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -ar 48000 OUTPUT.mp4
~~~~

Perintah ini belum diuji pada footage pengguna. Ganti X dan ukuran crop berdasarkan source; jangan gunakan bila crop membuang HUD atau avatar penting.

## Checklist QA
- [ ] Gameplay event terbaca pada layar ponsel.
- [ ] Avatar cukup besar untuk mengenali ekspresi.
- [ ] HUD/score/target yang relevan tidak terpotong.
- [ ] Hook tidak membocorkan payoff.
- [ ] Build-up dan hasil tersambung secara logis.
- [ ] Tidak ada zoom atau SFX dekoratif tanpa fungsi.
- [ ] Crop diperiksa pada frame bergerak, bukan satu screenshot saja.

## Kesalahan umum
- Memilih center crop tanpa inspeksi.
- Mempertahankan avatar besar sepanjang video meski gameplay menjadi tidak terlihat.
- Menghapus silence horror yang justru membangun scare.
- Memotong aksi sebelum hasil terlihat.
- Menambahkan impact setiap kali cut.

## Batas kemampuan AI
AI dapat menilai layout dari frame dan metadata, tetapi tidak dapat memastikan reaksi terasa lucu atau gameplay mudah dipahami tanpa menonton hasil render secara utuh.
