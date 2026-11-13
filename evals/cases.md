# Evaluation cases

Retain Gates 1–8 as regression gates. E01–E12 expand editorial evaluation.
Use the [anchored rubric](../qa-and-self-review/references/editorial-rubric.md).
These are test specifications, not completed test results. Footage-dependent
evaluation remains NOT_RUN when source/render artifacts are unavailable.

## Gate 1 — Routing
Input scenario: landscape gameplay dengan facecam, HUD, dan reaksi setelah gagal.
PASS: router memilih gameplay-facecam, mempertahankan game/HUD/avatar, dan memberi alasan layout.
FAIL: crop menghilangkan salah satu bukti penting tanpa alasan.

Expected editorial behavior: Identify the event cause/result before layout selection.
Common mistakes: Choose a center crop from a single frame.
Evidence required: Route rationale, source/HUD frames and output preview.
Execution status: NOT_RUN without the specified source/artifacts.


## Gate 2 — Conversation camera
Input scenario: dua VTuber bergantian bicara dan sesekali overlap.
PASS: solo crop mengikuti speaker; shared two-shot hanya saat overlap/reaksi bersama.
FAIL: split-screen permanen atau stacked panel dipakai sepanjang klip.

Expected editorial behavior: Follow each active speaker and use one continuous shared shot only for meaningful overlap.
Common mistakes: Treat a two-shot as two separately stacked panels.
Evidence required: Speaker ledger, timecoded shot list and output at every turn.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 3 — Transcript integrity
Input scenario: bahasa Indonesia bercampur Jepang, slang, dan satu bagian overlap; hanya ASR tersedia.
PASS: kata tetap ASR_RAW dan tidak dipakai sebagai subtitle final sebelum diverifikasi.
FAIL: AI mengklaim ASR sebagai transcript verified.

Expected editorial behavior: Preserve raw uncertainty until the verification protocol is actually completed.
Common mistakes: Treat confidence or alignment as listening.
Evidence required: Original ASR, word ledger and actual verification receipts if any.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 4 — Speaker attribution
Input scenario: dua avatar, diarization S1/S2, dan salah satu avatar idle.
PASS: speaker mapping tetap provisional sampai ada bukti visual/audio yang cukup.
FAIL: S1 otomatis dipetakan ke avatar berdasarkan posisi atau warna.

Expected editorial behavior: Keep diarization and avatar identity separate.
Common mistakes: Use hair color or a single lip flap as proof.
Evidence required: Multiple turn observations or explicit user confirmation.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 5 — Caption safety
Input scenario: ASS 1080×1920 dengan dua speaker dan satu baris panjang.
PASS: maksimal dua baris, speaker color konsisten, posisi aman, tidak menutup wajah/HUD.
FAIL: caption menghalangi ekspresi atau mengandung kata yang belum diverifikasi.

Expected editorial behavior: Use readable phrases and source-linked emphasis.
Common mistakes: Shrink text until all overlapping speech fits.
Evidence required: Transcript links and phone/full-frame caption previews.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 6 — Audio
Input scenario: voice, game audio, dan BGM.
PASS: voice jelas, game cue penting tetap terdengar, loudness terukur, dan manusia mendengar preview.
FAIL: angka loudness dipakai sebagai pengganti review audio.

Expected editorial behavior: Measure signals and separately review voice/game/music comfort.
Common mistakes: Report loudness PASS as overall audio PASS.
Evidence required: Measurement log, rendered audio and human listening report.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 7 — Retention
Input scenario: horror scare dengan quiet build-up, scare, dan reaksi avatar.
PASS: build-up yang menyiapkan scare dipertahankan, hook tidak membocorkan payoff.
FAIL: silence dihapus otomatis atau scare/reaction terpotong.

Expected editorial behavior: Preserve suspense and the cause of the reaction.
Common mistakes: Cut every quiet interval automatically.
Evidence required: Source/output timing comparison and full-beat playback.
Execution status: NOT_RUN without the specified source/artifacts.

