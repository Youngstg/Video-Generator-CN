"""Original, logo-free object artwork. 480 px tiles; no labels needed for recognition.
Use cutaways/diagrams for mechanisms; these are illustrative, not engineering drawings.
"""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw
import math

NAMES = {'earth', 'satellite', 'mouse', 'mouse_under', 'phone', 'laptop',
         'server', 'chip', 'router', 'clock', 'receipt', 'mug'}
INK = '#24443F'
CREAM = '#FFFDF7'
TEAL = '#489890'
GOLD = '#DFAF62'

@lru_cache(96)
def sprite(name, accent='#28735E'):
    if name not in NAMES:
        raise ValueError('Draw or import the actual subject; unknown object: ' + name)
    im = Image.new('RGBA', (480, 480))
    d = ImageDraw.Draw(im)
    def rr(b, fill, radius=18, outline=INK, width=5):
        d.rounded_rectangle(b, radius, fill=fill, outline=outline, width=width)
    def line(points, fill=INK, width=6):
        d.line(points, fill=fill, width=width, joint='curve')
    if name == 'earth':
        d.ellipse((17, 17, 463, 463), fill='#BCDDE2')
        d.ellipse((31, 31, 449, 449), fill='#4A8CA8', outline=INK, width=5)
        # Stylized Eurasia/Africa/Australia and Americas, not a geographic data map.
        land = [
          [(269,49),(310,49),(355,67),(396,105),(397,128),(370,151),(382,175),(341,191),(331,215),(306,209),(286,180),(262,169),(262,146),(236,132),(245,109),(227,86)],
          [(242,170),(278,174),(305,215),(294,259),(274,278),(263,318),(244,312),(225,270),(207,248),(207,210)],
          [(351,314),(392,306),(415,336),(403,365),(359,366),(337,347)],
          [(79,90),(125,55),(171,63),(186,99),(167,127),(167,160),(145,184),(153,207),(132,214),(114,185),(87,175),(65,140)],
          [(145,215),(171,218),(190,244),(187,284),(161,323),(151,357),(135,373),(126,324),(108,278),(114,239)],
          [(89,385),(163,405),(244,414),(320,403),(376,389),(338,423),(273,439),(192,437),(127,416)]
        ]
        for points in land: d.polygon(points, fill='#A9CC8D')
        for box in [(90,109,211,126),(276,276,379,289),(161,351,273,365),(305,87,374,99)]:
            d.rounded_rectangle(box, 9, fill='#E7F0E7')
        d.arc((42,42,438,438), 215, 280, fill='#D7EBE8', width=9)
    elif name == 'satellite':
        # Two segmented photovoltaic wings, gold bus, antenna dish.
        line([(41,248),(437,248)], GOLD, 13)
        for x in (15, 307):
            rr((x,156,x+157,326),'#355F81',9)
            for j in range(1,4): line([(x+j*39,161),(x+j*39,321)],'#8CCAD2',3)
            for yy in (211,266): line([(x+5,yy),(x+152,yy)],'#8CCAD2',3)
        d.polygon([(189,174),(261,154),(292,188),(292,292),(218,317),(184,284)], fill=GOLD, outline=INK)
        rr((195,190,266,286),'#F3D58B',9)
        line([(269,194),(286,183)],'#9D763E',3)
        line([(232,173),(243,104)],INK,7)
        d.pieslice((196,57,298,153),0,180,fill=CREAM,outline=INK,width=5)
        line([(245,105),(267,79)],INK,5)
        d.ellipse((258,70,277,89),fill=accent)
        line([(219,313),(206,350)],INK,5)
        d.ellipse((198,348,214,364),fill=accent)
    elif name in ('mouse','mouse_under'):
        # A curved shell, split primary buttons, wheel, cable. Under-view shows optics.
        line([(239,75),(239,36),(271,15),(313,18)], '#677C73', 9)
        d.ellipse((105,71,393,467),fill=(30,58,50,20))
        rr((96,63,384,447),'#E7E7DC',135,INK,7)
        d.arc((111,75,370,431),115,260,fill='#FFFDF7',width=15)
        if name == 'mouse':
            d.pieslice((105,68,375,326),180,360,fill='#F9F8EC')
            line([(240,68),(240,214)],INK,5)
            d.arc((101,78,379,310),0,180,fill=INK,width=4)
            rr((218,98,261,183),accent,19,INK,4)
            for y in range(117,175,12): line([(227,y),(251,y)],'#97C6AE',3)
            d.arc((124,180,365,408),25,65,fill='#BCC9BC',width=7)
            line([(100,226),(99,281)],'#9BAE9D',8)
        else:
            for b in [(149,100,331,134),(145,361,335,397)]:rr(b,'#9FAEA2',15,None)
            rr((192,210,288,305),'#526C61',16)
            d.ellipse((212,230,268,286),fill='#E57452',outline=INK,width=4)
            d.ellipse((228,246,252,270),fill='#FBE0A4')
            for x,y in [(144,173),(336,173),(144,332),(336,332)]:
                d.ellipse((x-6,y-6,x+6,y+6),fill=INK)
    elif name == 'phone':
        rr((116,28,364,458),INK,38,INK)
        rr((132,51,348,427),'#D8E3D1',25,None)
        # Draw a map with streets and a familiar location pin.
        for pts in [[(132,151),(348,151)],[(132,331),(348,331)],[(176,51),(176,427)],[(292,51),(292,427)]]:
            line(pts,CREAM,18)
        line([(154,363),(236,363),(236,252),(287,252)],accent,9)
        d.ellipse((202,178,278,254),fill='#DE805A',outline=INK,width=4)
        d.polygon([(207,224),(240,284),(273,224)],fill='#DE805A')
        d.ellipse((227,203,253,229),fill=CREAM)
        rr((199,56,281,72),INK,8,None)
        rr((205,439,275,445),'#9CAFA1',3,None)
    elif name == 'laptop':
        rr((51,62,429,321),INK,16)
        rr((68,80,412,299),'#E2EADD',6,None)
        for j, w in enumerate([182,245,147,211]):
            rr((93,116+j*39,93+w,129+j*39),accent if j==0 else '#ABBFAC',5,None)
        d.polygon([(51,321),(429,321),(472,400),(459,423),(21,423),(8,400)],fill='#CBD5C9',outline=INK)
        for row in range(3):
            for col in range(11):
                x=72+col*30-row*9;y=339+row*18
                rr((x,y,x+21,y+9),'#91A596',3,None)
        rr((192,383,288,408),'#DFE5D9',5,INK,2)
    elif name == 'server':
        d.polygon([(119,37),(342,37),(388,70),(164,70)],fill='#97B5A8',outline=INK)
        d.polygon([(342,37),(388,70),(388,430),(342,408)],fill='#506F66',outline=INK)
        rr((109,65,345,441),'#CFD9C9',13)
        for y in (94,192,290):
            rr((130,y,324,y+78),CREAM,8)
            for x in range(148,269,18):line([(x,y+20),(x,y+57)],'#92AAA0',4)
            d.ellipse((290,y+31,304,y+45),fill=accent)
        d.ellipse((202,392,250,420),fill=INK)
    elif name == 'chip':
        for x in range(133,360,42):
            rr((x,35,x+19,122),GOLD,4,INK,3);rr((x,358,x+19,445),GOLD,4,INK,3)
            rr((35,x,122,x+19),GOLD,4,INK,3);rr((358,x,445,x+19),GOLD,4,INK,3)
        rr((103,103,377,377),'#385F55',24)
        rr((141,141,339,339),'#8CAB96',10)
        for j in range(4):
            line([(162,175+j*36),(235,175+j*36),(257,193+j*36),(316,193+j*36)],'#D9DBA2',5)
        d.ellipse((120,119,136,135),fill=CREAM)
    elif name == 'router':
        for x in (126,352):
            line([(x,239),(x-25,91)],INK,21)
        rr((67,241,413,362),'#DBE3D4',30)
        d.arc((143,87,337,281),220,320,fill=accent,width=9)
        d.arc((178,125,302,249),220,320,fill=accent,width=9)
        d.ellipse((229,182,251,204),fill=accent)
        for x in (115,155,195):d.ellipse((x,293,x+13,306),fill=accent)
        for x in range(276,375,17):line([(x,278),(x,325)],'#90A597',5)
    elif name == 'clock':
        d.ellipse((59,62,437,440),fill='#AFCBB7')
        d.ellipse((41,40,419,418),fill=CREAM,outline=INK,width=10)
        for n in range(12):
            a=n*math.pi/6
            line([(230+153*math.sin(a),230-153*math.cos(a)),(230+171*math.sin(a),230-171*math.cos(a))],INK,7)
        line([(230,230),(230,116)],accent,12)
        line([(230,230),(310,279)],INK,14)
        d.ellipse((215,215,245,245),fill=GOLD,outline=INK,width=3)
    elif name == 'receipt':
        pts=[(102,42),(378,42),(378,431)]
        pts += [(x,413 if j%2 else 431) for j,x in enumerate(range(356,101,-23))]
        pts += [(102,42)]
        d.polygon(pts,fill=CREAM,outline=INK)
        for j,w in enumerate([156,206,136,182]):
            rr((131,111+j*46,131+w,122+j*46),'#97AB9B',3,None)
        line([(131,307),(347,307)],INK,4)
        rr((224,331,348,354),accent,4,None)
    elif name == 'mug':
        d.ellipse((303,133,447,322),fill=accent,outline=INK,width=6)
        d.ellipse((331,162,415,292),fill=(0,0,0,0),outline=INK,width=5)
        rr((79,95,333,381),'#C8D9B4',33,INK,6)
        d.ellipse((81,76,331,144),fill='#F9F6DE',outline=INK,width=6)
        d.ellipse((106,95,306,131),fill='#75543E')
        d.arc((127,144,267,324),95,166,fill='#EAF0DA',width=13)
    return im


