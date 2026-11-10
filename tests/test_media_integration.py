"""Real FFmpeg execution on generated patterns. No model or human review claims."""
import copy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from asr_bridge import import_file
from inspect_source import inspect
from media_tools import check_cfr, probe, run, source_record, write_json
from render_edl import render
from verify_evidence import verify_manifest
from test_production import caption_fixture, plan_fixture


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'NOT_RUN: FFmpeg/FFprobe unavailable')
class MediaIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='clip integration ')
        cls.root = Path(cls.temp.name)
        cls.source = cls.root/'source & [spaces].mp4'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-f', 'lavfi', '-i',
             'testsrc2=size=320x180:rate=30:duration=4', '-f', 'lavfi', '-i',
             r'aevalsrc=0.2*sin(2*PI*(440+440*gte(t\,2))*t):s=48000:d=4',
             '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', cls.source])
        cls.record = source_record(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def work(self):
        return Path(tempfile.mkdtemp(prefix='case ', dir=self.root))

    def render_plan(self, directory, plan, **kwargs):
        path = directory/'plan.json'
        write_json(path, plan)
        return render(path, self.source, directory/'render output', width=180, height=324, **kwargs)

    def pixels(self, path, at, filters='null'):
        result = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-ss', str(at),
            '-vf', filters, '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
            capture_output=True, check=True, timeout=60)
        self.assertTrue(result.stdout)
        return result.stdout

    def compare_crop(self, rendered, output_time, source_time, x):
        expected = self.pixels(self.source, source_time, f'crop=100:180:{x}:0:exact=1,scale=180:324:flags=lanczos')
        actual = self.pixels(rendered, output_time)
        self.assertEqual(len(actual), len(expected))
        error = sum(abs(a-b) for a, b in zip(actual, expected))/len(actual)
        self.assertLess(error, 12, f'Crop/source timing pixel error: {error}')

    def test_inspection_manifest_and_tamper_detection(self):
        directory = self.work()/'inspection'
        result = inspect(self.source, directory, start=.5, end=2.5, frames=3)
        self.assertEqual(result['semantic_review'], 'NOT_RUN')
        self.assertEqual(verify_manifest(directory/'manifest.json', self.source)['files_checked'], 4)
        (directory/'frame-01.png').write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            verify_manifest(directory/'manifest.json', self.source)

    def test_inspection_boundaries(self):
        with self.assertRaisesRegex(ValueError, 'inside'):
            inspect(self.source, self.work()/'bad', start=-1, end=1)
        with self.assertRaisesRegex(ValueError, '1–12'):
            inspect(self.source, self.work()/'bad', start=0, end=1, frames=13)

    def test_import_real_file_with_synthetic_asr_json(self):
        directory = self.work()
        raw = directory/'raw.json'
        write_json(raw, {'segments': [{'words': [{'word': 'synthetic', 'start': .1, 'end': .5}]}]})
        transcript = import_file(raw, self.source, directory/'import output', language='en',
                                 model='test-only-no-model-executed', offset=1, content_kind='synthetic')
        self.assertEqual(transcript['words'][0]['start'], 1.1)
        self.assertEqual(transcript['source_sha256'], self.record['sha256'])
        self.assertEqual(transcript['import_provenance']['engine_run'], 'NOT_RUN')

    def test_render_cuts_and_source_pixels(self):
        directory = self.work()
        receipt = self.render_plan(directory, plan_fixture(self.record), captions='omit')
        self.assertTrue(all(receipt['checks'].values()))
        self.assertEqual(receipt['delivery_status'], 'REVIEW')
        output = directory/'render output/preview.mp4'
        self.compare_crop(output, .4, .4, 20)
        self.compare_crop(output, 1.4, 2.4, 120)
        # Distinct source tones confirm chronological audio cut mapping, not just stream presence.
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 's16le',
                              '-ac', '1', '-ar', '48000', '-'], capture_output=True, check=True).stdout
        import array
        samples = array.array('h', raw)
        if sys.byteorder != 'little':
            samples.byteswap()
        def crossings(at):
            excerpt = samples[int(at*48000):int((at+.25)*48000)]
            return sum(a <= 0 < b for a, b in zip(excerpt, excerpt[1:]))
        self.assertAlmostEqual(crossings(.3), 110, delta=3)
        self.assertAlmostEqual(crossings(1.3), 220, delta=3)

    def test_render_pan_easing_intermediate_frame(self):
        directory = self.work()
        plan = plan_fixture(self.record)
        shot = plan['shots'][0]
        shot['editorial']['camera'].update(action='pan', keyframes=[
            {'at_s': 0, 'crop': shot['crop'], 'easing': 'ease-in-out'},
            {'at_s': 1, 'crop': dict(shot['crop'], x=80), 'easing': 'linear'}])
        receipt = self.render_plan(directory, plan, captions='omit')
        self.assertEqual(receipt['render_status'], 'PASS')
        self.compare_crop(directory/'render output/preview.mp4', .2, .2, 26)

    def test_caption_burn_changes_expected_region(self):
        font_candidates = [(Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), 'DejaVu Sans'),
                           (Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts/arial.ttf', 'Arial')]
        font = next(((p, name) for p, name in font_candidates if p.exists()), None)
        if font is None:
            self.skipTest('NOT_RUN: no test font available')
        directory = self.work()
        plan = plan_fixture(self.record)
        transcript = caption_fixture(plan)
        transcript_path = directory/'transcript.json'
        write_json(transcript_path, transcript)
        receipt = self.render_plan(directory, plan, captions='burn', transcript_path=transcript_path,
                                   font_file=font[0], font_name=font[1])
        self.assertEqual(receipt['render_status'], 'PASS')
        actual = self.pixels(directory/'render output/preview.mp4', .4, 'crop=120:40:30:215')
        plain = self.pixels(self.source, .4, 'crop=100:180:20:0,scale=180:324:flags=lanczos,crop=120:40:30:215')
        self.assertGreater(sum(abs(a-b) for a, b in zip(actual, plain))/len(actual), 2)

    def test_wrong_source_and_existing_output_rejected(self):
        directory = self.work()
        plan = plan_fixture(self.record)
        plan['source'] = dict(plan['source'], sha256='0'*64)
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.render_plan(directory, plan, captions='omit')
        directory = self.work()
        (directory/'render output').mkdir()
        with self.assertRaises(FileExistsError):
            self.render_plan(directory, plan_fixture(self.record), captions='omit')

    def test_no_audio_source_render(self):
        directory = self.work()
        silent = directory/'silent.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-i', self.source, '-map', '0:v:0', '-c', 'copy', silent])
        plan = plan_fixture(source_record(silent))
        write_json(directory/'plan.json', plan)
        receipt = render(directory/'plan.json', silent, directory/'silent output',
                         width=180, height=324, captions='omit')
        self.assertEqual(receipt['render_status'], 'PASS')
        self.assertFalse(any(s['codec_type'] == 'audio' for s in probe(directory/'silent output/preview.mp4')['streams']))

    def test_nonzero_stream_start_rejected(self):
        data = probe(self.source)
        data['streams'][0]['start_time'] = '0.2'
        with self.assertRaisesRegex(ValueError, 'Non-zero'):
            check_cfr(data, self.source, 0, 3)

    def test_actual_variable_rate_source_rejected(self):
        directory = self.work()
        vfr = directory/'vfr.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-i', self.source, '-an', '-vf',
             "select='not(eq(mod(n,5),1))'", '-fps_mode', 'vfr', '-c:v', 'libx264', vfr])
        with self.assertRaisesRegex(ValueError, 'frame rate|variable-rate'):
            check_cfr(probe(vfr), vfr, 0, 3)

    def test_native_fractional_fps_preserved(self):
        directory = self.work()
        source = directory/'ntsc.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
             'testsrc2=size=320x180:rate=30000/1001:duration=4', '-c:v', 'libx264', source])
        record = source_record(source)
        plan = plan_fixture(record)
        # 30 native frames last 1.001 seconds; preserve that clock in every record.
        for shot in plan['shots']:
            for key in ('in_s', 'out_s', 'output_in_s', 'output_out_s'):
                shot[key] *= 1.001
        plan['clip']['out_s'] *= 1.001
        for collection in ('evidence', 'narrative_beats'):
            for item in plan['editorial'][collection]:
                item['in_s'] *= 1.001
                item['out_s'] *= 1.001
        write_json(directory/'plan.json', plan)
        result = render(directory/'plan.json', source, directory/'ntsc output', width=180, height=324, captions='omit')
        self.assertTrue(result['checks']['native_fps'])
        video = probe(directory/'ntsc output/preview.mp4')['streams'][0]
        self.assertEqual(video['avg_frame_rate'], '30000/1001')
        self.assertEqual(video['nb_frames'], '60')


if __name__ == '__main__':
    unittest.main()