## Gate 8 — Delivery
Input scenario: source bernama "my stream 01.mp4", pengguna minta paket PC dan Colab.
PASS: source tidak masuk ZIP, path berspasi di-quote, FFmpeg menjadi dependensi render dasar.
FAIL: source dibundel atau script memakai path hard-coded.

Expected editorial behavior: Keep original source external and test actual package commands.
Common mistakes: Rename source media to disguise it in the archive.
Evidence required: Archive inventory, path-with-spaces execution log and output probe.
Execution status: NOT_RUN without the specified source/artifacts.

## E01 Natural comedy
Input scenario: a calm claim, meaningful pause, ordinary mistake and delayed laugh; no large volume peak.
Expected editorial behavior: explain the contrast, preserve pause and reaction onset; choose selective emphasis only if it helps.
PASS criteria: viewer can identify the joke's cause; direct-cut version remains coherent; each addition has evidence.
FAIL criteria: selection depends only on loudness, pause disappears, or a laugh is moved to a new cause.
Common mistakes: decorating the pause, revealing the punchline in the opening caption.
Evidence required: source interval, beat map, plain/treated previews and timecoded comparison.
Execution status: NOT_RUN until source and previews are reviewed.

## E02 Overediting versus restraint
Input scenario: the same exchange edited with periodic zoom/SFX and with beat-based cuts.
Expected editorial behavior: compare both at native speed and identify which treatments improve comprehension.
PASS criteria: remove distractions with a specific reason; retain an expressive effect if comparison supports it.
FAIL criteria: prefer the busier version by effect count or ban all creativity without examining the moment.
Common mistakes: arbitrary effects-per-minute quotas, treating restraint as no editing.
Evidence required: two previews, per-effect decisions, rejected alternatives and rubric observations.
Execution status: NOT_RUN until both previews exist.

## E03 Punchline timing
Input scenario: one word reverses the meaning after a short hesitation.
Expected editorial behavior: retain hesitation and negation; reveal caption emphasis at the verified word onset.
PASS criteria: punchline is audible before/with its emphasis; reaction is not clipped; nearby cut alternatives are compared.
FAIL criteria: caption spoils the word or a trim removes its initial consonant or the reaction.
Common mistakes: timing to waveform peak, imposing fixed 300 ms holds.
Evidence required: word receipts, source/output time mapping and replay around the reveal.
Execution status: NOT_RUN without verified audio and output playback.

## E04 Emotional storytelling
Input scenario: a sincere thank-you followed by a breath and quiet recovery.
Expected editorial behavior: preserve emotional context without imposing comedy structure or sentimental music.
PASS criteria: optional music is compared with silence; pauses and expression remain understandable.
FAIL criteria: invented emotion, comic impact or speed-up changes the speaker's meaning.
Common mistakes: assuming quiet speech means sadness, forcing hook/build-up/punchline into every clip.
Evidence required: source context, alternatives, audio review and timecoded emotion assessment with uncertainty.
Execution status: NOT_RUN without audiovisual source/review.

## E05 Context preservation
Input scenario: a funny answer refers to a rule explained several seconds earlier.
Expected editorial behavior: include the prerequisite or a clearly labeled, evidenced information caption.
PASS criteria: a first-time reviewer explains the cause and answer without extra lore; no misleading reorder.
FAIL criteria: removed negation/rule changes meaning or an editorial note appears as a spoken quote.
Common mistakes: trimming for target duration before identifying context debt.
Evidence required: source setup, selected EDL, context dependency explanation and reviewer account.
Execution status: NOT_RUN until source and first-view review are available.

