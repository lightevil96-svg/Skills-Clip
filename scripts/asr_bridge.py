#!/usr/bin/env python3
"""Import WhisperX/faster-whisper words, or run an already-installed local model.

Never downloads models, infers avatar identities, fabricates missing word times,
or promotes machine output to VERIFIED. Import provenance is a declared source
association; only actual listening can verify the text.
"""
import argparse
from importlib.metadata import version
import math
from pathlib import Path
import shutil
import subprocess
import sys

from media_tools import new_directory, sha256, source_record, write_json
from validate_artifacts import load_json, normalized_text, validate


def convert(raw, source, *, language, model, offset=0.0, content_kind='real'):
    if not isinstance(raw, dict) or not isinstance(raw.get('segments'), list):
        raise ValueError('Expected JSON object with segments[].words[]')
    if not math.isfinite(offset) or not 0 <= offset < source['duration_s']:
        raise ValueError('Invalid source-clock offset')
    words, unresolved, speaker_ids = [], [], set()
    for segment_index, segment in enumerate(raw['segments']):
        entries = segment.get('words')
        if not entries:
            if segment.get('text', '').strip():
                unresolved.append({'text': segment['text'], 'raw_location': f'segments[{segment_index}]',
                                   'reason': 'Segment has no word alignment; no word timestamps invented.'})
            continue
        if not isinstance(entries, list):
            raise ValueError('segments[].words must be a list')
        if segment.get('text') and normalized_text(segment['text']) != normalized_text(
                ' '.join(str(w.get('word', w.get('text', ''))) for w in entries)):
            unresolved.append({'text': segment['text'], 'raw_location': f'segments[{segment_index}]',
                               'reason': 'Segment text differs from word list; reconcile omissions/tokenization against source.'})
        for index, word in enumerate(entries):
            text = word.get('word', word.get('text'))
            if not isinstance(text, str) or not text.strip():
                raise ValueError('Every ASR word needs nonempty text')
            location = f'segments[{segment_index}].words[{index}]'
            if word.get('start') is None or word.get('end') is None:
                unresolved.append({'text': text, 'raw_location': location,
                                   'reason': 'Missing word start/end; review or realign against source.'})
                continue
            start, end = word['start'], word['end']
            if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) for t in (start, end)):
                raise ValueError(f'{location}: invalid timestamps')
            if not 0 <= start < end or end + offset > source['duration_s'] + .001:
                raise ValueError(f'{location}: word outside source or invalid duration')
            speaker = word.get('speaker', segment.get('speaker'))
            if speaker is not None:
                if not isinstance(speaker, str) or not speaker:
                    raise ValueError(f'{location}: invalid diarization label')
                speaker_ids.add(speaker)
            confidence = word.get('probability', word.get('score'))
            words.append({'id': f'w{len(words)+1}', 'start': start+offset, 'end': end+offset,
                          'text': text.strip(), 'speaker_id': speaker, 'language': language,
                          'asr_confidence': confidence, 'verification_status': 'ASR_RAW',
                          'verified_by': None, 'notes': f'Imported {location}. Speaker label is not avatar identity.'})
    words.sort(key=lambda w: w['start'])  # retain overlapping turns, order by onset only
    transcript = {'schema_version': '2.0', 'source_file': source['path'],
                  'source_duration_s': source['duration_s'], 'source_sha256': source['sha256'],
                  'content_kind': content_kind, 'audio_source_access': False,
                  'language': language, 'asr_model': model, 'verification_policy': 'human-listen-required',
                  'speakers': [{'speaker_id': s, 'mapping_status': 'UNKNOWN',
                                'display_name': None, 'avatar_ref': None} for s in sorted(speaker_ids)],
                  'words': words, 'unresolved_words': unresolved}
    errors, _ = validate('transcript', transcript)
    if errors:
        raise ValueError('; '.join(errors))
    return transcript


