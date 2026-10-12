"""Object-led motion scenes. Extend draw() for each new topic's causal mechanism.
Seven mouse recipes are worked examples, not a universal theme for every episode.
"""
from PIL import Image, ImageDraw
from functools import lru_cache
from pathlib import Path
import math
import illustrations as art


def label(d, e, x, y, value, size=48, width=880, color=None):
    """Caption under/next to an object. Wraps to at most two lines and is clamped to the canvas safe
    area, so a label near the edge can never leave the screen. Raises with a fix instead of overflowing."""
    if not value or not getattr(e, 'SHOW_LABELS', True): return
    room = 2 * min(x - e.SAFE[0], e.SAFE[1] - x)
    if room < 200:
        raise e.LayoutError(f'Label {value!r} is centred at x={x}, too close to the screen edge; move it inward (x between {e.SAFE[0]+100} and {e.SAFE[1]-100}).')
    for k, row in enumerate(e.wrap(value, size, min(width, room), max_lines=2)):
        e.txt(d, x, y + k * 62, row, size, color or e.T['ink'], anchor='mt', role='label')


def signal(d,e,a,b,t,phase=0,color=None):
    """Directional explanation: the line draws itself source -> destination, then dots stream along it."""
    c=color or e.T['accent']
    p=e.ease(t/.6);end=(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p)
    e.arrow(d,a,end,e.T['soft'],5,19)
    for k in range(3):
        u=((t-.5)*.42+phase+k/3)%1
        if t<.5: break
        x,y=a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u
        d.ellipse((x-17,y-17,x+17,y+17),fill=e.blendcol(c,e.T['bg'],.6))
        d.ellipse((x-10,y-10,x+10,y+10),fill=c)


@lru_cache(32)
def bitmap(path):
    with Image.open(path) as im:
        im.load()
        return im.convert('RGBA')


def position(o,t,e,i):
    x,y=o['x'],o['y'];m=o.get('motion',{});kind=m.get('kind','still')
    local=t-e.cue_time(i,m['cue'],m.get('at',0)) if m.get('cue') else t-m.get('at',0)
    if kind=='orbit':
        a=local*2*math.pi/m.get('period',18)+m.get('phase',0)
        x+=m['radius'][0]*math.cos(a);y+=m['radius'][1]*math.sin(a)
    elif kind=='move':
        u=e.ease(local/m.get('duration',3))
        x+=m.get('dx',0)*u;y+=m.get('dy',0)*u
    return x,y


def appear(o,idx,t,e,i):
    """Seconds since this object entered. Default: staggered pop-ins after the scene transition."""
    base=(.15 if i==0 else .55)+.18*idx
    at=e.cue_time(i,o['cue'],o.get('at',base)) if o.get('cue') else o.get('at',base)
    return t-at


def pop(u):
    """Ease-out-back: grows past 1.0 and settles, so objects feel like they land."""
    if u<=0: return 0.0
    k=min(1.0,u/.5); return 1+2.3*(k-1)**3+1.3*(k-1)**2


def objects(im,v,t,e,i):
    """Compose recognizable sprites/assets; annotate links with a real causal meaning.
    Objects pop in (staggered or on a narration cue), idle-float gently and cast a soft shadow."""
    d=ImageDraw.Draw(im);positions={}
    for idx,o in enumerate(v['objects']):
        x,y=position(o,t,e,i)
        if not o.get('motion') and o.get('float',True) and appear(o,idx,t,e,i)>.5: y+=7*math.sin(t*1.7+idx*1.3)
        positions[o['id']]=(x,y)
    for link in v.get('links',[]):
        at=e.cue_time(i,link['cue'],link.get('at',0)) if link.get('cue') else link.get('at',0)
        if t>=at:signal(d,e,positions[link['from']],positions[link['to']],t-at)
    for idx,o in enumerate(v['objects']):
        x,y=positions[o['id']];w=o['width'];u=appear(o,idx,t,e,i);k=pop(u)
        if k<=.03: continue
        if 'sprite' in o:box=art.place(im,o['sprite'],x,y,w*k,e.T['accent'],o.get('angle',0),shadow=o.get('shadow',True))
        else:
            tile=bitmap(str((e.P/o['asset']).resolve())).copy();tile.thumbnail((w*k,w*k),Image.Resampling.LANCZOS)
            ox,oy=round(x-tile.width/2),round(y-tile.height/2);im.paste(tile,(ox,oy),tile);box=(ox,oy,ox+tile.width,oy+tile.height)
        e.mark_object(box)
        d=ImageDraw.Draw(im)
        # Label sits just under the VISIBLE silhouette, not under the (transparent-margin) sprite tile.
        if k>=.9: label(d,e,x,(box[3]+14) if box else y+w/2+12,o.get('label',''),width=o.get('label_width',400))
    for a in v.get('annotations',[]):
        at=e.cue_time(i,a['cue'],a.get('at',0)) if a.get('cue') else a.get('at',0)
        if t<at: continue
        if a.get('style','chip')=='plain': label(d,e,a['x'],a['y'],a['text'],width=a.get('width',880))
        elif e.SHOW_LABELS:
            slide=14*(1-e.out((t-at)/.4));e.chip(d,a['x'],a['y']+slide,a['text'],max_w=min(a.get('width',900),900))