@lru_cache(64)
def _shadow(name, accent, width):
    from PIL import ImageFilter
    tile = sprite(name, accent).resize((width, width), Image.Resampling.LANCZOS)
    alpha = tile.getchannel('A').filter(ImageFilter.GaussianBlur(max(2, width * .02))).point(lambda v: int(v * .20))
    sh = Image.new('RGBA', tile.size, (22, 32, 34, 0)); sh.putalpha(alpha)
    return sh


def place(im, name, x, y, width, accent='#28735E', angle=0, shadow=False):
    """Paste a sprite centred on (x, y). Returns the VISIBLE bounding box (alpha > 0) for layout checks."""
    wr = max(2, round(width))
    tile = sprite(name, accent).resize((wr, wr), Image.Resampling.LANCZOS)
    sh = _shadow(name, accent, wr) if shadow else None
    if angle:
        tile = tile.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        if sh: sh = sh.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    ox, oy = round(x - tile.width / 2), round(y - tile.height / 2)
    if sh: im.paste(sh, (ox + round(wr * .018), oy + round(wr * .04)), sh)   # soft contact shadow = depth
    im.paste(tile, (ox, oy), tile)
    box = tile.getchannel('A').getbbox()
    return (ox + box[0], oy + box[1], ox + box[2], oy + box[3]) if box else None


def cursor(d,x,y,size=65,color=INK):
    d.polygon([(x,y),(x+size*.24,y+size),(x+size*.46,y+size*.63),
               (x+size*.81,y+size*.95),(x+size,y+size*.73),
               (x+size*.66,y+size*.42),(x+size,y+size*.28)],fill=color,outline=CREAM,width=4)


def desk(d,b,offset=0,plain=False):
    """A wood surface with persistent grain (or glass), not a text card."""
    x1,y1,x2,y2=b
    d.rounded_rectangle(b,25,fill='#DCEBEC' if plain else '#E7C99F',outline='#B48C61',width=4)
    if plain:
        for x in (x1+60,x1+240):d.line((x,y1+20,x+80,y2-20),fill='#F5FBF7',width=10)
    else:
        for j in range(9):
            y=y1+24+j*(y2-y1-40)/9
            points=[(x,y+5*math.sin((x+offset)/58+j)) for x in range(round(x1+10),round(x2-10),10)]
            d.line(points,fill='#BA9266',width=2)
