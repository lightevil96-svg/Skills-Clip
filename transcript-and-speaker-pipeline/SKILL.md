---
name: transcript-and-speaker-pipeline
description: Produces word-level transcripts, timestamps, speaker diarization, and a verification ledger for VTuber clips in Indonesian, Japanese, English, or mixed-language speech. Use before creating dialogue captions or speaker-colored subtitles.
---

# Transcript & Speaker Pipeline

## Tujuan
Menghasilkan transcript yang dapat ditelusuri ke audio asli. Transcript mesin adalah draft, bukan fakta final. Caption tidak boleh dibuat dari kata yang belum diverifikasi.

## Aturan wajib
1. ASR_RAW tidak boleh dianggap VERIFIED.
2. Jangan memperbaiki slang, nama talent, game terms, atau Japanese phrase dengan tebakan.
3. Pertahankan bahasa asli, code-switching, filler yang bermakna, negasi, dan interjeksi.
4. Speaker diarization tidak sama dengan identifikasi orang/avatar.
5. Overlap, laughter, whisper, scream, dan speech yang tertutup musik harus diberi status uncertainty.
6. Simpan timestamp kata; jangan hanya menyimpan satu timestamp per paragraf.
7. Jika audio tidak tersedia atau tidak dapat didengar, jangan mengklaim transcript akurat.

## Langkah kerja

### 1. Siapkan audio
- Probe sample rate, channels, duration, start time.
- Jika perlu, konversi ke WAV mono 16 kHz untuk ASR.
- Jangan mengganti source asli; simpan hasil ekstraksi sebagai file kerja.
- Pisahkan audio hanya bila source separation tersedia dan hasilnya diperiksa.

### 2. Jalankan ASR
Whisper/faster-whisper/WhisperX dapat digunakan sebagai kandidat pipeline. Pilih bahasa sesuai source; deteksi otomatis dapat gagal pada code-switching. Simpan model, versi, language, compute type, dan konfigurasi.

### 3. Word alignment dan diarization
- Alignment memberi timestamp kata, bukan jaminan kata benar.
- Diarization memberi label speaker sementara seperti S1/S2.
- Periksa speaker change dengan mendengarkan audio dan melihat giliran bicara.
- Jangan mapping S1 ke avatar tanpa bukti tambahan.

### 4. Buat verification ledger
Setiap kata memiliki:
- start dan end;
- teks ASR;
- speaker_id;
- confidence bila tersedia;
- status ASR_RAW / VERIFIED / USER_CONFIRMED / UNKNOWN;
- siapa yang memverifikasi;
- catatan jika ada ambiguity.

Dengarkan minimal konteks sebelum dan sesudah kata yang tidak jelas. Jangan memotong konsonan awal/akhir saat membuat caption.

### 5. Buat transcript final
Hanya kata VERIFIED atau USER_CONFIRMED boleh masuk subtitle final. Untuk bagian UNKNOWN, pilih: minta klarifikasi, hilangkan caption, atau gunakan [unclear] bila pengguna meminta transcript verbatim.

## Potongan FFmpeg
Ekstrak audio untuk transkripsi:

~~~~bash
ffmpeg -i INPUT.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le transcript_audio.wav
~~~~

## Checklist QA
- [ ] Bahasa dan code-switching diperiksa.
- [ ] Nama, slang, dan istilah game diverifikasi.
- [ ] Timestamp kata diperiksa di bagian penting.
- [ ] Speaker diarization tidak dianggap identitas avatar.
- [ ] Semua caption final berstatus VERIFIED/USER_CONFIRMED.
- [ ] Bagian overlap/unclear ditandai.
- [ ] Source audio asli tetap tersimpan.

## Kesalahan umum
- Menyalin output ASR langsung menjadi caption.
- Mengubah kalimat karena tata bahasa dianggap salah.
- Menebak nama talent dari suara.
- Menggunakan confidence ASR sebagai bukti kebenaran.
- Mengabaikan negasi atau kata pendek yang mengubah makna.

## Batas kemampuan AI
ASR sering salah pada bahasa campuran, nama proper, slang, tawa, dan mic buruk. Validasi akhir memerlukan pendengaran manusia yang memahami bahasa/konteks.