def import_file(raw_path, source_path, output_dir, *, language, model, offset=0.0, content_kind='real'):
    source = source_record(source_path)
    if not source['audio_present']:
        raise ValueError('Source has no audio; cannot associate an ASR transcript')
    transcript = convert(load_json(raw_path), source, language=language, model=model,
                         offset=offset, content_kind=content_kind)
    transcript['import_provenance'] = {'raw_sha256': sha256(raw_path), 'source_offset_s': offset,
                                     'source_association': 'DECLARED', 'engine_run': 'NOT_RUN'}
    directory = new_directory(output_dir)
    shutil.copyfile(raw_path, directory/'raw-asr.json')
    write_json(directory/'transcript.json', transcript)
    return transcript


def run_local(source_path, model_path, output_dir, *, language, device='cpu', compute_type='int8', content_kind='real'):
    # Model aliases are intentionally forbidden: no implicit network/download.
    model_path = Path(model_path).resolve(strict=True)
    if not model_path.is_dir():
        raise ValueError('--model-dir must be an existing local CTranslate2 model directory')
    source = source_record(source_path)
    if not source['audio_present']:
        raise ValueError('Source has no audio')
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise ValueError('faster-whisper is not installed. See docs/production-tools.md; inference NOT_RUN.') from exc
    directory = new_directory(output_dir)
    model = WhisperModel(str(model_path), device=device, compute_type=compute_type, local_files_only=True)
    segments, info = model.transcribe(str(Path(source_path).resolve()), language=language,
                                      word_timestamps=True, vad_filter=False)
    raw = {'language': info.language, 'segments': []}
    for segment in segments:  # iteration actually executes transcription
        raw['segments'].append({'start': segment.start, 'end': segment.end, 'text': segment.text,
            'words': [{'word': w.word, 'start': w.start, 'end': w.end, 'probability': w.probability}
                      for w in (segment.words or [])]})
    write_json(directory/'raw-asr.json', raw)
    transcript = convert(raw, source, language=language, model=str(model_path), content_kind=content_kind)
    transcript['import_provenance'] = {'raw_sha256': sha256(directory/'raw-asr.json'), 'source_offset_s': 0,
                                     'source_association': 'LOCAL_RUN', 'engine_run': 'PASS'}
    write_json(directory/'transcript.json', transcript)
    write_json(directory/'run.json', {'engine': 'faster-whisper', 'version': version('faster-whisper'),
        'model_dir': str(model_path), 'device': device, 'compute_type': compute_type,
        'word_timestamps': True, 'vad_filter': False, 'source_sha256': source['sha256'],
        'transcript_sha256': sha256(directory/'transcript.json'), 'verification': 'ASR_RAW'})
    return transcript


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('import', 'run-local'):
        p = commands.add_parser(command)
        p.add_argument('source', type=Path)
        p.add_argument('output_dir', type=Path)
        p.add_argument('--language', required=True)
        p.add_argument('--content-kind', choices=['real', 'synthetic'], default='real')
        if command == 'import':
            p.add_argument('--raw', type=Path, required=True)
            p.add_argument('--model', required=True)
            p.add_argument('--offset', type=float, required=True,
                           help='Source offset of excerpt. Explicitly pass 0 for full-source ASR.')
        else:
            p.add_argument('--model-dir', type=Path, required=True)
            p.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
            p.add_argument('--compute-type', choices=['int8', 'float16', 'float32'], default='int8')
    args = parser.parse_args()
    try:
        common = dict(language=args.language, content_kind=args.content_kind)
        if args.command == 'import':
            result = import_file(args.raw, args.source, args.output_dir, model=args.model, offset=args.offset, **common)
        else:
            result = run_local(args.source, args.model_dir, args.output_dir, device=args.device, compute_type=args.compute_type, **common)
        print(f'PASS: {len(result["words"])} ASR_RAW words; {len(result["unresolved_words"])} unresolved; verification NOT_RUN')
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
