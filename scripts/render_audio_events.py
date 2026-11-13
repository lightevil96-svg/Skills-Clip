#!/usr/bin/env python3
"""Mix evidence-linked SFX events over an already rendered Skills-Clip preview.

This is a bounded post-render audio pass. It does not generate editorial choices,
verify dialogue, isolate voice stems, or replace human listening QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
from media_tools import confined_file, new_directory, probe, run, sha256, write_json
from validate_artifacts import VERIFIED, load_json

REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_EVENTS = 60
MAX_SIMULTANEOUS = 2


def _number(value, label, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number')
    if minimum is not None and value < minimum:
        raise ValueError(f'{label} must be >= {minimum}')
    if maximum is not None and value > maximum:
        raise ValueError(f'{label} must be <= {maximum}')
    return float(value)


def _video_info(path: Path):
    data = probe(path)
    videos = [s for s in data['streams'] if s['codec_type'] == 'video']
    audios = [s for s in data['streams'] if s['codec_type'] == 'audio']
    if len(videos) != 1 or len(audios) > 1:
        raise ValueError('Input preview must contain exactly one video and at most one audio stream')
    return data, videos[0], (audios[0] if audios else None)


def _map_word_to_output(plan: dict, word: dict):
    start, end = float(word['start']), float(word['end'])
    mapped = []
    for shot in plan['shots']:
        segments = shot.get('time_map') or [{
            'kind': 'play', 'source_in_s': shot['in_s'], 'source_out_s': shot['out_s'],
            'output_in_s': shot['output_in_s'], 'output_out_s': shot['output_out_s'],
        }]
        for seg in segments:
            if seg['kind'] != 'play':
                continue
            left = max(start, float(seg['source_in_s']))
            right = min(end, float(seg['source_out_s']))
            if right <= left:
                continue
            ratio = ((float(seg['output_out_s']) - float(seg['output_in_s'])) /
                     (float(seg['source_out_s']) - float(seg['source_in_s'])))
            mapped.append((float(seg['output_in_s']) + (left - float(seg['source_in_s'])) * ratio,
                           float(seg['output_in_s']) + (right - float(seg['source_in_s'])) * ratio))
    covered = sum(right - left for left, right in mapped)
    if not mapped or covered + 0.001 < end - start:
        return None
    return min(x[0] for x in mapped), max(x[1] for x in mapped)


def validate_audio_plan(audio_plan: dict, edit_plan: dict, *, transcript: dict | None = None, asset_root: Path | None = None):
    schema_path = REPO_ROOT / 'schemas' / 'audio-design.schema.json'
    schema = load_json(schema_path)
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(audio_plan),
                           key=lambda error: list(map(str, error.absolute_path)))
    if schema_errors:
        error = schema_errors[0]
        location = '.'.join(map(str, error.absolute_path)) or '$'
        raise ValueError(f'Audio design schema: {location}: {error.message}')
    source_hash = edit_plan.get('source', {}).get('sha256')
    if not source_hash or audio_plan.get('source_sha256') != source_hash:
        raise ValueError('Audio design source_sha256 must match the edit plan')
    if not edit_plan.get('shots'):
        raise ValueError('Edit plan has no output shots')
    output_duration = float(edit_plan['shots'][-1]['output_out_s'])
    declared_duration = _number(audio_plan.get('output_duration_s'), 'output_duration_s', 0.001)
    if abs(output_duration - declared_duration) > 0.05:
        raise ValueError('Audio design output_duration_s does not match the edit plan')

    assets = audio_plan.get('assets', [])
    asset_root = Path(asset_root or '.').resolve()
    events = audio_plan.get('events', [])
    if len(events) > MAX_EVENTS:
        raise ValueError(f'Audio design is limited to {MAX_EVENTS} SFX events')
    asset_map = {}
    for asset in assets:
        asset_id = asset.get('id')
        if not isinstance(asset_id, str) or not asset_id or asset_id in asset_map:
            raise ValueError('Audio asset IDs must be unique non-empty strings')
        if not asset.get('path') or not asset.get('source') or not asset.get('license'):
            raise ValueError(f'{asset_id}: path, source and license are required')
        if not isinstance(asset.get('sha256'), str) or len(asset['sha256']) != 64:
            raise ValueError(f'{asset_id}: SHA-256 is required')
        asset_map[asset_id] = asset

    evidence = {e['id']: e for e in edit_plan.get('editorial', {}).get('evidence', [])}
    word_map = {}
    if transcript is not None:
        if transcript.get('source_sha256') != source_hash:
            raise ValueError('Transcript source_sha256 does not match the edit plan')
        word_map = {w['id']: w for w in transcript.get('words', []) if 'id' in w}

    ordered = sorted(events, key=lambda e: float(e.get('at_s', -1)))
    if events != ordered:
        raise ValueError('Audio events must be sorted by at_s for reproducible review')
    intervals = []
    seen = set()
    resolved_assets = {}
    for event in events:
        event_id = event.get('id')
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            raise ValueError('SFX event IDs must be unique non-empty strings')
        seen.add(event_id)
        trigger = event.get('trigger')
        if trigger not in {'motion', 'word-emphasis', 'reaction', 'transition', 'impact', 'other'}:
            raise ValueError(f'{event_id}: unsupported trigger')
        at = _number(event.get('at_s'), f'{event_id}.at_s', 0, declared_duration)
        duration = _number(event.get('duration_s'), f'{event_id}.duration_s', 0.02, 3.0)
        if at + duration > declared_duration + 0.001:
            raise ValueError(f'{event_id}: event extends beyond output duration')
        gain = _number(event.get('gain_db'), f'{event_id}.gain_db', -36, -6)
        fade_in = _number(event.get('fade_in_s', 0), f'{event_id}.fade_in_s', 0, duration)
        fade_out = _number(event.get('fade_out_s', 0), f'{event_id}.fade_out_s', 0, duration)
        if fade_in + fade_out > duration:
            raise ValueError(f'{event_id}: fade durations exceed event duration')
        asset_id = event.get('asset_id')
        if asset_id not in asset_map:
            raise ValueError(f'{event_id}: unknown asset_id {asset_id!r}')
        evidence_ids = event.get('evidence_ids', [])
        if not evidence_ids or any(eid not in evidence for eid in evidence_ids):
            raise ValueError(f'{event_id}: evidence_ids must reference edit-plan evidence')
        for eid in evidence_ids:
            if evidence[eid].get('status') not in VERIFIED:
                raise ValueError(f'{event_id}: source evidence {eid} is not verified')

        if trigger == 'word-emphasis':
            ids = event.get('word_ids', [])
            if not ids or transcript is None:
                raise ValueError(f'{event_id}: word-emphasis requires transcript and word_ids')
            words = [word_map.get(wid) for wid in ids]
            if any(word is None for word in words):
                raise ValueError(f'{event_id}: word_ids do not all exist in transcript')
            if any(word.get('verification_status') not in VERIFIED for word in words):
                raise ValueError(f'{event_id}: word-emphasis requires verified words')
            mapped = _map_word_to_output(edit_plan, words[0])
            if mapped is None or abs(at - mapped[0]) > 0.20:
                raise ValueError(f'{event_id}: SFX must align within 200 ms of the first linked word onset')

        if trigger == 'motion':
            matching = [shot for shot in edit_plan['shots']
                        if shot['output_in_s'] - 0.05 <= at <= shot['output_out_s'] + 0.05]
            if not matching or not any(shot['editorial']['camera']['action'] in
                                       {'pan', 'track', 'punch-in', 'punch-out', 'reaction-close-up'}
                                       for shot in matching):
                raise ValueError(f'{event_id}: motion SFX needs a matching motion camera decision')
            if any(evidence[eid].get('method') != 'visual-inspection' for eid in evidence_ids):
                raise ValueError(f'{event_id}: motion SFX requires visual-inspection evidence')

        if trigger == 'transition':
            boundaries = [float(shot['output_in_s']) for shot in edit_plan['shots'][1:]]
            if not boundaries or min(abs(at - boundary) for boundary in boundaries) > 0.12:
                raise ValueError(f'{event_id}: transition SFX must align within 120 ms of a shot boundary')

        asset = asset_map[asset_id]
        if asset_id not in resolved_assets:
            resolved = confined_file(asset_root, asset['path'])
            if sha256(resolved) != asset['sha256']:
                raise ValueError(f'{asset_id}: asset SHA-256 mismatch')
            data = probe(resolved)
            if not any(s['codec_type'] == 'audio' for s in data['streams']):
                raise ValueError(f'{asset_id}: asset has no audio stream')
            asset_duration = float(data['format'].get('duration', 0))
            if asset_duration + 0.01 < duration:
                raise ValueError(f'{asset_id}: audio asset is shorter than event duration')
            resolved_assets[asset_id] = resolved
        intervals.append((at, at + duration, event_id))
        event['_resolved_asset'] = str(resolved_assets[asset_id])
        event['_gain_db'] = gain
        event['_fade_in_s'] = fade_in
        event['_fade_out_s'] = fade_out

    # Limit simultaneous accents. Dense sound beds belong in a separately reviewed mix.
    for at, end, event_id in intervals:
        simultaneous = sum(1 for other_at, other_end, _ in intervals
                           if other_at < end and other_end > at)
        if simultaneous > MAX_SIMULTANEOUS:
            raise ValueError(f'{event_id}: more than {MAX_SIMULTANEOUS} simultaneous SFX events')
    mix = audio_plan.get('mix', {})
    if mix.get('voice_priority') is not True:
        raise ValueError('voice_priority must remain true')
    duck = mix.get('ducking', {})
    if not isinstance(duck, dict):
        raise ValueError('mix.ducking must be an object')
    _number(duck.get('threshold_db', -30), 'ducking.threshold_db', -48, -12)
    _number(duck.get('ratio', 2.5), 'ducking.ratio', 1, 8)
    _number(duck.get('attack_ms', 10), 'ducking.attack_ms', 1, 100)
    _number(duck.get('release_ms', 180), 'ducking.release_ms', 40, 1000)
    ceiling = _number(mix.get('limiter_ceiling', 0.95), 'mix.limiter_ceiling', 0.80, 0.99)
    return resolved_assets, ceiling


def build_filtergraph(events: list[dict], *, has_audio: bool, duration: float,
                      ducking: dict, limiter_ceiling: float) -> str:
    graph = []
    if has_audio:
        graph.append('[0:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[base]')
    else:
        graph.append(f'anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration={duration:.6f}[base]')
    duck_enabled = bool(ducking.get('enabled', True))
    ducked = [i for i, event in enumerate(events) if duck_enabled and event.get('ducking', True)]
    split_labels = ['[base_mix]'] + [f'[sc{i}]' for i in ducked]
    graph.append(f'[base]asplit={len(split_labels)}' + ''.join(split_labels))
    mix_labels = ['[base_mix]']
    for index, event in enumerate(events):
        input_index = index + 1
        duration_s = float(event['duration_s'])
        delay_ms = round(float(event['at_s']) * 1000)
        gain_db = float(event['_gain_db'])
        fade_in = float(event['_fade_in_s'])
        fade_out = float(event['_fade_out_s'])
        chain = (f'[{input_index}:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,'
                 f'atrim=duration={duration_s:.6f},asetpts=PTS-STARTPTS,volume={gain_db:.3f}dB')
        if fade_in > 0:
            chain += f',afade=t=in:st=0:d={fade_in:.6f}'
        if fade_out > 0:
            chain += f',afade=t=out:st={max(0.0, duration_s-fade_out):.6f}:d={fade_out:.6f}'
        chain += f',adelay={delay_ms}:all=1,apad=whole_dur={duration:.6f},atrim=duration={duration:.6f}[sfx{index}]'
        graph.append(chain)
        if index in ducked:
            d = ducking
            threshold = 10 ** (float(d.get('threshold_db', -30)) / 20)
            graph.append(f'[sfx{index}][sc{index}]sidechaincompress=threshold={threshold:.8f}:'
                         f'ratio={float(d.get("ratio", 2.5)):.3f}:attack={float(d.get("attack_ms", 10)):.3f}:'
                         f'release={float(d.get("release_ms", 180)):.3f}:makeup=1[duck{index}]')
            mix_labels.append(f'[duck{index}]')
        else:
            mix_labels.append(f'[sfx{index}]')
    graph.append(''.join(mix_labels) +
                 f'amix=inputs={len(mix_labels)}:duration=first:dropout_transition=0:normalize=0,'
                 f'alimiter=limit={limiter_ceiling:.4f}[aout]')
    return ';\n'.join(graph)


def render_audio_events(video_path: str | Path, audio_plan_path: str | Path,
                        edit_plan_path: str | Path, output_dir: str | Path,
                        transcript_path: str | Path | None = None) -> dict:
    video_path = Path(video_path).resolve(strict=True)
    audio_plan_path = Path(audio_plan_path).resolve(strict=True)
    edit_plan_path = Path(edit_plan_path).resolve(strict=True)
    audio_plan = load_json(audio_plan_path)
    edit_plan = load_json(edit_plan_path)
    transcript = load_json(transcript_path) if transcript_path else None
    resolved_assets, ceiling = validate_audio_plan(audio_plan, edit_plan, transcript=transcript,
                                                   asset_root=audio_plan_path.parent)
    video_probe, video_stream, audio_stream = _video_info(video_path)
    duration = float(audio_plan['output_duration_s'])
    if abs(float(video_probe['format']['duration']) - duration) > 0.10:
        raise ValueError('Rendered preview duration does not match audio design output duration')
    events = audio_plan['events']
    output = new_directory(output_dir)
    graph = build_filtergraph(events, has_audio=audio_stream is not None, duration=duration,
                              ducking=audio_plan.get('mix', {}).get('ducking', {}),
                              limiter_ceiling=ceiling)
    (output / 'audio-filtergraph.txt').write_text(graph + '\n', encoding='utf-8')
    argv = ['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-n', '-i', str(video_path)]
    for event in events:
        argv += ['-i', event['_resolved_asset']]
    argv += ['-filter_complex', graph, '-map', '0:v:0', '-map', '[aout]', '-c:v', 'copy',
             '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
             'preview-with-sfx.mp4']
    if len(subprocess.list2cmdline(argv)) > 28000:
        raise ValueError('Audio event graph exceeds portable command-length budget')
    write_json(output / 'command.json', {'argv': argv, 'cwd': str(output),
                                         'note': 'Input paths are argv entries; no shell interpolation.'})
    run(argv, cwd=output)
    rendered = output / 'preview-with-sfx.mp4'
    result = probe(rendered)
    out_video = next(s for s in result['streams'] if s['codec_type'] == 'video')
    out_audio = next(s for s in result['streams'] if s['codec_type'] == 'audio')
    checks = {
        'video_stream_preserved': out_video['codec_name'] == video_stream['codec_name'],
        'video_dimensions_preserved': (out_video['width'], out_video['height']) ==
                                      (video_stream['width'], video_stream['height']),
        'audio_aac_48k': out_audio['codec_name'] == 'aac' and out_audio['sample_rate'] == '48000',
        'duration': abs(float(result['format']['duration']) - duration) <= 0.12,
    }
    run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', rendered, '-f', 'null', '-'])
    checks['full_decode'] = True
    receipt = {
        'kind': 'skills-clip-audio-events-v1',
        'render_status': 'PASS' if all(checks.values()) else 'FAIL',
        'delivery_status': 'REVIEW',
        'input_video_sha256': sha256(video_path),
        'source_sha256': audio_plan['source_sha256'],
        'audio_plan_sha256': sha256(audio_plan_path),
        'output_sha256': sha256(rendered),
        'ffmpeg_version': run(['ffmpeg', '-version']).splitlines()[0],
        'events_applied': [{'id': e['id'], 'trigger': e['trigger'], 'at_s': e['at_s'],
                            'asset_id': e['asset_id'], 'gain_db': e['gain_db']} for e in events],
        'checks': checks,
        'not_run': ['semantic appropriateness of each SFX', 'human listening comfort',
                    'perceptual dialogue masking', 'platform loudness target assessment'],
        'limitations': ['Ducking is keyed to the complete source mix, not an isolated voice stem.',
                        'No loudness normalization or voice/game stem separation is performed.',
                        'Human listening and editorial review remain required.'],
    }
    write_json(output / 'audio-mix-receipt.json', receipt)
    if not all(checks.values()):
        raise ValueError('SFX render failed technical checks; inspect audio-mix-receipt.json')
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, required=True, help='Already rendered Skills-Clip preview MP4')
    parser.add_argument('--audio-plan', type=Path, required=True, help='Audio design JSON')
    parser.add_argument('--edit-plan', type=Path, required=True, help='Matching v2 edit plan JSON')
    parser.add_argument('--transcript', type=Path, help='Verified word-level transcript; required for word-emphasis events')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = render_audio_events(args.video, args.audio_plan, args.edit_plan,
                                     args.output_dir, args.transcript)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print(f'PASS: {len(result["events_applied"])} SFX events mixed; delivery REVIEW; human listening NOT_RUN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

