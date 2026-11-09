"""Model-free regression checks. Synthetic data never verifies real dialogue."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from asr_bridge import convert
from media_tools import confined_file, new_directory, write_json
from render_edl import check_supported, frame_number, make_ass, motion_expression
from validate_artifacts import load_json, validate


def source_fixture():
    return {'path': 'synthetic.mp4', 'sha256': 'a'*64, 'duration_s': 4,
            'width': 320, 'height': 180, 'fps': 30, 'audio_present': True}


def plan_fixture(source=None):
    plan = load_json(ROOT/'examples/edit-plan.editorial.example.json')
    plan['source'] = source or source_fixture()
    plan['clip'].update(in_s=0, out_s=3)
    plan['captions'] = []
    plan['shots'] = plan['shots'][:2]
    plan['editorial']['evidence'] = plan['editorial']['evidence'][:2]
    plan['editorial']['narrative_beats'] = plan['editorial']['narrative_beats'][:2]
    for index, shot in enumerate(plan['shots']):
        start = index * 2
        shot.update(in_s=start, out_s=start+1, output_in_s=index, output_out_s=index+1,
                    crop={'x': 20+100*index, 'y': 0, 'w': 100, 'h': 180}, caption_ids=[])
        plan['editorial']['evidence'][index].update(in_s=start, out_s=start+1, source_ref=plan['source']['path'])
        plan['editorial']['narrative_beats'][index].update(in_s=start, out_s=start+1)
    return plan


def caption_fixture(plan):
    transcript = convert({'segments': [{'words': [{'word': 'TEST', 'start': .2, 'end': .6, 'speaker': 'S1'}]}]},
                         plan['source'], language='en', model='synthetic-test', content_kind='synthetic')
    word = transcript['words'][0]
    word.update(verification_status='VERIFIED', verification={
        'method': 'human-listen', 'reviewer': 'SYNTHETIC TEST DECLARATION', 'tool': 'unit-test',
        'reviewed_at': '2026-11-10T00:00:00Z', 'source_ref': plan['source']['path'],
        'source_in_s': .1, 'source_out_s': .8, 'language': 'en', 'context_checked': True,
        'uncertainties': [], 'evidence_ref': 'synthetic-receipt-not-a-human-review'})
    cap = load_json(ROOT/'examples/edit-plan.editorial.example.json')['captions'][0]
    cap.update(start_s=.2, end_s=.6, text='TEST', word_ids=['w1'], style='static-white',
               verification_status='VERIFIED', language='en')
    cap['position'] = {'x': 90, 'y': 250, 'safe_area_checked': True}
    plan['captions'] = [cap]
    plan['shots'][0]['caption_ids'] = [cap['id']]
    return transcript


class ASRBridgeTests(unittest.TestCase):
    def convert(self, raw, **kwargs):
        return convert(raw, source_fixture(), language='id', model='fixture-only', **kwargs)

    def test_raw_words_offset_and_unknown_identity(self):
        out = self.convert({'segments': [{'speaker': 'SPEAKER_00', 'words': [
            {'word': ' tidak', 'start': .2, 'end': .5, 'score': .99}]}]}, offset=1)
        self.assertEqual(out['words'][0]['start'], 1.2)
        self.assertEqual(out['words'][0]['text'], 'tidak')
        self.assertEqual(out['words'][0]['verification_status'], 'ASR_RAW')
        self.assertEqual(out['speakers'][0]['mapping_status'], 'UNKNOWN')
        self.assertFalse(out['audio_source_access'])

    def test_missing_times_retained_as_unresolved(self):
        out = self.convert({'segments': [{'words': [{'word': '£13.60'},
            {'word': 'okay', 'start': .1, 'end': .3}]}]})
        self.assertEqual(len(out['words']), 1)
        self.assertEqual(out['unresolved_words'][0]['text'], '£13.60')
        self.assertTrue(any('unresolved' in e for e in validate('transcript', out, stage='final')[0]))

    def test_segment_only_does_not_invent_word_alignment(self):
        out = self.convert({'segments': [{'text': 'Tidak menekan tombol', 'start': 0, 'end': 2}]})
        self.assertEqual(out['words'], [])
        self.assertEqual(len(out['unresolved_words']), 1)

    def test_overlap_is_preserved(self):
        out = self.convert({'segments': [{'speaker': 'B', 'words': [{'word': 'B', 'start': .3, 'end': .8}]},
                                        {'speaker': 'A', 'words': [{'word': 'A', 'start': .1, 'end': .6}]}]})
        self.assertEqual([w['speaker_id'] for w in out['words']], ['A', 'B'])
        self.assertEqual(out['words'][0]['end'], .6)

    def test_segment_word_omission_is_not_hidden(self):
        out = self.convert({'segments': [{'text': 'tidak tekan', 'words': [
            {'word': 'tekan', 'start': .1, 'end': .6}]}]})
        self.assertEqual(out['unresolved_words'][0]['text'], 'tidak tekan')
        self.assertEqual(out['words'][0]['text'], 'tekan')

    def test_invalid_timing_rejected(self):
        for start, end in [(-1, 1), (1, 1), (0, 5), (True, 1), (float('nan'), 1)]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                self.convert({'segments': [{'words': [{'word': 'x', 'start': start, 'end': end}]}]})

    def test_invalid_confidence_rejected(self):
        with self.assertRaises(ValueError):
            self.convert({'segments': [{'words': [{'word': 'x', 'start': 0, 'end': 1, 'score': 3}]}]})

    def test_invalid_offset_rejected(self):
        for offset in (-1, 5, float('inf')):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                self.convert({'segments': []}, offset=offset)

    def test_schema_checks_unresolved_and_provenance(self):
        out = self.convert({'segments': []})
        out['unresolved_words'] = [{'text': 'x'}]
        self.assertTrue(validate('transcript', out)[0])
        out['unresolved_words'] = []
        out['import_provenance'] = {'raw_sha256': 'invalid'}
        self.assertTrue(validate('transcript', out)[0])


class RendererContractTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan_fixture()

    def check(self, **kwargs):
        return check_supported(self.plan, width=180, height=324, captions=kwargs.pop('captions', 'omit'), **kwargs)

    def test_bounded_plan_supported(self):
        self.assertEqual(validate('edit-plan', self.plan)[0], [])
        self.assertEqual(self.check(), [])

    def test_unverified_caption_burn_rejected(self):
        transcript = caption_fixture(self.plan)
        self.plan['captions'][0]['verification_status'] = 'ASR_RAW'
        with self.assertRaisesRegex(ValueError, 'Unverified'):
            self.check(captions='burn', transcript=transcript)

    def test_static_verified_fixture_supported(self):
        transcript = caption_fixture(self.plan)
        self.check(captions='burn', transcript=transcript)

    def test_caption_without_transcript_rejected(self):
        caption_fixture(self.plan)
        with self.assertRaisesRegex(ValueError, 'linked transcript'):
            self.check(captions='burn')

    def test_ass_injection_rejected(self):
        for text in ('{TEST}', r'TEST\N', 'TEST\n'):
            with self.subTest(text=text):
                transcript = caption_fixture(self.plan)
                self.plan['captions'][0]['text'] = text
                transcript['words'][0]['text'] = text
                with self.assertRaisesRegex(ValueError, 'ASS/control'):
                    self.check(captions='burn', transcript=transcript)

    def test_unsupported_style_and_animation_rejected(self):
        transcript = caption_fixture(self.plan)
        self.plan['captions'][0]['animation']['movement'] = 'bounce'
        with self.assertRaises(ValueError):
            self.check(captions='burn', transcript=transcript)
        self.plan['captions'][0]['animation']['movement'] = 'none'
        self.plan['captions'][0]['style'] = 'unknown-font-treatment'
        with self.assertRaisesRegex(ValueError, 'restyling'):
            self.check(captions='burn', transcript=transcript)

    def test_off_frame_cuts_rejected(self):
        with self.assertRaisesRegex(ValueError, 'frame'):
            frame_number(.011, 30)
        self.assertEqual(frame_number(1001/30000, 30000/1001), 1)

    def test_aspect_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'aspect'):
            check_supported(self.plan, width=200, height=200, captions='omit')

    def test_assets_are_not_silently_ignored(self):
        self.plan['audio']['ducking_db'] = -6
        with self.assertRaisesRegex(ValueError, 'ducking'):
            self.check()

    def test_zoom_requires_other_renderer(self):
        shot = self.plan['shots'][0]
        shot['editorial']['camera'].update(action='punch-in', keyframes=[
            {'at_s': 0, 'crop': shot['crop'], 'easing': 'linear'},
            {'at_s': 1, 'crop': shot['crop'], 'easing': 'linear'}])
        with self.assertRaisesRegex(ValueError, 'Zoom'):
            self.check()

    def test_pan_has_explicit_endpoints(self):
        shot = self.plan['shots'][0]
        shot['editorial']['camera'].update(action='pan', keyframes=[
            {'at_s': .1, 'crop': shot['crop'], 'easing': 'ease-in-out'},
            {'at_s': .9, 'crop': shot['crop'], 'easing': 'linear'}])
        with self.assertRaisesRegex(ValueError, 'boundaries'):
            self.check()

    def test_easing_expression_is_numeric(self):
        keys = [{'at_s': 2, 'crop': {'x': 10}, 'easing': 'ease-in-out'},
                {'at_s': 3, 'crop': {'x': 30}, 'easing': 'linear'}]
        expression = motion_expression(keys, 'x', 2)
        self.assertIn('20*', expression)
        self.assertIn('clip((t-0.000000000)', expression)

    def test_ass_times_and_positions_preserved(self):
        caption_fixture(self.plan)
        ass = make_ass(self.plan, 180, 324, 'DejaVu Sans')
        self.assertIn('0:00:00.20,0:00:00.60', ass)
        self.assertIn(r'{\pos(90,250)}TEST', ass)


class FilesystemTests(unittest.TestCase):
    def test_output_never_overwrites(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(FileExistsError):
                new_directory(root)
            p = Path(root)/'data.json'
            write_json(p, {'value': 1})
            with self.assertRaises(FileExistsError):
                write_json(p, {'value': 2})
            self.assertEqual(load_json(p), {'value': 1})

    def test_evidence_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root/'inner').mkdir()
            (root/'outside.txt').write_text('x')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                confined_file(root/'inner', '../outside.txt')
            with self.assertRaisesRegex(ValueError, 'relative'):
                confined_file(root/'inner', str((root/'outside.txt').resolve()))


if __name__ == '__main__':
    unittest.main()
