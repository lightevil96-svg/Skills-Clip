# Skills-Clip evaluation suite

Evals menguji apakah AI mengikuti workflow pada klip baru, bukan sekadar menghasilkan video yang tampak ramai.

## Cara menjalankan
1. Pilih fixture pada cases.md.
2. Berikan source video atau frame/transcript sesuai fixture.
3. Minta AI mengikuti README dan skill yang relevan.
4. Simpan edit plan, transcript ledger, render command, dan QA report.
5. Nilai setiap gate PASS/FAIL/REVIEW/SKIP/NOT_RUN berdasarkan bukti.
6. Gunakan [rubric editorial](../qa-and-self-review/references/editorial-rubric.md)
   dan [schema review](../schemas/editorial-review.schema.json). Skor 0–4 hanya
   untuk assessment yang benar-benar dilakukan. NOT_RUN/REVIEW/SKIP memakai null.

## Gate kelulusan
- Semua gate wajib PASS untuk delivery final.
- Jika audio belum didengar manusia, status audio adalah REVIEW.
- Jika transcript belum diverifikasi, status caption adalah FAIL untuk subtitle final.
- Minimal 10 klip nyata lintas kategori perlu direview manusia sebelum mengklaim workflow konsisten.
- Tidak ada skor eval yang menjamin viral atau kualitas profesional universal.

## Pengujian yang dapat dijalankan tanpa footage
```bash
python scripts/validate_skill_repo.py
python -m unittest discover -s tests -v
python scripts/smoke_ffmpeg.py --output-dir test-results/smoke
```

Tests memakai data sintetik untuk menguji schema, kompatibilitas legacy, timeline,
caption linkage, receipt policy dan batas klaim QA. Receipt di unit test adalah
test double, bukan hasil pendengaran. Smoke test menjalankan FFmpeg pada pola
gambar dan tone buatan; tidak menilai humor, ekspresi atau kenyamanan manusia.

Production tests juga menjalankan importer dan renderer EDL terbatas. Tes
membandingkan piksel crop, posisi audio dua nada, pan/easing, caption, sumber
tanpa audio, native fractional FPS, penolakan VFR dan perubahan hash bukti.
Windows dan Ubuntu memakai jalur Python yang sama. Smoke ZIP/Bash tetap diuji
khusus Linux; Windows batch dan Colab tidak otomatis teruji oleh job Windows.
Audio-event unit/integration tests memakai aset dan video sintetis; human listening
serta kecocokan SFX pada footage VTuber nyata tetap NOT_RUN sampai direview.
Lihat [hasil production](production-results.json), [panduan](../docs/production-tools.md)
dan [riset GitHub](../docs/github-integration-research.md). Hasil awal tetap
tersimpan dalam [snapshot audit pertama](implementation-results.json).

## Protokol regression
Tetap jalankan Gate 1–9 pada footage yang sesuai. Tambahkan E01–E16 untuk
kemampuan editorial, termasuk word-accent timing, motion/reaction sync, voice-priority mix dan asset integrity. Untuk setiap run simpan case ID, source hash, route, plan,
transcript, render/tool version, reviewer/mode, status, evidence dan revisi.
Jangan ubah ketidaktersediaan footage menjadi SKIP; gunakan NOT_RUN.

Reviewer menilai berdasarkan anchor yang sama. Selisih dua poin atau lebih
memerlukan pemeriksaan bersama pada timestamp yang dirujuk. Nilai tidak boleh
menutupi FAIL akurasi, atribusi atau source exclusion. Jalankan kembali bagian
yang terdampak setelah revisi dan simpan bukti perbandingan.
