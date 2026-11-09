# Evaluation cases

## Gate 1 — Routing
Fixture: landscape gameplay dengan facecam, HUD, dan reaksi setelah gagal.
PASS: router memilih gameplay-facecam, mempertahankan game/HUD/avatar, dan memberi alasan layout.
FAIL: crop menghilangkan salah satu bukti penting tanpa alasan.

## Gate 2 — Conversation camera
Fixture: dua VTuber bergantian bicara dan sesekali overlap.
PASS: solo crop mengikuti speaker; shared two-shot hanya saat overlap/reaksi bersama.
FAIL: split-screen permanen atau stacked panel dipakai sepanjang klip.

## Gate 3 — Transcript integrity
Fixture: bahasa Indonesia bercampur Jepang, slang, dan satu bagian overlap; hanya ASR tersedia.
PASS: kata tetap ASR_RAW dan tidak dipakai sebagai subtitle final sebelum diverifikasi.
FAIL: AI mengklaim ASR sebagai transcript verified.

## Gate 4 — Speaker attribution
Fixture: dua avatar, diarization S1/S2, dan salah satu avatar idle.
PASS: speaker mapping tetap provisional sampai ada bukti visual/audio yang cukup.
FAIL: S1 otomatis dipetakan ke avatar berdasarkan posisi atau warna.

## Gate 5 — Caption safety
Fixture: ASS 1080×1920 dengan dua speaker dan satu baris panjang.
PASS: maksimal dua baris, speaker color konsisten, posisi aman, tidak menutup wajah/HUD.
FAIL: caption menghalangi ekspresi atau mengandung kata yang belum diverifikasi.

## Gate 6 — Audio
Fixture: voice, game audio, dan BGM.
PASS: voice jelas, game cue penting tetap terdengar, loudness terukur, dan manusia mendengar preview.
FAIL: angka loudness dipakai sebagai pengganti review audio.

## Gate 7 — Retention
Fixture: horror scare dengan quiet build-up, scare, dan reaksi avatar.
PASS: build-up yang menyiapkan scare dipertahankan, hook tidak membocorkan payoff.
FAIL: silence dihapus otomatis atau scare/reaction terpotong.

## Gate 8 — Delivery
Fixture: source bernama "my stream 01.mp4", pengguna minta paket PC dan Colab.
PASS: source tidak masuk ZIP, path berspasi di-quote, FFmpeg menjadi dependensi render dasar.
FAIL: source dibundel atau script memakai path hard-coded.
