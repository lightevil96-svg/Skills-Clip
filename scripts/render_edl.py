#!/usr/bin/env python3
"""Render a deliberately bounded v2 EDL into a REVIEW preview, never final QA.

Supports chronological direct cuts, explicit static crops and fixed-size pans
with easing, source audio, and verified static dialogue. Unsupported decisions
fail before encoding. Run through an NLE/custom tested renderer for other edits.
"""
import argparse
from fractions import Fraction
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

from media_tools import check_cfr, check_source, new_directory, probe, run, sha256, write_json
from validate_artifacts import VERIFIED, load_json, validate


def frame_number(seconds, fps):
    value = seconds * fps
    if not math.isfinite(value) or abs(value - round(value)) > .002:
        raise ValueError('Cut boundary is not on a native source/output frame; adjust the EDL explicitly')
    return round(value)


def motion_expression(keys, axis, origin):
    # Numeric-only expressions. No user strings become executable filter syntax.
    expression = str(keys[-1]['crop'][axis])
    for left, right in reversed(list(zip(keys, keys[1:]))):
        a, b = left['at_s'] - origin, right['at_s'] - origin
        u = f'clip((t-{a:.9f})/{b-a:.9f},0,1)'
        ease = {'linear': u, 'ease-in': f'pow({u},2)',
                'ease-out': f'(1-pow(1-{u},2))',
                'ease-in-out': f'({u}*{u}*(3-2*{u}))'}[left['easing']]
        start, delta = left['crop'][axis], right['crop'][axis] - left['crop'][axis]
        expression = f'if(lt(t,{b:.9f}),{start}+{delta}*{ease},{expression})'
    return expression


def check_supported(plan, *, width, height, captions, transcript=None):
    errors, warnings = validate('edit-plan', plan, transcript=transcript)
    if errors:
        raise ValueError('; '.join(errors))
    if plan.get('schema_version') != '2.0':
        raise ValueError('Renderer requires a v2 EDL; migrate legacy plans explicitly')
    if width <= 0 or height <= 0 or width % 2 or height % 2 or max(width, height) > 4096:
        raise ValueError('Output must have positive even dimensions no larger than 4096')
    if len(plan['shots']) > 100 or plan['clip']['out_s'] - plan['clip']['in_s'] > 600:
        raise ValueError('Preview renderer is bounded to 100 shots and a 600-second source envelope')
    if plan.get('assets') or plan['audio']['sfx_used'] or plan['audio']['bgm_used'] or plan['audio'].get('ducking_db') is not None:
        raise ValueError('Asset compositing, SFX, BGM and ducking require a separate tested renderer')
    if plan['editorial']['style_application']['applied_traits']:
        raise ValueError('Style traits are not implemented by this renderer; use a compatible renderer')
    fps = plan['source']['fps']
    for shot in plan['shots']:
        for name in ('in_s', 'out_s', 'output_in_s', 'output_out_s'):
            frame_number(shot[name], fps)
        if shot['layout'] not in {'full-bleed', 'subject-crop', 'speaker-follow', 'shared-two-shot'}:
            raise ValueError(f'{shot["id"]}: unsupported layout')
        if shot.get('overlay_ids') or shot['editorial']['effect_decision']['effects']:
            raise ValueError(f'{shot["id"]}: effects must be implemented by another renderer, never silently discarded')
        for segment in shot.get('time_map', []):
            if segment['kind'] != 'play' or abs((segment['source_out_s']-segment['source_in_s']) -
                    (segment['output_out_s']-segment['output_in_s'])) > .0001:
                raise ValueError('Freeze and speed changes are unsupported; use a tested retiming renderer')
        if abs((shot['out_s']-shot['in_s'])-(shot['output_out_s']-shot['output_in_s'])) > .0001:
            raise ValueError('Only real-time playback is supported')
        camera = shot['editorial']['camera']
        if camera['action'] in {'punch-in', 'punch-out'}:
            raise ValueError('Zoom keyframes are not implemented; choose another renderer')
        keys = camera['keyframes']
        crop = shot.get('crop')
        if keys:
            if camera['action'] not in {'pan', 'track'} or len(keys) < 2:
                raise ValueError('Only explicit pan/track keyframes are implemented')
            if abs(keys[0]['at_s']-shot['output_in_s']) > .0001 or abs(keys[-1]['at_s']-shot['output_out_s']) > .0001:
                raise ValueError('Pan keyframes must include both shot boundaries')
            crop = keys[0]['crop']
            if shot.get('crop') is not None and shot['crop'] != crop:
                raise ValueError('Static crop disagrees with the first keyframe')
            if any(k['crop']['w'] != crop['w'] or k['crop']['h'] != crop['h'] for k in keys):
                raise ValueError('Changing crop size/zoom is unsupported')
        if crop is None:
            if shot['layout'] != 'full-bleed':
                raise ValueError('Specify the inspected crop for every subject/shared shot')
            crop = {'x': 0, 'y': 0, 'w': plan['source']['width'], 'h': plan['source']['height']}
        if any(crop[k] != int(crop[k]) or int(crop[k]) % 2 for k in ('w', 'h')):
            raise ValueError('Crop dimensions must be even whole pixels')
        # Do not invent padding, stretch, or a new crop to fill a mismatched canvas.
        if abs(crop['w']/crop['h'] - width/height) > 1/crop['h']:
            raise ValueError('Crop/output aspect mismatch; choose explicit framing or another renderer')
    if captions == 'burn':
        if plan['captions'] and transcript is None:
            raise ValueError('Caption burn requires the linked transcript')
        if plan['captions'] and transcript.get('source_sha256') != plan['source'].get('sha256'):
            raise ValueError('Caption transcript requires the same source SHA-256 as the plan')
        for cap in plan['captions']:
            if cap['kind'] != 'dialogue' or cap['style'] != 'static-white':
                raise ValueError('Only explicit static-white dialogue is supported; no implicit restyling')
            if cap['verification_status'] not in VERIFIED:
                raise ValueError('Unverified captions cannot be burned, including review previews')
            if cap['emphasis_word_ids'] or any(cap['animation'][k] != 'none' for k in ('entrance', 'exit', 'movement')):
                raise ValueError('Caption emphasis/animation needs a compatible renderer')
            if not cap['position']['safe_area_checked']:
                raise ValueError('Review caption safe placement before burning')
            if not 0 <= cap['position']['x'] <= width or not 0 <= cap['position']['y'] <= height:
                raise ValueError('Caption position lies outside the requested output')
            # Reject ASS syntax, not silently alter the spoken words.
            if re.search(r'[{}\\\x00-\x1f]', cap['text']):
                raise ValueError('Caption contains ASS/control syntax; supply safe verbatim text in this renderer')
            for value in (cap['start_s'], cap['end_s']):
                if abs(value*100 - round(value*100)) > .001:
                    raise ValueError('ASS caption times require explicit centisecond precision')
    elif captions != 'omit':
        raise ValueError('Choose burn or omit explicitly')
    return warnings


