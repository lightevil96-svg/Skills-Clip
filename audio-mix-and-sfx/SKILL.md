---
name: audio-mix-and-sfx
description: Designs expressive, evidence-linked sound effects and protects VTuber dialogue during short-form editing. Use for word accents, visible motion, reactions, transitions, source-audio balance, ducking and loudness QA.
---

# Audio Mix & Expressive Sound Design

## Tujuan
Membuat audio terasa hidup dan sinkron dengan cerita tanpa mengalahkan voice VTuber. Sound effect adalah aksen editorial yang mengikuti kejadian, bukan dekorasi yang ditempel pada setiap cut atau kata.

Baca [Agent Operating Contract](../AGENT_OPERATING_CONTRACT.md), [Editorial Intelligence](../editorial-intelligence/SKILL.md), dan [Expressive Sound Design Protocol](references/expressive-sound-design.md) sebelum menyusun event.

## Aturan wajib
1. Voice/dialogue adalah prioritas tertinggi. SFX harus mendukung, bukan bersaing dengan kata yang sedang diucapkan.
2. Setiap SFX wajib memiliki alasan editorial, event pemicu, timestamp output, bukti sumber, asset ID, gain, dan alternatif tanpa SFX.
3. Jangan menambah bunyi yang menyiratkan kejadian palsu, seperti hit, kill, alarm, kemenangan, jatuh, tawa penonton, atau benda pecah yang tidak terjadi.
4. Jangan menebak emosi dari satu ekspresi avatar. Gunakan reaksi hanya bila konteks visual/audio mendukung; selain itu tandai CANDIDATE atau hilangkan efek.
5. Jangan menambahkan SFX pada setiap kata, gerakan kecil, atau pergantian shot. Silence dan source audio tetap pilihan utama.
6. Word-emphasis wajib memakai word ID yang sudah VERIFIED/USER_CONFIRMED dan timestamp dari transcript yang cocok dengan source SHA.
7. Motion SFX wajib terhubung ke visual evidence dan keputusan kamera/gerak yang benar-benar diperiksa.
8. Asset eksternal wajib memiliki source, license, dan SHA-256. Jangan menganggap aset yang ditemukan di internet otomatis bebas digunakan.
9. Jika source hanya satu mixed stereo track, sidechain hanya dapat bereaksi terhadap keseluruhan mix. Jangan mengklaim voice stem terpisah.
10. Angka loudness/limiter tidak menggantikan human listening. Delivery tetap REVIEW sampai audio didengar.

## Langkah kerja

### 1. Peta sumber audio
Identifikasi apakah source memiliki stem terpisah atau satu mix. Catat voice, game, BGM, SFX, ambience, clipping, noise, dan jeda yang punya fungsi. Dengarkan kandidat pada kecepatan normal. ASR, waveform, dan VAD tidak memverifikasi dialog.

### 2. Ambil intent dari beat
Dari editorial-intelligence, identifikasi kata kunci, gerak kamera, reaksi, payoff, perubahan adegan, dan momen yang lebih kuat tanpa efek. Jangan menciptakan event hanya untuk memenuhi kuota SFX.

### 3. Pilih keluarga efek

| Trigger | Pilihan awal | Penggunaan |
|---|---|---|
| `word-emphasis` | soft-pop / word-tick | Satu kata penting yang benar-benar mengubah punchline atau pemahaman |
| `motion` | whoosh-short | Gerak kamera/objek yang jelas dan relevan |
| `reaction` | boing-soft / sparkle | Reaksi komedi atau menggemaskan yang teramati, bukan emosi tebakan |
| `transition` | whoosh-short | Perubahan adegan/ide yang bermakna, bukan setiap cut |
| `impact` | soft-impact | Reveal, hasil, atau payoff yang memiliki onset nyata |
| `other` | pilih aset yang relevan | Harus dijelaskan; bila tidak jelas, jangan gunakan |

Efek adalah pilihan, bukan pemetaan otomatis. Bandingkan preview dengan versi tanpa SFX.

