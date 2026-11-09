# Camera, motion and expressive treatment

Use source-space pixel crops and output-time keyframes. Inspect endpoints AND
intermediate frames; an in-bounds crop can still hide a mouth or HUD. These are
decision recipes, not a bundled render engine or an automatic tracker.

| Treatment | Editorial trigger | Timing and fallback |
|---|---|---|
| Hold / direct cut | Focus already clear / speaker changes | Preserve useful reaction; prefer stable composition |
| Punch-in / punch-out | Word, expression or revealed context needs emphasis | Start at the actual beat; return when context becomes relevant |
| Smooth zoom | Attention narrows gradually | Keyframe position and size; avoid continuous motion during reading |
| Pan / reframing | Relevant subject moves or turn changes | Choose a cut if travel exposes irrelevant space or delays the speaker |
| Tracking | Moving target must stay readable | Require observed landmarks or available tracker with checked output; fall back to wider crop |
| Reaction close-up | Visible reaction adds information | Preserve trigger and onset; do not imply an unrelated reaction |
| Shared shot | Concurrent exchange/reaction matters | One continuous composition for conversation; return to active solo |
| Contextual transition | Actual change of place/time/idea | Direct cut unless continuity benefits; do not apply on a schedule |
| Flash / impact | Strong observed beat benefits from accent | Keep brief; compare without it; avoid repeated high-contrast flashes |
| Motion blur | Fast authored motion needs continuity | Confine to movement; never blur subtitles/HUD or disguise bad timing |
| Freeze frame | Viewer needs time to inspect a real result | Label deliberate freeze when ambiguity exists; keep explicit time map |
| Speed ramp | Compress nonessential travel or inspect action | Map source to output; preserve event order and voice intelligibility |
| Overlay / sticker | Supports a specific expression or idea | Anchor away from face/HUD; exit when the beat ends |
| Meme insert | Shared context makes the association understandable | Document relevance and asset rights; omit if it explains a joke poorly |
| Background treatment | Vertical fit needs context or separation | Keep source evidence legible; do not duplicate conversation panels |

## Motion execution contract
For each motion, record keyframes `(at_s, crop, easing)` with absolute output
seconds and full source-pixel crop rectangles. `linear`, `ease-in`, `ease-out`
and `ease-in-out` describe interpolation intent, not FFmpeg option names.
An executor must implement the curve, record its expression/tool version and
preview it. Do not paste an easing label into an unsupported filter parameter.

Use a stable crop if motion cannot be implemented or inspected. Detecting a
face automatically does not identify the active speaker. Do not infer smooth
tracking from a single still. Keep enlargement within acceptable source detail.

For freezes and ramps, supply piecewise `time_map` entries: `play` maps a
positive source interval linearly to a positive output interval; `freeze` maps
one source instant to a positive output interval. A ramp is an approximation
with multiple play pieces, not an implied magic command. The executor must
also specify treatment of dialogue, ambience and captions. Recheck every mapped
word onset after retiming. Preserve synchronized dialogue at normal speed unless
an explicit creative decision and listening review support the change.

## Visual hierarchy review
Conversation: active face/expression → important dialogue → referenced object
→ graphic. Competitive play: action/target/result HUD → avatar reaction →
dialogue → decoration. Collab: relevant speaker pair/chain → readable attributed
dialogue → group context. Change the hierarchy at a beat boundary only when
the source supports the change. Review a phone-sized preview and full-size HUD.
