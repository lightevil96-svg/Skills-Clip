# Expressive Sound Design Protocol

## The principle: sync the accent to the meaning
A sound effect should reinforce a real source event or a clearly editorial emphasis. It must not fabricate a physical action, emotion, result, or off-screen reaction. The clean version with no SFX is the control condition; keep an effect only when the treated version improves clarity, timing, or emotional readability.

## Event decision matrix

| Source observation | Event trigger | Preferred treatment | Avoid |
|---|---|---|---|
| A verified key word changes the meaning or punchline | `word-emphasis` | Quiet soft-pop or tick, one per phrase | A pop on every subtitle token |
| Camera begins a purposeful move | `motion` | Short whoosh aligned to movement onset | Repeated whoosh on idle motion |
| A visible action reaches a clear endpoint | `impact` | Restrained impact at the endpoint | Sounding like an unobserved collision |
| A source-supported comic response occurs | `reaction` | Short boing or sparkle after reaction onset | Assigning comedy to an ambiguous face |
| The story changes scene or idea at a cut | `transition` | Short swish if the cut needs continuity | SFX on every edit point |
| A pause builds anticipation | none | Preserve the pause | Filling silence with a riser by default |

## Timing policy
- Store all event `at_s` values in the rendered output clock.
- Link each event to one or more evidence IDs from the edit plan.
- For word emphasis, also link `word_ids`; use the mapped onset of the first linked word. The renderer rejects events more than 200 ms away from that onset.
- For motion, link verified visual-inspection evidence and place the event within the corresponding motion shot.
- For transition, align the event within 120 ms of a real shot boundary.
- Preserve the original dialogue and causal order. Never move an SFX to imply a different cause.

## Density and mix
- Conversation starting point: 1–3 accents per 10 seconds, usually no more than one per phrase.
- Maximum two simultaneous SFX events in the bounded renderer.
- Keep most accents between -24 and -16 dB gain as a starting point. The correct level depends on the actual asset and source mix.
- Duck SFX under source audio using sidechain compression. The current implementation keys from the complete source mix, not isolated dialogue.
- Apply a conservative peak limiter after mixing. Do not claim loudness compliance without measuring and listening.

## Starter sound palette
The procedural pack provides soft-pop, word-tick, whoosh-short, soft-impact, sparkle, and boing-soft. These are intentionally simple synthesized accents, not realistic Foley or a universal style. Preview each asset, replace it when unsuitable, and keep asset metadata and SHA-256 in the audio design plan.

## Required audio-design.json shape
The separate `audio-design.json` uses `schemas/audio-design.schema.json`. Asset paths are relative to that file's directory and may not escape it. Every asset includes a SHA-256, source and license. Events are sorted by output `at_s`, carry evidence IDs and a reason, and are limited to 60 events and two simultaneous events. Word-emphasis events require a verified word-level transcript. Motion events require verified visual evidence and a motion camera decision. Transition events must align to a shot boundary.

## Preview and stop conditions
Render the ordinary EDL first, then run `scripts/render_audio_events.py`. The result is a technical preview, not final approval. Stop and revise if dialogue becomes harder to understand, an effect implies an unsupported event, the timing masks a consonant or reaction, the effect palette becomes repetitive, or the mix is uncomfortable on a phone speaker. Human listening remains mandatory.

