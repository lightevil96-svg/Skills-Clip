# Editorial rubric: observable 0–4 anchors

Use this rubric on the actual source and output. First identify intended beat,
audience context and constraints. Score each applicable dimension independently.
Record timecoded evidence, a concrete issue and the next action. Never fill a
score from metadata or an average of other scores. Do not award a professional
label from a total. Use the [review schema](../../schemas/editorial-review.schema.json).

| Dimension | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Storytelling clarity | Edit contradicts cause or meaning | Essential setup absent | Story recoverable but one dependency unclear | Cause, context and payoff clear on first viewing | Every retained beat has a role; a new viewer can explain the exchange without missing context |
| Hook effectiveness | Opening misleads or reveals the wrong event | Opening gives no understandable reason to continue | Relevant opening needs avoidable explanation | Immediate meaningful question/action consistent with payoff | Opening establishes curiosity and necessary context with precise economy, verified against the source |
| Timing precision | Cuts/captions reverse or destroy the beat | Key reveal, word or reaction is cut off | Beat survives but one anticipation/hold feels rushed or late | Word, reveal and reaction boundaries land naturally | Comparison of nearby alternatives supports each sensitive boundary; no useful pause or recovery is lost |
| Humor/emotional delivery | Edit fabricates reaction or changes sentiment | Treatment masks the actual emotion/joke | Meaning remains but an accent distracts | Source humor/emotion reads without added interpretation | Expression, silence and response timing support the specific content; a simpler comparison confirms the treatment helps |
| Visual composition | Essential face, action or result invisible | Repeated obstruction or wrong speaker focus | One distracting crop/move or weak hierarchy | Faces/HUD/action readable with stable attention order | Focus shifts exactly with the beat; endpoints and intermediate motion preserve all necessary evidence |
| Caption readability | Invented/unreadable/misattributed text | Frequent collision, missing glyphs or major timing errors | Accurate text with one reading-speed or hierarchy issue | Accurate, synchronized phrases readable on phone preview | Emphasis and multilingual hierarchy improve comprehension without leading the reveal or competing with faces |
| Audio comfort | False event or unintelligible/distorted voice | Repeated masking, clipping or painful accents | Dialogue understandable with one level/cut/ducking issue | Clear voice, preserved cues and comfortable transitions | Listening comparison supports music/silence and every accent at low/normal levels; no fatigue or misleading cue |
| Editing naturalness | Mechanical cadence destroys conversation/action | Regular zoom/cut/effect pattern dominates | Some motivated choices but repeated template residue | Timing and movement follow source behavior | Variable holds, cuts and restraint feel intentional throughout; removing a treatment demonstrably weakens its role |
| Effect restraint | Effects obscure or falsify meaning | Multiple effects compete at key beats | Mostly relevant with one removable decoration | Every applied effect has evidence and a role; clean beats remain | Plain and expressive treatments were compared; additions are selective and absence is intentional |
| Overall coherence | Style/story/audio conflict or causal meaning fails | Major inconsistency between scenes/speakers | Complete clip with one unresolved mismatch | Story, camera, captions and audio support one intent | Consistent identity adapts to changing beats; ending resolves the story and all revisions were rechecked |

Scores 0–1 identify major problems; 2 identifies a concrete revision; 3 is a
well-supported acceptable result; 4 requires comparative evidence, not more
effects. Do not invent observations to reach an anchor. Scores are judgments,
not measured audience outcomes or promises of retention.

A completed assessment with score 0–2 is FAIL until the deficiency is fixed
and reassessed. This is a revision threshold, not a professional-quality
certificate. Core story/timing/composition/naturalness/restraint/coherence checks
cannot be skipped to make final delivery pass.

## Status and reviewer rules
- PASS/FAIL: assessment actually performed; supply score and evidence.
- REVIEW: missing perception, ambiguous interpretation or unresolved reviewer
  disagreement; score is null.
- NOT_RUN: no assessment performed; score is null.
- SKIP: genuinely inapplicable, with a reason; score is null. No captions can
  justify caption SKIP; missing footage is NOT_RUN, not SKIP.
- Automated checks may report technical results. They must not assign the ten
  editorial scores. Agent audiovisual review requires actual source/output
  access and named tools. Human listening remains required for final audio QA.

## Consistent review procedure
1. Watch the source context and rendered clip at native speed. Inspect a phone
   preview, keyframes and relevant audio at low/normal volume.
2. Score applicable dimensions using the same anchors. Cite the actual source
   and output artifact/time; distinguish source defects from editing defects.
3. Record each issue as “at time X, observed Y; change Z; recheck by W.” Example:
   “At output 3.2 s, emphasis reveals the answer before the voice; move the
   emphasis to the mapped word onset and replay the full exchange.”
4. If reviewers differ by two or more points, compare the cited interval and
   record disagreement as REVIEW until reconciled. Keep individual scores;
   do not hide disagreements in a mean.
5. Re-render affected beats and recheck timing/audio/captions around boundaries.
   Mark a revision resolved only with recheck evidence.
6. Report technical QA, editorial QA, human review and automated checks as
   separate results. A high score cannot override an integrity failure.

Keep the original eight gates in [evals](../../evals/cases.md). Missing real
footage leaves footage-dependent gates NOT_RUN. A synthetic timing test can
pass while humor, naturalness and actual speaker correctness remain untested.