def texture(im,cx,cy,r,shift=0,glass=False):
    """Enlarged surface image; the same feature moves between frames."""
    tile=Image.new('RGBA',(round(2*r),round(2*r)))
    d=ImageDraw.Draw(tile)
    d.ellipse((2,2,2*r-3,2*r-3),fill='#DCE9E9' if glass else '#E7C99F',outline=art.INK,width=5)
    mask=Image.new('L',tile.size);ImageDraw.Draw(mask).ellipse((6,6,2*r-7,2*r-7),fill=255)
    detail=Image.new('RGBA',tile.size);p=ImageDraw.Draw(detail)
    if not glass:
        for j in range(32):
            x=(j*63+21+shift)%(2*r);y=(j*83+27)%(2*r)
            p.ellipse((x-6,y-3,x+11,y+7),fill='#A88259')
        # Reference knot stays inside the crop and moves right, unlike the sensor.
        x=r-37+shift;y=r+12
        p.ellipse((x-25,y-19,x+25,y+19),fill='#937251')
        p.ellipse((x-44,y-38,x+44,y+38),outline='#DC7252',width=6)
    else:
        p.line((r-80,20,r+20,2*r),fill='#F5FAF6',width=18)
    detail.putalpha(Image.composite(detail.getchannel('A'),Image.new('L',tile.size),mask))
    tile.alpha_composite(detail)
    im.paste(tile,(round(cx-r),round(cy-r)),tile)


def mouse(im,v,t,e,i):
    d=ImageDraw.Draw(im);phase=v['phase'];c=e.T
    # Physical displacement rather than decorative card bobbing.
    move=48*math.sin(t*.72)
    if phase in ('overview','ending'):
        art.desk(d,(70,990,544,1320),offset=0)
        art.place(im,'mouse',295+move,1030,430,c['accent'])
        art.place(im,'laptop',774,1030,492,c['accent'])
        d=ImageDraw.Draw(im);art.cursor(d,744+move*.6,947,58)
        signal(d,e,(480,1140),(620,1110),t)
        label(d,e,300,1370,'MOUSE OPTIK',width=440)
        label(d,e,783,1370,'KURSOR',width=370)
    elif phase=='light':
        art.desk(d,(90,1170,990,1385))
        d.polygon([(322,962),(185,1251),(534,1251)],fill='#F1B582')
        art.place(im,'mouse_under',327,808,459,c['accent'])
        art.place(im,'chip',774,867,300,c['accent'])
        d=ImageDraw.Draw(im)
        signal(d,e,(332,992),(267,1242),t,color='#DE805A')
        signal(d,e,(440,1242),(409,1005),t,.5)
        signal(d,e,(448,898),(663,877),t,.3)
        label(d,e,772,1054,'SENSOR',width=370)
        label(d,e,540,1410,'SKEMA CAHAYA PANTUL',width=930)
    elif phase in ('sampling','compare'):
        art.place(im,'mouse_under',540+move*.4,775,330,c['accent'])
        d=ImageDraw.Draw(im)
        d.line((457,904,317,1040),fill=c['soft'],width=5)
        d.line((623,904,763,1040),fill=c['soft'],width=5)
        # An explanatory before/after detail of actual surface texture, not stats.
        texture(im,298,1167,192,0)
        texture(im,782,1167,192,50*e.ease(((t-1)%4)/2))
        d=ImageDraw.Draw(im)
        e.arrow(d,(501,1170),(574,1170),c['accent'],7)
        label(d,e,298,1420,'GAMBAR A',width=410)
        label(d,e,782,1420,'GAMBAR B',width=410)
        if phase=='sampling':
            # Soft shutter ring, never a full-screen flash.
            r=30+35*((t*.65)%1)
            d.ellipse((540-r,803-r,540+r,803+r),outline='#DC7252',width=4)
    elif phase=='compute':
        art.desk(d,(80,1005,415,1310))
        art.place(im,'mouse',245+move*.5,1070,330,c['accent'])
        art.place(im,'chip',541,788,290,c['accent'])
        art.place(im,'laptop',827,1155,358,c['accent'])
        d=ImageDraw.Draw(im)
        signal(d,e,(366,976),(466,905),t)
        signal(d,e,(661,853),(783,1042),t,.5)
        art.cursor(d,790+move*.36,1110,45)
        label(d,e,540,573,'PERGESERAN → GERAKAN',width=925)
        label(d,e,260,1370,'TEKSTUR',width=360)
        label(d,e,812,1370,'KURSOR',width=360)
    elif phase=='glass':
        art.desk(d,(84,910,996,1280),plain=True)
        art.place(im,'mouse_under',320+move*.4,923,398,c['accent'])
        texture(im,801,1070,167,glass=True)
        d=ImageDraw.Draw(im)
        label(d,e,540,1385,'TERGANTUNG SENSOR',width=900)
    else:
        raise ValueError('Unknown mouse recipe: '+phase)


def draw(im,key,i,t,e):
    v=e.SERIES[key]['visuals'][i]
    if v['kind']=='objects':objects(im,v,t,e,i)
    elif v['kind']=='mouse':mouse(im,v,t,e,i)
    else:raise ValueError('Implement this custom mechanism in project artwork.py: '+v['kind'])
