---
name: vtuber-conversation-clip
description: Use when editing VTuber livestream conversations into vertical short clips with speaker-specific subtitles, quick reaction cuts, close-ups, and context-aware meme or sticker overlays. Also use when analyzing a reference clip to reproduce this dialogue-led editing style.
---

# VTuber Conversation Clip

## Objective

Turn a real VTuber conversation into a compact, readable vertical clip. Preserve the original exchange and timing; make the humor legible through speaker changes, facial reactions, color-coded subtitles, and a few well-timed visual gags.

The reference is a 23.6-second, 9:16 conversation clip. It is not a gameplay montage. Its identity comes from the interaction between speakers, not from a title sequence, countdown, gameplay HUD, or constant transitions.

## Non-negotiable rules

1. **Do not invent dialogue.** Captions must match verified speech or text supplied by the user. If speech cannot be transcribed reliably, ask for a transcript or omit uncertain words.
2. **Keep speaker identity consistent.** Assign one subtitle color to each known speaker and keep it stable throughout the clip. If speaker identity is uncertain, do not guess; use neutral styling until confirmed.
3. **Cut for the conversation.** Prefer cuts at speaker turns, expression changes, punchlines, and reaction holds. Do not cut on an arbitrary beat if it damages the exchange.
4. **Keep faces readable.** Reframe around the active speaker's face and upper body. Never let captions, stickers, or meme inserts obscure the eyes or mouth during important dialogue.
5. **Use visual gags selectively.** A meme, spinner, emote, or doodle must clarify the joke or reaction. Do not decorate every shot.
6. **Protect the original voices.** Dialogue is the primary audio. Optional music and sound effects must sit underneath it and must not mask speech.
7. **Do not force a generic hook or CTA.** The reference starts directly in the conversation and ends on a reaction/laugh. Keep that structure unless the user asks for a hook, title card, or follow CTA.
8. **Do not copy unrelated assets.** Recreate the visual function of an insert, not a specific logo, character sticker, or copyrighted image from the reference unless the user supplies or requests it.

## Style identity

Use these as reference anchors, not rigid presets:

- **Canvas:** vertical 9:16. The supplied reference is 360×640 at 30 fps; for a clean final render, use 1080×1920 at 30 fps.
- **Framing:** one main avatar in a medium or medium-close crop, usually centered. Alternate to the next speaker when the conversation changes. Use a two-shot or split composition only when seeing both reactions helps the joke.
- **Pacing:** conversational jump cuts, usually around 1–3 seconds per visual beat in the reference. Let a reaction breathe when it is funny; do not shorten every shot to the same duration.
- **Subtitles:** rounded, bold sans-serif appearance; colored fill per speaker; thick light outline and a restrained dark shadow for contrast. Ordinary dialogue captions have no opaque caption box in the reference.
- **Placement:** generally centered in the lower-middle area, adjusted shot by shot to avoid faces and important UI. Use one or two short lines, not paragraph blocks.
- **Reaction graphics:** small, expressive overlays such as a contextual image above a character's head, a loading/confusion spinner, or hand-drawn laughter marks. Their timing should coincide with the reaction.
- **Transitions:** mostly direct cuts. A short flash or blur can punctuate a major shift, but should not be applied to every cut.
- **Ending:** land on the strongest reaction or laugh. Do not append an unrelated outro.

See [references/style-reference.md](references/style-reference.md) for the source-specific observations and approximate palette.

## Editing workflow

### 1. Inspect the source

- Run `ffprobe` and record duration, frame size, frame rate, video/audio start times, sample rate, and channel layout.
- Build a contact sheet at 1 fps. Increase to 2–4 fps around likely speaker changes, inserts, and punchlines.
- Inspect full-resolution frames before choosing crops. A contact sheet is for navigation, not final crop decisions.
- Check the audio waveform and levels. Use speech recognition only if available, then manually verify the transcript against the source.
- Identify any existing chat strip, stream labels, emotes, or separators. Preserve them only when they contribute context.

### 2. Find the story inside the real conversation

Create a short beat outline using only what is actually said and shown:

- opening observation or question;
- misunderstanding, unexpected answer, or contrast;
- clarification or escalation;
- reaction and payoff.

The reference's broad rhythm is an observation, a word/color misunderstanding, a meme association, a second speaker's emphatic interjection, a confused reaction, a clarification, then recognition and laughter. Do not reuse those lines or that exact joke for unrelated footage.

