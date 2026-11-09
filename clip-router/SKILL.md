---
name: clip-router
description: Master entry point for analyzing VTuber VODs and routing each clip to the correct gameplay, conversation, collaboration, reaction, transcript, caption, audio, and render workflow. Use first for every new VTuber clipping task.
---

# Clip Router

## Tujuan
Menjadi pintu masuk tunggal bagi AI yang baru membuka repository. Skill ini mengubah permintaan pengguna dan bukti dari source menjadi rute kerja yang tepat. Jangan langsung menerapkan satu template editing ke semua tipe VTuber clip.

## Aturan wajib
1. Source footage adalah ground truth. Jangan mengarang ucapan, aksi, identitas talent, emosi, atau konteks yang tidak terlihat/terdengar.
2. Inspeksi source sebelum memilih crop, subtitle, pacing, atau efek.
3. Pilih satu rute utama dan skill pendukung. Jangan memanggil seluruh skill tanpa alasan.
4. Jika bukti tidak cukup, tandai UNKNOWN dan minta input paling penting; jangan mengisi kekosongan dengan asumsi.
5. Pertahankan maksud percakapan, timing reaksi, game HUD, dan elemen visual yang penting.
6. Skill conversation memiliki aturan kamera khusus: solo crop mengikuti speaker, shared two-shot hanya saat overlap/reaksi bersama. Jangan mengubahnya menjadi split-screen permanen.
7. Output final tidak boleh disebut selesai sebelum render dan QA benar-benar diperiksa.

## Langkah kerja

### 1. Pahami brief
Ambil tujuan platform, bahasa, target durasi, gaya referensi, apakah pengguna meminta hasil MP4 atau paket render, dan batasan aset. Jika pengguna hanya memberikan video tanpa arahan detail, gunakan keputusan konservatif: pertahankan konteks dan hindari dekorasi berlebihan.

### 2. Inspeksi source
- Probe metadata: durasi, resolusi, FPS, codec, audio stream, sample rate, channel layout, stream start time.
- Buat contact sheet untuk keseluruhan video.
- Ambil frame lebih rapat pada perubahan speaker, ekspresi, gameplay event, chat reaction, dan kemungkinan payoff.
- Dengarkan bagian kandidat. ASR hanya alat bantu pencarian, bukan sumber kebenaran.
- Catat posisi avatar, gameplay, HUD, chat, dan safe areas.

### 3. Pilih rute utama

| Bukti dominan | Rute utama | Skill pendukung |
|---|---|---|
| Gameplay/HUD dan satu facecam/avatar | vtuber-gameplay-facecam-clip | hook-pacing-retention, ffmpeg-vertical-quality |
| Percakapan dua orang atau lebih, pergantian speaker | vtuber-conversation-clip | transcript-and-speaker-pipeline, caption-design |
| Collab, reaction chain, group banter, beberapa avatar | vtuber-collab-reaction-clip | transcript-and-speaker-pipeline, caption-design |
| Hanya perlu menemukan momen terbaik | hook-pacing-retention | transcript-and-speaker-pipeline |
| Butuh transkrip/speaker map | transcript-and-speaker-pipeline | caption-design |
| Butuh paket PC/HP/Colab | render-package-for-user | ffmpeg-vertical-quality, qa-and-self-review |

Jika konten campuran, segmentasikan berdasarkan beat dan tentukan rute per segmen.

### 3a. Handoff editorial dan kemampuan
Untuk pemilihan/editing kreatif, baca
[editorial-intelligence](../editorial-intelligence/SKILL.md) setelah inspeksi awal.
Kembalikan context brief, sumber bukti, beat, unknowns dan fokus visual. Kirim
brief tersebut ke hook-pacing-retention untuk discovery, lalu ke specialist
yang dipilih untuk implementasi. Jangan duplikasi pemeringkatan kandidat di
modul editorial. Catat kemampuan mendengar/melihat yang benar-benar tersedia.

Transcript-only cukup memakai pipeline transcript; encode/package-only memakai
plan yang sudah ada dan QA terkait. Jika route campuran, isi `shots[].route`.
Beat percakapan tetap memakai speaker-follow meskipun clip utamanya gameplay.
Aturan layout specialist mengikat skill FFmpeg; kemampuan membuat split-screen
bukan alasan menggunakannya. Shared shot hanya untuk interaksi yang relevan.

### 4. Buat edit decision list
Setiap shot harus memiliki:
- source in/out time;
- tujuan beat;
- subjek utama;
- layout/crop;
- bukti visual;
- caption IDs yang sudah diverifikasi;
- audio/SFX cue;
- alasan pemilihan.

Jangan render sebelum EDL cukup jelas untuk direproduksi.

Gunakan v2 [edit plan](../schemas/edit-plan.schema.json): setiap shot menyimpan
`editorial` dan waktu output. Jalankan validator artifact sebelum render.
Perbaiki error struktural; unknown perseptual tetap REVIEW. Contoh legacy yang
valid tidak otomatis menjadi siap render atau siap delivery.

### 5. Render dan QA
Panggil ffmpeg-vertical-quality, audio-mix-and-sfx, render-package-for-user, dan qa-and-self-review sesuai kebutuhan. Pisahkan hasil otomatis dari penilaian manusia.

## Potongan FFmpeg
Contoh pemeriksaan metadata, bukan perintah render final:

~~~~bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,start_time,duration -of json INPUT.mp4
~~~~

## Checklist QA
- [ ] Rute dipilih berdasarkan bukti, bukan asumsi.
- [ ] Semua kandidat clip memiliki setup dan payoff yang dapat dijelaskan.
- [ ] Crop mempertahankan subjek dan informasi penting.
- [ ] Caption hanya memakai kata VERIFIED atau USER_CONFIRMED.
- [ ] Voice dan game cue penting tidak tertutup musik/SFX.
- [ ] Render diperiksa pada frame awal, tengah, akhir, dan setiap perubahan layout.
- [ ] QA report menyatakan PASS/FAIL/REVIEW secara jujur.

## Kesalahan umum
- Memakai template percakapan untuk gameplay.
- Menganggap semua VTuber harus selalu tampil di layar.
- Menambah title card, CTA, zoom, meme, dan SFX tanpa fungsi.
- Menentukan speaker hanya dari posisi avatar.
- Menyebut ASR sebagai transkrip final.
- Menganggap sukses render sama dengan hasil berkualitas.

## Batas kemampuan AI
AI dapat mengorganisasi bukti, menyusun EDL, dan menjalankan pemeriksaan teknis. Humor, ekspresi, kualitas suara, serta keputusan akhir atas ambiguitas memerlukan review manusia.
