# Editorial intelligence upgrade

## Baseline and audit scope

Audit base: `82ced39b89452e36ca4e06ee520af1c50300d561` on `main`.
Read all 22 tracked files before editing. No source footage, rendered clips,
media fixtures, CI workflow, or executable render engine existed at this base.
The baseline structural validator passed for all 11 skills.

| Files inspected | Keep | Change and reason |
|---|---|---|
| README.md, AGENT_OPERATING_CONTRACT.md | Entry points, evidence/status vocabulary | Add capability-aware workflow and one decision owner; remove conflicting ZIP exception |
| clip-router/SKILL.md | Evidence-based routes and minimum skill selection | Add editorial handoffs and mixed-content precedence |
| vtuber-conversation-clip/SKILL.md | Speaker-follow camera and continuous shared shots | Scope sample-specific visual choices; add decision records |
| vtuber-conversation-clip/references/style-reference.md | All historical observations and camera constraints | Link reusable style analysis without turning sample values into defaults |
| vtuber-conversation-clip/references/render-workflow.md | Portable source-free production workflow | Clarify tested-build limits and event-based SFX |
| vtuber-gameplay-facecam-clip/SKILL.md | HUD, cause/result, horror silence | Add composition priorities and action/reaction decisions |
| vtuber-collab-reaction-clip/SKILL.md | Speaker uncertainty and reaction chains | Add overlap hierarchy and camera handoff |
| transcript-and-speaker-pipeline/SKILL.md | Raw ASR, word timing, speaker ledger | Add auditable direct-audio review with human escalation |
| caption-design/SKILL.md | Verbatim integrity and safe zones | Add phrase/word timing, restrained animation and multilingual hierarchy |
| hook-pacing-retention/SKILL.md | Discovery and 0–12 candidate score | Use causal/context evidence; keep ranking separate from editorial QA |
| audio-mix-and-sfx/SKILL.md | Voice priority, measured loudness, human listening | Add silence, music and event-linked SFX decisions |
| ffmpeg-vertical-quality/SKILL.md | Crop/encode guidance | Resolve generic layout advice against conversation rules; add motion execution contract |
| render-package-for-user/SKILL.md | No source media in ZIP; portable paths | Add reproducibility and test-status manifest |
| qa-and-self-review/SKILL.md | Technical checks and honest status | Add anchored editorial rubric and separate review modes |
| schemas/edit-plan.schema.json, schemas/transcript.schema.json | Existing fields and unversioned examples | Add opt-in v2 structures plus semantic validation |
| examples/edit-plan.example.json, examples/transcript.example.json | Original legacy examples unchanged | Add new explicitly synthetic v2 examples alongside them |
| evals/README.md, evals/cases.md | Eight original gates | Add twelve editorial scenarios and repeatable evidence rules |
| scripts/validate_skill_repo.py | Entry command and legacy skill sections | Check schema validity, examples, links and integration; add behavioral regression tests |

## Gaps and implementation plan

1. Centralize contextual reasoning in one `editorial-intelligence` skill. Keep
   discovery in hook-pacing-retention and execution in existing specialists.
2. Add evidence, narrative beats, simpler alternatives, motion/effect intent,
   output timing and verification receipts without rejecting legacy v1 data.
3. Add executable schema and semantic checks. Reject impossible ranges,
   dangling IDs, unsupported verification claims and unsafe final captions.
4. Teach specialists to consume the same decision records. Use style profiles
   as scoped preferences, never as replacement source evidence.
5. Define ten editorial dimensions with observable 0–4 anchors. Keep automated
   checks, audiovisual agent review and human judgment separate.
6. Run negative regression tests, legacy compatibility tests and a synthetic
   FFmpeg smoke test. Mark real-footage evaluations NOT_RUN until footage exists.
7. Review consistency and publish changes on a development branch for review.

## Architecture boundaries

The new skill owns **why and when**. Specialist skills own **how**. Validators
check representational consistency; they cannot determine whether a joke works.
FFmpeg executes explicit instructions; it does not infer emotion, identify
speakers or choose story beats. No automatic audiovisual model is bundled.

## Verification results

Local run: 2026-11-09. See [machine-readable results](../evals/implementation-results.json).

| Check executed | Result | Scope |
|---|---|---|
| Baseline validator | PASS | Original 11 skill structures |
| Upgraded repository validator | PASS | 12 skills, five schemas, six examples and local Markdown links |
| `python -m unittest discover -s tests -q` | PASS | 55 tests, including invalid inputs and legacy fixture hashes |
| `python -m compileall -q scripts tests` | PASS | Python source compilation |
| `git diff --check` | PASS | Whitespace/patch consistency |
| `python scripts/smoke_ffmpeg.py --output-dir test-results/smoke` | PASS | Ten synthetic technical checks on FFmpeg 7.1.5, Linux |
| Synthetic preview inspection | PASS, narrow scope | One 180×320 output frame inspected; ASS label readable |
| [Fresh-agent forward tests](../evals/forward-tests.md) | PASS, text-only scope | Two planning responses respected evidence/capability limits |
| GitHub Actions, push and PR runs | PASS | Remote logs confirm validator, 55 tests and ten smoke checks on Python 3.11.18 / FFmpeg 6.1.1 |
| Gates 1–8 on actual fixtures | NOT_RUN | No real footage/delivery fixture supplied |
| E01–E12 audiovisual editorial assessment | NOT_RUN | No source/render/reference review available |
| Human listening, Windows and Colab execution | NOT_RUN | Those environments/reviewers were not exercised |

