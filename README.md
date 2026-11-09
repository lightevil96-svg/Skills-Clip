# Skills-Clip

Professional skill system for analyzing, selecting, editing, rendering, and quality-checking VTuber short clips.

This repository is designed so a new AI agent can enter the project, understand the workflow, choose the correct specialist skill, and produce reproducible edit plans instead of blindly applying one visual template to every video.

## Start here: reading order

1. **[Agent Operating Contract](AGENT_OPERATING_CONTRACT.md)** — universal rules, evidence labels, workflow, and delivery contract.
2. **[Clip Router](clip-router/SKILL.md)** — classifies the source and selects the correct specialist skills.
3. Inspect the source and read [Editorial Intelligence](editorial-intelligence/SKILL.md) for selection/editing decisions.
4. Read only the selected specialists and the references needed for the task.
5. Create and validate one edit plan, render, review and revise before final delivery.

## Skill directory

| Skill | Use it when |
|---|---|
| [clip-router](clip-router/SKILL.md) | Every new VTuber clipping task; routes the work |
| [editorial-intelligence](editorial-intelligence/SKILL.md) | Context, story, timing, attention, effects, alternatives and scoped style decisions |
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

Brief → contract → provisional route → source inspection → editorial context →
clip discovery → transcript/speaker verification → specialist decisions → EDL →
render → technical QA → editorial QA/revision → delivery.

Not every project needs every skill. The router chooses the minimum set that fits the source and brief.

Inspection, discovery and transcription may iterate. Transcript-only tasks skip
camera/render work. Package-only tasks validate the supplied edit rather than
inventing a new story. The editorial module owns why/when; specialists own how.
See [audit and implementation report](docs/implementation-report.md).

## Core principles

- Source footage and verified user instructions outrank generic editing heuristics.
- ASR output is **ASR_RAW**, never automatically final subtitle text.
- Speaker diarization IDs are not real identities; map them to avatars only with evidence or user confirmation.
- Every shot and effect must have an editorial reason.
- Compare each nontrivial treatment with a simpler alternative. Natural holds,
  silence and direct cuts can be the strongest choices.
- Preserve setup, cause-and-effect, gameplay evidence, and reaction timing.
- Conversation edits follow the active speaker; shared two-shots are reserved for genuine overlap/shared reactions. Do not default to permanent stacked or split-screen panels.
- A render is not final until its frames, audio, metadata, and package have been checked.
- Never include the user's original VOD/source media in a render ZIP.

## Structured artifacts

- [Edit plan JSON Schema](schemas/edit-plan.schema.json) — source, routing, clip, shots, captions, audio, assets, and QA.
- [Transcript JSON Schema](schemas/transcript.schema.json) — word timestamps, speaker IDs, and verification state.
- [Schema and migration guide](schemas/README.md): v1 compatibility, v2 decisions, clocks and verification receipts.
- [Style profile schema](schemas/style-profile.schema.json): scoped reference traits and adaptations.
- [Editorial review schema](schemas/editorial-review.schema.json): ten anchored dimensions, reviewer mode and revision evidence.
- [Example edit plan](examples/edit-plan.example.json) — dummy data; replace with real source evidence.
- [Example transcript](examples/transcript.example.json) — dummy ASR_RAW word; not a real quote.
- [Editorial edit example](examples/edit-plan.editorial.example.json): synthetic v2 decision records with [linked words](examples/transcript.editorial.example.json).
- [Style example](examples/style-profile.example.json) and [review example](examples/editorial-review.example.json): honest CANDIDATE/NOT_RUN states.
- [Evaluation cases](evals/cases.md): eight original gates plus twelve editorial scenarios.
- [Editorial rubric](qa-and-self-review/references/editorial-rubric.md): observable 0–4 anchors, evidence and revision procedure.
- [Repository validator](scripts/validate_skill_repo.py): discovery, frontmatter, links, schemas and examples.

Run from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_skill_repo.py
python -m unittest discover -s tests -v
python scripts/validate_artifacts.py edit-plan examples/edit-plan.editorial.example.json --transcript examples/transcript.editorial.example.json
python scripts/smoke_ffmpeg.py --output-dir test-results/smoke
```

The artifact validator rejects invalid ranges/crops, broken IDs, unsupported
verification claims, changed dialogue, inconsistent time maps and incomplete
final-review declarations. Use `--stage final` with actual transcript/review
artifacts for final readiness checks. Draft schema PASS is not approval to render
unverified captions. Existing unversioned examples remain valid as drafts.

The smoke script executes a small synthetic FFmpeg pan, ASS burn-in, Bash package
with spaced paths, decode and stream checks. It is not a generic EDL renderer.
Python/jsonschema/PyYAML are developer validation dependencies, separate from
FFmpeg/FFprobe for basic rendering. Only actually tested builds/platforms may
be reported PASS. Missing tools fail explicitly instead of silently skipping.

## Capability and quality limits
No ASR model, audiovisual perception model, tracker or automatic editor is
bundled. Agents must declare the tools they have actually used. Direct source
audio review can verify words only with the explicit policy and auditable
receipts; ASR alone remains raw. Ambiguous words/speakers require human review.
Final audio comfort still requires human listening.

Validators check declarations, not their truth. They cannot authenticate a
receipt, license, expression, lip sync or joke. Keep technical QA, editorial QA,
human review and automated checks separate. Scores never promise professional
quality or viral reach. Footage-dependent evals are NOT_RUN without footage.

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
