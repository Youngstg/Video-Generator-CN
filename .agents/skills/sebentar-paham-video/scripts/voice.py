#!/usr/bin/env python3
"""Export narration briefs, import supplied audio, and verify real word timestamps.

Quota-saving workflow (one provider request per episode instead of seven):
  gemini      one request for the whole narration -> <key>/tts/full.wav   (needs GEMINI_API_KEY)
  align-full  real word timestamps for that single take (local faster-whisper)
  split       cut the take into the seven scene clips + per-scene alignment, ready for `verify`
  quota       local request ledger and the next daily reset
Any other provider (ElevenLabs, a web tool) can supply the single take; `split` is provider-neutral.

This adapter does not purchase credits or assume that a chat subscription includes API access.
"""
import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path
import re
import shutil
import subprocess
import sys

SKILL = Path(__file__).resolve().parent.parent
EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac')


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(p.suffix + '.part')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(p)


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def audio_path(folder, i):
    files = [folder / f'{i}{ext}' for ext in EXTENSIONS if (folder / f'{i}{ext}').is_file()]
    if len(files) != 1:
        raise ValueError(f'Expected exactly one audio file for scene {i}, found {len(files)} in {folder}')
    return files[0]


def duration(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', str(p)], check=True, capture_output=True, text=True)
    return float(json.loads(r.stdout)['format']['duration'])


def fingerprints(project, key):
    s = read(project / 'series.json')[key]
    return {'script_sha256': hashlib.sha256(json.dumps(s['scripts'], ensure_ascii=False).encode()).hexdigest(),
            'audio_sha256': [digest(audio_path(project / key / 'audio', i)) for i in range(7)],
            'alignment_sha256': digest(project / key / 'alignment.json')}


def check_alignment(project, key):
    rows = read(project / key / 'alignment.json')
    if len(rows) != 7:
        raise ValueError('Alignment must contain seven lists of word timestamps.')
    scripts = read(project / 'series.json')[key]['scripts']
    for i, words in enumerate(rows):
        end_audio = duration(audio_path(project / key / 'audio', i))
        if not words:
            raise ValueError(f'Scene {i} has no timestamps.')
        last = 0
        for w in words:
            a, b = float(w['start']), float(w['end'])
            if not str(w['word']).strip() or not all(math.isfinite(x) for x in (a, b)):
                raise ValueError('Invalid word or nonfinite timestamps.')
            if a < 0 or b <= a or a < last - .025 or b > end_audio + .15:
                raise ValueError(f'Invalid timing in scene {i}: {w}')
            last = b
        # Detect unrelated transcripts; small pronunciation/number differences remain reviewable.
        from difflib import SequenceMatcher
        clean = lambda t: re.findall(r'\w+', t.casefold())
        expected = clean(scripts[i]); actual = clean(' '.join(w['word'] for w in words))
        ratio = SequenceMatcher(None, expected, actual, autojunk=False).ratio()
        if ratio < .60:
            raise ValueError(f'Scene {i}: transcript/script match only {ratio:.0%}; review the audio and alignment.')


def reset_reviews(project):
    p = project / 'production.json'
    meta = read(p)
    meta.update(voice_review=False, visual_review=False, final_status='draft')
    write(p, meta)


def stamp_provenance(project, key, provider):
    check_alignment(project, key)
    record = fingerprints(project, key)
    record.update(provider=provider, timing_source='supplied_word_timestamps', reviewed=False)
    write(project / key / 'voice-manifest.json', record)
    reset_reviews(project)


def requests(args):
    project = Path(args.project).resolve(); s = read(project / 'series.json')[args.key]
    direction = read(project / 'voice-direction.json')
    scenes = []
    for i, text in enumerate(s['scripts']):
        role = 'hook' if i == 0 else ('ending' if i == 6 else ('caveat' if i == 5 else 'body'))
        beat = ROLES[i]
        scenes.append({'scene': i, 'role': role, 'text': text, 'style': direction.get('gemini_style', {}).get(beat, ''),
                       'direction': direction, 'output': f'{i}.wav',
                       'request': 'Read only text. Indonesian conversational delivery. Keep English technical terms. '
                                  'Natural varied intonation. Warm curious opening; engaged explanatory body; '
                                  'slower, satisfied closing with a resolved cadence. No music or spoken stage directions.'})
    dest = project / args.key / 'voice-requests.json'; write(dest, scenes)
    print(dest)


def import_audio(args):
    project = Path(args.project).resolve(); src = Path(args.audio_dir).resolve()
    out = project / args.key / 'audio'; out.mkdir(parents=True, exist_ok=True)
    sources = [audio_path(src, i) for i in range(7)]
    for p in sources:
        if duration(p) <= .2:
            raise ValueError('Audio is empty or too short: ' + str(p))
    alignment = Path(args.alignment).resolve()
    if len(read(alignment)) != 7:
        raise ValueError('Expected seven scene alignments.')
    for i, p in enumerate(sources):
        target = out / (str(i) + p.suffix.lower())
        # Explicit import replaces working clips; preserve source audio outside the project.
        if p != target:
            temp = target.with_suffix(target.suffix + '.part'); shutil.copy2(p, temp); temp.replace(target)
        for ext in EXTENSIONS:
            other = out / f'{i}{ext}'
            if other != target:
                other.unlink(missing_ok=True)
    target_alignment = project / args.key / 'alignment.json'
    if target_alignment != alignment:
        write(target_alignment, read(alignment))
    stamp_provenance(project, args.key, args.provider)
    print('IMPORTED: seven clips and real word timestamps. Listening review still required.')


def register(args):
    project = Path(args.project).resolve()
    stamp_provenance(project, args.key, args.provider)
    print('REGISTERED: existing clips and supplied timestamps. Listening review still required.')


def verify(args):
    project = Path(args.project).resolve()
    check_alignment(project, args.key)
    stored = read(project / args.key / 'voice-manifest.json')
    current = fingerprints(project, args.key)
    if any(stored.get(k) != value for k, value in current.items()):
        raise ValueError('Narration inputs changed. Regenerate affected audio/timestamps, then import or register again.')
    print('VOICE INPUTS VERIFIED', args.key)


def align(args):
    # Optional local ASR; reads actual audio, never invents timing from character counts.
    # A local model directory avoids any download. Model-name downloads require network access.
    from faster_whisper import WhisperModel
    project = Path(args.project).resolve()
    model = WhisperModel(args.model, device='cpu', compute_type='int8')
    rows = []
    for i in range(7):
        p = audio_path(project / args.key / 'audio', i)
        segments, _ = model.transcribe(str(p), language='id', word_timestamps=True,
                                       vad_filter=False, beam_size=5)
        words = [{'word': w.word.strip(), 'start': float(w.start), 'end': float(w.end)}
                 for segment in segments for w in (segment.words or []) if w.end > w.start]
        rows.append(words)
    write(project / args.key / 'alignment.json', rows)
    stamp_provenance(project, args.key, 'import_with_local_asr')
    record = read(project / args.key / 'voice-manifest.json')
    record['timing_source'] = 'faster_whisper_word_timestamps'; write(project / args.key / 'voice-manifest.json', record)
    print('ALIGNED: inspect technical terms and subtitle boundaries against the audio.')


# ------------------------------------------------------------------ single-take workflow
ROLES = ['hook', 'body', 'body', 'mechanism', 'body', 'caveat', 'ending']
GEMINI_MODEL = 'gemini-3.8-flash-tts'
LEDGER = 'tts-ledger.json'


def zone(name, fallback_hours):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        from datetime import timezone, timedelta
        return timezone(timedelta(hours=fallback_hours))


def pacific_day(now=None):
    from datetime import datetime
    return datetime.fromtimestamp(now or time.time(), zone('America/Los_Angeles', -7)).date().isoformat()


def next_reset_text(now=None):
    """Daily quotas reset at midnight Pacific time; show it in Western Indonesia Time."""
    from datetime import datetime, timedelta
    pac = zone('America/Los_Angeles', -7); wib = zone('Asia/Jakarta', 7)
    t = datetime.fromtimestamp(now or time.time(), pac)
    reset = (t + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return reset.astimezone(wib).strftime('%d %b %H:%M WIB')


def ledger_read(project):
    p = project / LEDGER
    return read(p) if p.exists() else {'events': []}


def ledger_add(project, model, ok, key, note=''):
    data = ledger_read(project)
    data['events'].append({'t': round(time.time(), 1), 'day': pacific_day(), 'model': model,
                           'ok': ok, 'key': key, 'note': note[:200]})
    data['events'] = data['events'][-500:]
    write(project / LEDGER, data)


def used_today(project, model):
    day = pacific_day()
    return sum(1 for e in ledger_read(project)['events'] if e['model'] == model and e['day'] == day)


def guard(project, model, rpd, rpm):
    """Local, best-effort guard. EVERY attempt counts, failures included, because providers meter them too.
    Quotas are per cloud project, so this ledger cannot see use from other tools or other machines."""
    used = used_today(project, model)
    if used >= rpd:
        raise ValueError(f'Local guard: {used}/{rpd} {model} requests already attempted today (Pacific day). '
                         f'Next reset {next_reset_text()}. Switch this WHOLE episode to another provider, or wait. '
                         'Raise --rpd only if the provider dashboard shows real headroom.')
    recent = sorted(e['t'] for e in ledger_read(project)['events'] if e['model'] == model and e['t'] > time.time() - 60)
    if len(recent) >= rpm:
        wait = math.ceil(recent[0] + 61 - time.time())
        print(f'RPM guard: waiting {wait}s (this costs no quota).', flush=True)
        time.sleep(max(1, wait))


def gemini_payload(project, key, mode, voice):
    s = read(project / 'series.json')[key]
    direction = read(project / 'voice-direction.json')
    styles = direction.get('gemini_style', {})
    if mode == 'single':
        parts = [{'text': ' '.join(s['scripts']), 'speech_metadata': {'style': styles.get('body', '')}}]
    else:  # one text block per scene so each beat gets its own acting direction, still ONE request
        parts = [{'text': t, 'speech_metadata': {'style': styles.get(ROLES[i], '')}} for i, t in enumerate(s['scripts'])]
    for part in parts:
        if not part['speech_metadata']['style']:
            part.pop('speech_metadata')
    return {'contents': [{'role': 'user', 'parts': parts}],
            'config': {'response_modalities': ['AUDIO'], 'speech_config': {'voice_config': {'voice': voice}}}}


def wav_bytes(data, mime):
    """Gemini 3.8 returns WAV by default; older/headerless PCM (audio/l16) is wrapped here."""
    if data[:4] == b'RIFF':
        return data
    import io, wave
    m = re.search(r'rate=(\d+)', mime or ''); rate = int(m.group(1)) if m else 24000
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data)
    return buf.getvalue()


def gemini(args):
    project = Path(args.project).resolve()
    payload = gemini_payload(project, args.key, args.mode, args.voice)
    if args.dry_run:
        print(json.dumps({'model': args.model, **payload}, ensure_ascii=False, indent=2))
        print(f'DRY RUN: nothing sent, nothing counted. A real run is ONE request. Used today: {used_today(project, args.model)}/{args.rpd}.')
        return
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError('Set GEMINI_API_KEY in your shell (key from Google AI Studio). It is never read from or written to the project.')
    try:
        from google import genai
    except ImportError:
        raise ValueError('Install the SDK first: python -m pip install "google-genai>=2.25.0"')
    guard(project, args.model, args.rpd, args.rpm)
    out = project / args.key / 'tts'; out.mkdir(parents=True, exist_ok=True)
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=args.model, contents=payload['contents'], config=payload['config'])
        audio = None
        for cand in (getattr(response, 'candidates', None) or []):
            for part in (getattr(getattr(cand, 'content', None), 'parts', None) or []):
                inline = getattr(part, 'inline_data', None)
                if inline is not None and inline.data:
                    audio = wav_bytes(inline.data, getattr(inline, 'mime_type', ''))
        if not audio:
            raise RuntimeError('The response contained no audio part.')
    except Exception as exc:  # one attempt only: retrying blindly burns the daily quota
        ledger_add(project, args.model, False, args.key, type(exc).__name__)
        write(out / 'last-error.json', {'type': type(exc).__name__, 'code': getattr(exc, 'code', None),
                                         'status': getattr(exc, 'status', None), 'message': str(exc)[:4000],
                                         'model': args.model, 'when_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
        hint = ''
        if getattr(exc, 'code', None) == 429 or '429' in str(exc) or 'RESOURCE_EXHAUSTED' in str(exc):
            hint = (' Quota error: NOT retried. Open the error file and read which limit it names (per-minute vs per-day, '
                    'and whether the limit is 0). Then use another model or provider for the whole episode.')
        raise ValueError(f'{type(exc).__name__}: {str(exc)[:300]}. Details: {out / "last-error.json"}.{hint}')
    ledger_add(project, args.model, True, args.key)
    target = out / 'full.wav'; temp = target.with_suffix('.part.wav'); temp.write_bytes(audio); temp.replace(target)
    write(out / 'request-log.json', {'model': args.model, 'mode': args.mode, 'voice': args.voice, 'requests_used': 1,
                                     'seconds': round(duration(target), 2)})
    print(f'SAVED {target} ({duration(target):.1f}s) using 1 request. Used today: {used_today(project, args.model)}/{args.rpd}.')
    print('Next: voice.py align-full, then voice.py split. Listen to the take first; a rejected take costs another request.')


def quota(args):
    project = Path(args.project).resolve(); day = pacific_day()
    rows = {}
    for e in ledger_read(project)['events']:
        if e['day'] == day:
            r = rows.setdefault(e['model'], [0, 0]); r[0] += 1; r[1] += 0 if e['ok'] else 1
    print(f'Pacific day {day}; daily quotas reset {next_reset_text()}.')
    for model, (n, bad) in rows.items():
        print(f'  {model}: {n} attempts today ({bad} failed) - from this project\'s ledger only')
    if not rows:
        print('  no attempts recorded today')
    print('Note: AI Studio\'s "Rate limits by model" page shows PEAK usage over 28 days, not what is left today.')


def align_full(args):
    from faster_whisper import WhisperModel
    project = Path(args.project).resolve(); src = Path(args.audio or project / args.key / 'tts' / 'full.wav')
    model = WhisperModel(args.model, device='cpu', compute_type='int8')
    segments, _ = model.transcribe(str(src), language='id', word_timestamps=True, vad_filter=False, beam_size=5)
    words = [{'word': w.word.strip(), 'start': float(w.start), 'end': float(w.end)}
             for seg in segments for w in (seg.words or []) if w.end > w.start]
    dest = project / args.key / 'tts' / 'full-alignment.json'; write(dest, words)
    print(f'ALIGNED {len(words)} words -> {dest}. Check technical terms against the audio.')


def scene_ranges(scripts, words):
    """Map every script token to a real timestamped word; return (first, last) word index per scene."""
    from difflib import SequenceMatcher
    tok = lambda t: re.findall(r'\w+', t.casefold())
    src, owner = [], []
    for i, text in enumerate(scripts):
        for t in tok(text):
            src.append(t); owner.append(i)
    asr, asr_word = [], []
    for j, w in enumerate(words):
        for t in tok(w['word']):
            asr.append(t); asr_word.append(j)
    mapped = {}
    for tag, a, b, c, d in SequenceMatcher(None, src, asr, autojunk=False).get_opcodes():
        if tag == 'equal':
            for k in range(b - a): mapped[a + k] = asr_word[c + k]
        elif tag == 'replace' and d > c:
            for k in range(a, b): mapped[k] = asr_word[min(d - 1, c + int((k - a) * (d - c) / (b - a)))]
    ranges = []
    for i in range(len(scripts)):
        idx = [mapped[k] for k in range(len(src)) if owner[k] == i and k in mapped]
        total = sum(1 for o in owner if o == i)
        if not idx or len(idx) < .7 * total:
            raise ValueError(f'Scene {i}: only {len(idx)}/{total} script words were found in the timestamps. '
                             'The take does not match the script (skipped/extra/misheard text); listen and fix before splitting.')
        ranges.append((min(idx), max(idx)))
    for i in range(len(ranges) - 1):
        if ranges[i][1] >= ranges[i + 1][0]:
            raise ValueError(f'Scenes {i} and {i + 1} overlap in the timestamps; the take is out of order or repeated.')
    return ranges


def split_episode(args):
    project = Path(args.project).resolve(); s = read(project / 'series.json')[args.key]
    src = Path(args.audio or project / args.key / 'tts' / 'full.wav')
    words = read(args.alignment or project / args.key / 'tts' / 'full-alignment.json')
    if not src.is_file():
        raise ValueError('Full take not found: ' + str(src))
    ranges = scene_ranges(s['scripts'], words); total = duration(src)
    out = project / args.key / 'audio'; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (a, b) in enumerate(ranges):
        speech_a, speech_b = float(words[a]['start']), float(words[b]['end'])
        prev_end = float(words[ranges[i - 1][1]]['end']) if i else 0.0
        next_start = float(words[ranges[i + 1][0]]['start']) if i < 6 else total
        t0 = max(0.0, speech_a - min(.15, max(0.0, (speech_a - prev_end) / 2)))
        t1 = min(total, speech_b + min(.30, max(0.0, (next_start - speech_b) / 2)))
        target = out / f'{i}.wav'; temp = target.with_suffix('.part.wav')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', str(src),
                        '-ac', '1', '-c:a', 'pcm_s16le', str(temp)], check=True)
        temp.replace(target)
        for ext in EXTENSIONS:
            other = out / f'{i}{ext}'
            if other != target: other.unlink(missing_ok=True)
        rows.append([{'word': w['word'].strip(), 'start': round(max(0.0, float(w['start']) - t0), 3),
                      'end': round(max(float(w['end']), float(w['start']) + .02) - t0, 3)} for w in words[a:b + 1]])
        print(f'scene {i}: {t0:.2f}-{t1:.2f}s ({t1 - t0:.1f}s, {b - a + 1} words)')
    write(project / args.key / 'alignment.json', rows)
    stamp_provenance(project, args.key, args.provider)
    print('SPLIT: seven clips + per-scene timestamps from ONE take. Listening review still required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command, func in [('requests', requests), ('import', import_audio), ('register', register), ('verify', verify), ('align', align)]:
        q = sub.add_parser(command); q.add_argument('project'); q.add_argument('--key', required=True); q.set_defaults(func=func)
        if command in ('import', 'register'):
            q.add_argument('--provider', required=True, help='Provider/source label, never an API key')
        if command == 'import':
            q.add_argument('--audio-dir', required=True); q.add_argument('--alignment', required=True)
        if command == 'align':
            q.add_argument('--model', default='small', help='Local Whisper model directory or model name')
    q = sub.add_parser('gemini', help='ONE request for the whole episode (needs GEMINI_API_KEY, pip install google-genai)')
    q.add_argument('project'); q.add_argument('--key', required=True)
    q.add_argument('--model', default=GEMINI_MODEL); q.add_argument('--voice', default='Kore', help='prebuilt name or a voice_... id from Voice design')
    q.add_argument('--mode', choices=['beats', 'single'], default='beats', help='beats: one block per scene with its own style; single: one block')
    q.add_argument('--rpd', type=int, default=10, help='local daily attempt cap (match your dashboard)'); q.add_argument('--rpm', type=int, default=3)
    q.add_argument('--dry-run', action='store_true'); q.set_defaults(func=gemini)
    q = sub.add_parser('quota'); q.add_argument('project'); q.set_defaults(func=quota)
    q = sub.add_parser('align-full'); q.add_argument('project'); q.add_argument('--key', required=True)
    q.add_argument('--audio'); q.add_argument('--model', required=True, help='local faster-whisper model directory/name'); q.set_defaults(func=align_full)
    q = sub.add_parser('split'); q.add_argument('project'); q.add_argument('--key', required=True)
    q.add_argument('--audio', help='default <key>/tts/full.wav'); q.add_argument('--alignment', help='flat [{word,start,end}] list, default <key>/tts/full-alignment.json')
    q.add_argument('--provider', required=True, help='label only, never a key'); q.set_defaults(func=split_episode)
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, KeyError, OSError, ImportError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'ERROR: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