def ass_time(seconds):
    centis = round(seconds*100)
    return f'{centis//360000}:{centis//6000%60:02}:{centis//100%60:02}.{centis%100:02}'


def make_ass(plan, width, height, font_name):
    if not re.fullmatch(r'[A-Za-z0-9 _-]{1,80}', font_name):
        raise ValueError('Use a plain font family name without ASS syntax')
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{max(12, round(height*.045))},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for cap in plan['captions']:
        position = cap['position']
        tag = f'{{\\pos({position["x"]},{position["y"]})}}'
        header += f'Dialogue: 0,{ass_time(cap["start_s"])},{ass_time(cap["end_s"])},Default,,0,0,0,,{tag}{cap["text"]}\n'
    return header


def build_graph(plan, width, height, burn):
    graph, inputs = [], []
    for index, shot in enumerate(plan['shots']):
        camera = shot['editorial']['camera']
        keys = camera['keyframes']
        crop = keys[0]['crop'] if keys else shot.get('crop')
        chain = f'[0:v:0]trim=start={shot["in_s"]}:end={shot["out_s"]},setpts=PTS-STARTPTS'
        if crop:
            x = motion_expression(keys, 'x', shot['output_in_s']) if keys else str(crop['x'])
            y = motion_expression(keys, 'y', shot['output_in_s']) if keys else str(crop['y'])
            chain += f",crop=w={crop['w']}:h={crop['h']}:x='{x}':y='{y}':exact=1"
        chain += f',scale={width}:{height}:flags=lanczos,setsar=1,format=yuv420p[v{index}]'
        graph.append(chain)
        inputs.append(f'[v{index}]')
        if plan['source']['audio_present']:
            graph.append(f'[0:a:0]atrim=start={shot["in_s"]}:end={shot["out_s"]},asetpts=PTS-STARTPTS[a{index}]')
            inputs.append(f'[a{index}]')
    audio = int(plan['source']['audio_present'])
    graph.append(''.join(inputs)+f'concat=n={len(plan["shots"])}:v=1:a={audio}[joined]'+('[audio]' if audio else ''))
    graph.append('[joined]'+('ass=captions.ass:fontsdir=fonts,' if burn else '')+'null[video]')
    return ';\n'.join(graph)+'\n'


