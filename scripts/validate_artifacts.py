#!/usr/bin/env python3
"""Offline schema and semantic checks. Presence of evidence is not its truth."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'schemas'
KINDS = ('edit-plan', 'transcript', 'style-profile', 'editorial-review')
SKILLS = {
    'clip-router', 'editorial-intelligence', 'vtuber-gameplay-facecam-clip',
    'vtuber-conversation-clip', 'vtuber-collab-reaction-clip',
    'transcript-and-speaker-pipeline', 'caption-design', 'hook-pacing-retention',
    'audio-mix-and-sfx', 'ffmpeg-vertical-quality', 'render-package-for-user',
    'qa-and-self-review',
}
VERIFIED = {'VERIFIED', 'USER_CONFIRMED'}
EPS = 0.001
FORMATS = FormatChecker()


@FORMATS.checks('date-time')
def valid_review_time(value):
    # jsonschema's optional format dependencies are not guaranteed installed.
    if not isinstance(value, str):
        return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})', value):
        return False
    try:
        return datetime.fromisoformat(value.upper().replace('Z', '+00:00')).tzinfo is not None
    except ValueError:
        return False


def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f'non-finite JSON number: {value}')

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            invalid(value)
        return number

    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite_float)


def schema_errors(kind, data):
    registry = Registry()
    schemas = {}
    for path in sorted(SCHEMAS.glob('*.schema.json')):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        schemas[path.stem.removesuffix('.schema')] = schema
        registry = registry.with_resource(schema['$id'], Resource.from_contents(schema))
    validator = Draft202012Validator(schemas[kind], registry=registry,
                                    format_checker=FORMATS)
    return [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: str(list(e.absolute_path)))]


def normalized_text(value):
    # Ignore typography/case, not words, negation or word order.
    value = unicodedata.normalize('NFKC', value).casefold()
    value = ''.join(c for c in value if not unicodedata.category(c).startswith('P'))
    return ' '.join(value.split())


def validate(kind, data, *, stage='draft', transcript=None, review=None, style=None):
    """Return (errors, warnings); final is readiness, not an aesthetic verdict."""
    errors = schema_errors(kind, data)
    warnings = []
    if errors:
        return errors, warnings

    def require(condition, message):
        if not condition:
            errors.append(message)

    def interval(start, end, limit, label, allow_point=False):
        require(end >= start if allow_point else end > start, f'{label}: invalid interval')
        require(start >= 0 and end <= limit + EPS, f'{label}: outside source/output bounds')

    def unique(items, key, label):
        ids = [item[key] for item in items if key in item]
        require(len(ids) == len(set(ids)), f'{label}: duplicate {key}')
        return {item[key]: item for item in items if key in item}

    def receipt(item, start, end, source, label, policy=None, access=True):
        v = item.get('verification')
        if not v:
            require(False, f'{label}: verified claim requires a verification receipt')
            return
        require(v['source_ref'] == source, f'{label}: receipt source does not match')
        require(v['source_in_s'] <= start + EPS and v['source_out_s'] >= end - EPS,
                f'{label}: receipt does not cover source interval')
        require(v['source_out_s'] > v['source_in_s'], f'{label}: empty receipt interval')
        require(v['context_checked'] and not v['uncertainties'], f'{label}: unresolved verification')
        if item.get('verification_status') == 'USER_CONFIRMED':
            require(v['method'] == 'user-confirmation', f'{label}: missing user confirmation method')
        elif item.get('verification_status') == 'VERIFIED':
            require(v['method'] != 'user-confirmation', f'{label}: use USER_CONFIRMED for user evidence')
        if v['method'] == 'direct-audio-review':
            require(access, f'{label}: direct review requires source audio access')
            require(policy != 'human-listen-required', f'{label}: human-listen-required policy rejects agent verification')

    if kind == 'transcript':
        v2 = data.get('schema_version') == '2.0'
        speakers = unique(data['speakers'], 'speaker_id', 'speakers')
        if v2:
            for speaker in speakers.values():
                if speaker['mapping_status'] in VERIFIED:
                    require(bool(speaker.get('mapping_evidence')), 'verified speaker mapping requires evidence')
        unique(data['words'], 'id', 'words')
        limit = data.get('source_duration_s', float('inf'))
        previous_start = -1
        for index, word in enumerate(data['words']):
            label = f'word {word.get("id", index)}'
            interval(word['start'], word['end'], limit, label)
            require(word['start'] >= previous_start, f'{label}: words must be ordered by source onset (overlap is allowed)')
            previous_start = word['start']
            require(word['speaker_id'] is None or word['speaker_id'] in speakers, f'{label}: unknown speaker ID')
            if word['verification_status'] in VERIFIED and (v2 or stage == 'final' or 'verification' in word):
                receipt(word, word['start'], word['end'], data['source_file'], label,
                        data['verification_policy'], data.get('audio_source_access', False))
            if stage == 'final':
                require(word['verification_status'] in VERIFIED, f'{label}: unverified final word')
        if stage == 'final':
            require(v2, 'final transcript requires v2 provenance; legacy remains valid as draft')
            require(data.get('content_kind') == 'real', 'synthetic transcript is not a final source transcript')
            require(bool(data.get('source_sha256')), 'final transcript requires source_sha256')
            require(not data.get('unresolved_words'), 'final transcript has unresolved alignment/text gaps')

    elif kind == 'style-profile':
        references = unique(data['references'], 'id', 'references')
        for name, trait in data['traits'].items():
            require(trait['reference_id'] in references, f'{name}: missing reference')
            require(trait['out_s'] >= trait['in_s'], f'{name}: invalid reference interval')
            if trait['status'] == 'VERIFIED':
                reference = references.get(trait['reference_id'], {})
                require(reference.get('available', False), f'{name}: absent reference cannot be newly verified')
                require(trait['method'] not in {'document-only', 'user-preference'}, f'{name}: observation method cannot establish VERIFIED')
                if name == 'sfx':
                    require(trait['method'] == 'audio-visual-inspection', 'sfx: visual frames cannot verify sound')

    elif kind == 'editorial-review':
        for name, metric in data['metrics'].items():
            assessed = metric['status'] in {'PASS', 'FAIL'}
            require((metric['score'] is not None) == assessed, f'{name}: score only for completed PASS/FAIL assessment')
            if assessed:
                require(bool(metric['evidence_refs']), f'{name}: scored assessment requires evidence')
                require(data['review_mode'] != 'automated', f'{name}: automated checks cannot score editorial quality')
            if metric['status'] == 'FAIL' or metric.get('score') in (0, 1, 2):
                require(metric['next_action'].strip().lower() not in {'none', 'n/a'}, f'{name}: specify a concrete repair')
            if metric.get('score') in (0, 1, 2):
                require(metric['status'] == 'FAIL', f'{name}: unresolved rubric deficiency cannot be PASS')
        human = data['human_review']
        if human['status'] == 'PASS':
            require(bool(human['reviewer']) and bool(human['evidence_refs']), 'human PASS needs named reviewer and evidence')
        for revision in data['revisions']:
            if revision['status'] == 'resolved':
                require(bool(revision['recheck_evidence']), 'resolved revision requires recheck evidence')
        if data['status'] == 'PASS' or stage == 'final':
            require(data['status'] == 'PASS', 'final editorial review must be PASS')
            require(all(m['status'] in {'PASS', 'SKIP'} for m in data['metrics'].values()), 'editorial review has unresolved metrics')
            require(human['status'] == 'PASS', 'final review requires human listening/review evidence')
            require(all(c['status'] in {'PASS', 'SKIP'} for c in data['technical_checks']) and bool(data['technical_checks']), 'final review requires completed technical checks')
            require(all(r['status'] == 'resolved' for r in data['revisions']), 'review has open revisions')
            require(data['metrics']['audio_comfort']['status'] == 'PASS', 'final audio comfort requires assessment')
            for core in ('storytelling_clarity','timing_precision','visual_composition',
                         'editing_naturalness','effect_restraint','overall_coherence'):
                require(data['metrics'][core]['status'] == 'PASS', f'{core}: core editorial assessment cannot be skipped for final delivery')

    elif kind == 'edit-plan':
        v2 = data.get('schema_version') == '2.0'
        duration = data['source']['duration_s']
        clip = data['clip']
        interval(clip['in_s'], clip['out_s'], duration, 'clip')
        require(bool(data['shots']), 'edit plan requires at least one shot')
        require(data['routing']['primary_route'] in SKILLS, 'unknown primary route')
        require(all(r in SKILLS for r in data['routing'].get('supporting_routes', [])), 'unknown supporting route')
        speakers = unique(data.get('speakers', []), 'speaker_id', 'speakers')
        shots = unique(data['shots'], 'id', 'shots')
        captions = unique(data['captions'], 'id', 'captions')
        assets = unique(data.get('assets', []), 'id', 'assets')
        ed = data.get('editorial', {})
        evidence = unique(ed.get('evidence', []), 'id', 'evidence')
        beats = unique(ed.get('narrative_beats', []), 'id', 'beats')
        source_ref = data['source']['path']
        access = ed.get('capabilities', {}).get('audio_source_access', False)
        visual_access = ed.get('capabilities', {}).get('visual_source_access', False)

        def refs(ids, records, label):
            require(all(i in records for i in ids), f'{label}: dangling reference')

        if v2:
            for speaker in speakers.values():
                if speaker['mapping_status'] in VERIFIED:
                    require(bool(speaker.get('evidence_ids')), 'verified speaker mapping requires evidence IDs')
                    refs(speaker.get('evidence_ids', []), evidence, 'speaker mapping')

        def check_crop(crop, label):
            if crop is None:
                return
            require(set(('x', 'y', 'w', 'h')).issubset(crop), f'{label}: incomplete crop')
            if not set(('x', 'y', 'w', 'h')).issubset(crop):
                return
            require(crop['x'] >= 0 and crop['y'] >= 0 and crop['w'] > 0 and crop['h'] > 0,
                    f'{label}: nonpositive/outside crop')
            require(crop['x'] + crop['w'] <= data['source']['width'] + EPS and
                    crop['y'] + crop['h'] <= data['source']['height'] + EPS, f'{label}: crop outside source')

        for ev in evidence.values():
            interval(ev['in_s'], ev['out_s'], duration, f'evidence {ev["id"]}', True)
            require(ev['source_ref'] == source_ref, f'evidence {ev["id"]}: source mismatch')
            if ev['method'] == 'asr':
                require(ev['status'] not in VERIFIED, 'ASR evidence cannot be VERIFIED/USER_CONFIRMED')
            if ev['status'] == 'VERIFIED' and ev['method'] == 'audio-review':
                require(access, 'audio evidence requires actual source access')
            if ev['status'] == 'VERIFIED' and ev['method'] == 'visual-inspection':
                require(visual_access, 'visual evidence requires actual source access')
        for beat in beats.values():
            interval(beat['in_s'], beat['out_s'], duration, f'beat {beat["id"]}')
            refs(beat['evidence_ids'], evidence, 'beat evidence')

        output_cursor = 0.0
        previous_source_end = clip['in_s']
        mappings = []
        applied_effects = []
        for shot in data['shots']:
            sid = shot['id']
            interval(shot['in_s'], shot['out_s'], duration, sid)
            require(shot['in_s'] >= clip['in_s'] - EPS and shot['out_s'] <= clip['out_s'] + EPS, f'{sid}: outside clip envelope')
            require(shot['in_s'] >= previous_source_end - EPS, f'{sid}: source chronology reversed/overlapped')
            previous_source_end = shot['out_s']
            check_crop(shot.get('crop'), sid)
            refs(shot.get('caption_ids', []), captions, f'{sid} captions')
            refs(shot.get('overlay_ids', []), assets, f'{sid} overlays')
            if not v2:
                output_cursor += shot['out_s'] - shot['in_s']
                continue
            start, end = shot['output_in_s'], shot['output_out_s']
            require(abs(start - output_cursor) <= EPS, f'{sid}: output timeline gap/overlap')
            require(end > start, f'{sid}: invalid output interval')
            output_cursor = end
            segments = shot.get('time_map', [{'kind': 'play', 'source_in_s': shot['in_s'],
                'source_out_s': shot['out_s'], 'output_in_s': start, 'output_out_s': end}])
            if 'time_map' not in shot:
                require(abs((end - start) - (shot['out_s'] - shot['in_s'])) <= EPS, f'{sid}: retiming requires explicit time_map')
            sc, oc = shot['in_s'], start
            for seg in segments:
                require(abs(seg['source_in_s'] - sc) <= EPS and abs(seg['output_in_s'] - oc) <= EPS, f'{sid}: discontinuous time_map')
                require(seg['output_out_s'] > seg['output_in_s'], f'{sid}: empty output mapping')
                if seg['kind'] == 'freeze':
                    require(abs(seg['source_out_s'] - seg['source_in_s']) <= EPS, f'{sid}: freeze must map a single source instant')
                else:
                    require(seg['source_out_s'] > seg['source_in_s'], f'{sid}: invalid play mapping')
                sc, oc = seg['source_out_s'], seg['output_out_s']
                mappings.append(seg)
            require(abs(sc - shot['out_s']) <= EPS and abs(oc - end) <= EPS, f'{sid}: incomplete time_map')
            d = shot['editorial']
            refs([d['beat_id']], beats, f'{sid} beat')
            refs(d['source_evidence_ids'], evidence, f'{sid} evidence')
            refs(d['active_speaker_ids'], speakers, f'{sid} speakers')
            if stage == 'final':
                require(all(speakers.get(s, {}).get('mapping_status') in VERIFIED for s in d['active_speaker_ids']), f'{sid}: active speaker mapping unresolved')
                if shot['layout'] in {'subject-crop','speaker-follow'}:
                    require(bool(shot.get('crop') or d['camera']['keyframes']), f'{sid}: final subject framing requires crop coordinates')
            route = shot.get('route', data['routing']['primary_route'])
            require(route in SKILLS, f'{sid}: unknown route')
            if route == 'vtuber-conversation-clip':
                restricted = shot['layout'] in {'stacked','side-by-side','avatar-inset','blur-fit'}
                require(not restricted or bool(data['project'].get('composition_override')), f'{sid}: conversation layout requires explicit user override')
                if len(d['active_speaker_ids']) == 1 and d['camera']['action'] != 'reaction-close-up' and not d['shared_interaction']:
                    require(shot.get('primary_subject') == d['active_speaker_ids'][0], f'{sid}: solo shot must follow active speaker')
                if shot['layout'] == 'shared-two-shot':
                    require(d['shared_interaction'] or len(d['active_speaker_ids']) > 1, f'{sid}: shared shot lacks shared interaction')
            keyframes = d['camera']['keyframes']
            require([k['at_s'] for k in keyframes] == sorted(set(k['at_s'] for k in keyframes)), f'{sid}: keyframes must have unique increasing times')
            if d['camera']['action'] in {'pan','track','punch-in','punch-out'}:
                require(len(keyframes) >= 2, f'{sid}: camera motion requires endpoint keyframes')
            for k in keyframes:
                require(start <= k['at_s'] <= end, f'{sid}: keyframe outside shot')
                check_crop(k['crop'], f'{sid} keyframe')
            effects = d['effect_decision']['effects']
            require(bool(effects) == (d['effect_decision']['choice'] == 'apply'), f'{sid}: effect choice does not match effects')
            for fx in effects:
                applied_effects.append(fx['type'])
                interval(fx['start_s'], fx['end_s'], end, f'{sid} effect')
                require(fx['start_s'] >= start, f'{sid}: effect starts before shot')
                refs(fx['evidence_ids'], evidence, f'{sid} effect evidence')
                if fx['asset_id'] is not None:
                    refs([fx['asset_id']], assets, f'{sid} effect asset')

        if v2:
            require(data['audio']['sfx_used'] == ('sfx' in applied_effects), 'sfx_used disagrees with effect decisions')
            require(data['audio']['bgm_used'] == ('music' in applied_effects), 'bgm_used disagrees with music decisions')

        def mapped_interval(word):
            pieces = []
            covered = 0.0
            for seg in mappings:
                if seg['kind'] != 'play' or seg['source_out_s'] <= seg['source_in_s']:
                    continue
                left = max(word['start'], seg['source_in_s'])
                right = min(word['end'], seg['source_out_s'])
                if right <= left:
                    continue
                ratio = (seg['output_out_s'] - seg['output_in_s']) / (seg['source_out_s'] - seg['source_in_s'])
                pieces.append((seg['output_in_s'] + (left-seg['source_in_s'])*ratio,
                               seg['output_in_s'] + (right-seg['source_in_s'])*ratio))
                covered += right - left
            if covered + EPS < word['end'] - word['start'] or not pieces:
                return None
            return min(p[0] for p in pieces), max(p[1] for p in pieces)

        words = {}
        if transcript is not None:
            te, tw = validate('transcript', transcript, stage='draft')
            errors.extend('transcript: '+e for e in te)
            warnings.extend(tw)
            if not te:
                words = {w['id']: w for w in transcript['words'] if 'id' in w}
                require(transcript['source_file'] == source_ref, 'transcript source must match plan source clock/file')
                if 'source_sha256' in transcript and 'sha256' in data['source']:
                    require(transcript['source_sha256'] == data['source']['sha256'], 'transcript source hash mismatch')
        for cap in data['captions']:
            label = f'caption {cap["id"]}'
            interval(cap['start_s'], cap['end_s'], output_cursor, label)
            require(cap['speaker_id'] is None or cap['speaker_id'] in speakers, f'{label}: unknown speaker')
            if stage == 'final':
                require(cap['verification_status'] in VERIFIED, f'{label}: unverified final caption')
            if not v2:
                continue
            ids = cap['word_ids']
            require(len(ids) == len(set(ids)), f'{label}: duplicate word ID')
            refs(cap['emphasis_word_ids'], {i: True for i in ids}, f'{label} emphasis')
            refs(cap['evidence_ids'], evidence, f'{label} information evidence')
            linked = [words[i] for i in ids if i in words]
            if cap['kind'] != 'information':
                require(bool(ids), f'{label}: spoken text requires word_ids')
                if transcript is None:
                    (errors if stage == 'final' else warnings).append(f'{label}: supply transcript to verify words and mapping')
                else:
                    refs(ids, words, label)
                    require([w['start'] for w in linked] == sorted(w['start'] for w in linked), f'{label}: word order changed')
                    if cap['kind'] in {'dialogue','emphasis'} and len(linked) == len(ids):
                        require(normalized_text(cap['text']) == normalized_text(' '.join(w['text'] for w in linked)), f'{label}: text differs from transcript')
                    if cap['speaker_id'] is not None:
                        require(all(w['speaker_id'] == cap['speaker_id'] for w in linked), f'{label}: speaker disagrees with transcript')
                    if cap['verification_status'] in VERIFIED:
                        require(all(w['verification_status'] in VERIFIED for w in linked), f'{label}: unverified word used as verified caption')
                    for word in linked:
                        mapped = mapped_interval(word)
                        require(mapped is not None, f'{label}: word removed or truncated by edit')
                        if mapped:
                            require(cap['start_s'] <= mapped[0] + EPS and cap['end_s'] >= mapped[1] - EPS, f'{label}: caption does not cover spoken word in output')
                    if linked and cap['kind'] in {'dialogue','emphasis'}:
                        mapped = mapped_interval(linked[0])
                        if mapped and mapped[0] - cap['start_s'] > 0.1:
                            warnings.append(f'{label}: text leads speech by >100 ms; inspect punchline reveal')
            else:
                require(not ids and bool(cap['evidence_ids']), f'{label}: information requires evidence, not dialogue word IDs')
            if cap['kind'] in {'translation','reading-aid'} and cap['verification_status'] in VERIFIED:
                if linked:
                    receipt(cap, min(w['start'] for w in linked), max(w['end'] for w in linked), source_ref, label, access=access)
                else:
                    require(False, f'{label}: language review needs source-linked transcript')
            for shot in data['shots']:
                if cap['id'] in shot.get('caption_ids', []):
                    require(cap['start_s'] < shot['output_out_s'] and cap['end_s'] > shot['output_in_s'], f'{label}: referenced by non-overlapping shot')
            if stage == 'final':
                require(cap['position']['safe_area_checked'], f'{label}: safe area not reviewed')
                if cap['speaker_id'] is not None:
                    require(speakers.get(cap['speaker_id'], {}).get('mapping_status') in VERIFIED, f'{label}: speaker mapping unresolved')

        if style is not None:
            se, sw = validate('style-profile', style)
            errors.extend('style: '+e for e in se)
            warnings.extend(sw)
            if not se and v2:
                require(ed['style_application']['profile_id'] == style['id'], 'style profile ID mismatch')
                refs(ed['style_application']['applied_traits'], style['traits'], 'applied style traits')
        elif v2 and ed['style_application']['profile_id']:
            (errors if stage == 'final' else warnings).append('supply the referenced style profile')
        if stage == 'final':
            require(v2, 'final plan requires v2 evidence and timeline; legacy remains valid as draft')
            require(data['project'].get('content_kind') == 'real', 'synthetic example cannot certify a final video')
            require(bool(data['source'].get('sha256')), 'final plan requires source checksum')
            require(bool(data.get('render')), 'final plan requires render output hash, command and probe records')
            require(clip.get('context_preserved') is True, 'context preservation has not been checked')
            require(not ed.get('unknowns', []) and not data['routing']['unknowns'], 'final plan has unresolved unknowns')
            require(all(e['status'] in VERIFIED for e in evidence.values()), 'final source evidence is unresolved')
            require(data['qa']['status'] == 'PASS' and bool(data['qa']['checks']), 'final QA is incomplete')
            require(all(c['status'] in {'PASS','SKIP'} for c in data['qa']['checks']), 'final QA has unresolved checks')
            require(review is not None, 'final plan requires a separate editorial review report')
        if review is not None:
            re_, rw = validate('editorial-review', review, stage=stage)
            errors.extend('review: '+e for e in re_)
            warnings.extend(rw)
            if not re_:
                require(review['project_id'] == data['project']['title'], 'review project does not match plan')
                if data.get('render'):
                    require(review['reviewed_artifact'] == data['render']['output_path'], 'review does not identify rendered artifact')
        if not v2:
            warnings.append('legacy plan: no v2 decision/provenance checks; migrate before final delivery')
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=KINDS)
    parser.add_argument('path', type=Path)
    parser.add_argument('--stage', choices=('draft','final'), default='draft')
    parser.add_argument('--transcript', type=Path)
    parser.add_argument('--review', type=Path)
    parser.add_argument('--style', type=Path)
    args = parser.parse_args(argv)
    try:
        data = load_json(args.path)
        supplied = {key: load_json(getattr(args, key)) if getattr(args, key) else None
                    for key in ('transcript','review','style')}
        errors, warnings = validate(args.kind, data, stage=args.stage, **supplied)
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    for message in warnings:
        print(f'REVIEW: {message}')
    for message in errors:
        print(f'FAIL: {message}')
    if errors:
        return 1
    print(f'PASS: {args.kind} {args.stage} schema and semantic checks. Evidence truth and editorial quality are not certified.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
