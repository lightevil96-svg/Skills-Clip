---
name: hook-pacing-retention
description: Selects strong VTuber moments and structures hook, context, escalation, payoff, reaction, and ending for Shorts, TikTok, and Reels. Use for clip discovery, pacing decisions, context trimming, and loop endings.
---

# Hook, Pacing & Retention

## Tujuan
Membuat penonton memahami alasan menonton sejak awal dan tetap mengikuti alur sampai payoff. Retensi dibangun lewat kejelasan, bukan efek berlebihan.

## Aturan wajib
1. Jangan menyebut momen lucu hanya karena volume, gerakan, atau ekspresi besar.
2. Jangan mengarang dialog, konteks, atau hasil gameplay.
3. Hook tidak boleh membocorkan payoff.
4. Jangan memotong setup yang diperlukan untuk memahami punchline.
5. Silence dapat membangun humor, horror, atau ketegangan; jangan hapus otomatis.
6. Intro, title card, CTA, progress bar, dan loop bukan elemen wajib.
7. Skor kandidat adalah alat bantu, bukan jaminan viral.

## Langkah kerja

### 1. Cari kandidat
Gunakan perubahan state game, reaksi avatar, pergantian speaker, overlap, jeda, chat, atau hasil tak terduga. Waveform dapat membantu menemukan aktivitas, tetapi tidak menjelaskan makna dialog.

### 2. Skor 0–12
Beri 0–2 poin per dimensi:
- Clarity: momen dapat dipahami?
- Surprise/contrast: ekspektasi berubah?
- Reaction: respons terlihat/terdengar?
- Visual evidence: aksi/ekspresi ada dalam frame?
- Standalone context: konteks cukup?
- Payoff: ada hasil atau penutup?

9–12 kandidat utama; 6–8 perlu review konteks; 0–5 jangan dipilih kecuali pengguna meminta momen itu. Gunakan UNKNOWN bila bukti tidak cukup.

### 3. Susun beat
- Hook: aksi/pertanyaan/reaksi yang memancing rasa ingin tahu.
- Setup: konteks minimum.
- Build-up: ekspektasi meningkat.
- Payoff: punchline, scare, clutch, jawaban, atau hasil.
- Reaction: ruang untuk tawa/emosi.
- Exit: akhiri setelah beat selesai.

Hook 0–1,5 detik dan reaction hold 0,3–1,2 detik adalah starting point eksperimen, bukan hukum universal.

### 4. Potong dengan alasan
- Conversation: pertahankan negasi, respons, dan setup joke.
- Horror: pertahankan ambience yang menyiapkan scare.
- Competitive: pertahankan keputusan, aksi, score/result.
- Collab: pertahankan timing overlap dan reaction chain.
- Fail/win: pertahankan aksi penyebab, hasil, dan reaksi.

### 5. Ending
Akhiri setelah payoff/reaction terasa selesai. Loop hanya jika sambungan alami. Jangan mengulang kata atau membuang konteks demi loop palsu.

## Potongan FFmpeg
Trim dengan re-encode untuk akurasi frame:

~~~~bash
ffmpeg -ss 12.5 -i INPUT.mp4 -t 18 -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k OUTPUT.mp4
~~~~

Contoh belum diuji; sesuaikan in/out dari EDL dan periksa sync.

## Checklist QA
- [ ] Hook menarik tanpa spoiler.
- [ ] Setup cukup.
- [ ] Build-up penting tidak hilang.
- [ ] Payoff jelas.
- [ ] Reaction tidak terpotong.
- [ ] Silence dipertahankan bila punya fungsi.
- [ ] Ending menutup beat atau loop alami.
- [ ] Skor kandidat disertai alasan dan unknowns.

## Kesalahan umum
- Memulai dengan judul generik.
- Memotong tepat sebelum reaksi.
- Memilih momen berdasarkan volume saja.
- Memasang zoom/SFX setiap beberapa detik.
- Membuat CTA setelah punchline selesai.

## Batas kemampuan AI
AI dapat menyusun bukti dan membandingkan kandidat, tetapi humor dan daya tarik akhir bergantung pada konteks budaya dan respons audiens.
