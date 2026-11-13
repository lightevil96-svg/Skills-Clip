"""Tests for original procedural SFX and evidence-linked audio rendering."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_sfx_pack import generate_pack
from render_audio_events import build_filtergraph, render_audio_events, validate_audio_plan


def edit_fixture(source_hash: str, duration: float = 2.0):
    return {
        'source': {'sha256': source_hash},
        'shots': [
            {'id': 's1', 'in_s': 0.0, 'out_s': 1.0, 'output_in_s': 0.0, 'output_out_s': 1.0,
             'editorial': {'camera': {'action': 'pan'}}},
            {'id': 's2', 'in_s': 1.0, 'out_s': 2.0, 'output_in_s': 1.0, 'output_out_s': 2.0,
             'editorial': {'camera': {'action': 'hold'}}},
        ],
        'editorial': {'evidence': [
            {'id': 'ev-motion', 'status': 'VERIFIED', 'method': 'visual-inspection',
             'in_s': 0.25, 'out_s': 0.55, 'observation': 'Avatar makes a visible head movement.'},
            {'id': 'ev-word', 'status': 'VERIFIED', 'method': 'audio-review'},
        ]},
    }


def audio_fixture(asset_path: str, asset_hash: str, source_hash: str, duration: float = 2.0):
    return {
        'schema_version': '1.0', 'project_id': 'synthetic-audio-test',
        'source_sha256': source_hash, 'output_duration_s': duration,
        'assets': [{'id': 'soft-pop', 'path': asset_path,
                    'source': 'test-generated', 'license': 'test-only', 'sha256': asset_hash}],
        'events': [
            {'id': 'sfx-motion', 'trigger': 'motion', 'at_s': 0.35, 'duration_s': 0.14,
             'asset_id': 'soft-pop', 'gain_db': -18, 'evidence_ids': ['ev-motion'],
             'reason': 'A visible camera movement receives one restrained accent.'},
        ],
        'mix': {'voice_priority': True,
                'ducking': {'enabled': True, 'threshold_db': -30, 'ratio': 2.5,
                            'attack_ms': 10, 'release_ms': 180},
                'limiter_ceiling': 0.95},
    }


class GeneratorTests(unittest.TestCase):
    def test_pack_generates_six_valid_mono_wavs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'sfx'
            manifest = generate_pack(root)
            self.assertEqual(len(manifest['assets']), 6)
            for item in manifest['assets']:
                path = root / item['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])
                with wave.open(str(path), 'rb') as wav:
                    self.assertEqual(wav.getframerate(), 48_000)
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertGreater(wav.getnframes(), 100)

    def test_generator_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'sfx'
            generate_pack(root)
            with self.assertRaises(FileExistsError):
                generate_pack(root)


class GraphTests(unittest.TestCase):
    def test_filtergraph_has_voice_sidechain_and_limiter(self):
        event = {'id': 'one', 'at_s': .5, 'duration_s': .2, '_gain_db': -18,
                 '_fade_in_s': .01, '_fade_out_s': .04}
        graph = build_filtergraph([event], has_audio=True, duration=2.0,
                                  ducking={'enabled': True, 'threshold_db': -30,
                                           'ratio': 2.5, 'attack_ms': 10, 'release_ms': 180},
                                  limiter_ceiling=.95)
        self.assertIn('sidechaincompress', graph)
        self.assertIn('adelay=500:all=1', graph)
        self.assertIn('alimiter=limit=0.9500', graph)

    def test_filtergraph_can_create_audio_for_silent_video(self):
        graph = build_filtergraph([], has_audio=False, duration=2.0,
                                  ducking={'enabled': False}, limiter_ceiling=.95)
        self.assertIn('anullsrc', graph)
        self.assertIn('amix=inputs=1', graph)


class ValidationTests(unittest.TestCase):
    def test_rejects_unverified_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = generate_pack(root / 'sfx')
            asset = pack['assets'][0]
            plan = edit_fixture('a' * 64)
            plan['editorial']['evidence'][0]['status'] = 'CANDIDATE'
            audio = audio_fixture(f'sfx/{asset["path"]}', asset['sha256'], 'a' * 64)
            with self.assertRaisesRegex(ValueError, 'not verified'):
                validate_audio_plan(audio, plan, asset_root=root)

    def test_rejects_event_beyond_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = generate_pack(root / 'sfx')
            asset = pack['assets'][0]
            plan = edit_fixture('a' * 64)
            audio = audio_fixture(f'sfx/{asset["path"]}', asset['sha256'], 'a' * 64)
            audio['events'][0]['at_s'] = 1.95
            audio['events'][0]['duration_s'] = .2
            with self.assertRaisesRegex(ValueError, 'extends beyond'):
                validate_audio_plan(audio, plan, asset_root=root)

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = generate_pack(root / 'sfx')
            asset = pack['assets'][0]
            plan = edit_fixture('a' * 64)
            audio = audio_fixture('../outside.wav', asset['sha256'], 'a' * 64)
            with self.assertRaises((ValueError, FileNotFoundError)):
                validate_audio_plan(audio, plan, asset_root=root)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg/FFprobe unavailable')
class RenderIntegrationTests(unittest.TestCase):
    def test_render_adds_sfx_and_preserves_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.mp4'
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                            'color=c=blue:s=180x320:r=30:d=2', '-f', 'lavfi', '-i',
                            'sine=frequency=220:sample_rate=48000:duration=2', '-c:v', 'libx264',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(source)], check=True)
            pack = generate_pack(root / 'audio-assets')
            asset = pack['assets'][0]
            source_hash = 'a' * 64
            edit_plan = edit_fixture(source_hash)
            audio_plan = audio_fixture(f'audio-assets/{asset["path"]}', asset['sha256'], source_hash)
            edit_path = root / 'edit-plan.json'
            audio_path = root / 'audio-design.json'
            edit_path.write_text(json.dumps(edit_plan), encoding='utf-8')
            audio_path.write_text(json.dumps(audio_plan), encoding='utf-8')
            result = render_audio_events(source, audio_path, edit_path, root / 'out')
            self.assertEqual(result['render_status'], 'PASS')
            self.assertEqual(len(result['events_applied']), 1)
            self.assertTrue((root / 'out' / 'preview-with-sfx.mp4').exists())


if __name__ == '__main__':
    unittest.main()

