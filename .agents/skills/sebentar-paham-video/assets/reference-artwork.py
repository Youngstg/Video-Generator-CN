"""Original animated editorial diagrams. No borrowed artwork or product UI."""
from PIL import ImageDraw
import math

def draw(im,key,i,t,e):
 d=ImageDraw.Draw(im);C=e.T;ink=C['ink'];acc=C['accent'];soft=C['soft'];white=e.WHITE
 def text(x,y,s,n=52,c=ink,mono=False):e.txt(d,x,y,s,n,c,mono,anchor='mt')
 def box(b,c=white):e.rr(d,b,c,26)
 def label(y,s,n=50,c=ink):text(540,y,s,n,c)
 def card(y,title,sub=None):
  e.paper(im,(112,y,968,y+180));text(540,y+27,title,58)
  if sub:text(540,y+106,sub,48,acc)
 def arrow(y):
  e.arrow(d,(540,y),(540,y+65),acc,6)
  q=(t*.7)%1;d.ellipse((531,y+q*55-9,549,y+q*55+9),fill=acc)
 def dotgrid():
  for j in range(12):
   x=110+(j*137)%850;y=640+(j*83+t*14)%830
   d.ellipse((x,y,x+5,y+5),fill=soft)
 def pill(y,s):e.pill(d,y,s,acc,white,48)
 def folder(x,y,title):
  box((x-170,y,x+170,y+180),soft);box((x-170,y-20,x-20,y+45),soft);text(x,y+60,title,48)
 def wave(y,mode=0):
  pts=[]
  for x in range(170,911,6):
   amp=(30+35*math.sin(x*.008+t*.7)**2)*(1+.35*mode)
   pts.append((x,y+math.sin(x*.07-t*6)*amp*math.sin((x-170)/740*math.pi)))
  d.line(pts,fill=acc,width=7)
 dotgrid()
 if key=='eval':
  if i==0:
   card(695,'SOAL SULIT','Temukan informasi di web');arrow(900);folder(540,1050,'KUNCI?');pill(1370,'JALUR YANG TAK TERDUGA')
  elif i==1:
   card(680,'BROWSECOMP','Tes pencarian web');label(1020,'06 MARET 2026',65,acc);wave(1230)
  elif i==2:
   for j in range(3):
    y=720+j*190;box((135,y,945,y+145));text(475,y+42,['Pencarian web','Sumber lain','Cari lagi'][j],55);e.cross(d,875,y+76,acc)
   pill(1370,'BANYAK UPAYA GAGAL')
  elif i==3:
   card(690,'Cari jawaban');arrow(900);card(1010,'Cari identitas tes','Apakah ini benchmark?');pill(1370,'PERTANYAAN BERUBAH')
  elif i==4:
   folder(315,760,'DATA');folder(765,760,'METODE');arrow(1000);card(1110,'Kunci ditemukan','Bahan tersedia di web')
  elif i==5:
   label(695,'2 / 1.266',112,acc);label(850,'Pada konfigurasi multi-agent',48)
   for j in range(1266):
    x=180+(j%42)*17;y=990+(j//42)*10;d.ellipse((x,y,x+5,y+5),fill=acc if j<2 else soft)
   label(1385,'Jumlah kasus, bukan semua AI',48)
  else:
   card(690,'SKOR','Seberapa tinggi?');arrow(905);card(1040,'PROSES','Dari mana jawabannya?');pill(1380,'CEK KEDUANYA')
 elif key=='tokens':
  if i in [0,4]:
   e.paper(im,(145,690,935,1150));text(540,737,'FINAL ANSWER',55);d.line((210,845,870,845),fill=soft,width=3)
   if int(t*2)%2:d.line((225,904,225,958),fill=acc,width=5)
   pill(1290,'THINKING TETAP DIHITUNG')
  elif i==1:
   card(680,'REASONING','Thinking tokens');wave(1040);card(1190,'JAWABAN','Teks yang terlihat')
  elif i in [2,3]:
   label(670,'BATAS OUTPUT',65);label(765,'1.000 token • contoh',54,acc)
   for j in range(40):
    x=170+j%8*95;y=925+j//8*69;box((x,y,x+65,y+45),acc if j<int((t%5)/5*41) else soft)
   label(1330,'Thinking + jawaban',58);label(1415,'Berbagi jatah yang sama',48)
  elif i==5:
   card(680,'thinking_level','Atur proses reasoning');arrow(905);card(1030,'usage + status','Periksa hasil request');pill(1380,'SESUAI DUKUNGAN MODEL')
  else:
   card(700,'TEKS TERLIHAT');label(960,'≠',120,acc);card(1160,'SELURUH TOKEN')
 elif key=='video':
  if i in [0,1,6]:
   label(658,['REKAMAN RAPAT','NAVIGASI KONTEN','PETUNJUK TRANSCRIPT','PILIHAN FRAME','','','BAGIAN YANG RELEVAN'][i],52)
   for j in range(6):
    x=160+j%3*267;y=780+j//3*235;sel=j==int(t*.65)%6
    box((x,y,x+226,y+165),acc if sel else soft)
    d.polygon([(x+94,y+49),(x+94,y+111),(x+147,y+80)],fill=white)
    text(x+113,y+177,f'{j*10:02d}:00',48)
   pill(1350,'DI MANA BIAYA DIBAHAS?' if i!=3 else 'STATIS / ADAPTIF')
  elif i==2:
   card(660,'TRANSCRIPT RAPAT','Petunjuk waktu dari teks')
   for j,(stamp,topic) in enumerate([('08:20','Rencana'),('24:10','Biaya proyek'),('46:35','Jadwal')]):
    y=940+j*140;box((130,y,950,y+110),soft if j==1 else white);text(305,y+27,stamp,51);text(665,y+27,topic,50)
   pill(1400,'PERIKSA FRAME / AUDIO')
  elif i==3:
   for row,title in enumerate(['STATIS: INTERVAL TETAP','ADAPTIF: SESUAI PERTANYAAN']):
    y=730+row*390;label(y,title,49)
    for j in range(8):
     x=160+j*100;box((x,y+100,x+70,y+220),acc if row==0 or j in [2,3] else soft)
   label(1450,'Ilustrasi pemilihan konten',48)
  elif i==4:
   label(700,'HINGGA',58);label(850,'88%',160,acc);label(1080,'lebih sedikit token',62);label(1250,'Klaim Google • video panjang',48);label(1360,'Hasil dapat berbeda',49)
  else:
   card(690,'VIDEO PANJANG','Bisa hemat token');arrow(910);card(1060,'KLIP PENDEK','Navigasi bisa menambah waktu')
 elif key=='agent':
  if i in [0,1,4,6]:
   card(665,'API REQUEST','Buat grafik penjualan');arrow(870)
   e.paper(im,(120,980,960,1440));text(540,1010,'LINUX SANDBOX',58)
   for j,s in enumerate(['BACA','JALANKAN','SIMPAN']):
    x=270+j*270;box((x-113,1150,x+113,1330),soft);text(x,1200,s,48)
    if j==int(t)%3:e.check(d,x,1380,acc,1.2)
  elif i==2:
   folder(300,710,'CSV');folder(780,710,'PYTHON');arrow(980);card(1120,'Data → grafik','Ilustrasi tugas agent')
  elif i==3:
   e.paper(im,(140,660,940,1250));text(540,700,'PENJUALAN',55)
   for j,h in enumerate([140,220,175,290]):
    x=230+j*160;hh=h*(.94+.06*math.sin(t+j));box((x,1130-hh,x+95,1130),acc)
   pill(1370,'PERIKSA → SIMPAN')
  else:
   card(690,'SESI LANJUTAN','File dan state');arrow(910);card(1070,'AKSES TOOLS','Sesuai kebutuhan tugas')
 elif key=='voice':
  if i in [0,1,2,6]:
   card(675,'DESKRIPSI KARAKTER', ['Persona suara baru','Usia • timbre • aksen','Hangat • jelas • santai','','','','Bagian dari desain produk'][i]);arrow(900);wave(1110,i%3);label(1320,'Ilustrasi visual voice design',48)
  elif i==3:
   wave(830);card(1070,'voice_…','Persona yang dapat dipakai lagi');pill(1390,'KARAKTER KONSISTEN')
  elif i==4:
   card(685,'VOICE DESIGN','Membuat persona baru');card(1090,'VOICE REPLICATION','Menggunakan referensi suara')
  else:
   e.paper(im,(180,720,900,1240));d.ellipse((420,790,660,1030),fill=soft);e.check(d,540,915,acc,3);label(1100,'PERSETUJUAN',60);pill(1380,'VERIFIKASI REPLICATION')
 elif key=='json':
  if i in [0,1,3,4]:
   e.paper(im,(120,700,960,1230));text(540,750,'ATURAN SCHEMA' if i==1 else 'JSON OUTPUT',55)
   lines=['{','  "total": 90000,','  "currency": "IDR"','}'] if i!=1 else ['{','  total: number,','  currency: string','}']
   for j,s in enumerate(lines):e.txt(d,177,875+j*73,s,48,ink,True)
   pill(1350,'STRUKTUR ≠ KEBENARAN' if i!=1 else 'ILUSTRASI ATURAN SCHEMA')
  elif i==2:
   folder(310,740,'30.000');folder(770,740,'30.000');label(540 if False else 1010,'+',80,acc);label(1190,'60.000',120,acc);label(1370,'TOTAL YANG BENAR',53)
  elif i==5:
   card(690,'DATA SUMBER','2 × 30.000');arrow(910);card(1070,'HITUNG ULANG','Hasil: 60.000')
  else:
   card(680,'VALID FORMAT');e.check(d,870,770,acc,1.2);card(1090,'BENAR ISI?');label(1390,'Dua pemeriksaan berbeda',50)
 elif key=='tools':
  if i in [0,2,3]:
   label(670,'58 TOOLS' if i!=3 else 'SATU TUGAS',75,acc)
   for j in range(15):
    x=180+j%5*150;y=850+j//5*130+math.sin(t+j)*7;box((x,y,x+115,y+100),soft)
    for k in range(3):d.line((x+20,y+25+k*20,x+94,y+25+k*20),fill=acc,width=4)
   label(1315,'≈55.000 token',76,acc);label(1420,'Contoh 5 integrasi • Anthropic',48)
  elif i==1:
   for j,s in enumerate(['NAMA TOOL','DESKRIPSI','ATURAN INPUT']):card(680+j*260,s)
  elif i in [4,5]:
   card(670,'TOOL SEARCH','Cari yang relevan');arrow(880)
   for j,s in enumerate(['CARI','PILIH','MUAT']):
    y=1030+j*135;box((250,y,830,y+95),soft if j!=int(t)%3 else white);text(540,y+19,s,51)
  else:
   card(700,'BANYAK ALAT');arrow(930);card(1100,'PILIH SESUAI TUGAS');pill(1390,'EFISIEN DALAM CONTEXT')
 # Continuous gentle motion without a playback progress indicator.
 z=1.003+.003*math.sin(t*.85);crop=im.crop((65,603,1015,1527));w,h=crop.size
 crop=crop.resize((round(w*z),round(h*z)));dx=(crop.width-w)//2;dy=(crop.height-h)//2
 im.paste(crop.crop((dx,dy,dx+w,dy+h)),(65,603))
