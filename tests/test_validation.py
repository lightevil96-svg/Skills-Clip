"""Synthetic declarations exercise validation, never establish media evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_artifacts import load_json, validate
from validate_skill_repo import check_structure


def example(name):
    return load_json(ROOT/'examples'/name)


def receipt(word, method='human-listen'):
    return {'method':method,'reviewer':'SYNTHETIC TEST REVIEWER','tool':'test-double',
            'reviewed_at':'2026-11-09T00:00:00Z','source_ref':'synthetic-not-footage.mp4',
            'source_in_s':word['start'],'source_out_s':word['end'],'language':'id',
            'context_checked':True,'uncertainties':[],'evidence_ref':'test-only-receipt'}


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.plan = example('edit-plan.editorial.example.json')
        self.transcript = example('transcript.editorial.example.json')

    def problems(self, plan=None, **kwargs):
        return validate('edit-plan', self.plan if plan is None else plan,
                        transcript=kwargs.pop('transcript', self.transcript), **kwargs)[0]

    def rejects(self, fragment, **kwargs):
        errors = self.problems(**kwargs)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def verify_words(self, method='human-listen'):
        for word in self.transcript['words']:
            word['verification_status'] = 'VERIFIED'
            word['verification'] = receipt(word, method)

    def ready_declarations(self):
        """Build complete test-only declarations, not real inspected content."""
        self.verify_words()
        self.plan['project']['content_kind'] = 'real'
        self.plan['source']['sha256'] = 'a'*64
        self.plan['clip']['context_preserved'] = True
        self.plan['routing']['unknowns'] = []
        self.plan['editorial']['unknowns'] = []
        self.plan['editorial']['capabilities'].update(audio_source_access=True,visual_source_access=True)
        for evidence in self.plan['editorial']['evidence']:
            evidence['status'] = 'VERIFIED'
        for speaker in self.plan['speakers']:
            speaker.update(mapping_status='VERIFIED',evidence_ids=['e1','e2'])
        self.transcript['content_kind'] = 'real'
        self.transcript['source_sha256'] = 'a'*64
        for speaker in self.transcript['speakers']:
            speaker.update(mapping_status='VERIFIED',mapping_evidence=['test-turn-1','test-turn-2'])
        for cap in self.plan['captions']:
            cap['verification_status'] = 'VERIFIED'
            cap['position']['safe_area_checked'] = True
        self.plan['qa'] = {'status':'PASS','checks':[{'name':'synthetic check','status':'PASS'}]}
        self.plan['render'] = {'output_path':'test-output.mp4','output_sha256':'b'*64,
            'ffmpeg_version':'test-double','command_ref':'test-command','probe_ref':'test-probe'}
        review = example('editorial-review.example.json')
        review.update(review_mode='human',status='PASS',reviewer='TEST REVIEWER',reviewed_artifact='test-output.mp4')
        for metric in review['metrics'].values():
            metric.update(status='PASS',score=3,evidence_refs=['synthetic-review-note'],observation='Synthetic declaration accepted by shape checks.',next_action='none')
        review['human_review'] = {'status':'PASS','reviewer':'TEST REVIEWER','evidence_refs':['synthetic-listen-note']}
        review['technical_checks'] = [{'name':'synthetic-probe','status':'PASS','evidence_ref':'synthetic-log'}]
        return review

    def test_all_examples_validate(self):
        for name, kind in [('edit-plan.example.json','edit-plan'),('transcript.example.json','transcript'),
                           ('style-profile.example.json','style-profile'),('editorial-review.example.json','editorial-review')]:
            with self.subTest(name=name):
                self.assertEqual(validate(kind,example(name))[0], [])
        self.assertEqual(self.problems(), [])

    def test_original_examples_unchanged(self):
        for name, expected in [('edit-plan.example.json','4f483babf97a23cdc9037727c7be6d6d76316c4f'),
                               ('transcript.example.json','29bc4db33f64ac7d155f3938ee434b43a3d278d7')]:
            raw=(ROOT/'examples'/name).read_bytes()
            self.assertEqual(hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest(),expected)

    def test_legacy_not_final(self):
        self.assertTrue(validate('edit-plan',example('edit-plan.example.json'),stage='final')[0])

    def test_schema_rejects_wrong_type_and_unknown_version(self):
        for key, value in [('schema_version','3.0'),('shots','not a list')]:
            plan=copy.deepcopy(self.plan);plan[key]=value
            self.assertTrue(self.problems(plan))

    def test_duplicate_ids(self):
        self.plan['shots'][1]['id']=self.plan['shots'][0]['id']
        self.rejects('duplicate id')

    def test_inverted_interval(self):
        self.plan['shots'][0]['out_s']=3
        self.rejects('invalid interval')

    def test_source_bounds(self):
        self.plan['shots'][-1]['out_s']=21
        self.rejects('outside source')

    def test_output_gap_and_overlap(self):
        for value in [1.9,2.1]:
            self.plan['shots'][1]['output_in_s']=value
            self.rejects('output timeline gap/overlap')

    def test_reversed_causality(self):
        self.plan['shots'][1]['in_s']=5
        self.rejects('source chronology')

    def test_crop_bounds(self):
        self.plan['shots'][0]['crop']['x']=1800
        self.rejects('crop outside source')

    def test_dangling_references(self):
        for field in ['caption_ids','overlay_ids']:
            plan=copy.deepcopy(self.plan);plan['shots'][0][field]=['missing']
            self.assertTrue(self.problems(plan))
        self.plan['shots'][0]['editorial']['source_evidence_ids']=['missing']
        self.rejects('dangling reference')

    def test_invalid_route(self):
        self.plan['routing']['primary_route']='imaginary-tool'
        self.rejects('unknown primary route')

    def test_conversation_split_requires_explicit_override(self):
        self.plan['shots'][0]['layout']='stacked'
        self.rejects('conversation layout')
        self.plan['project']['composition_override']={'user_instruction':'TEST: request this layout','reason':'Explicit project exception'}
        self.assertEqual(self.problems(),[])

    def test_active_speaker_follow(self):
        self.plan['shots'][0]['primary_subject']='S2'
        self.rejects('follow active speaker')

    def test_shared_shot_requires_interaction(self):
        self.plan['shots'][0]['layout']='shared-two-shot'
        self.rejects('shared shot lacks')

    def test_motion_endpoints(self):
        self.plan['shots'][0]['editorial']['camera']['action']='pan'
        self.rejects('endpoint keyframes')

    def test_keyframe_bounds_and_order(self):
        cam=self.plan['shots'][0]['editorial']['camera']
        cam['keyframes']=[{'at_s':3,'crop':{'x':0,'y':0,'w':608,'h':1080},'easing':'linear'}]
        self.rejects('keyframe outside shot')
        cam['keyframes']=[dict(cam['keyframes'][0],at_s=0)]*2
        self.rejects('unique increasing times')

    def test_effect_choice_and_asset(self):
        d=self.plan['shots'][0]['editorial']['effect_decision']
        d['choice']='apply';self.rejects('effect choice')
        d['effects']=[{'type':'meme','start_s':0,'end_s':1,'purpose':'test','evidence_ids':['e1'],'asset_id':'missing','implementation':'test'}]
        self.rejects('effect asset')

    def test_audio_flags_match_decisions(self):
        self.plan['audio']['sfx_used']=True
        self.rejects('sfx_used disagrees')
        self.plan['audio']['sfx_used']=False
        self.plan['audio']['bgm_used']=True
        self.rejects('bgm_used disagrees')

    def test_retime_requires_map(self):
        self.plan['shots'][-1]['output_out_s']=9
        self.rejects('retiming requires')

    def test_explicit_speed_map(self):
        shot=self.plan['shots'][-1]
        shot['output_out_s']=10
        shot['time_map']=[{'kind':'play','source_in_s':10,'source_out_s':12,'output_in_s':6,'output_out_s':10}]
        self.assertEqual(self.problems(),[])

    def test_explicit_freeze_and_play_map(self):
        shot=self.plan['shots'][-1];shot['output_out_s']=9
        shot['time_map']=[{'kind':'freeze','source_in_s':10,'source_out_s':10,'output_in_s':6,'output_out_s':7},
                          {'kind':'play','source_in_s':10,'source_out_s':12,'output_in_s':7,'output_out_s':9}]
        self.assertEqual(self.problems(),[])
        shot['time_map'][0]['source_out_s']=11
        self.rejects('freeze must map')

    def test_discontinuous_time_map(self):
        self.plan['shots'][0]['time_map']=[{'kind':'play','source_in_s':4.1,'source_out_s':6,'output_in_s':0,'output_out_s':2}]
        self.rejects('discontinuous time_map')

    def test_caption_text_integrity(self):
        self.plan['captions'][0]['text']='Aku menyentuh tombol.'
        self.rejects('text differs')

    def test_caption_word_order(self):
        self.plan['captions'][0]['word_ids'].reverse()
        self.rejects('word order changed')

    def test_caption_speaker(self):
        self.plan['captions'][0]['speaker_id']='S2'
        self.rejects('speaker disagrees')

    def test_caption_mapped_clock(self):
        self.plan['captions'][1]['start_s']=6.2
        self.plan['captions'][1]['end_s']=6.7
        self.rejects('does not cover spoken word')

    def test_truncated_word(self):
        self.plan['shots'][0]['in_s']=4.3
        self.rejects('word removed or truncated')

    def test_emphasis_requires_same_words(self):
        self.plan['captions'][0]['emphasis_word_ids']=['w5']
        self.rejects('emphasis: dangling')

    def test_raw_word_cannot_be_verified_caption(self):
        self.plan['captions'][0]['verification_status']='VERIFIED'
        self.rejects('unverified word used')

    def test_translation_requires_language_review(self):
        self.verify_words()
        cap=self.plan['captions'][0];cap.update(kind='translation',text='I did not touch the button.',verification_status='VERIFIED')
        self.rejects('verification receipt')

    def test_asr_not_verified_evidence(self):
        self.plan['editorial']['evidence'][0].update(method='asr',status='VERIFIED')
        self.rejects('ASR evidence cannot')

    def test_perception_access_honesty(self):
        self.plan['editorial']['evidence'][0].update(status='VERIFIED')
        self.rejects('visual evidence requires')

    def test_word_verification_requires_receipt(self):
        self.transcript['words'][0]['verification_status']='VERIFIED'
        self.assertTrue(validate('transcript',self.transcript)[0])

    def test_direct_audio_policy(self):
        self.verify_words('direct-audio-review')
        self.assertTrue(validate('transcript',self.transcript)[0])
        self.transcript.update(verification_policy='source-audio-review',audio_source_access=True)
        self.assertEqual(validate('transcript',self.transcript)[0],[])

    def test_user_confirmation_cannot_be_claimed_from_agent(self):
        self.verify_words()
        self.transcript['words'][0]['verification_status']='USER_CONFIRMED'
        self.assertTrue(validate('transcript',self.transcript)[0])

    def test_receipt_must_cover_source_and_resolve_uncertainty(self):
        self.verify_words()
        v=self.transcript['words'][0]['verification']
        for field,value in [('source_ref','different.mp4'),('source_in_s',5),('uncertainties',['unclear name']),('context_checked',False),('reviewed_at','yesterday')]:
            previous=v[field];v[field]=value
            self.assertTrue(validate('transcript',self.transcript)[0],field)
            v[field]=previous

    def test_overlap_is_allowed(self):
        w=copy.deepcopy(self.transcript['words'][0]);w.update(id='overlap',start=4.3,end=4.6,speaker_id='S2')
        self.transcript['words'].insert(1,w)
        self.assertEqual(validate('transcript',self.transcript)[0],[])

    def test_style_reference_unavailable(self):
        style=example('style-profile.example.json');style['traits']['font']['status']='VERIFIED'
        self.assertTrue(validate('style-profile',style)[0])

    def test_sound_style_needs_audio(self):
        style=example('style-profile.example.json');style['references'][0]['available']=True
        style['traits']['sfx'].update(status='VERIFIED',method='visual-inspection')
        self.assertTrue(validate('style-profile',style)[0])

    def test_automated_editorial_score_rejected(self):
        report=example('editorial-review.example.json')
        report['metrics']['timing_precision'].update(status='PASS',score=4,evidence_refs=['metadata'])
        self.assertTrue(validate('editorial-review',report)[0])

    def test_unrun_score_rejected(self):
        report=example('editorial-review.example.json');report['metrics']['audio_comfort']['score']=3
        self.assertTrue(validate('editorial-review',report)[0])

    def test_missing_human_review_blocks_final(self):
        report=self.ready_declarations();report['human_review']['status']='NOT_RUN'
        self.rejects('human listening',stage='final',review=report)

    def test_synthetic_examples_block_final(self):
        self.rejects('synthetic example',stage='final')

    def test_complete_declarations_are_structurally_accepted(self):
        report=self.ready_declarations()
        self.assertEqual(self.problems(stage='final',review=report),[])

    def test_review_must_identify_output(self):
        report=self.ready_declarations();report['reviewed_artifact']='unrelated.mp4'
        self.rejects('rendered artifact',stage='final',review=report)

    def test_open_revision_blocks_final(self):
        report=self.ready_declarations();report['revisions']=[{'issue':'caption too early','at_s':0,'action':'retime','status':'open','recheck_evidence':None}]
        self.rejects('open revisions',stage='final',review=report)

    def test_low_score_requires_repair(self):
        report=self.ready_declarations();report['metrics']['audio_comfort']['score']=1
        self.assertTrue(validate('editorial-review',report)[0])

    def test_low_score_cannot_pass_even_with_planned_repair(self):
        report=self.ready_declarations()
        report['metrics']['audio_comfort'].update(score=1,next_action='Lower the masking music and listen again.')
        self.assertTrue(validate('editorial-review',report)[0])

    def test_core_review_cannot_be_skipped(self):
        report=self.ready_declarations()
        report['metrics']['storytelling_clarity'].update(status='SKIP',score=None)
        self.assertTrue(validate('editorial-review',report)[0])

    def test_final_speaker_mapping_and_crop_required(self):
        report=self.ready_declarations()
        self.plan['speakers'][0]['mapping_status']='UNKNOWN'
        self.rejects('active speaker mapping unresolved',stage='final',review=report)
        self.plan['speakers'][0]['mapping_status']='VERIFIED'
        self.plan['shots'][0]['crop']=None
        self.rejects('requires crop coordinates',stage='final',review=report)

    def test_duplicate_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.json'
            for raw in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}','{"a":1e999}']:
                path.write_text(raw)
                with self.assertRaises(ValueError): load_json(path)

    def test_cli_nonzero_on_invalid_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.json';path.write_text('{}')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/validate_artifacts.py'),'edit-plan',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('FAIL:',result.stdout)


class RepositoryTests(unittest.TestCase):
    def test_repository_structure(self):
        self.assertEqual(check_structure(),[])

    def test_broken_link_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'repo'
            shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','test-results'))
            with (root/'README.md').open('a') as file: file.write('\n[Broken](absent.md)\n')
            self.assertTrue(any('broken link absent.md' in e for e in check_structure(root)))


if __name__ == '__main__':
    unittest.main()
