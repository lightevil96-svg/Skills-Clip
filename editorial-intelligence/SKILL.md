---
name: editorial-intelligence
description: Decide why, when and how strongly to edit a VTuber moment using source evidence, causal context, story beats, emotion, visual focus and simpler alternatives. Use after inspection for clip selection or editing; return a shared decision brief to the router and selected specialists.
---

# Editorial Intelligence

## Tujuan
Make intentional editorial decisions that preserve the source meaning. Prefer
an understandable, well-timed exchange over a high effect count. Own reasoning
and the decision brief; leave discovery ranking and production to their existing
skills. Read the [operating contract](../AGENT_OPERATING_CONTRACT.md) first.

## Aturan wajib
1. Separate observed facts, interpretations and unknowns. Loudness, avatar
   motion, chat spikes and cuts locate candidates; none proves humor or emotion.
2. Explain the trigger, response and minimum viewer context before calling a
   moment a highlight. If the evidence is incomplete, return a provisional plan.
3. Preserve negation, qualifiers, causal order, hesitation, silence and reactions
   when they carry meaning. Never invent a line or move a laugh to a new cause.
4. Compare every nontrivial treatment with a stable shot/direct cut/no added
   sound alternative. Choose expressive editing only for a specific function.
5. Follow the selected specialist's composition constraints. Conversation solo
   shots follow the active speaker; a shared two-shot serves an actual shared
   exchange. Never default to a permanent split-screen or stacked composition.
6. Record capability limits. Reading ASR or measuring audio is not listening;
   generating a frame is not inspecting it. Do not infer hidden mental states.
7. Keep aesthetic confidence separate from evidence confidence. A confidence
   number is a working judgment, not a probability of audience enjoyment.

## Langkah kerja

### 1. Establish context
Record in `editorial`: intent, what happens, who speaks, what causes each
reaction, what the audience already knows and what must be retained. Include
source-time evidence with an artifact locator, observation method and status.
For an ambiguous pun, note competing interpretations and inspect surrounding
audio. Do not style a guessed joke into apparent fact.

### 2. Build only the necessary story
Use any subset of hook, setup, context, build-up, escalation, punchline,
reaction, payoff and ending. A sincere answer may need context → answer → hold;
a failure may need attempt → result → reaction. A quiet smile can be the payoff.
Do not force a nine-beat template. Preserve prerequisite beats even when they
lower a candidate's apparent speed. Pass context and evidence to
[hook-pacing-retention](../hook-pacing-retention/SKILL.md) for candidate comparison.

### 3. Decide per beat and shot
Record editorial intent, narrative beat, emotional context, visual focus,
camera choice, effect choice, timing rationale, intensity, evidence IDs,
confidence and a simpler alternative in each v2 shot's `editorial` object.
Use the [decision guide](references/decision-guide.md) for timing and intensity.
Let the primary specialist implement those choices; revise this same record if
the preview changes the decision. Do not create a second conflicting EDL.

### 4. Set attention order
Rank visual focus per beat. Conversation usually prioritizes the active face
and dialogue; clutch gameplay prioritizes target/HUD before avatar reaction;
collab prioritizes the initiating speaker and the next relevant responder.
Decorations always yield to meaning. Inspect moving footage, not only the best
single frame. Use [camera and effects](references/camera-and-effects.md) for
reframing, motion, freezes, speed changes, inserts and safe fallback behavior.

### 5. Apply scoped style preferences
If a user supplies a reference, use the
[style protocol](references/style-profiles.md). Extract visual characteristics
with timestamps and uncertainty. Keep universal principles, user preferences
and project instructions distinct. Do not copy a reference's specific assets,
dialogue, jokes or cadence into unrelated footage.

### 6. Compare and revise
Preview the plain treatment and the proposed treatment around the whole beat.
Check whether the change improves comprehension, timing or emotion. If it
only adds activity, remove it. Record rejected options and revision evidence.
Use [editorial QA](../qa-and-self-review/references/editorial-rubric.md). A score
never replaces a specific observation or human review of ambiguous material.

## Structured handoff
Use [v2 EDL](../schemas/edit-plan.schema.json) and
[annotated example](../examples/edit-plan.editorial.example.json). `in_s/out_s`
are source seconds; `output_in_s/output_out_s` and caption times are output
seconds. Use explicit `time_map` segments for speed changes or freezes.
Run `python scripts/validate_artifacts.py edit-plan PLAN.json --transcript WORDS.json`.
This checks the records, not the truth of their content. Use `--stage final` only
for delivery readiness checks, never to promote fixture data to verified footage.

## Potongan FFmpeg
This skill does not render. Hand explicit coordinates and time mappings to
[ffmpeg-vertical-quality](../ffmpeg-vertical-quality/SKILL.md). Check the local
build's filter help before constructing commands; no tracking model is assumed.

## Checklist QA
- [ ] Explain why the moment matters without describing only volume or motion.
- [ ] Preserve context needed to understand the payoff.
- [ ] Anchor each nontrivial decision to source evidence and a narrative beat.
- [ ] Compare with a simpler treatment; allow intentional stillness.
- [ ] Follow the speaker and protect gameplay evidence where required.
- [ ] Mark unobserved audio/visual properties and unavailable tools honestly.
- [ ] Recheck timing in the output and update decisions after revision.

## Kesalahan umum
Avoid periodic zooms, constant caption movement, SFX on each cut, irrelevant
memes, premature punchline text, transitions used as filler, uniform shot
durations, compressed reaction chains and a single template for every genre.

## Batas kemampuan AI
Text-only agents can organize supplied evidence but cannot certify source
emotion, lip sync, attribution or comfort. Audiovisual agents must log actual
inspection and unresolved ambiguity. Humans resolve culture-dependent humor,
uncertain language and final listening comfort. No viral or universal
professional-quality guarantee follows from this workflow.