### 3. Select and reframe shots

- Start as close as possible to the first meaningful line; remove dead air before it.
- Use the active speaker's medium-close crop for the line.
- Cut to another avatar when they speak or when their reaction is the joke.
- Use a two-shot when simultaneous reactions matter; otherwise prefer a clean single-speaker crop.
- Keep the crop stable enough to read expressions. Add a small punch-in only for a clear emphasis, not as constant motion.
- Keep useful source UI in frame when it establishes who is speaking or shows a relevant chat/emote. Do not preserve irrelevant empty strips just because they exist in the reference.

### 4. Build subtitles

- Transcribe first; style second. Time each caption to the spoken phrase.
- Keep phrasing short and natural. Use line breaks at semantic pauses.
- Assign and document a speaker-to-color map before styling the full clip.
- Use a rounded bold font, a thick outline, and a subtle shadow. Avoid a large opaque box for ordinary dialogue unless the background makes text unreadable.
- Place captions in the lower-middle region by default, then move them to protect faces, hands, or important overlays.
- When showing an original Japanese term with a reading, keep the original and reading distinct (for example, original text on one line and `[reading]` below). Do not label a reading as a translation.
- Use neutral white text with a dark outline for narrator notes or captions that are not spoken by a particular avatar.
- Do not add captions to silence, infer a speaker from appearance alone, or turn an editor's interpretation into a quotation.

### 5. Add reaction graphics

Use a small number of context-specific visual inserts:

- **Meme/image insert:** anchor it near the character or object that creates the joke; scale it large enough to read, but do not cover the face.
- **Confusion/loading graphic:** place it above the confused avatar's head or near the face; keep it on screen only for the confusion beat.
- **Laughter doodles/emotes:** cluster them around the reacting character, with slight variation in angle/scale. Avoid filling the entire frame.
- **Chat/emote strip:** retain only if it helps explain the exchange or adds a visible reaction.
- Add a quick flash/blur only for a strong transition or emphasis. Keep it brief and do not use it as a substitute for good cut timing.

### 6. Audio treatment

- Keep dialogue at the front of the mix and preserve natural pauses and reactions.
- Do not assume that every conversation clip needs background music. The reference is dialogue-led; use music only when requested or when it clearly improves pacing.
- If adding music, duck it under speech. If adding SFX, align them with visible gags or cuts and keep them short.
- Avoid clipping, pumping that damages speech, or excessive loudness normalization.
- Keep the source audio synchronized with the video; inspect stream start times before trimming or concatenating.

### 7. Render and package

Default final target: 1080×1920, 30 fps, H.264 video, yuv420p, AAC audio at 48 kHz, with fast-start enabled. Match the source frame rate if there is a specific reason to do so.

When the user wants a render package rather than a finished render:

- include `render.sh` and `render.bat`;
- include only the script, overlays, fonts/assets that may legally be redistributed, and a concise `BACA_DULU.txt`;
- accept the source video path as a script argument;
- **never put the user's original video inside the ZIP**;
- keep the workflow compatible with FFmpeg 6–8 and avoid deprecated `-filter_complex_script`;
- make instructions usable from a phone and Google Colab when relevant.

The detailed workflow is in [references/render-workflow.md](references/render-workflow.md).

## Quality-control checklist

- [ ] The opening begins on a meaningful spoken line.
- [ ] Every subtitle is supported by audible speech or user-provided text.
- [ ] Speaker colors remain consistent.
- [ ] Cuts follow the exchange and preserve reaction timing.
- [ ] Faces and mouths remain visible during important lines.
- [ ] Meme/sticker overlays are readable, relevant, and do not cover expressions.
- [ ] Any Japanese text, reading, or translation is labeled correctly.
- [ ] Dialogue remains clear; music/SFX do not overpower it.
- [ ] No accidental black frames, flash held too long, or abrupt audio cut.
- [ ] The ending lands on a reaction/payoff rather than an unrelated CTA.
- [ ] The original source video is excluded from any delivered ZIP.

## Anti-patterns

Do not automatically import a gameplay-highlight template into this style: no racing HUD, countdown timer, leaderboard narration, neon VTuber-card ring, constant beat-synced zoom, teaser countdown, or mandatory follow CTA unless the footage or user explicitly calls for them. Those elements belong to a different edit format.