The first regression run found that JSON Schema date-time validation depended
on an unavailable optional format checker. A receipt time such as “yesterday”
was accepted. The validator now checks the timestamp explicitly, and the
regression passes. No failed run was relabeled as successful.

The synthetic smoke test generated its own source, rendered a linear crop pan
and ASS captions through an extracted Bash package with spaced paths, checked
codec/dimensions/frame count/audio/timestamps, decoded the full output and
verified a source-free allowlisted ZIP. It did not listen to the tone or judge
editing quality. The generated test media stays outside the tracked repository.

## Implemented changes and decision impact

| Before | After | Practical effect |
|---|---|---|
| A shot had a general `reason` string | Intent, beat, emotional context, focus, camera/effect choice, timing rationale, intensity, evidence, confidence and alternative | An agent must explain what a treatment contributes and compare a simpler option |
| Candidate scoring could proceed without a shared context record | Context brief and causal dependencies feed discovery and specialist work | A quiet complete story can outrank a loud contextless reaction |
| Generic vertical layout advice could conflict with conversation rules | Route-specific constraints govern rendering; explicit override required for restricted conversation layouts | Speaker-follow survives the transition from editorial plan to production |
| The reference's 30 fps could be read as a universal conversation default | Source frame rate governs; changes need a project reason | Sample-specific encoding no longer conflicts with the FFmpeg skill |
| ASR policy allowed only human verification but did not model review evidence | Default human policy remains; optional direct-audio policy requires an auditable receipt and actual audio access | Capable agents can verify directly without pretending that ASR confidence equals listening |
| Source and output clocks were ambiguous after retiming | Explicit output clock and contiguous play/freeze time maps, linked word IDs | Validator catches caption drift caused by removed words or incorrect time mappings |
| Validator checked headings and frontmatter only | Schema and semantic checks reject broken IDs, crops, attribution claims, text changes, incomplete reviews and inconsistent timelines | Invalid plans fail before they become render instructions |
| QA mostly listed technical checks | Ten anchored editorial dimensions, reviewer modes and repair/recheck records | Weak timing or excessive decoration requires a concrete revision rather than a successful encode |
| Eight short evaluation gates | Eight preserved gates plus twelve structured editorial scenarios and two text-only forward tests | Future changes can be assessed with the same evidence and failure criteria |

### Concrete example (invented, not a tested source clip)
Given a claim, pause, clarification and laugh, a poorly specified plan could
trim the pause, add periodic zooms and show all avatars permanently. The v2
plan records the pause's possible narrative role, keeps speaker-follow solo
shots, permits a shared shot only for actual shared interaction, and chooses
no added sound when the reaction communicates the beat. Captions remain raw
until source verification. These are stronger decision requirements, not proof
that the unobserved joke is funny.

## Skill and file inventory
All 11 existing skills were updated in place. Exactly one skill was added:
`editorial-intelligence`, with three references for decisions, motion/effects
and style profiles. No existing skill or legacy example was removed.

Updated files: both repository entry documents; all 11 existing `SKILL.md`
files; the two conversation reference documents; both existing schemas;
`evals/README.md`, `evals/cases.md`; and `scripts/validate_skill_repo.py`.

Added files:
- `editorial-intelligence/SKILL.md` and its three reference documents.
- `schemas/common.schema.json`, `schemas/style-profile.schema.json`,
  `schemas/editorial-review.schema.json`, `schemas/README.md`.
- Four v2/style/review example JSON files alongside unchanged legacy examples.
- `scripts/validate_artifacts.py`, `scripts/smoke_ffmpeg.py`, `tests/test_validation.py`.
- `qa-and-self-review/references/editorial-rubric.md`.
- `evals/forward-tests.md`, `evals/implementation-results.json`, this report.
- `requirements-dev.txt`, `.gitignore`, `.github/workflows/validate.yml`.

The edit-plan and transcript changes are additive and versioned. Existing
unversioned/1.0 examples still validate as drafts. Version 2.0 is required for
the stronger final-readiness checks. Style and review schemas are version 1.0.
Shared definitions prevent duplicated verification/evidence rules.

## Remaining limits and publication
This repository is an agent skill system with executable validation and a
synthetic production smoke test. It does not bundle an audiovisual model, ASR,
tracker, automatic EDL compiler or generic renderer. It does not authenticate
evidence receipts, source annotations or asset licenses. Perceptual timing,
humor, composition and comfort still require actual source/output review.

The time-map validator supports chronological, contiguous piecewise play/freeze
mapping. It deliberately rejects unexplained reordered/overlapping source shots;
a nonlinear retrospective montage needs an explicit future contract. The
smoke render tests 180×320 synthetic content, not full-resolution VTuber quality.

Development branch: `feat/editorial-intelligence-v2`. The base remains
`82ced39b89452e36ca4e06ee520af1c50300d561`. Implementation commit:
`d08b9fb264d8e5195434104d6fc9a0cfa0505528`. Changes are published in
[draft PR #1](https://github.com/lightevil96-svg/Skills-Clip/pull/1), without
replacing or merging `main`. The remote tree matched the locally validated
tree exactly. [PR CI](https://github.com/lightevil96-svg/Skills-Clip/actions/runs/42627889295)
and [push CI](https://github.com/lightevil96-svg/Skills-Clip/actions/runs/42627801870)
both completed successfully for the implementation commit. This report update
records those completed runs; it does not infer results for future commits.
