from pathlib import Path
import json,sys,subprocess
P=Path(__file__).resolve().parent
S=json.loads((P/'series.json').read_text(encoding='utf-8'))
def groups(txt):
 out=[];buf=[]
 for w in txt.split():
  if buf and len(' '.join(buf+[w]))>43:out.append(' '.join(buf));buf=[]
  buf.append(w)
  if w.endswith(('.', '?','!')) and len(' '.join(buf))>20:out.append(' '.join(buf));buf=[]
 if buf:
  if out and len(buf)<3 and len(out[-1]+' '+' '.join(buf))<=43:out[-1]+=' '+' '.join(buf)
  else:out.append(' '.join(buf))
 return out
(P/'captions.json').write_text(json.dumps({k:[groups(x) for x in s['scripts']] for k,s in S.items()},ensure_ascii=False,indent=2), encoding='utf-8')
for k in sys.argv[1:] or S:
 subprocess.run([sys.executable,str(P/'engine.py'),'prepare',k],check=True)
