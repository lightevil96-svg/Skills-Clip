#!/usr/bin/env python3
"""Generate a small original, royalty-free-style procedural SFX pack.

No third-party recordings or samples are used. The generated WAVs are mono PCM
and intended as restrained editorial accents, not realistic Foley.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import wave

SAMPLE_RATE = 48_000
SOUNDS = ('soft-pop', 'word-tick', 'whoosh-short', 'soft-impact', 'sparkle', 'boing-soft')


def _env(t: float, duration: float, attack: float = 0.004, release: float = 0.06) -> float:
    if t < 0 or t >= duration:
        return 0.0
    a = min(1.0, t / max(attack, 1e-6))
    r = min(1.0, (duration - t) / max(release, 1e-6))
    return max(0.0, min(a, r))


def _synthesize(name: str, sample_rate: int = SAMPLE_RATE) -> list[float]:
    durations = {
        'soft-pop': 0.15, 'word-tick': 0.075, 'whoosh-short': 0.42,
        'soft-impact': 0.24, 'sparkle': 0.58, 'boing-soft': 0.34,
    }
    if name not in durations:
        raise ValueError(f'Unknown sound: {name}')
    duration = durations[name]
    count = round(duration * sample_rate)
    rng = random.Random(20261113 + SOUNDS.index(name))
    samples: list[float] = []
    low_noise = 0.0
    for i in range(count):
        t = i / sample_rate
        p = t / duration
        noise = rng.uniform(-1.0, 1.0)
        if name == 'soft-pop':
            freq = 980.0 * (0.52 ** p)
            value = math.sin(2 * math.pi * freq * t) * math.exp(-10.5 * p) * 0.52
            value += noise * math.exp(-55 * p) * 0.035
        elif name == 'word-tick':
            freq = 2_100.0 - 550.0 * p
            value = math.sin(2 * math.pi * freq * t) * math.exp(-36 * p) * 0.30
            value += noise * math.exp(-95 * p) * 0.18
        elif name == 'whoosh-short':
            # Smoothly shaped, low-passed noise creates a short air movement.
            low_noise += (0.13 + 0.22 * p) * (noise - low_noise)
            swell = math.sin(math.pi * p) ** 1.35
            value = low_noise * swell * 0.82
            value += math.sin(2 * math.pi * (105 + 180 * p) * t) * swell * 0.08
        elif name == 'soft-impact':
            freq = 118.0 * (0.48 ** p)
            thump = math.sin(2 * math.pi * freq * t) * math.exp(-13 * p) * 0.72
            click = noise * math.exp(-65 * p) * 0.12
            value = thump + click
        elif name == 'sparkle':
            value = 0.0
            for offset, freq, amp in ((0.00, 1_620, 0.20), (0.09, 2_180, 0.16), (0.20, 2_760, 0.12), (0.31, 3_220, 0.08)):
                local = t - offset
                if local >= 0:
                    value += math.sin(2 * math.pi * freq * local) * math.exp(-9.0 * local) * amp
            value += noise * math.exp(-22 * p) * 0.012
        else:  # boing-soft
            freq = 690.0 * (0.27 ** p)
            value = math.sin(2 * math.pi * freq * t) * math.exp(-7.0 * p) * 0.55
            value += math.sin(2 * math.pi * (freq * 0.5) * t) * math.exp(-10 * p) * 0.12
        samples.append(value)
    peak = max((abs(x) for x in samples), default=1.0)
    scale = 0.72 / max(peak, 1e-9)
    return [max(-0.95, min(0.95, x * scale)) for x in samples]


def _write_wav(path: Path, samples: list[float], sample_rate: int = SAMPLE_RATE) -> None:
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(struct.pack('<h', round(x * 32767)) for x in samples))


def generate_pack(output_dir: str | Path) -> dict:
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=False)
    assets = []
    for name in SOUNDS:
        path = root / f'{name}.wav'
        _write_wav(path, _synthesize(name))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assets.append({
            'id': name,
            'path': path.name,
            'source': 'Skills-Clip procedural SFX generator; original synthesized waveform; no third-party samples',
            'license': 'Original procedural asset; no third-party sample or attribution dependency',
            'sha256': digest,
            'duration_s': round(len(_synthesize(name)) / SAMPLE_RATE, 3),
        })
    manifest = {
        'format': 'skills-clip-procedural-sfx-v1',
        'sample_rate': SAMPLE_RATE,
        'channels': 1,
        'assets': assets,
        'note': 'Generated WAVs are intentionally simple editorial accents. Preview and mix to taste.',
    }
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('work/audio-assets'))
    args = parser.parse_args()
    try:
        result = generate_pack(args.output_dir)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f'PASS: generated {len(result["assets"])} original SFX in {args.output_dir}')
    print('Review each sound and keep only assets that fit the source and style.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

