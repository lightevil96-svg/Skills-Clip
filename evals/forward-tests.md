# Text-only skill forward tests

Run date: 2026-11-09. Two fresh agent threads received the repository entry point
and a task scenario. They did not receive expected answers or the implementation
diagnosis. No source footage or render was available. The parent agent reviewed
the responses as text-only policy smoke tests. These are not audiovisual or
human editorial reviews and do not pass Gates 1–8 or E01–E12 on real footage.

## F01 Conversation with only ASR
Task: prepare a natural 12-second two-avatar conversation clip. Supplied ASR
describes “I did not press it” at 0–3 s, silence at 3–5 s, “Then who did?” at
5–7 s and laughter at 7–12 s. No audio/video or avatar mapping exists. The user
requests colorful final subtitles, zoom every two seconds and impacts on turns.

Observed response:
- Delivered a provisional denial → pause → question → possible-laughter story.
- Kept what “it” refers to, who laughs and why UNKNOWN; did not infer confession.
- Kept ASR_RAW, neutral provisional attribution and missing source metadata.
- Preserved the pause initially, and conditioned shared shots on verified shared
  reaction. Did not invent word timestamps, crops or a completed render.
- Treated the explicit periodic-effect request as a project instruction to
  compare against stable framing/no sound, without making it a default style.
- Separated provisional planning from final audio/caption/visual review.

Response excerpts:
> “The transcript does not establish a confession, shared reaction or complete punchline.”

> “Keep the current handoff incomplete rather than invent dimensions, frame rate or a source path to make it validate.”

Result: PASS for these observed text-policy behaviors. NOT_RUN for speaker
correctness, caption accuracy, timing quality, humor and actual render quality.

## F02 Gameplay fail, ramp and unavailable reference
Task: plan a 9:16 clip from an annotated 1920×1080/60 fps storyboard. Aiming and
edge low-ammo HUD occur at 10–13 s, miss/result at 13–14 s, avatar reaction at
14–17 s and an off-screen speaker at 16–17 s. Only ASR exists. User requests a
dramatic ramp, accurate captions and portable ZIP; meme-heavy reference media
and assets are unavailable.

Observed response:
- Selected gameplay with a separate conversation decision for the final second.
- Preserved target/HUD and the visible result before the avatar close-up.
- Refused to attribute the off-screen voice to the visible avatar without evidence.
- Proposed explicit piecewise source/output ramp timings as trial values, with
  native-speed comparison and a requirement to preserve necessary dialogue.
- Kept raw subtitles unverified, reference traits UNKNOWN and assets uncleared.
- Distinguished a documented EDL from an unimplemented automatic renderer or tracker.
- Required source-free ZIP, spaced paths, per-platform tests and human listening;
  all actual render/package/perception tests remained NOT_RUN.

Response excerpts:
> “These boundaries are trial values, not inspected event onsets.”

> “The repository supplies neither a universal EDL renderer nor automatic tracking.”

Result: PASS for these observed text-policy behaviors. NOT_RUN for gameplay
readability, real ramp/audio sync, subtitle accuracy and reference-style quality.

## Limits and repeat procedure
These two responses are a narrow sample, not a general capability benchmark.
Repeat the task prompts in fresh threads after relevant changes, retain their
responses, and check actual artifacts when footage is available. Do not provide
the observations above to the responding agent as an answer key.