## E06 Dynamic subtitle emphasis
Input scenario: Indonesian dialogue with a Japanese term, one key negation and a speaker overlap.
Expected editorial behavior: retain verified wording, distinguish reading from translation, animate only useful emphasis.
PASS criteria: words and speaker IDs trace to transcript; glyphs/phrases remain readable and emphasis follows mapped onset.
FAIL criteria: rewritten wording, missing negation, constant bounce, three illegibly stacked language layers.
Common mistakes: believing word alignment verifies text or a guessed font covers all glyphs.
Evidence required: word ledger, language review, caption records and moving phone preview.
Execution status: NOT_RUN for perceptual assessment; synthetic linkage checks do not establish readability.

## E07 Appropriate sound effects
Input scenario: gameplay fail with an already audible game cue and a strong avatar reaction.
Expected editorial behavior: consider no added sound; use an accent only if it supports the actual event without masking voice.
PASS criteria: source event, purpose, timing, level and asset rights documented; listen comparison supports choice.
FAIL criteria: fake victory/kill cue, laughter added as if real, SFX on every cut, or voice masked.
Common mistakes: matching SFX by genre alone, assuming a license from a filename.
Evidence required: source/output audio, effect decision, asset provenance and human listening notes.
Execution status: NOT_RUN until audio/assets are reviewed.

## E08 Camera movement and reframing
Input scenario: moving gameplay target, essential edge HUD and a later avatar reaction.
Expected editorial behavior: prioritize target/HUD, keyframe deliberate pan, then reframe reaction when it becomes the payoff.
PASS criteria: crop bounds and intermediate frames preserve evidence; motion has beat-specific intent and fallback.
FAIL criteria: periodic zoom hides result, jittery tracking, unimplemented easing passed as a filter option.
Common mistakes: checking only endpoint stills; claiming an AI tracker exists without a tool.
Evidence required: source landmarks, keyframes/time map, executed command and moving preview.
Execution status: NOT_RUN for real footage; synthetic crop tests cover only tested technical behavior.

## E09 Multi-speaker reaction timing
Input scenario: S1 triggers S2's response while S3 interrupts and the group laughs.
Expected editorial behavior: preserve actual onset/overlap and reaction chain; select relevant shared composition.
PASS criteria: attribution supported, captions readable, cuts follow the active exchange and return from cutaways.
FAIL criteria: reordered reactions, fabricated speaker mapping, persistent avatar grid or all voices reduced to tiny text.
Common mistakes: separating simultaneous speech into a new sequential exchange.
Evidence required: multi-speaker ledger, overlap intervals, camera/caption EDL and source/output playback.
Execution status: NOT_RUN without source and verified attribution.

## E10 Visual consistency
Input scenario: multiple shots alternate between bright gameplay and dark avatar close-ups.
Expected editorial behavior: keep speaker identity and typography stable while adapting safe placement/contrast.
PASS criteria: stable visual vocabulary, readable important content and motivated exceptions.
FAIL criteria: speaker colors swap, caption hierarchy changes arbitrarily or a consistent template hides HUD.
Common mistakes: equating consistency with one global caption coordinate.
Evidence required: style application, frame sequence, phone preview and exception rationale.
Execution status: NOT_RUN without rendered sequence inspection.

## E11 Reference-style adaptation
Input scenario: user supplies a fast comedic reference but current source is a quiet conversation; reference contains proprietary stickers.
Expected editorial behavior: separate observed traits, user preferences and project constraints; adapt compatible traits only.
PASS criteria: reference timestamps/method/confidence recorded; emotion/timing preserved; assets original or licensed.
FAIL criteria: exact assets copied, inferred font asserted as fact, sample cadence made universal or absent audio marked verified.
Common mistakes: applying reference gag timestamps to new footage.
Evidence required: reference access record, style-profile JSON, project decisions and asset provenance.
Execution status: NOT_RUN until reference and current footage are supplied and reviewed.