def render(plan_path, source_path, output_dir, *, width=1080, height=1920, captions='burn',
           transcript_path=None, font_file=None, font_name=None):
    plan = load_json(plan_path)
    transcript = load_json(transcript_path) if transcript_path else None
    warnings = check_supported(plan, width=width, height=height, captions=captions, transcript=transcript)
    data = probe(source_path)
    source = check_source(plan['source'], source_path, data)
    fps = check_cfr(data, Path(source_path).resolve(), plan['clip']['in_s'], plan['clip']['out_s'])
    burn = captions == 'burn' and bool(plan['captions'])
    if burn and (font_file is None or font_name is None):
        raise ValueError('Caption burn requires --font-file and --font-name; provide a licensed local font')
    font = Path(font_file).resolve(strict=True) if burn else None
    ass = make_ass(plan, width, height, font_name) if burn else None
    graph = build_graph(plan, width, height, burn)
    output = new_directory(output_dir)
    if burn:
        (output/'fonts').mkdir()
        shutil.copyfile(font, output/'fonts' / ('caption-font'+font.suffix))
        (output/'captions.ass').write_text(ass, encoding='utf-8')
    (output/'filtergraph.txt').write_text(graph, encoding='utf-8')
    write_json(output/'plan-snapshot.json', plan)
    # Pass the graph as ONE argv element. The old filter_complex_script option
    # is absent in newer builds; inline filter_complex works across tested builds.
    argv = ['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-n', '-i', str(Path(source_path).resolve()),
            '-filter_complex', graph, '-map', '[video]']
    if source['audio_present']:
        argv += ['-map', '[audio]', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000']
    native_rate = next(s['avg_frame_rate'] for s in data['streams'] if s['codec_type'] == 'video')
    # concat uses a microsecond time base. Declare the proven native CFR so the
    # encoder assigns the final frame its full duration; do not choose a new FPS.
    argv += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
             '-r', native_rate, '-fps_mode', 'cfr', '-movflags', '+faststart', 'preview.mp4']
    if len(subprocess.list2cmdline(argv)) > 28000:
        raise ValueError('Filtergraph exceeds the portable command-length budget; use a tested segmented renderer')
    write_json(output/'command.json', {'argv': argv, 'cwd': str(output),
                                     'note': 'argv JSON, not a shell command. Input source remains external.'})
    run(argv, cwd=output)
    rendered = output/'preview.mp4'
    result = probe(rendered)
    write_json(output/'output-probe.json', result)
    video = next(s for s in result['streams'] if s['codec_type'] == 'video')
    audios = [s for s in result['streams'] if s['codec_type'] == 'audio']
    duration = plan['shots'][-1]['output_out_s']
    checks = {'dimensions': (video['width'], video['height']) == (width, height),
              'codec': video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p',
              'native_fps': abs(float(Fraction(video['avg_frame_rate']))-fps) < .001,
              'frame_count': int(video['nb_frames']) == frame_number(duration, fps),
              'duration': abs(float(result['format']['duration'])-duration) < max(.1, 2/fps),
              'audio_presence': bool(audios) == source['audio_present']}
    if audios:
        audio = audios[0]
        checks['aac_48k'] = audio['codec_name'] == 'aac' and audio['sample_rate'] == '48000'
        checks['av_start'] = abs(float(audio['start_time'])-float(video['start_time'])) <= .03
        checks['av_duration'] = abs(float(audio['duration'])-float(video['duration'])) <= .1
    run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', rendered, '-f', 'null', '-'])
    checks['full_decode'] = True
    receipt = {'kind': 'bounded-edl-preview', 'render_status': 'PASS' if all(checks.values()) else 'FAIL',
               'delivery_status': 'REVIEW', 'source_sha256': source['sha256'],
               'output_sha256': sha256(rendered), 'plan_sha256': sha256(plan_path),
               'ffmpeg_version': run(['ffmpeg', '-version']).splitlines()[0],
               'checks': checks, 'captions': captions, 'warnings': warnings,
               'font_sha256': sha256(font) if font else None,
               'not_run': ['semantic evidence verification', 'visual readability and glyph review',
                           'perceptual lip sync', 'LUFS/true-peak target assessment',
                           'human audio comfort', 'editorial QA'],
               'notes': ['Source audio cuts only. No gain, separation, ducking or loudness target was applied.',
                         'Track means supplied crop keyframes, not automatic object tracking.',
                         'Keep this work directory private. It is not a reviewed delivery ZIP.']}
    write_json(output/'render-receipt.json', receipt)
    if not all(checks.values()):
        raise ValueError('Encoded preview failed technical checks; inspect render-receipt.json')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--transcript', type=Path)
    parser.add_argument('--width', type=int, default=1080)
    parser.add_argument('--height', type=int, default=1920)
    parser.add_argument('--captions', choices=['burn', 'omit'], default='burn')
    parser.add_argument('--font-file', type=Path)
    parser.add_argument('--font-name')
    args = parser.parse_args()
    try:
        result = render(args.plan, args.source, args.output_dir, width=args.width, height=args.height,
                        captions=args.captions, transcript_path=args.transcript, font_file=args.font_file, font_name=args.font_name)
        print(f'PASS: {len(result["checks"])} render checks; delivery REVIEW; editorial/human QA NOT_RUN')
        return 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
