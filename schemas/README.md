# Artifact schemas and migration

All schemas use JSON Schema draft 2020-12. The `.example` schema identifiers
are offline registry keys, not URLs to download. The validator resolves only
the checked-in schemas. Install developer dependencies with
`python -m pip install -r requirements-dev.txt`.

| Artifact | Version | Purpose |
|---|---|---|
| edit-plan | absent/1.0 | Existing fields remain accepted; draft compatibility |
| edit-plan | 2.0 | Decisions, evidence, explicit output clock and retiming |
| transcript | absent/1.0 | Existing word data and human-listen policy remain valid |
| transcript | 2.0 | Word IDs, language, source clock and verification receipts |
| style-profile | 1.0 | Scoped reference observations and adaptations |
| editorial-review | 1.0 | Ten scored dimensions, evidence and separate human/technical review |
| audio-design | 1.0 | Separate output-clock SFX events, evidence/word links, licensed asset hashes and voice-priority mix |
| common | definitions | Shared evidence, receipt, crop and status types |

## Clocks and IDs
- All times are seconds. Ranges are half-open `[start, end)`; evidence may mark
  one instant. Clip `in_s/out_s` bounds the source envelope, not output duration.
- Shot `in_s/out_s`, transcript word `start/end`, receipts, narrative beats and
  evidence use original source time. Compensate extraction/stream offsets.
- Shot `output_in_s/output_out_s`, captions, effects and keyframe `at_s` use
  output time starting at zero. Shots tile the output without gaps or overlaps.
- `audio-design.json` is a separate artifact. Its event `at_s` and `duration_s`
  use the final rendered output clock, not source time. Each event references
  edit-plan evidence; word-emphasis additionally references verified transcript
  word IDs. Asset paths are relative to the audio-design file and SHA-256 checked.
- Without a time_map, shot duration must equal source duration. A time_map is
  contiguous piecewise linear play segments or explicit single-instant freezes.
  Ramps require multiple pieces. It describes timing, not an implemented filter.
- Caption `word_ids` point to transcript words. `caption_ids` link shots to
  caption records. `overlay_ids` point to assets; effect `asset_id` is null for
  procedural effects or an existing asset ID. Decisions reference beat/evidence
  IDs. Speaker IDs remain provisional until mapping evidence supports them.
- Source chronology stays monotonic. A nonlinear retrospective montage needs
  an explicitly extended mapping contract; this validator does not silently
  approve reordering that could falsify reactions.
- Final plans include a `render` record with output_path, output_sha256,
  ffmpeg_version, command_ref and probe_ref. The separate review must identify
  that output path. Hash/receipt declarations still require checking real files.
- Verified speaker mappings need evidence IDs in the plan and mapping_evidence
  references in the transcript. Word verification does not identify an avatar.

## Migration
Keep original v1 files when needed. Add schema_version 2.0, content_kind,
source-aware editorial evidence and beats, then per-shot editorial decisions
and output times. Add word IDs/language/receipts to the transcript, and link
caption kinds/word IDs/animation/position to that transcript. Recheck mappings
after any speed change. Populate real observations; never copy fixture receipts.

The default transcript policy remains human-listen-required. Under the explicit
source-audio-review policy, direct-audio-review requires actual audio access,
reviewer/tool/time, source interval, language, context and no unresolved
uncertainty. ASR and forced alignment alone cannot produce VERIFIED.

## Commands
```bash
python scripts/validate_skill_repo.py
python scripts/validate_artifacts.py edit-plan examples/edit-plan.editorial.example.json --transcript examples/transcript.editorial.example.json
python scripts/validate_artifacts.py transcript examples/transcript.example.json
python scripts/validate_artifacts.py style-profile examples/style-profile.example.json
python scripts/validate_artifacts.py editorial-review examples/editorial-review.example.json
python scripts/validate_artifacts.py edit-plan PLAN.json --transcript WORDS.json --review REVIEW.json --style STYLE.json --stage final
```

`--style` is needed only when a profile is referenced. Final checks require real
provenance, resolved evidence, verified linked words, reviewed positioning and
a completed editorial/human review. The checks validate declarations; they
cannot authenticate receipts, inspect source content, confirm asset licenses,
detect all occlusions or prove aesthetic quality. Review the real artifacts.

Legacy examples remain unchanged and valid as drafts. Draft PASS means schema
and semantic consistency only. New examples are synthetic with NOT_RUN QA and
raw/unverified words. They must fail final readiness checks. Test-created
verification receipts are synthetic test data, never evidence of real review.

## Optional ASR import ledger

`transcript.unresolved_words` retains raw words or segments with missing alignment or a segment/word-list mismatch. Each entry has text, raw_location and reason. A final transcript must resolve these entries. `import_provenance` records the raw SHA-256, source offset, source association (`DECLARED` for imports or `LOCAL_RUN`) and engine execution status. These are additive fields; legacy artifacts remain valid. An executed engine still produces ASR_RAW, not verified dialogue. See the [production tools](../docs/production-tools.md).
