"""Media integrity, synchronized caption coverage and encoded contact sheets."""
from pathlib import Path
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
import io,json,math,re,subprocess,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from engine import subtitle_lines,subtitle_size,font,save_image
S=json.loads((P/'series.json').read_text(encoding='utf-8'));Q=P/'qa';Q.mkdir(exist_ok=True)
def run(args):return subprocess.run(args,check=True,capture_output=True)
def norm(s):return re.sub(r'\s+',' ',s).strip()
def stamp(s):
 h,m,sec,ms=map(int,re.split('[:,]',s));return h*3600+m*60+sec+ms/1000
def captions(key):
 s=S[key];tl=json.loads((P/key/'timeline.json').read_text(encoding='utf-8'));cues=json.loads((P/key/'cues.json').read_text(encoding='utf-8'));total=sum(x['duration'] for x in tl)
 assert 70<=total<=90,(key,total)
 assert norm(' '.join(c['text'] for c in cues))==norm(' '.join(s['scripts'])),key
 assert norm((P/key/'internal'/(s['filename']+'_Narasi.txt')).read_text(encoding='utf-8'))==norm(' '.join(s['scripts']))
 blocks=(P/key/'internal'/(s['filename']+'.srt')).read_text(encoding='utf-8').strip().split('\n\n');assert len(blocks)==len(cues)
 last=0
 for i,(c,block) in enumerate(zip(cues,blocks),1):
  assert c['start']>=last-.001 and c['end']>c['start'] and c['end']<=total,(key,c)
  lines=subtitle_lines(c['text']);assert 1<=len(lines)<=2
  assert all(font(subtitle_size(lines),weight=650).getlength(x)<=790 and font(55,weight=650).getlength(x)<=932 for x in lines)
  bl=block.splitlines();assert int(bl[0])==i and bl[2:]==lines
  a,b=map(stamp,bl[1].split(' --> '));assert abs(a-c['start'])<=.00051 and abs(b-c['end'])<=.00051
  last=c['end']
 return tl,cues,total
def media(key):
 tl,cues,total=captions(key);name=S[key]['filename']+'.mp4';p=P/key/'output'/name
 data=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]).stdout)
 v=next(x for x in data['streams'] if x['codec_type']=='video');a=next(x for x in data['streams'] if x['codec_type']=='audio')
 assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
 assert (v['width'],v['height'])==(1080,1920)
 assert Fraction(v['avg_frame_rate'])==30 and int(v['nb_frames'])==round(total*30)
 assert abs(float(v['duration'])-total)<.034 and abs(float(a['duration'])-total)<.08
 assert a['codec_name']=='aac' and a['channels']==2 and int(a['sample_rate'])==48000
 run(['ffmpeg','-v','error','-xerror','-threads','1','-i',str(p),'-map','0:v','-map','0:a','-f','null','-'])
 row=dict(file=name,duration=round(total,3),frames=int(v['nb_frames']),width=v['width'],height=v['height'],fps=30,video_codec='h264',audio_codec='aac',captions=len(cues),full_decode='passed',bytes=p.stat().st_size)
 r=run(['ffmpeg','-hide_banner','-nostats','-threads','1','-i',str(p),'-vn','-af','loudnorm=I=-15:TP=-1.5:LRA=9:print_format=json','-f','null','-'])
 loud=json.loads(re.search(r'\{\s*"input_i"[\s\S]+?\}',r.stderr.decode()).group())
 row.update(loudness_lufs=float(loud['input_i']),true_peak_dbtp=float(loud['input_tp']))
 assert -18<row['loudness_lufs']<-12 and row['true_peak_dbtp']<=-.5,row
 # Exactly two public files; working captions and mix stay internal.
 expected={S[key]['filename']+'.mp4',S[key]['filename']+'_Narasi.wav'}
 actual={x.name for x in (P/key/'output').iterdir() if x.is_file()}
 assert actual==expected,('Delivery must contain only vertical MP4 and narration WAV',actual)
 voice=P/key/'output'/(S[key]['filename']+'_Narasi.wav')
 ap=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(voice)]).stdout)
 assert len(ap['streams'])==1
 stream=ap['streams'][0]
 assert stream['codec_name']=='pcm_s16le' and stream['channels']==1 and int(stream['sample_rate'])==48000
 assert abs(float(ap['format']['duration'])-total)<.01
 run(['ffmpeg','-v','error','-xerror','-i',str(voice),'-f','null','-'])
 row['narration_audio']={'file':voice.name,'channels':1,'sample_rate':48000,'codec':'pcm_s16le','full_decode':'passed'}
 tw,th,cols=270,480,4
 sheet=Image.new('RGB',(tw*cols,(th+32)*math.ceil(7/cols)),'#ECE8E1');d=ImageDraw.Draw(sheet);f=ImageFont.truetype(str(P/'Inter.ttf'),20)
 for i,s in enumerate(tl):
  cs=[c for c in cues if c['scene']==i];c=cs[len(cs)//2];t=(c['start']+c['end'])/2
  png=run(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-']).stdout
  im=Image.open(io.BytesIO(png)).convert('RGB');x,y=(i%cols)*tw,(i//cols)*(th+32)
  sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+32));d.text((x+10,y+4),f'{key} / {i+1} / {t:.1f}s',font=f,fill='#242424')
 save_image(sheet,Q/(key+'_encoded.jpg'),quality=92)
 (Q/(name+'.json')).write_text(json.dumps(row,indent=2), encoding='utf-8');print('VERIFIED',name,round(total,2),flush=True);return row
if __name__=='__main__':
 keys=sys.argv[1:] or list(S)
 # Keep variable font mutation and cached font instances sequential.
 rows=[media(k) for k in keys]
 (Q/'validation.json').write_text(json.dumps({'videos':rows},indent=2),encoding='utf-8')
 print('VALIDATION COMPLETE',len(rows),'vertical video + narration pairs',flush=True)
