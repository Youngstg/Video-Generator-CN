#!/usr/bin/env python3
"""Portable bootstrap, preflight, rendering, validation and delivery for the series."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SKILL = Path(__file__).resolve().parent.parent
SKILL_NAME = 'sebentar-paham-video'
ASSETS = SKILL / 'assets'
KINDS = {'objects', 'mouse', 'custom'}
VERSION = '2.1.1'
MOODS = {'light', 'dark'}
BACKDROPS = {'spot', 'rings', 'blobs', 'grid', 'sparkle', 'none'}
TRANSITIONS = {'dissolve', 'push', 'zoom'}
BACKDROP_CYCLE = ['spot', 'rings', 'blobs', 'grid', 'spot', 'blobs', 'sparkle']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def run(args, cwd=None):
    subprocess.run([str(x) for x in args], cwd=cwd, check=True)


def series(project):
    return read(project / 'series.json')


def selected(project, key):
    data = series(project)
    if key and key not in data:
        raise ValueError('Unknown episode key: ' + key)
    return {key: data[key]} if key else data


def input_signature(project, key):
    files = sorted(project.glob('*.py')) + [project / name for name in ('series.json', 'captions.json', 'Inter.ttf', 'JetBrainsMono.ttf')]
    files += sorted((project / 'assets').rglob('*')) if (project / 'assets').exists() else []
    files += [project / key / name for name in ('alignment.json', 'voice-manifest.json')]
    files += sorted((project / key / 'audio').glob('*'))
    h = hashlib.sha256()
    for path in files:
        if path.is_file():
            h.update(path.relative_to(project).as_posix().encode()); h.update(path.read_bytes())
    return h.hexdigest()


def doctor(_):
    report = {'python': sys.version.split()[0], 'ffmpeg': shutil.which('ffmpeg'),
              'ffprobe': shutil.which('ffprobe'), 'modules': {}, 'optional': {}}
    for module in ('PIL', 'numpy', 'scipy'):
        report['modules'][module] = importlib.util.find_spec(module) is not None
    for module in ('edge_tts', 'faster_whisper'):
        report['optional'][module] = importlib.util.find_spec(module) is not None
    if report['ffmpeg']:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        report['libx264'] = 'libx264' in r.stdout
    report['ready'] = bool(report['ffmpeg'] and report['ffprobe'] and report.get('libx264')
                           and all(report['modules'].values()))
    print(json.dumps(report, indent=2))
    if not report['ready']:
        raise SystemExit('Install requirements.txt and FFmpeg with libx264; see references/portability.md.')


def init(args):
    dest = Path(args.project).resolve()
    if dest == SKILL or SKILL in dest.parents:
        raise ValueError('Create production projects outside the installed skill.')
    if dest.exists() and any(dest.iterdir()):
        raise ValueError('Project directory must be empty; existing work is never overwritten.')
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'assets').mkdir(exist_ok=True)
    for p in (ASSETS / 'template').iterdir():
        if p.is_file():
            shutil.copy2(p, dest / p.name)
    for p in (ASSETS / 'fonts').iterdir():
        shutil.copy2(p, dest / p.name)
    history = read(Path(args.history).expanduser()) if args.history else {'episodes': []}
    number = args.number if args.number is not None else max([e['number'] for e in history['episodes']] + [0]) + 1
    if args.example:
        data = read(ASSETS / 'example-episode.json')
    else:
        beats = ['Hook', 'Latar belakang', 'Analogi', 'Mekanisme', 'Konsekuensi', 'Batasan', 'Penutup']
        s = {'number': number, 'filename': f'{number:02d}_Video_Funfact',
             'title': args.topic, 'branding': 'SEBENTAR, PAHAM.',
             'theme': read(ASSETS / 'brand.json')['palettes']['sage'],
             'scripts': [f'TODO: {beat}' for beat in beats],
             'headers': [[beat.upper(), 'TODO'] for beat in beats],
             'visuals': [{'kind': 'custom', 'subject': 'TODO: recognizable subject',
                          'features': ['TODO: distinguishing shape', 'TODO: visible detail'],
                          'action': 'TODO: visible cause and effect',
                          'purpose': beat, 'backdrop': BACKDROP_CYCLE[n],
                          # the mechanism scene is the dark focus scene; others stay light
                          **({'mood': 'dark'} if n == 3 else {})} for n, beat in enumerate(beats)],
             'minimums': [7, 10, 11, 11, 12, 11, 9], 'sources': [], 'notes': ''}
        data = {'episode': s}
    write(dest / 'series.json', data)
    write(dest / 'captions.json', {})
    for key in data:
        (dest / key / 'audio').mkdir(parents=True, exist_ok=True)
    write(dest / 'production.json', {'schema_version': 2, 'skill_version': VERSION,
          'deliverables': ['vertical_mp4', 'clean_narration_wav'],
          'budget': 'free_only', 'topic_status': 'reference_example' if args.example else 'proposed',
          'source_review': False, 'voice_review': False, 'visual_review': False,
          'final_status': 'draft', 'voice_provider': 'import',
          'note': 'Set review flags only after actually checking sources, listening, and viewing exports.'})
    write(dest / 'history.json', history)
    shutil.copy2(ASSETS / 'voice-direction.json', dest / 'voice-direction.json')
    print(str(dest))


def check(args):
    project = Path(args.project).resolve()
    from PIL import ImageFont
    font = ImageFont.truetype(str(project / 'Inter.ttf'), 48)
    try:  # measure exactly as the engine renders: Inter at weight 700, not the variable font's default 400
        font.set_variation_by_axes([700 if a['name'] == b'Weight' else a['default'] for a in font.get_variation_axes()])
    except Exception:
        pass
    all_series = series(project)
    numbers = [s['number'] for s in all_series.values()]
    if len(numbers) != len(set(numbers)):
        raise ValueError('Duplicate episode numbers in series.json.')
    filenames = [s['filename'] for s in all_series.values()]
    if len(filenames) != len(set(filenames)):
        raise ValueError('Duplicate output filenames in series.json.')
    history = read(project / 'history.json')
    for key, s in selected(project, args.key).items():
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', key):
            raise ValueError('Episode keys must be safe lowercase directory names.')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', s['filename']):
            raise ValueError('Use a safe filename with letters, digits, underscores or hyphens.')
        if not isinstance(s['number'], int) or s['number'] < 1:
            raise ValueError('Episode number must be a positive integer.')
        for old in history['episodes']:
            if old['number'] == s['number'] and old.get('filename') != s['filename']:
                raise ValueError(f'Episode number {s["number"]} is already assigned in history.json.')
            if old.get('title', '').casefold() == s['title'].casefold() and old['number'] != s['number']:
                raise ValueError('This title already exists in history.json; choose a fresh angle.')
        for field in ('scripts', 'headers', 'minimums', 'visuals'):
            if len(s[field]) != 7:
                raise ValueError(f'{key}: {field} must have seven scene entries.')
        if 'TODO' in json.dumps(s, ensure_ascii=False):
            raise ValueError('Finish the script and visuals before production; TODO found.')
        if not s.get('sources'):
            raise ValueError('Add primary source URLs before production.')
        for _, url in s['sources']:
            if not url.startswith('https://'):
                raise ValueError('Source URLs must use HTTPS.')
        for col in ('bg', 'ink', 'accent', 'soft', 'dark'):
            if not re.fullmatch(r'#[0-9A-Fa-f]{6}', s['theme'][col]):
                raise ValueError('Invalid theme color: ' + col)
        for i, head in enumerate(s['headers']):
            if len(head) != 2 or any(font.getlength(x) > 934 for x in head):
                raise ValueError(f'{key}/{i}: shorten header to two readable lines.')
        sys.path.insert(0,str(project))
        from illustrations import NAMES
        for i, v in enumerate(s['visuals']):
            if v['kind'] not in KINDS:
                raise ValueError('Use an object-led scene or implement a custom mechanism; text-card layouts are not final visuals.')
            for field in ('subject', 'action', 'purpose'):
                if not isinstance(v.get(field),str) or len(v[field].strip())<8:
                    raise ValueError(f'{key}/{i}: describe the actual {field}.')
            if not isinstance(v.get('features'),list) or len(v['features'])<2:
                raise ValueError(f'{key}/{i}: name two visible identifying features, not labels or statistics.')
            if v.get('mood','light') not in MOODS:
                raise ValueError(f'{key}/{i}: mood must be light or dark.')
            if v.get('backdrop','spot') not in BACKDROPS:
                raise ValueError(f'{key}/{i}: backdrop must be one of {sorted(BACKDROPS)}.')
            if v.get('transition','dissolve') not in TRANSITIONS:
                raise ValueError(f'{key}/{i}: transition must be one of {sorted(TRANSITIONS)}.')
            if 'focus' in v and (not isinstance(v['focus'], list) or len(v['focus']) != 2):
                raise ValueError(f'{key}/{i}: focus must be [x, y].')
            if v['kind']=='mouse' and v.get('phase') not in {'overview','light','sampling','compare','compute','glass','ending'}:
                raise ValueError('Unknown mouse example phase.')
            if v['kind']=='objects':
                objects=v.get('objects',[])
                if not 1<=len(objects)<=6:raise ValueError('Use one to six actual objects per scene.')
                ids=[o['id'] for o in objects]
                if len(set(ids))!=len(ids):raise ValueError('Object IDs must be unique within a scene.')
                if not v.get('links') and not any(o.get('motion',{}).get('kind') in ('move','orbit') for o in objects):
                    raise ValueError('Add a meaningful state change, movement or directed signal; static objects are not a motion scene.')
                for o in objects:
                    if ('sprite' in o)==('asset' in o):raise ValueError('Choose one sprite or one asset per object.')
                    if o.get('sprite') and o['sprite'] not in NAMES:raise ValueError('Unknown sprite; draw/import the actual object.')
                    if 'asset' in o:
                        asset=(project/o['asset']).resolve()
                        if (project/'assets') not in asset.parents or not asset.is_file():raise ValueError('Asset must exist under project/assets/ for cache tracking.')
                        if not o.get('credit'):raise ValueError('Record asset origin/license or original generation provenance.')
                    if not 100<=o['width']<=1000:raise ValueError('Object width must be 100–1000px.')
                    if not 0<=o['x']<=1080 or not 560<=o['y']<=1450:raise ValueError('Keep the object center in the illustration safe area.')
                    motion=o.get('motion',{})
                    if motion.get('kind','still') not in ('still','move','orbit'):raise ValueError('Unknown object motion.')
                    if motion.get('kind')=='orbit' and (len(motion.get('radius',[]))!=2 or motion.get('period',18)<=0):raise ValueError('Orbit needs two radii and a positive period.')
                    if motion.get('kind')=='move' and motion.get('duration',3)<=0:raise ValueError('Movement duration must be positive.')
                for link in v.get('links',[]):
                    if link['from'] not in ids or link['to'] not in ids or link['from']==link['to']:raise ValueError('Signal endpoints must be distinct object IDs.')
                    if not link.get('meaning'):raise ValueError('Explain what each directed signal represents.')
        if sum(1 for v in s['visuals'] if v.get('mood') == 'dark') > 3:
            raise ValueError(f'{key}: use mood dark on at most three scenes; it is an accent, not the default.')
        words = len(' '.join(s['scripts']).split())
        if not 110 <= words <= 210:
            raise ValueError(f'{key}: {words} words; aim for 145–180, allowed 110–210.')
        print(f'PREFLIGHT {key}: {words} words, seven scenes')


def prepare(args):
    check(args)
    project = Path(args.project).resolve()
    for key in selected(project, args.key):
        run([sys.executable, SKILL / 'scripts' / 'voice.py', 'verify', project, '--key', key])
        alignment = read(project / key / 'alignment.json')
        if len(alignment) != 7 or any(not row for row in alignment):
            raise ValueError('Provide real word timestamps for every scene; see references/audio.md.')
    cache_path = project / 'preparation-cache.json'
    cache = read(cache_path) if cache_path.exists() else {}
    pending = []
    for key, s in selected(project, args.key).items():
        outputs = [project / key / x for x in ('timeline.json', 'cues.json', 'storyboard.jpg', 'internal/mix.wav')]
        outputs += [project / key / 'output' / (s['filename'] + '_Narasi.wav')]
        outputs += [project / key / 'internal' / (s['filename'] + suffix) for suffix in ('.srt', '_Narasi.txt')]
        if cache.get(key) != input_signature(project, key) or not all(p.exists() for p in outputs):
            pending.append(key)
    if pending:
        run([sys.executable, project / 'prepare_all.py', *pending])
        for key in pending:
            cache[key] = input_signature(project, key)
        write(cache_path, cache)
    else:
        print('PREPARATION CACHE VERIFIED')


def lint(args, captions=None):
    """Layout gate: fail on text outside its box/canvas/caption zone. Captions mode needs `prepare` first."""
    check(args)
    project = Path(args.project).resolve()
    captions = getattr(args, 'captions', False) if captions is None else captions
    failed = []
    for key in selected(project, args.key):
        cmd = [sys.executable, project / 'engine.py', 'lint', key] + (['--captions'] if captions else [])
        result = subprocess.run([str(x) for x in cmd], cwd=project)
        name = f'{key}_layout{"_captions" if captions else ""}'
        report_path = project / 'qa' / (name + '.json')
        if report_path.exists():
            report = read(report_path)
            report['input_signature'] = input_signature(project, key)
            write(report_path, report)
        if result.returncode:
            failed.append(key)
    if failed:
        raise ValueError('Layout check failed for ' + ', '.join(failed) + '. Fix every LAYOUT ERROR above (red-boxed frames are in qa/*_layout*_scene*.png), then rerun.')


def storyboard(args):
    check(args)
    project = Path(args.project).resolve()
    for key in selected(project, args.key):
        run([sys.executable, project / 'engine.py', 'storyboard', key])
    lint(args, captions=False)


def render(args):
    project = Path(args.project).resolve()
    prepare(args)
    lint(args, captions=True)
    meta = read(project / 'production.json')
    if not args.draft and not all(meta.get(x) for x in ('source_review', 'voice_review')):
        raise ValueError('Final render needs actual source and voice reviews. Use --draft for inspection.')
    env = os.environ.copy()
    env['SP_RENDER_WORKERS'] = str(args.workers)
    subprocess.run([sys.executable, str(project / 'render_batch.py'), *selected(project, args.key)],
                   env=env, check=True)
    for key in selected(project, args.key):
        write(project / key / 'render-manifest.json', {'input_signature': input_signature(project, key)})
    meta['final_status'] = 'draft' if args.draft else 'rendered_pending_visual_review'
    meta['visual_review'] = False
    write(project / 'production.json', meta)


def validate(args):
    project = Path(args.project).resolve()
    run([sys.executable, project / 'validate.py', *selected(project, args.key)])


def deliver(args):
    """Validate and expose only MP4 + WAV; keep all QA/source documents internal."""
    project = Path(args.project).resolve()
    meta = read(project / 'production.json')
    draft = args.draft
    if not draft and not all(meta.get(x) for x in ('source_review', 'voice_review', 'visual_review')):
        raise ValueError('Complete source, listening and visual reviews before final delivery.')
    for key in selected(project, args.key):
        if read(project / key / 'render-manifest.json').get('input_signature') != input_signature(project, key):
            raise ValueError('Render inputs changed; re-render and review before delivery.')
    for key in selected(project, args.key):
        report_path = project / 'qa' / f'{key}_layout_captions.json'
        report = read(report_path) if report_path.exists() else {}
        if not report.get('ok') or report.get('input_signature') != input_signature(project, key):
            raise ValueError(f'{key}: no clean, current layout report. Run `studio.py lint <project> --captions --key {key}` and fix every error.')
    validate(args)
    manifest = []
    history = read(project / 'history.json')
    for key, s in selected(project, args.key).items():
        for suffix in ('.mp4', '_Narasi.wav'):
            path = project / key / 'output' / (s['filename'] + suffix)
            manifest.append({'file': str(path.relative_to(project)), 'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'draft': draft})
            print(('DRAFT ' if draft else 'READY ') + str(path))
        if not draft:
            history['episodes'] = [e for e in history['episodes'] if e['number'] != s['number']]
            history['episodes'].append({'number': s['number'], 'filename': s['filename'],
                'title': s['title'], 'angle': s.get('angle', s['title']), 'key': key,
                'completed_utc': datetime.now(timezone.utc).isoformat()})
    write(project / 'delivery-manifest.json', manifest)
    history['episodes'].sort(key=lambda e: e['number'])
    write(project / 'history.json', history)
    meta['final_status'] = 'draft_review_pending' if draft else 'validated_ready_to_upload'
    write(project / 'production.json', meta)


def install(args):
    if args.project:
        dest = Path(args.project).expanduser().resolve() / '.agents' / 'skills' / SKILL_NAME
    elif args.host == 'codex':
        dest = Path.home() / '.agents' / 'skills' / SKILL_NAME
    elif args.host == 'antigravity':
        dest = Path.home() / '.gemini' / 'config' / 'skills' / SKILL_NAME
    else:
        raise ValueError('Choose --project or --host.')
    dest = dest.resolve()
    if dest == SKILL or SKILL in dest.parents:
        raise ValueError('Installation destination cannot be inside the source skill.')
    if dest.exists():
        raise ValueError('Skill destination exists; review it before updating.')
    shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
    print(str(dest))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor').set_defaults(func=doctor)
    q = sub.add_parser('init'); q.add_argument('project'); q.add_argument('--topic', default='New IT fun fact')
    q.add_argument('--number', type=int); q.add_argument('--history'); q.add_argument('--example', action='store_true'); q.set_defaults(func=init)
    for name, fun in [('check', check), ('storyboard', storyboard), ('lint', lint), ('prepare', prepare), ('render', render), ('validate', validate), ('deliver', deliver), ('package', deliver)]:
        q = sub.add_parser(name); q.add_argument('project'); q.add_argument('--key'); q.set_defaults(func=fun)
        if name == 'lint':
            q.add_argument('--captions', action='store_true', help='Also check burned-in subtitles (run after prepare)')
        if name == 'render':
            q.add_argument('--draft', action='store_true'); q.add_argument('--workers', type=int, choices=range(1, 5), default=2)
        if name in ('deliver', 'package'):
            q.add_argument('--draft', action='store_true', help='Validate a review draft pair; do not mark history complete')
    q = sub.add_parser('install'); q.add_argument('--project'); q.add_argument('--host', choices=['codex', 'antigravity']); q.set_defaults(func=install)
    args = p.parse_args()
    try:
        args.func(args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        p.exit(1, 'ERROR: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
