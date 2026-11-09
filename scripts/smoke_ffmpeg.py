#!/usr/bin/env python3
"""Exercise a synthetic pan, ASS burn-in and portable Bash package on this build.

This is a production-tool smoke test, not a VTuber render engine or editorial eval.
No user footage is required or included. Real-footage and listening checks remain
NOT_RUN. Outputs are temporary unless --output-dir is supplied.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ASS = '''[Script Info]
ScriptType: v4.00+
PlayResX: 180
PlayResY: 320
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,2,8,8,40,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.20,0:00:01.70,Default,,0,0,0,,SYNTHETIC TEST
'''
RENDER = '''#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo 'Usage: render.sh SOURCE OUTPUT' >&2
  exit 2
fi
clip_source="$1"
clip_output="$2"
clip_package_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$clip_package_dir"
ffmpeg -nostdin -hide_banner -y -i "$clip_source" \\
  -vf "crop=100:180:x=20+60*t:y=0,scale=180:320:flags=lanczos,setsar=1,subtitles=captions.ass,format=yuv420p" \\
  -map 0:v:0 -map 0:a:0 -t 2 -c:v libx264 -preset fast -crf 18 \\
  -c:a aac -b:a 128k -ar 48000 -ac 2 -movflags +faststart "$clip_output"
'''


def run_smoke(directory):
    directory=Path(directory).resolve()
    directory.mkdir(parents=True,exist_ok=True)
    log=[]

    def run(args, name, cwd=None):
        result=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=60)
        log.append({'name':name,'argv':list(map(str,args)),'returncode':result.returncode})
        (directory/f'{name}.log').write_text(result.stdout+'\n'+result.stderr)
        if result.returncode:
            raise RuntimeError(f'{name} failed; inspect {directory/name}.log')
        return result.stdout

    for binary in ('ffmpeg','ffprobe','bash'):
        if not shutil.which(binary):
            raise RuntimeError(f'Required tool missing: {binary}')
    version=run(['ffmpeg','-version'],'version').splitlines()[0]
    source=directory/'source with spaces.mp4'
    run(['ffmpeg','-nostdin','-hide_banner','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=30:duration=2',
         '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=2','-c:v','libx264','-pix_fmt','yuv420p',
         '-c:a','aac','-shortest',str(source)],'generate-source')
    package=directory/'package with spaces';package.mkdir(exist_ok=True)
    (package/'captions.ass').write_text(ASS)
    (package/'render.sh').write_text(RENDER)
    (package/'README.txt').write_text('Synthetic 320x180 two-second fixture only. Run bash render.sh ABSOLUTE_SOURCE ABSOLUTE_OUTPUT. Requires FFmpeg with libx264 and libass. No source included. Not an EDL renderer.\n')
    archive=directory/'synthetic-package.zip'
    allowed=('render.sh','captions.ass','README.txt')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in allowed:z.write(package/name,name)
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(allowed):raise RuntimeError('Unexpected archive entry')
        if any(hashlib.sha256(z.read(n)).hexdigest()==source_hash for n in z.namelist()):
            raise RuntimeError('Source media leaked into ZIP')
        extracted=directory/'extracted package';z.extractall(extracted)
    output=directory/'output with spaces.mp4'
    run(['bash',str(extracted/'render.sh'),str(source),str(output)],'render-package',cwd='/tmp')
    raw=run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)],'probe')
    probe=json.loads(raw)
    (directory/'probe.json').write_text(json.dumps(probe,indent=2)+'\n')
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    checks={
        'vertical_dimensions':(video['width'],video['height'])==(180,320),
        'h264_yuv420p':video['codec_name']=='h264' and video['pix_fmt']=='yuv420p',
        'fps_and_frame_count':video['r_frame_rate']=='30/1' and int(video['nb_frames'])==60,
        'aac_48k_stereo':audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and audio['channels']==2,
        'duration':abs(float(probe['format']['duration'])-2)<=.12,
        'stream_start_delta':abs(float(video['start_time'])-float(audio['start_time']))<=.08,
        'stream_duration_delta':abs(float(video['duration'])-float(audio['duration']))<=.12,
        'package_allowlist_source_excluded':True,
        'bash_path_with_spaces':True,
    }
    run(['ffmpeg','-nostdin','-v','error','-y','-ss','0.8','-i',str(output),'-frames:v','1',str(directory/'preview.png')],'extract-preview')
    run(['ffmpeg','-nostdin','-v','error','-i',str(output),'-f','null','-'],'decode-output')
    checks['full_decode']=True
    report={'kind':'synthetic-technical-smoke','status':'PASS' if all(checks.values()) else 'FAIL',
            'ffmpeg_version':version,'checks':checks,'commands':log,
            'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'not_run':['real-footage gates 1–8','editorial scenarios E01–E12','human listening','Windows batch','Colab runtime','other FFmpeg builds','automatic tracking','EDL-to-render compilation'],
            'limitations':['ASS burned during command execution; inspect preview for visual readability.',
                           'Stream timestamps are not proof of perceptual lip sync.',
                           'Small synthetic fixture is not a quality benchmark for 1080x1920 VTuber footage.']}
    (directory/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not all(checks.values()):raise RuntimeError('Smoke output failed one or more probe checks')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    try:
        if args.output_dir:
            report=run_smoke(args.output_dir)
        else:
            with tempfile.TemporaryDirectory(prefix='skills-clip-smoke-') as directory:
                report=run_smoke(directory)
        print(f'PASS: {len(report["checks"])} synthetic technical checks on {report["ffmpeg_version"]}')
        print('NOT_RUN: real-footage editorial assessment, human listening, Windows and Colab.')
        return 0
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