## E12 End-to-end editorial decisions
Input scenario: a mixed gameplay/conversation source, ASR draft, style reference and request for a source-free PC/Colab render package.
Expected editorial behavior: route per beat; inspect context; verify words; implement one EDL; render, review, revise and package.
PASS criteria: linked evidence/words/decisions validate, executed render matches timing, eight original gates pass where applicable, rubric issues resolved and human review recorded.
FAIL criteria: valid JSON treated as finished editing, untested scripts called tested, source included in ZIP, unknowns silently removed.
Common mistakes: running every skill, disconnected plans, scoring unobserved footage, claiming cross-platform tests from Linux only.
Evidence required: brief, source hash, route, evidence ledger, transcript, EDL, commands/tool versions, render, technical/editorial/human QA and package inventory.
Execution status: NOT_RUN without a complete source-to-delivery run on real footage.


## Gate 9 — Expressive sound design
Input scenario: dialogue-led VTuber clip with one key phrase, a visible camera move and a playful reaction.
PASS: each SFX is linked to verified evidence; word accents map to verified word IDs; motion/transition cues align to visible events; voice remains clear; asset hashes/licenses are recorded.
FAIL: effects are placed on every word/cut, a guessed emotion is sonified, or SFX masks dialogue.
Evidence required: edit plan, verified transcript, audio-design.json, asset manifest, base preview, SFX preview, audio-mix receipt and human listening report.
Execution status: NOT_RUN until real footage and listening review are completed.

## E13 Word-accent timing
Input scenario: a verified punchline word follows a hesitation and changes the sentence meaning.
Expected editorial behavior: use at most one quiet pop/tick on the key word, preserve the hesitation, and keep the word intelligible.
PASS criteria: event links to verified word IDs and lands within the mapped output onset window; no SFX is required if the word is already clear.
FAIL criteria: accent is based only on subtitle color, ASR_RAW text, or a guessed word.
Common mistakes: placing the pop before the word, covering a plosive, or accenting every caption token.
Evidence required: transcript receipt, source/output mapping, audio-design plan and listened preview.
Execution status: NOT_RUN without verified source audio and final listening.

## E14 Motion and reaction sync
Input scenario: a VTuber makes a visible movement followed by a clearly observed reaction.
Expected editorial behavior: use one whoosh at the motion onset or one light reaction accent after the reaction begins, not both by default.
PASS criteria: event is source-linked, restrained and synchronized; the simpler no-SFX alternative is compared.
FAIL criteria: whoosh on idle movement, boing on ambiguous expression, or an impact implying an action that did not occur.
Common mistakes: treating every camera keyframe as a reason for sound.
Evidence required: inspected frames, shot camera decision, evidence IDs and SFX preview.
Execution status: NOT_RUN until audiovisual review.

## E15 Voice-priority mix
Input scenario: source has one mixed stereo voice/game track and two short SFX accents.
Expected editorial behavior: use conservative SFX gain, source-mix sidechain ducking and peak limiting; do not claim isolated voice processing.
PASS criteria: dialogue remains intelligible on earphones and phone speaker; receipt describes the mixed-source limitation.
FAIL criteria: loudness meter alone certifies comfort or the SFX overwhelms speech.
Common mistakes: excessive bass, aggressive limiter, continuous pumping.
Evidence required: input/output probe, mix receipt, loudness analysis and human listening report.
Execution status: NOT_RUN until human listening.

## E16 Asset integrity and event bounds
Input scenario: audio plan references a generated or licensed WAV asset with a declared hash.
Expected editorial behavior: resolve relative paths, verify hashes, output-clock duration, evidence links and event overlap limits.
PASS criteria: path traversal, mismatched hash, out-of-range event, unverified word and excessive overlap are rejected.
FAIL criteria: renderer silently ignores a missing/unsupported asset or continues after a validation error.
Common mistakes: absolute machine-specific paths and untracked third-party sounds.
Evidence required: schema validation, unit tests, FFmpeg integration test and receipt.
Execution status: automated synthetic tests only until CI executes the new branch.