### 4. Timing dan kepadatan
- `at_s` selalu menggunakan output timeline, bukan source timeline.
- Word-emphasis harus mengikuti kata yang sudah diverifikasi. Tempatkan aksen dekat onset kata, tetapi hindari menutupi konsonan/plosive; geser sedikit ke setelah onset jika diperlukan.
- Whoosh dimulai pada atau sedikit sebelum gerakan yang terlihat, lalu selesai bersama gerak. Impact ditempatkan pada hasil/landing, bukan pada gerakan yang belum selesai.
- Reaksi komedi diberi ruang: jangan menutupi jeda sebelum punchline atau tawa/recovery setelahnya.
- Awali dengan sekitar 1–3 aksen per 10 detik untuk percakapan; ini batas eksperimen, bukan target. Satu aksen per frasa biasanya cukup.
- Maksimal dua SFX simultan. Hindari layer beruntun yang membuat video terdengar seperti game arcade.
- Event pendek lebih aman: pop/tick sekitar 0.07–0.18 s, impact sekitar 0.12–0.30 s, whoosh sekitar 0.25–0.60 s, sparkle sekitar 0.25–0.70 s. Sesuaikan berdasarkan aset dan preview.

### 5. Susun Audio Design Plan terpisah
Jangan memasukkan SFX ke `shots[].editorial.effect_decision` untuk renderer bounded yang belum mengeksekusinya. Buat `audio-design.json` menggunakan [audio-design schema](../schemas/audio-design.schema.json). Referensikan bukti dari edit plan dan word ID dari transcript. Simpan asset path relatif terhadap folder audio-design, hash, source, dan license.

### 6. Generate atau siapkan aset
Starter pack original dapat dibuat tanpa unduhan:

```bash
python scripts/generate_sfx_pack.py --output-dir work/audio-assets
```

Script menghasilkan `soft-pop`, `word-tick`, `whoosh-short`, `soft-impact`, `sparkle`, dan `boing-soft` dalam WAV mono 48 kHz. Aset ini sintetis dan sederhana, bukan Foley realistis. Dengarkan dan pilih hanya yang cocok. Aset eksternal boleh digunakan jika lisensi dan hash dicatat.

### 7. Render SFX pass
Setelah base preview selesai, overlay SFX dengan:

```bash
python scripts/render_audio_events.py \
  --video work/preview/preview.mp4 \
  --audio-plan work/audio-design.json \
  --edit-plan work/edit-plan.json \
  --transcript work/transcript.json \
  --output-dir work/audio-preview
```

`--transcript` wajib jika ada event `word-emphasis`. Renderer memvalidasi source hash, output duration, bukti, word mapping, path aset, SHA-256, event overlap, lalu membuat `preview-with-sfx.mp4` dan `audio-mix-receipt.json`. Jangan bypass error dengan menghapus evidence atau mengubah hash.

### 8. Mix dan QA
- SFX gain awal umumnya -24 sampai -16 dB, disesuaikan dengan aset dan source mix; jangan mengejar angka tanpa mendengar.
- Sidechain ducking memakai source mix sebagai key, bukan isolated voice stem. Default awal: threshold -30 dB, ratio 2.5:1, attack 10 ms, release 180 ms.
- Limiter ceiling default 0.95 linear. Ini mencegah puncak berlebihan, bukan pengganti loudness mastering.
- Tidak ada loudness normalization otomatis pada SFX pass.
- Dengarkan pada earphone dan speaker HP. Periksa kata penting, plosive, sibilance, tawa, transisi, awal/akhir video, dan perubahan loudness antarbagian.

## Checklist QA
- [ ] Setiap SFX punya alasan dan evidence IDs yang valid.
- [ ] Word-emphasis cocok dengan word ID terverifikasi dan output timing.
- [ ] Motion/transition cue cocok dengan gerakan atau batas shot yang terlihat.
- [ ] Tidak ada efek yang mengubah makna kejadian.
- [ ] Voice tetap jelas; SFX tidak menutupi kata, tawa, atau game cue penting.
- [ ] Kepadatan efek tidak melelahkan.
- [ ] Asset source, license, dan SHA-256 tercatat.
- [ ] Audio preview didengar manusia di earphone dan speaker HP.
- [ ] Receipt memisahkan technical PASS dari human listening NOT_RUN.

## Kesalahan umum
- Pop pada setiap kata berwarna.
- Whoosh pada setiap zoom kecil atau cut.
- Boing untuk ekspresi yang belum tentu lucu.
- Impact keras yang menutupi punchline.
- SFX terlalu stereo/lebar atau terlalu bass-heavy untuk speaker HP.
- Mengira sidechain pada mixed source sama dengan voice isolation.
- Menganggap limiter atau LUFS otomatis membuat mix nyaman.

## Batas kemampuan AI
AI dapat memilih event berdasarkan evidence, menyiapkan timeline, memeriksa file/hash, dan menjalankan SFX pass. AI tidak dapat mengesahkan kenyamanan tonal, kecocokan budaya humor, atau kualitas emosional hanya dari meter. Human listening tetap wajib untuk final delivery.

