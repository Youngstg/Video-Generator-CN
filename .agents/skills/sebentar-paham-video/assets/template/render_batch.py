"""Portrait-only rendering, bounded concurrency, atomic verified MP4 publication."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, sys, json, time, os
P=Path(__file__).resolve().parent
S=json.loads((P/'series.json').read_text(encoding='utf-8'))
keys=[x for x in sys.argv[1:] if not x.startswith('--')] or list(S)
def frames(p):
 try:return int(json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(p)],stderr=subprocess.DEVNULL))['streams'][0]['nb_frames'])
 except Exception:return 0

def scene(job):
 key,i=job;s=json.loads((P/key/'timeline.json').read_text(encoding='utf-8'))[i];expected=round(s['duration']*30)
 final=P/key/f'scene{i}.mp4'
 inputs=list(P.glob('*.py'))+[P/'series.json',P/key/'cues.json',P/key/'timeline.json']
 inputs += [x for x in (P/'assets').rglob('*') if x.is_file()] if (P/'assets').exists() else []
 fresh=max(f.stat().st_mtime for f in inputs)
 if final.exists() and final.stat().st_mtime>fresh and frames(final)==expected:return
 for attempt in range(2):
  r=subprocess.run([sys.executable,str(P/'engine.py'),'render',key,str(i)])
  if r.returncode==0 and frames(final)==expected:return
 raise RuntimeError(f'Failed scene {key} {i}')

def assemble(key):
 folder=P/key;tl=json.loads((folder/'timeline.json').read_text(encoding='utf-8'));total=sum(x['duration'] for x in tl);expected=round(total*30)
 final=folder/'output'/(S[key]['filename']+'.mp4')
 required=[folder/f'scene{i}.mp4' for i in range(7)]+[folder/'internal/mix.wav']
 if final.exists() and final.stat().st_mtime>max(f.stat().st_mtime for f in required) and frames(final)==expected:return
 concat=folder/'concat.txt';concat.write_text(''.join(f"file 'scene{i}.mp4'\n" for i in range(7)),encoding='utf-8')
 temp=final.with_suffix('.part.mp4')
 subprocess.run(['ffmpeg','-y','-v','error','-xerror','-f','concat','-safe','0','-i',str(concat),'-i',str(folder/'internal/mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','20','-threads','4','-pix_fmt','yuv420p','-af','loudnorm=I=-15:TP=-1.5:LRA=9','-ar','48000','-c:a','aac','-b:a','192k','-t',str(total),'-movflags','+faststart',str(temp)],check=True)
 if frames(temp)!=expected:raise RuntimeError('Incomplete final MP4: '+key)
 temp.replace(final);print('FINAL READY',key,'9:16',round(total,2),flush=True)

if __name__=='__main__':
 start=time.monotonic()
 if '--assemble-only' not in sys.argv:
  with ThreadPoolExecutor(max_workers=max(1,int(os.environ.get('SP_RENDER_WORKERS','2')))) as pool:
   list(pool.map(scene,[(k,i) for k in keys for i in range(7)]))
 for key in keys:assemble(key)
 print('VERTICAL EXPORTS READY',round(time.monotonic()-start,1),flush=True)
