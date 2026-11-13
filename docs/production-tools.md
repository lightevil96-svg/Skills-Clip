# Production tools: bounded execution, explicit evidence

These tools implement part of the workflow; they do not autonomously discover,
understand and finish a clip. Read the [contract](../AGENT_OPERATING_CONTRACT.md)
and inspect the source before choosing an EDL. The [GitHub research](github-integration-research.md)
separates installed code from optional external components.

## Environment and paths

Install `requirements-dev.txt` in a project environment. FFmpeg and FFprobe must
be on PATH; the preview renderer needs libx264/AAC and libass for caption burn.
Use `ffmpeg -version` and `ffmpeg -h filter=ass` to inspect the actual build.
Commands below run from the repository root and work with quoted paths. Output
directories must not exist; scripts never overwrite sources or prior results.
All subprocesses use argv lists with no shell interpolation.

## Inspect the original source

```bash
python scripts/inspect_source.py "/media/source.mp4" "work/inspection-01" --start 120 --end 150 --frames 7
python scripts/verify_evidence.py "work/inspection-01/manifest.json" --source "/media/source.mp4"
```

The bundle contains the original probe, source SHA-256, sampled PNGs and a PCM
audio excerpt when audio is present. Samples are requested seek positions, not
measured exact frame timestamps. Review status starts at NOT_RUN. Each bundle
is limited to 120 seconds and 12 frames; create additional windows for discovery
or replay the source at native speed. Sampling never substitutes for playing the
selected moment. A separate source-hash check does not authenticate observations.
These source derivatives are private working evidence, excluded from delivery ZIPs.

Copy source metadata/hash from the manifest into the plan. Its absolute source
path may be replaced by a portable logical source reference consistently across
plan, transcript and receipts. The `--source` argument selects the actual local
file and must match its hash/metadata; relocation does not change the bytes.

## Import word-level ASR

```bash
python scripts/asr_bridge.py import "/media/source.mp4" "work/asr-import" --raw "aligned.json" --model "whisperx:model-and-version-used" --language id --offset 120
```

Accepted shape is `segments[].words[]` with `word` (or `text`), `start`, `end`,
optional `speaker`, and optional `score`/`probability`. WhisperX aligned words and
the local runner's faster-whisper JSON use this shape. Other formats need an
explicit adapter. Supply 0 for full-source times, or the exact extraction offset
for excerpt-relative times. Import preserves overlaps, negation and source order.
Language is an explicit label, not a language verification claim; review and
annotate code-switched words individually afterward.

Missing word times go into `unresolved_words`. Segment-only text stays unresolved;
the importer never distributes a sentence evenly into invented word timestamps.
Invalid/out-of-range times fail. Every imported word remains ASR_RAW and every
speaker identity UNKNOWN. `import_provenance` records the raw file hash, offset
and whether inference actually ran; importing someone else's JSON is DECLARED,
not proof of its source association. Preserve the raw JSON beside your work.

## Optional local ASR inference

This entry point is implemented, but no model weights/inference were exercised
in the repository upgrade. Install optional packages only in a separate environment:

```bash
python -m pip install -r requirements-asr.txt
python scripts/asr_bridge.py run-local "/media/source.mp4" "work/asr-run" --model-dir "/models/whisper-ctranslate2" --language id --device cpu --compute-type int8
```

The model directory must already exist and be compatible with faster-whisper.
The runner requests `local_files_only=True`; it does not fetch model aliases or
send audio to an API. It consumes the transcription generator, saves raw words
and runtime provenance, and leaves verification ASR_RAW. VAD is disabled; this
tool never deletes suspense or pauses from the edit. GPU use requires a suitable
installed backend; no GPU availability or speed claim is made. Model revisions,
licenses and the resolved dependency lock remain deployment responsibilities.

## Render an EDL preview

```bash
python scripts/render_edl.py "work/edit-plan.json" --source "/media/source.mp4" --output-dir "work/preview-01" --captions omit
```

This is an explicit captionless review. For verified static dialogue:

```bash
python scripts/render_edl.py "work/edit-plan.json" --source "/media/source.mp4" --output-dir "work/preview-02" --transcript "work/transcript.json" --captions burn --font-file "/fonts/YourLicensedFont.ttf" --font-name "Your Font Family"
```

