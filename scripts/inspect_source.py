#!/usr/bin/env python3
"""Create bounded, private source excerpts for actual audiovisual inspection."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

from media_tools import new_directory, probe, run, sha256, source_record, write_json


def inspect(source, output_dir, *, start, end, frames=5):
    data = probe(source)
    record = source_record(source, data)
    if not all(math.isfinite(t) for t in (start, end)) or not 0 <= start < end <= record['duration_s']:
        raise ValueError('Inspection interval must lie inside the source')
    if end-start > 120 or not 1 <= frames <= 12:
        raise ValueError('Inspect at most 120 seconds and 1–12 frames per bundle; use more bundles for a long VOD')
    output = new_directory(output_dir)
    write_json(output/'source-probe.json', data)
    artifacts = []
    for index in range(frames):
        # Midpoints avoid asking for a frame past end-of-file. These are requested
        # seek times, NOT claims that an exact source presentation time was measured.
        at = start + (index + .5) * (end-start) / frames
        name = f'frame-{index+1:02}.png'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-i', Path(source).resolve(),
             '-ss', str(at), '-map', '0:v:0', '-frames:v', '1', output/name])
        artifacts.append({'path': name, 'sha256': sha256(output/name), 'kind': 'sampled-frame',
                          'requested_source_time_s': at, 'review_status': 'NOT_RUN'})
    if record['audio_present']:
        name = 'review-audio.wav'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-i', Path(source).resolve(),
             '-ss', str(start), '-t', str(end-start), '-map', '0:a:0', '-vn',
             '-ar', '48000', '-c:a', 'pcm_s16le', output/name])
        artifacts.append({'path': name, 'sha256': sha256(output/name), 'kind': 'source-audio-excerpt',
                          'source_in_s': start, 'source_out_s': end, 'review_status': 'NOT_RUN'})
    manifest = {'format': 'skills-clip-inspection-v1', 'source': record,
                'source_in_s': start, 'source_out_s': end, 'artifacts': artifacts,
                'generation_status': 'PASS', 'semantic_review': 'NOT_RUN',
                'warning': 'Private source derivatives. Keep outside delivery ZIP. Sampling can miss reactions.'}
    write_json(output/'manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--start', type=float, required=True)
    parser.add_argument('--end', type=float, required=True)
    parser.add_argument('--frames', type=int, default=5)
    args = parser.parse_args()
    try:
        result = inspect(args.source, args.output_dir, start=args.start, end=args.end, frames=args.frames)
        print(f'PASS: generated {len(result["artifacts"])} inspection artifacts; semantic review NOT_RUN')
        return 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
