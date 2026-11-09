# GitHub integration research and gap closure

Reviewed 10 November 2026. This extends the [initial audit](implementation-report.md).
Repository HEADs, archive state and code-license metadata were inspected through
GitHub. The [machine-readable inventory](../integrations/github-components.json)
records the exact upstream commits. Those snapshots are inspection references,
not tested dependency locks. No third-party source, weights or assets were copied.

## What to use, and what it actually solves

| Gap | Upstream | Recommended handoff | Remaining boundary |
|---|---|---|---|
| Word transcription with modest hardware | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Optional CPU int8 local-model runner, then ASR_RAW transcript | Recognizing words does not verify them. CPU speed depends on model and hardware. No inference benchmark was run here. |
| Word timing after transcription | [WhisperX](https://github.com/m-bain/whisperX) | Import aligned segment words through asr_bridge; preserve missing times as unresolved | Its documented limitations include unalignable tokens, overlap and imperfect diarization. Never interpolate missing word times into apparent evidence. |
| Who spoke when | [pyannote-audio](https://github.com/pyannote/pyannote-audio) | External diarization, then compare turns against the original audio and visible avatars | Community-1 needs model access/terms and a token. Speaker labels are anonymous. Preserve overlap; an exclusive timeline must not erase shared speech. No adapter/runtime test here. |
| Audiovisual context and candidate explanations | [Qwen3-Omni](https://github.com/QwenLM/Qwen3-Omni) | Optional external perception worker returns timestamped CANDIDATE observations; editorial-intelligence checks causes and alternatives | Video audio must actually be enabled. The upstream BF16 table reports about 79 GB for a 15-second Instruct video example, so this is not a default laptop dependency. Interpretations still need source checking. |
| Avatar/object motion | [SAM 2](https://github.com/facebookresearch/sam2) | Seed the actual avatar using a box/points, track masks, convert inspected bounds to EDL crop keyframes | Segmentation does not identify the active speaker. Recheck occlusion, scene cuts, avatar pose and HUD collisions. No model execution or mask-to-EDL adapter is claimed. |
| Long-VOD navigation | [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Optional scene-boundary candidates to guide sampling, then inspect dialogue context | A scene change is not a narrative beat. Static VTuber layouts can contain the best moments without a detected cut. No runtime adapter here. |
| Timeline exchange with an editor | [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | Future NLE interchange with explicit adapter support and round-trip tests | OTIO is timeline interchange, not a renderer. Effects, retiming and captions need adapter-specific preservation checks. Export is not implemented here. |
| Deterministic preview and measurements | [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Implemented inspection and bounded EDL renderer, using existing editorial choices | Our renderer supports a defined subset, not every FFmpeg capability. Unsupported plans fail with a specific reason. Pixel/stream tests cannot judge humor or comfortable listening. |

Code-license snapshot: faster-whisper and pyannote MIT; WhisperX BSD-2-Clause;
PySceneDetect BSD-3-Clause; Qwen3-Omni, SAM 2 core and OTIO Apache-2.0.
Model weights, datasets, fonts and sample assets can have separate terms. FFmpeg
licensing depends on its build/components, as described by
[FFmpeg itself](https://ffmpeg.org/legal.html). This repository invokes the user's
installed FFmpeg and does not distribute binaries or model weights.

## Engineering decisions made from this research

1. Keep editorial-intelligence as the decision owner. Models provide observations,
   proposals and uncertainty, not automatic permission to cut or add effects.
2. Add small executable bridges before large model dependencies: source inspection,
   word import, file-integrity checking and preview rendering. These can be tested
   with generated media in CI without pretending the test is real VTuber footage.
3. Keep optional model environments separate. The pinned faster-whisper release
   has a local-only runner; WhisperX has a JSON import path. Remaining projects
   are documented integration options, not installed capabilities.
4. Fail on unsupported EDL decisions. An effects string is descriptive data, never
   executable shell/filter code. The renderer cannot silently remove an effect,
   replace a layout or relabel an ASR result as verified.
5. Keep final human/editorial review gates. Additional automation changes what can
   be checked mechanically; it does not prove the quality of a punchline.

## Coverage of the remaining shortcomings

| Shortcoming after the editorial upgrade | Implemented mitigation | Still needed for maximum practical quality |
|---|---|---|
| Source inspection exists mainly as instructions | Bounded frame/audio bundles with source hash and precise requested intervals | Play the complete selected sequence; sparse samples can miss anticipation, overlap and reactions |
| Word data requires manual conversion | WhisperX/faster-whisper JSON import, source offset, raw hash and unresolved-word ledger | Original-language listening, proper-name checks, code-switching and alignment review |
| Evidence is only a declaration | Verify actual source hash/metadata and inspection-file hashes; reject escaping paths | Review receipt authenticity, observation validity and exact media meaning remain human/perception work |
| EDL has no execution path | Native-CFR cuts, explicit crops, supplied pan keyframes/easing, verified static dialogue and source audio | Zoom, freeze, speed ramps, overlays, translations, animated emphasis, SFX and music require a separate tested renderer/NLE |
| Camera cannot track or map speakers automatically | Existing speaker-follow rule and explicit coordinates remain enforced | External SAM 2 tracking plus manual or source-evidenced identity/turn mapping; fall back to inspected stable framing when confidence drops |
| Audio mix cannot be certified by stream checks | Source audio timing is retained; synthetic two-tone tests check cut mapping | Measure with FFmpeg loudness tools, apply a project-specific mix, then listen; matching targets alone cannot judge comfort |
| Style extraction is subjective | Existing scoped style-profile schema plus bounded reference inspection | Compare caption, camera and pacing traits across several actual reference moments; no copied fonts/music/memes without permission |
| Platform compatibility was narrow | Add Windows and Ubuntu CI for the Python production path | Colab, mobile playback, production resolutions and other FFmpeg builds need separate actual runs |
| No actual footage regression data | Keep all eight footage gates and twelve editorial cases NOT_RUN | Licensed/user-provided fixtures covering conversation, gameplay, overlap, languages and different styles, assessed with the existing rubric |

## Practical deployment order

Start with core Python dependencies and FFmpeg. Run inspection, create a source-
grounded EDL, and test a representative preview. Add faster-whisper when a local
model is available; add alignment/diarization only when the source needs them.
Use a GPU perception/tracking worker only after measuring its value on actual
fixtures. Long videos should be narrowed through multiple evidence windows,
including context before and after candidates. Never rank clips from loudness,
scene boundaries or avatar movement alone.

Promotion of any optional component requires recorded tool/model revision,
hardware, source hash, commands, actual outputs, failure cases and review.
Compare the new path with a simpler baseline on the same footage. Retain it only
when it improves a specific measured deficiency without losing context or text.
See [production commands and supported features](production-tools.md).