| Supported | Conditions |
|---|---|
| Native-CFR chronological cuts | v2 validated plan; zero stream starts; square pixels; no rotation; one video and at most one audio stream; source hash/metadata match |
| Explicit static crop | Even pixel width/height; inspected crop inside source; crop/output aspect matches within one source pixel; no invented center crop, stretching or padding |
| Pan/track keyframes | Fixed crop dimensions; both shot boundaries present; linear, quadratic ease-in/out or smoothstep ease-in-out. `track` consumes supplied coordinates; it does not run a tracker |
| Static dialogue | `style: static-white`, linked verified words and source hash, checked position in output pixels, no emphasis/animation, explicit local font. Font size is 4.5% of output height with a 12 px minimum; inspect actual glyphs and line length |
| Audio | Original source audio with chronological cuts, encoded AAC 48 kHz; no new events or mix changes |
| Output | Default 1080×1920, H.264 CRF 18, yuv420p, square pixels. `--width`/`--height` permit explicit even dimensions up to 4096. Preserve source FPS |

Source/output cut boundaries must align with native frames. Caption times need
explicit centisecond precision for ASS. The renderer rejects ASS control syntax
instead of altering dialogue. All layouts requiring new composition, applied
style traits, assets/effects, changing-size zoom, retiming, music, SFX, ducking,
animated/translated captions and VFR input are unsupported and rejected. Use an
appropriate tested renderer/NLE, or revise the EDL to a genuinely acceptable
simpler alternative. Never strip fields simply to bypass the check.
Plans also have a portable 28,000-character command budget. Longer graphs need
a separately tested segmented renderer; the tool will not truncate the graph.

## Procedural SFX pack and evidence-linked audio pass

The base EDL renderer intentionally preserves source audio and rejects SFX,
BGM, ducking and other unimplemented treatments. For expressive SFX, keep the
visual edit plan unchanged and create a separate `audio-design.json` using
`schemas/audio-design.schema.json`.

Generate six original synthesized starter accents (no third-party samples):

```bash
python scripts/generate_sfx_pack.py --output-dir work/audio-assets
```

The pack contains `soft-pop`, `word-tick`, `whoosh-short`, `soft-impact`,
`sparkle`, and `boing-soft` WAV files plus a SHA-256 manifest. They are simple
procedural accents, not realistic Foley. Listen to them and select only those
that suit the source. External assets are allowed only with documented source,
license and SHA-256. Keep asset paths relative to the audio-design file.

After the ordinary EDL preview is rendered, apply the audio event plan:

```bash
python scripts/render_audio_events.py \\
  --video work/preview/preview.mp4 \\
  --audio-plan work/audio-design.json \\
  --edit-plan work/edit-plan.json \\
  --transcript work/transcript.json \\
  --output-dir work/audio-preview
```

`--transcript` is required when any event uses `trigger: word-emphasis`. All
events use output seconds and must link to evidence IDs in the matching edit
plan. Word accents must map to verified word IDs; motion cues need verified
visual evidence and a motion camera decision; transition cues must align to a
real shot boundary. Assets are hash-checked and paths cannot escape the audio
plan directory. The renderer limits the plan to 60 events and at most two
simultaneous SFX events, preserves the video stream, mixes AAC 48 kHz, applies
source-mix sidechain ducking and a conservative peak limiter. It does not isolate
voice stems or normalize loudness. Output is `preview-with-sfx.mp4` plus
`audio-mix-receipt.json`; technical PASS is not final audio approval.

The work directory records the plan snapshot, argv command, filtergraph, output
probe, output hash and technical receipt. Output is always `preview.mp4` with
delivery REVIEW. Native-frame count, codec, dimensions, audio timing and full
decode checks run automatically. Loudness targets in the plan remain unassessed;
this renderer does not normalize to them. Safe-area declarations, glyph coverage,
speaker accuracy, perceptual synchronization and editorial quality still require
inspection. Font files in the work directory also require appropriate rights.

## Validation and promotion

```bash
python scripts/validate_skill_repo.py
python -m unittest discover -s tests -v
python scripts/smoke_ffmpeg.py
```

Media integration tests generate color patterns and two audio tones, compare
crop pixels/source cut times, check pan interpolation, caption-region changes,
silent-video behavior and tamper detection. Their fabricated transcript receipts
are explicitly test fixtures, not human verification of the tones. Tests print
NOT_RUN skips if FFmpeg/FFprobe or the test font is unavailable. CI installs these
tools before testing. Inspect the full result, including skips, before claiming PASS.

Complete technical, editorial and human review on real footage, correct the EDL,
rerender, then use the existing final validator and delivery workflow. Package
only the reviewed deliverables and permitted assets. Do not zip inspection
directories, extracted source audio, model files or the source video.
