# Skills-Clip

Professional skill system for analyzing, selecting, editing, rendering, and quality-checking VTuber short clips.

This repository is designed so a new AI agent can enter the project, understand the workflow, choose the correct specialist skill, and produce reproducible edit plans instead of blindly applying one visual template to every video.

## Start here — mandatory reading order

1. **[Agent Operating Contract](AGENT_OPERATING_CONTRACT.md)** — universal rules, evidence labels, workflow, and delivery contract.
2. **[Clip Router](clip-router/SKILL.md)** — classifies the source and selects the correct specialist skills.
3. Read the selected specialist skill below.
4. Read any reference document linked by that skill.
5. Create an edit plan, render, and run QA before delivery.

## Skill directory

| Skill | Use it when |
|---|---|
| [clip-router](clip-router/SKILL.md) | Every new VTuber clipping task; routes the work |
| [vtuber-gameplay-facecam-clip](vtuber-gameplay-facecam-clip/SKILL.md) | Gameplay, HUD, facecam, clutch, horror, fail, competitive moments |
| [vtuber-conversation-clip](vtuber-conversation-clip/SKILL.md) | Dialogue-led clips, speaker-follow cuts, conversational reaction timing |
| [vtuber-collab-reaction-clip](vtuber-collab-reaction-clip/SKILL.md) | Multi-person collabs, overlapping dialogue, group reactions |
| [transcript-and-speaker-pipeline](transcript-and-speaker-pipeline/SKILL.md) | Word-level transcript, timestamps, diarization, speaker ledger |
| [caption-design](caption-design/SKILL.md) | Verbatim captions, translation, reading aids, speaker colors, safe placement |
| [hook-pacing-retention](hook-pacing-retention/SKILL.md) | Candidate discovery, hook, setup, escalation, payoff, ending |
| [audio-mix-and-sfx](audio-mix-and-sfx/SKILL.md) | Voice/game/BGM balance, ducking, loudness, SFX |
| [ffmpeg-vertical-quality](ffmpeg-vertical-quality/SKILL.md) | 16:9-to-9:16 reframing, crop, scaling, encoding |
| [render-package-for-user](render-package-for-user/SKILL.md) | Portable ZIP, Windows/Linux scripts, PC and Colab instructions |
| [qa-and-self-review](qa-and-self-review/SKILL.md) | Technical and editorial checks before delivery |

## Standard workflow

Brief → probe → inspect → listen → route → select highlight → edit decision list → transcript verification → shot/crop design → captions → audio → render → QA → delivery.

Not every project needs every skill. The router chooses the minimum set that fits the source and brief.

## Core principles

- Source footage and verified user instructions outrank generic editing heuristics.
- ASR output is **ASR_RAW**, never automatically final subtitle text.
- Speaker diarization IDs are not real identities; map them to avatars only with evidence or user confirmation.
- Every shot and effect must have an editorial reason.
- Preserve setup, cause-and-effect, gameplay evidence, and reaction timing.
- Conversation edits follow the active speaker; shared two-shots are reserved for genuine overlap/shared reactions. Do not default to permanent stacked or split-screen panels.
- A render is not final until its frames, audio, metadata, and package have been checked.
- Never include the user's original VOD/source media in a render ZIP.

## Structured artifacts

- [Edit plan JSON Schema](schemas/edit-plan.schema.json) — source, routing, clip, shots, captions, audio, assets, and QA.
- [Transcript JSON Schema](schemas/transcript.schema.json) — word timestamps, speaker IDs, and verification state.
- [Example edit plan](examples/edit-plan.example.json) — dummy data; replace with real source evidence.
- [Example transcript](examples/transcript.example.json) — dummy ASR_RAW word; not a real quote.
- [Evaluation cases](evals/cases.md) — eight regression gates for new AI/editor workflows.
- [Repository validator](scripts/validate_skill_repo.py) — checks skill folders, frontmatter, and required sections.

Run the structural validator from the repository root:

```bash
python scripts/validate_skill_repo.py
```

The validator checks documentation structure only. It does not prove that FFmpeg commands work, that a render is synchronized, or that the edit is entertaining.

## Existing conversation reference

The original [VTuber conversation skill](vtuber-conversation-clip/SKILL.md) and its [style reference](vtuber-conversation-clip/references/style-reference.md) remain in place. The reference observations come from a supplied sample clip and are not universal presets. Its speaker-follow camera rule is a critical style constraint.

## Output expectations

Depending on the request, deliver:
- MP4 master;
- edit-plan JSON / EDL;
- verified transcript and ASS/SRT captions;
- render scripts and a short usage guide;
- asset/license notes;
- QA report and keyframes.

Do not claim an output, script, or QA step is tested unless it was actually executed and inspected.
