"""Small local-media helpers. Hash integrity does not establish source meaning."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess


def run(argv, *, cwd=None, timeout=600):
    result = subprocess.run([str(a) for a in argv], cwd=cwd, capture_output=True,
                            encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        raise ValueError(f'{argv[0]} failed ({result.returncode}): {result.stderr[-3000:]}')
    return result.stdout


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def new_directory(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path


def probe(path):
    path = Path(path).resolve(strict=True)
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                           '-of', 'json', path]))
    return data


def source_record(path, data=None):
    data = probe(path) if data is None else data
    videos = [s for s in data['streams'] if s['codec_type'] == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    if len(videos) != 1:
        raise ValueError('Select a source with exactly one video stream; normalize explicitly first.')
    video = videos[0]
    duration = float(data['format']['duration'])
    fps = float(Fraction(video['avg_frame_rate']))
    if not math.isfinite(duration) or duration <= 0 or fps <= 0:
        raise ValueError('Missing/invalid source duration or frame rate')
    return {'path': str(Path(path).resolve()), 'sha256': sha256(path),
            'duration_s': duration, 'width': video['width'], 'height': video['height'],
            'fps': fps, 'audio_present': any(s['codec_type'] == 'audio' for s in data['streams'])}


def check_source(declared, path, data=None):
    actual = source_record(path, data)
    if declared.get('sha256') != actual['sha256']:
        raise ValueError('Source SHA-256 missing or mismatched; inspect the selected source first')
    for field in ('width', 'height', 'audio_present'):
        if declared[field] != actual[field]:
            raise ValueError(f'Source {field} mismatch')
    for field, tolerance in [('duration_s', .05), ('fps', .001)]:
        if abs(declared[field] - actual[field]) > tolerance:
            raise ValueError(f'Source {field} mismatch')
    return actual


def check_cfr(data, path, start, end):
    """Fail closed on source clocks this small renderer cannot safely normalize."""
    streams = [s for s in data['streams'] if s['codec_type'] in ('audio', 'video')]
    videos = [s for s in streams if s['codec_type'] == 'video']
    audios = [s for s in streams if s['codec_type'] == 'audio']
    if len(videos) != 1 or len(audios) > 1:
        raise ValueError('Renderer requires one video and at most one audio stream')
    video = videos[0]
    if video.get('sample_aspect_ratio', '1:1') not in ('1:1', 'N/A'):
        raise ValueError('Normalize non-square pixels explicitly before rendering')
    rotation = float(video.get('tags', {}).get('rotate', 0))
    rotations = [float(s.get('rotation', 0)) for s in video.get('side_data_list', [])]
    if rotation % 360 or any(r % 360 for r in rotations):
        raise ValueError('Normalize rotated media explicitly before rendering')
    if any(abs(float(s.get('start_time', '0'))) > .0001 for s in streams):
        raise ValueError('Non-zero stream starts require explicit synchronized normalization')
    fps = float(Fraction(video['avg_frame_rate']))
    if abs(float(Fraction(video['r_frame_rate'])) - fps) > .001:
        raise ValueError('Variable frame rate is not supported by this renderer')
    # Decode beyond the selection so reordered B-frames before `end` are flushed.
    # Filter presentation timestamps back to the exact selected interval below.
    raw = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-read_intervals',
               f'{start}%{end+2}', '-show_frames', '-show_entries',
               'frame=best_effort_timestamp_time', '-of', 'json', path])
    times = [float(f['best_effort_timestamp_time']) for f in json.loads(raw)['frames']
             if 'best_effort_timestamp_time' in f]
    times = [t for t in times if start - .0001 <= t < end - .0001]
    expected = round((end - start) * fps)
    if len(times) != expected or any(abs((b-a) - 1/fps) > .0001 for a, b in zip(times, times[1:])):
        raise ValueError('Selected source frames are missing or variable-rate; normalize explicitly')
    return fps


def confined_file(root, relative):
    relative = Path(relative)
    if relative.is_absolute():
        raise ValueError('Evidence paths must be relative to their manifest directory')
    root = Path(root).resolve()
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Evidence path escapes its directory or is not a file')
    return path
