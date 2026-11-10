---
name: audio-mix-and-sfx
description: Balances VTuber voice, game audio, background music, and sound effects for short-form clips. Use for dialogue clarity, music ducking, noise cleanup, loudness checks, and original procedural SFX.
---

# Audio Mix & SFX

## Tujuan
Menjaga voice VTuber tetap jelas, game cue penting tetap terdengar, dan musik/SFX mendukung cerita tanpa mengambil alih.

## Aturan wajib
1. Voice adalah prioritas utama kecuali pengguna meminta desain audio berbeda.
2. BGM tidak wajib. Jangan menambahkan musik hanya untuk mengisi keheningan.
3. Jangan menambah SFX yang mengubah arti aksi atau menyiratkan kejadian yang tidak ada.
4. Jangan memakai aset musik/SFX tanpa izin atau lisensi yang sesuai.
5. Jangan mengklaim audio enak didengar hanya dari angka loudness.
6. Jika audio source sudah satu mix stereo, jangan mengklaim voice/game terpisah sempurna.
7. Target -16 sampai -14 LUFS integrated dan true peak ≤ -1 dBTP adalah titik awal proyek, bukan aturan resmi YouTube/TikTok.

## Langkah kerja

### 1. Petakan track
Identifikasi VOICE, GAME, BGM, SFX, dan AMBIENCE. Tandai apakah source track terpisah atau sudah tercampur.

### 2. Bersihkan voice
- High-pass 70–100 Hz sebagai titik awal untuk mengurangi rumble.
- Kurangi mud sekitar 180–400 Hz hanya jika terdengar keruh.
- Uji presence sekitar 2–5 kHz jika artikulasi tertutup.
- De-esser sekitar 5–8 kHz jika sibilance mengganggu.
- Hindari noise reduction agresif yang membuat suara robotik.
- Jangan boost hingga clipping.

### 3. Atur BGM
Ducking 6–12 dB saat voice aktif dapat menjadi titik awal. Atur attack/release agar tidak pumping. Jangan menurunkan game cue penting seperti alarm, hit, objective, scare, atau kemenangan.

### 4. SFX
Pertimbangkan whoosh untuk gerak yang terlihat, impact untuk payoff atau accent
kecil hanya jika memperjelas beat. Riser memerlukan build-up yang benar-benar
berujung. Efek tersebut pilihan, bukan mapping otomatis. Silence juga pilihan.

Ambil intent dari [editorial-intelligence](../editorial-intelligence/SKILL.md).
Catat source event, waktu output, tujuan, intensitas, aset/lisensi, dan alternatif
tanpa SFX. Jangan menambah hit, kill, tawa penonton, alarm atau suara kemenangan
yang membuat penonton menyimpulkan kejadian palsu. Efek komedi harus terdengar
sebagai treatment editorial, tetap terkait kejadian dan tidak menutupi dialog.

### 4a. Musik, jeda dan transisi audio
Pilih mood/tempo musik dari tujuan adegan dan brief, bukan label genre video
saja. Bandingkan tanpa musik, khususnya cerita emosional atau horror. Pertahankan
napas, ambience dan jeda yang membangun antisipasi; noise floor bukan otomatis
dead air. Hindari musik sentimental yang memaksakan interpretasi sumber ambigu.

Ducking boleh memakai gain envelope atau sidechain yang tersedia. Jika sumber
sudah satu mix, penurunan gain menurunkan seluruh mix; jangan menjanjikan stem
voice terpisah. Periksa attack/release dan volume antarshot dengan mendengar.
Crossfade audio hanya untuk sambungan yang membutuhkannya, tanpa menggeser kata
atau memindahkan reaksi. Uji sync pada onset aksi, dialog dan efek setelah retime.
Jangan mengisi setiap cut dengan sound effect.

### 5. Loudness
Analisis loudness dan true peak. Lakukan normalization sesuai kebutuhan; jangan menormalkan hanya karena angka target tanpa mendengar hasil. EBU R128 -23 LUFS adalah konteks broadcast, bukan target wajib Shorts.

## Potongan FFmpeg
Analisis loudness:

~~~~bash
ffmpeg -i INPUT.mp4 -af loudnorm=I=-15:TP=-1:LRA=11:print_format=json -f null -
~~~~

Command ini untuk analisis; hasil normalization final perlu proses yang sesuai dan review dengar.

## Checklist QA
- [ ] Voice paling jelas.
- [ ] Game cue penting masih terdengar.
- [ ] BGM turun saat dialog.
- [ ] Tidak ada clipping/pumping.
- [ ] Loudness dan true peak terukur.
- [ ] SFX punya fungsi naratif/visual.
- [ ] Lisensi/asal aset tercatat.
- [ ] Preview final didengar manusia melalui earphone dan speaker HP.

## Kesalahan umum
- BGM terlalu keras.
- Impact pada setiap cut.
- Noise reduction berlebihan.
- Memakai -14 LUFS sebagai aturan platform.
- Mengira audio meter menggantikan pendengaran.

## Batas kemampuan AI
AI dapat mengukur sinyal dan menyusun filter, tetapi kualitas tonal, kenyamanan, emosi, dan sibilance harus diperiksa dengan mendengar.
