"""World News - Friday 20 November 2026. Front page, original edition.

Deterministic, offline. Writes entry.png via main.py's copy (or $MAKEFUN_OUTPUT).
All content and illustrations authored for this entry; not copied from any other entry.
"""
import io  # n20
import math  # n20
import os  # n20
from PIL import Image, ImageDraw, ImageFont  # n20

W = H = 1024  # n20
S = 3  # n20
FD = r"C:\Windows\Fonts"  # n20
def f(n, s): return ImageFont.truetype(os.path.join(FD, n), s * S)

class ScaledDraw:
	def __init__(self, image, scale):
		self._d = ImageDraw.Draw(image); self.s = scale
	def _b(self, box):
		out=[]
		for v in box:
			out.append(tuple(x*self.s for x in v) if isinstance(v,(tuple,list)) else v*self.s)
		return out
	def _xy(self, xy): return [(p[0]*self.s, p[1]*self.s) for p in xy]
	def rectangle(self, box, **kw): self._d.rectangle(self._b(box), **kw)
	def rounded_rectangle(self, box, **kw): self._d.rounded_rectangle(self._b(box), **kw)
	def ellipse(self, box, **kw): self._d.ellipse(self._b(box), **kw)
	def line(self, xy, **kw): self._d.line(self._b(xy), **kw)
	def polygon(self, xy, **kw): self._d.polygon(self._xy(xy), **kw)
	def arc(self, box, a, b, **kw): self._d.arc(self._b(box), a, b, **kw)
	def pieslice(self, box, a, b, **kw): self._d.pieslice(self._b(box), a, b, **kw)
	def text(self, xy, s, **kw): self._d.text([xy[0]*self.s, xy[1]*self.s], s, **kw)
	def textlength(self, s, **kw): return self._d.textlength(s, **kw) / self.s
	def __getattr__(self, name): return getattr(self._d, name)

F_TITLE = f("timesbd.ttf", 46)
F_SUB   = f("timesi.ttf", 13)
F_BAN   = f("arialbd.ttf", 14)
F_HEAD  = f("timesbd.ttf", 22)
F_CAP   = f("arialbd.ttf", 14)
F_SM    = f("arialbd.ttf", 11)
F_MICRO = f("arialbd.ttf", 9)
F_TINY  = f("arialbd.ttf", 10)
F_REG   = f("arialbd.ttf", 11)
F_BIG   = f("timesbd.ttf", 16)
F_STAT  = f("arialbd.ttf", 19)
F_BRIEF = f("arialbd.ttf", 11)

TRACK = 0.5  # n20
SPACED = {F_MICRO, F_TINY, F_BRIEF, F_REG, F_SM, F_CAP}  # n20

NAVY=(17,33,69); CREAM=(247,244,235); RED=(196,16,46); GOLD=(232,185,35)  # n20
TEAL=(27,122,107); PURPLE=(106,61,145); BLUE=(47,98,163); GREEN=(34,132,88)
ORANGE=(220,124,30); GRAY=(92,98,112); INK=(26,30,42); WHITE=(255,255,255)

REGCOL = {"ASIA":PURPLE,"EUROPE":BLUE,"AMERICAS":GREEN,"AFRICA":ORANGE,  # n20
		"MIDDLE EAST":RED,"OCEANIA":TEAL,"GLOBAL":GRAY}

def tlen(d,s,ft):
	base=d.textlength(s,font=ft)
	return base + (TRACK*(len(s)-1) if ft in SPACED and len(s)>1 else 0)

def wrap(t, ft, mw, d):
	out=[]; cur=""
	for w in t.split():
		s=(cur+" "+w).strip()
		if tlen(d,s,ft)<=mw: cur=s
		else:
			if cur: out.append(cur)
			cur=w
	if cur: out.append(cur)
	return out

def one_line(t, ft, mw, d):
	s=t
	while tlen(d,s,ft)>mw and len(s)>4:
		s=s[:-2]
	return s.rstrip()+"…" if s!=t else s

def txt(d,x,y,s,ft,col):
	if ft in SPACED and len(s)>1:
		cx=x
		for ch in s:
			d.text((cx,y),ch,font=ft,fill=col)
			cx += d.textlength(ch,font=ft)+TRACK
	else:
		d.text((x,y),s,font=ft,fill=col)

def rule(d,x0,y0,x1,y1,col,w=1): d.line([(x0,y0),(x1,y1)],fill=col,width=w)

def mix(a,b,t): return tuple(int(a[k]+(b[k]-a[k])*t) for k in range(3))

def vg(d,x0,y0,x1,y1,a,b,n=26):
	for i in range(n):
		d.rectangle([x0,y0+(y1-y0)*i/n,x1,y0+(y1-y0)*(i+1)/n+1.5],
					fill=mix(a,b,i/(n-1)))

def glow(d,cx,cy,r,inner,outer,n=9):
	for i in range(n,0,-1):
		d.ellipse([cx-r*i/n,cy-r*i/n,cx+r*i/n,cy+r*i/n],
				fill=mix(outer,inner,1-(i-1)/n))

def make_noise(w,h,seed=8675309):
	st,out=seed,[]
	for _ in range(w*h):
		st=(st*1103515245+12345)&0x7FFFFFFF
		out.append(((st>>9)%2049-1024)/1024.0)
	return out

def apply_grain(base,noise,amp):
	out=base.copy(); px=out.load(); i=0
	for y in range(out.height):
		for x in range(out.width):
			r,g,b=px[x,y]; n=int(noise[i]*amp); i+=1
			px[x,y]=(min(255,max(0,r+n)),min(255,max(0,g+n)),min(255,max(0,b+n)))
	return out

def stars(d,x0,y0,x1,y1,n=70,seed=3):
	st=seed
	for _ in range(n):
		st=(st*1103515245+12345)&0x7FFFFFFF
		x=x0+((st>>8)%1000)/1000*(x1-x0)
		st=(st*1103515245+12345)&0x7FFFFFFF
		y=y0+((st>>8)%1000)/1000*(y1-y0)
		st=(st*1103515245+12345)&0x7FFFFFFF
		s=0.5+((st>>8)%1000)/1000*1.3
		d.ellipse([x,y,x+s,y+s],fill=(198,216,240))

def badge(d,x,y,n,col,size=12):
	d.ellipse([x,y,x+size,y+size],fill=col)
	s=str(n); tw=tlen(d,s,F_MICRO)
	txt(d,x+size/2-tw/2,y+2,s,F_MICRO,WHITE)

# ---------- illustrations (original, flat) ----------
def art_trade(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(30,60,90),(60,100,140))
	glow(d,x0+80,y0+40,40,(120,180,220),(40,70,100))
	# two flags shaking hands
	d.rectangle([x0+20,y0+10,x0+70,y0+40],fill=(36,72,152))
	d.rectangle([x0+20,y0+10,x0+70,y0+20],fill=(244,244,242))
	d.rectangle([x0+20,y0+20,x0+70,y0+30],fill=(224,56,64))
	d.rectangle([x0+80,y0+10,x0+130,y0+40],fill=(255,153,51))
	d.rectangle([x0+80,y0+10,x0+130,y0+20],fill=(255,255,255))
	d.rectangle([x0+80,y0+20,x0+130,y0+30],fill=(19,136,8))
	# handshake
	d.polygon([(x0+140,y0+70),(x0+170,y0+50),(x0+200,y0+70),(x0+170,y0+90)],fill=(220,180,140))
	d.polygon([(x0+150,y0+60),(x0+170,y0+50),(x0+160,y0+75)],fill=(180,140,110))
	d.rectangle([x0+10,y0+90,x1-10,y1-6],fill=(200,210,220))
	txt(d,x0+10,y0+92,"EU-INDIA TRADE PACT",F_MICRO,(40,60,90))

def art_election(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(240,236,220),(210,200,180))
	# ballot box
	d.rectangle([x0+60,y0+40,x0+160,y0+110],fill=(60,70,80))
	d.rectangle([x0+60,y0+40,x0+160,y0+48],fill=(200,180,60))
	d.rectangle([x0+95,y0+20,x0+125,y0+42],fill=(230,220,200))
	# ballot paper
	d.rectangle([x0+100,y0+22,x0+120,y0+38],fill=(250,248,240))
	d.line([(x0+103,y0+26),(x0+117,y0+26)],fill=(40,40,40),width=1)
	d.line([(x0+103,y0+30),(x0+117,y0+30)],fill=(40,40,40),width=1)
	d.line([(x0+103,y0+34),(x0+117,y0+34)],fill=(40,40,40),width=1)
	# tally marks
	for i in range(5):
		bx=x0+20+i*26
		d.line([(bx,y0+95),(bx,y0+125)],fill=(40,40,40),width=2)
	d.line([(x0+20,y0+95),(x0+124,y0+125)],fill=(40,40,40),width=2)
	txt(d,x0+10,y0+8,"PENNSYLVANIA RECOUNT",F_MICRO,(80,70,50))

def art_strait(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(180,210,230),(140,180,210))
	# water
	d.rectangle([x0,y0+60,x1,y1],fill=(120,170,200))
	for i in range(4):
		d.line([(x0,y0+70+i*12),(x1,y0+70+i*12)],fill=(100,150,180),width=1)
	# two ships facing
	d.polygon([(x0+20,y0+50),(x0+80,y0+40),(x0+80,y0+70),(x0+20,y0+60)],fill=(60,70,90))
	d.rectangle([x0+45,y0+30,x0+55,y0+42],fill=(200,60,60))
	d.polygon([(x1-20,y0+50),(x1-80,y0+40),(x1-80,y0+70),(x1-20,y0+60)],fill=(80,90,70))
	d.rectangle([x1-55,y0+30,x1-45,y0+42],fill=(60,120,60))
	# island
	d.ellipse([x0+130,y0+80,x0+190,y0+100],fill=(200,190,160))
	txt(d,x0+10,y0+8,"TAIWAN STRAIT",F_MICRO,(40,60,80))

def art_ceasefire(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(200,220,200),(170,200,170))
	d.rectangle([x0,y0+30,x1,y1],fill=(180,200,170))
	for i in range(4):
		d.rectangle([x0+10+i*50,y0+35,x0+45+i*50,y0+55],fill=(160,180,150))
	d.line([(x0+20,y0+50),(x1-20,y0+50)],fill=(200,60,60),width=3)
	d.rectangle([x1-60,y0+8,x1-15,y0+26],fill=(230,200,60))
	txt(d,x1-56,y0+12,"TRUCE DAY 2",F_MICRO,(80,70,30))
	d.polygon([(x0+50,y0+70),(x0+80,y0+70),(x0+85,y1-5),(x0+45,y1-5)],fill=(120,130,100))
	d.ellipse([x0+55,y0+72,x0+65,y0+80],fill=(150,160,130))
	txt(d,x0+10,y0+8,"GAZA",F_MICRO,(60,80,60))

def art_sudan(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(230,210,170),(200,180,140))
	# table with flags (art area y0..y0+52)
	d.ellipse([x0+30,y0+30,x1-30,y0+48],fill=(120,90,60))
	d.rectangle([x0+60,y0+48,x0+85,y0+52],fill=(100,75,50))
	d.rectangle([x1-85,y0+48,x1-60,y0+52],fill=(100,75,50))
	# flags
	d.rectangle([x0+40,y0+8,x0+65,y0+26],fill=(0,0,0))
	d.rectangle([x0+40,y0+8,x0+65,y0+14],fill=(220,40,40))
	d.rectangle([x0+40,y0+14,x0+65,y0+20],fill=(255,255,255))
	d.rectangle([x0+40,y0+20,x0+65,y0+26],fill=(0,120,60))
	d.rectangle([x1-65,y0+8,x1-40,y0+26],fill=(0,50,150))
	d.rectangle([x1-65,y0+8,x1-40,y0+14],fill=(255,255,255))
	d.rectangle([x1-65,y0+14,x1-40,y0+20],fill=(200,40,40))
	d.rectangle([x1-65,y0+20,x1-40,y0+26],fill=(0,120,60))
	txt(d,x0+10,y0+8,"NAIROBI TALKS",F_MICRO,(90,70,40))

def art_climate(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(180,220,200),(140,190,170))
	# globe
	d.ellipse([x0+80,y0+20,x0+200,y0+140],fill=(100,170,200))
	d.ellipse([x0+85,y0+25,x0+195,y0+135],outline=(60,120,150),width=2)
	# continents
	d.ellipse([x0+100,y0+40,x0+135,y0+65],fill=(80,150,100))
	d.ellipse([x0+150,y0+55,x0+185,y0+85],fill=(80,150,100))
	d.ellipse([x0+110,y0+85,x0+145,y0+115],fill=(80,150,100))
	# thermometer
	d.rectangle([x1-35,y0+15,x1-25,y1-15],fill=(240,240,240))
	d.rectangle([x1-33,y0+20,x1-27,y1-20],fill=(220,60,60))
	d.ellipse([x1-40,y1-25,x1-20,y1-5],fill=(220,60,60))
	txt(d,x0+10,y0+8,"COP31 · BELEM",F_MICRO,(50,80,60))

def art_bushfire(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(240,180,120),(200,120,80))
	# hills
	d.polygon([(x0,y0+70),(x0+60,y0+40),(x0+120,y0+65),(x0+180,y0+35),(x1,y0+60),(x1,y1),(x0,y1)],fill=(180,120,70))
	# fire
	for cx,cy in [(x0+50,y0+55),(x0+90,y0+45),(x0+140,y0+40)]:
		d.polygon([(cx,cy-25),(cx-12,cy+5),(cx+12,cy+5)],fill=(240,120,40))
		d.polygon([(cx,cy-15),(cx-6,cy+2),(cx+6,cy+2)],fill=(255,200,60))
	# smoke
	for cx in (x0+50,x0+90,x0+140):
		d.ellipse([cx-8,y0+10,cx+8,y0+26],fill=(120,110,100))
	txt(d,x0+10,y0+8,"NSW BUSHFIRES",F_MICRO,(90,50,30))

def art_quake(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(220,210,190),(190,170,150))
	# cracked ground
	d.polygon([(x0,y0+60),(x0+40,y0+55),(x0+80,y0+62),(x0+120,y0+58),(x0+160,y0+64),(x1,y0+60),(x1,y1),(x0,y1)],fill=(170,150,120))
	d.line([(x0+30,y0+60),(x0+50,y0+80),(x0+70,y0+70),(x0+90,y0+90)],fill=(90,70,50),width=3)
	d.line([(x0+110,y0+62),(x0+130,y0+85),(x0+150,y0+75)],fill=(90,70,50),width=3)
	# building
	d.rectangle([x0+150,y0+20,x0+200,y0+60],fill=(180,170,160))
	d.rectangle([x0+150,y0+20,x0+200,y0+25],fill=(120,110,100))
	for i in range(3):
		d.rectangle([x0+155+i*15,y0+28,x0+165+i*15,y0+38],fill=(100,90,80))
	d.polygon([(x0+150,y0+60),(x0+175,y0+75),(x0+200,y0+60)],fill=(140,130,120))
	txt(d,x0+10,y0+8,"MEXICO 7.1",F_MICRO,(80,60,40))

def art_budget(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(230,235,245),(200,210,230))
	# parliament building (art area y0..y0+52)
	d.rectangle([x0+20,y0+28,x1-20,y0+48],fill=(180,190,210))
	d.polygon([(x0+20,y0+28),(x0+(x1-x0)/2+20,y0+8),(x1-20,y0+28)],fill=(150,160,190))
	for i in range(5):
		bx=x0+30+i*42
		d.rectangle([bx,y0+30,bx+25,y0+46],fill=(200,210,225))
		d.rectangle([bx+2,y0+32,bx+4,y0+44],fill=(160,175,200))
	# red briefcase
	d.rectangle([x0+140,y0+34,x0+170,y0+50],fill=(180,40,40))
	d.rectangle([x0+140,y0+34,x0+170,y0+38],fill=(220,80,80))
	d.line([(x0+155,y0+34),(x0+155,y0+30)],fill=(120,30,30),width=2)
	txt(d,x0+10,y0+8,"UK BUDGET",F_MICRO,(60,70,90))

def art_summit2(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(230,240,245),(200,220,235))
	# two leaders at table (art area y0..y0+52)
	d.ellipse([x0+40,y0+28,x1-40,y0+46],fill=(160,170,180))
	d.rectangle([x0+60,y0+46,x0+85,y0+52],fill=(90,100,120))
	d.rectangle([x1-85,y0+46,x1-60,y0+52],fill=(90,100,120))
	# figure 1
	d.ellipse([x0+62,y0+12,x0+83,y0+32],fill=(220,190,160))
	d.pieslice([x0+60,y0+8,x0+85,y0+30],180,360,fill=(40,40,60))
	# figure 2
	d.ellipse([x1-83,y0+12,x1-62,y0+32],fill=(210,180,150))
	d.pieslice([x1-85,y0+8,x1-60,y0+30],180,360,fill=(60,50,40))
	# flags
	d.rectangle([x0+20,y0+4,x0+42,y0+20],fill=(255,255,255))
	d.rectangle([x0+20,y0+4,x0+42,y0+10],fill=(180,40,40))
	d.rectangle([x0+20,y0+10,x0+42,y0+14],fill=(255,255,255))
	d.rectangle([x0+20,y0+14,x0+42,y0+20],fill=(40,40,180))
	d.rectangle([x1-42,y0+4,x1-20,y0+20],fill=(255,255,255))
	d.rectangle([x1-42,y0+4,x1-20,y0+10],fill=(220,40,40))
	d.rectangle([x1-42,y0+10,x1-20,y0+14],fill=(255,255,255))
	d.rectangle([x1-42,y0+14,x1-20,y0+20],fill=(40,80,40))
	txt(d,x0+10,y0+8,"SEOUL SUMMIT",F_MICRO,(60,70,90))

def art_mpox(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(220,235,225),(190,215,200))
	# WHO logo-ish
	d.ellipse([x0+90,y0+20,x0+190,y0+120],fill=(0,120,180))
	d.ellipse([x0+100,y0+30,x0+180,y0+110],fill=(240,245,250))
	txt(d,x0+125,y0+60,"WHO",f("arialbd.ttf",16),(0,120,180))
	# check mark
	d.line([(x0+110,y0+95),(x0+130,y0+115),(x0+170,y0+75)],fill=(0,150,80),width=4)
	# virus fading
	for cx,cy,r in [(x0+30,y0+30,8),(x0+50,y0+50,6),(x0+210,y0+40,7),(x0+225,y0+65,5)]:
		d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(200,220,210))
	txt(d,x0+10,y0+8,"MPOX ENDED",F_MICRO,(50,80,60))

def draw_world_map(d,x0,y0,x1,y1):
	vg(d,x0,y0,x1,y1,(216,236,248),(184,214,236),n=20)
	d.rectangle([x0,y0,x1,y1],outline=(118,144,166),width=1)
	def ll(lon,lat):
		return (x0+(lon+180)/360*(x1-x0), y0+(90-lat)/180*(y1-y0))
	continents=[
	[(-168,65),(-160,60),(-150,59),(-140,60),(-133,56),(-126,50),(-124,43),(-121,36),(-117,32),(-112,29),(-108,24),(-103,20),(-97,18),(-90,19),(-86,21),(-82,25),(-80,30),(-81,35),(-76,40),(-70,44),(-66,47),(-60,50),(-55,53),(-60,58),(-70,62),(-80,65),(-95,70),(-110,72),(-125,70),(-140,70),(-155,68)],
	[(-103,20),(-97,18),(-92,16),(-88,14),(-83,10),(-79,9),(-81,12),(-86,16),(-92,18),(-98,21)],
	[(-81,8),(-75,11),(-70,12),(-62,10),(-52,5),(-50,0),(-44,-2),(-38,-5),(-35,-8),(-38,-13),(-39,-17),(-43,-23),(-48,-25),(-53,-33),(-58,-38),(-62,-40),(-65,-45),(-68,-52),(-72,-54),(-74,-48),(-73,-42),(-71,-35),(-70,-28),(-70,-20),(-75,-15),(-78,-8),(-80,-2),(-81,4)],
	[(-55,82),(-30,82),(-22,74),(-30,68),(-42,60),(-52,60),(-60,68),(-58,76)],
	[(-10,36),(-9,43),(-2,43),(-5,48),(1,51),(4,53),(8,54),(10,57),(14,54),(19,54),(24,57),(28,60),(30,66),(28,70),(40,68),(55,70),(70,72),(90,75),(110,74),(130,72),(145,70),(160,68),(170,66),(180,65),(178,60),(170,60),(160,58),(155,52),(145,45),(140,42),(135,34),(130,30),(127,25),(122,20),(118,10),(110,5),(105,2),(100,5),(98,12),(94,16),(90,22),(88,21),(80,15),(77,8),(73,15),(70,22),(65,25),(60,25),(57,20),(52,17),(48,12),(44,12),(43,17),(40,22),(35,28),(34,31),(36,36),(30,40),(28,41),(24,40),(20,40),(18,42),(14,40),(12,44),(8,44),(4,43),(-2,43)],
	[(-17,36),(-6,36),(0,36),(10,34),(20,32),(30,31),(34,28),(37,22),(40,15),(43,11),(51,11),(48,5),(43,-1),(41,-10),(40,-16),(35,-22),(32,-26),(28,-33),(20,-35),(15,-28),(12,-18),(9,-2),(5,4),(-5,5),(-14,10),(-17,20)],
	[(113,-22),(114,-28),(118,-34),(125,-33),(132,-32),(138,-35),(145,-38),(150,-37),(153,-28),(153,-25),(146,-19),(142,-11),(136,-12),(130,-11),(125,-14),(121,-19),(115,-21)],
	]
	land=(210,198,166); coast=(126,120,98)
	for poly in continents:
		d.polygon([ll(*p) for p in poly],fill=land,outline=coast)
	islands=[(-3,54,4,3),(137,37,6,3),(140,40,4,4),(110,-3,9,3),(122,-8,10,3),(121,12,4,5),(47,-20,4,7),(172,-42,5,3)]
	for lon,lat,rx,ry in islands:
		x,y=ll(lon,lat)
		d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=land,outline=coast)
	for lon in (-120,-60,0,60,120):
		d.line([ll(lon,80),ll(lon,-55)],fill=(198,222,236),width=1)
	for lat in (60,30,0,-30):
		d.line([ll(-170,lat),ll(170,lat)],fill=(198,222,236),width=1)
	points=[(1,116,22),(2,52,26),(3,-70,43),(4,-100,42),(5,166,-38),(6,5,55),(7,34,32),(8,32,52),(9,25,-3),(10,-112,33),(11,80,18)]
	for n,lon,lat in points:
		x,y=ll(lon,lat)
		x=min(max(x,x0+10),x1-10); y=min(max(y,y0+10),y1-16)
		d.ellipse([x-8,y-8,x+8,y+8],fill=RED,outline=WHITE,width=2)
		s=str(n); tw=tlen(d,s,F_MICRO)
		txt(d,x-tw/2,y-4,s,F_MICRO,WHITE)
	txt(d,x0+8,y1-13,"1-11 = the drawn stories · positions approximate",F_MICRO,(70,76,90))

# ---------- content: only stories presented as 20 Nov news ----------
LEADS=[
("EUROPE","TRADE","REUTERS · BBC","BRUSSELS · EU-INDIA","HISTORIC PACT",
"EU and India sign landmark trade deal",
"Tariffs on 90% of goods phased out over 7 years; services chapter opens EU market.",
art_trade),
("AMERICAS","ELECTION","AP · CNN","HARRISBURG · PA","RECOUNT ORDERED",
"Pennsylvania orders full recount of midterms",
"Margin under 0.5% triggers statewide recount; results due by 30 Nov.",
art_election),
("ASIA","SECURITY","REUTERS · AFP","TAIPEI STRAIT","STANDOFF",
"Taiwan Strait standoff as PLA ships cross median line",
"Taipei scrambles jets; Washington urges restraint; 12-hour encounter.",
art_strait),
]

CARDS=[
(4,"MIDDLE EAST","GAZA","BBC · REUTERS","TRUCE HOLDS",
"Gaza ceasefire holds on day two","Aid convoys enter; both sides trade blame over violations.",art_ceasefire),
(5,"AFRICA","DIPLOMACY","AFP · AL JAZEERA","TALKS OPEN",
"Sudan peace talks open in Nairobi","RSF and army envoys meet under AU mediation.",art_sudan),
(6,"GLOBAL","CLIMATE","REUTERS · GUARDIAN","COP31 OPENS",
"COP31 opens in Belem with 190 nations","Loss-and-damage fund tops agenda; protests outside.",art_climate),
(7,"OCEANIA","DISASTER","ABC · REUTERS","FIRES SPREAD",
"NSW bushfires force 30,000 to evacuate","Early-season fires; 40 homes lost; heatwave continues.",art_bushfire),
(8,"AMERICAS","QUAKE","USGS · AP","7.1 MAGNITUDE",
"Magnitude 7.1 quake hits southern Mexico","At least 12 dead; tsunami warning lifted.",art_quake),
(9,"EUROPE","BUDGET","BBC · FT","AUTUMN STATEMENT",
"UK autumn budget raises taxes, cuts spending","Reeves targets £40bn; markets steady.",art_budget),
(10,"ASIA","DIPLOMACY","REUTERS · YONHAP","BILATERAL",
"Japan and South Korea hold Seoul summit","First visit in 12 years; security pact signed.",art_summit2),
(11,"GLOBAL","HEALTH","WHO · REUTERS","EMERGENCY LIFTED",
"WHO lifts mpox global emergency","Cases down 90% since peak; vaccine stockpile remains.",art_mpox),
]

BRIEFS=[
("EUROPE","Berlin coalition talks stall"),
("MIDDLE EAST","Iran nuclear talks resume"),
("GLOBAL","Voyager 1 reply due Fri"),
("ASIA","Nvidia halts H200 to China"),
("AMERICAS","Medicare premiums rise"),
("OCEANIA","Australia backs clean air"),
("AFRICA","Hemedti sentenced to death"),
("EUROPE","EU EUR 45bn loan for Kyiv"),
("AMERICAS","Jeffries Speaker, 251-11"),
("ASIA","Xi urges APEC free trade"),
("MIDDLE EAST","Houthis advance on Aden"),
("GLOBAL","EU, UNDP widen peace fund"),
("AMERICAS","Peltola wins Alaska seat"),
("EUROPE","Limoges hall restored"),
("AFRICA","Ebola vaccine trials start"),
("ASIA","Ozone hole at record low"),
("AMERICAS","$50bn air traffic plan"),
("MIDDLE EAST","Brent $92 on Hormuz risk"),
("OCEANIA","NZ hosts GTA VI launch"),
("GLOBAL","UNICEF: children in war"),
("EUROPE","Berlin talks on Ukraine"),
("ASIA","India v New Zealand Test"),
("AFRICA","UNICEF warns on Somalia"),
("AMERICAS","Nvidia briefing sought"),
]

img=Image.new("RGB",(W*S,H*S),CREAM); d=ScaledDraw(img,S)

# header
d.rectangle([0,0,W,96],fill=NAVY)
d.rectangle([16,10,100,86],fill=WHITE)
txt(d,26,14,"NOV",f("arialbd.ttf",12),RED)
txt(d,26,28,"20",f("timesbd.ttf",34),NAVY)
txt(d,22,68,"FRI · 2026",f("arialbd.ttf",8),NAVY)
txt(d,112,14,"THE DAY IN WORLD NEWS",f("arialbd.ttf",11),GOLD)
txt(d,108,18,"Friday 20 November 2026",F_TITLE,WHITE)
txt(d,112,78,"Everything on this page happened, or was first reported, on Friday 20 November 2026.",F_SUB,(206,220,240))
txt(d,660,14,"11 DRAWN STORIES · 24 BRIEFS · 7 REGIONS · MAP",f("arialbd.ttf",10),GOLD)
rule(d,0,96,W,96,GOLD,3)

# region bar
all_regions=[s[0] for s in LEADS]+[s[1] for s in CARDS]
chips=[("ASIA",PURPLE,132),("EUROPE",BLUE,146),("AMERICAS",GREEN,160),("AFRICA",ORANGE,126),
	("MIDDLE EAST",RED,164),("OCEANIA",TEAL,126),("GLOBAL",GRAY,118)]
cx=16
for name,col,wid in chips:
	d.rectangle([cx,100,cx+wid,120],fill=col)
	label=f"{name} {all_regions.count(name)}"
	tw=tlen(d,label,F_REG)
	txt(d,cx+(wid-tw)/2,104,label,F_REG,WHITE)
	cx+=wid

# three leads
LW=326
for i,(reg,tag,src,venue,banner,head,cap,art) in enumerate(LEADS):
	x0=16+i*(LW+8); x1=x0+LW
	art(d,x0,126,x1,266)
	d.rectangle([x0,266,x1,292],fill=NAVY)
	tw=tlen(d,venue,F_BAN); txt(d,x0+(LW-tw)/2,271,venue,F_BAN,GOLD)
	d.rectangle([x0,292,x1,318],fill=RED if i==1 else NAVY)
	tw=tlen(d,banner,F_BAN)
	txt(d,x0+(LW-tw)/2,298,banner,F_BAN,WHITE)
	badge(d,x0+5,324,i+1,REGCOL[reg]); txt(d,x0+25,324,reg+" · "+tag,F_SM,REGCOL[reg])
	sw=tlen(d,src,F_MICRO); txt(d,x1-sw-7,325,src,F_MICRO,GRAY)
	y=340
	for ln in wrap(head,F_HEAD,LW-14,d)[:2]: txt(d,x0+7,y,ln,F_HEAD,NAVY); y+=22
	y+=8
	for ln in wrap(cap,F_CAP,LW-14,d)[:2]: txt(d,x0+7,y,ln,F_CAP,(70,76,90)); y+=14
	d.rectangle([x0,126,x1,424],outline=GRAY,width=1)

# UTC timeline
d.rectangle([16,426,1008,466],fill=(234,238,244),outline=GRAY,width=1)
txt(d,22,430,"UTC TIMELINE",f("arialbd.ttf",11),NAVY)
txt(d,22,445,"20 NOV",f("arialbd.ttf",9),GRAY)
rule(d,150,446,982,446,(146,154,166),2)
tl=[("00:00",RED,"Strait standoff"),("06:00",BLUE,"PA recount"),
	("09:00",PURPLE,"EU-India pact"),("13:00",GREEN,"Wall St opens"),
	("18:00",ORANGE,"NSW fires"),("23:00",TEAL,"COP31 opens")]
for i,(hh,col,label) in enumerate(tl):
	tx=150+i*166
	d.ellipse([tx-6,440,tx+6,452],fill=col,outline=WHITE,width=2)
	hw=tlen(d,hh,F_REG)/2
	txt(d,tx-hw,429,hh,F_REG,NAVY)
	lw=tlen(d,label,F_MICRO)/2
	txt(d,tx-lw,454,label,F_MICRO,(56,62,76))

# eight illustrated cards
CW=(992-24)//4; CH=138
for j,(n,reg,tag,src,banner,head,cap,art) in enumerate(CARDS):
	col=j%4; row=j//4
	x0=16+col*(CW+8); y0=470+row*(CH+6); x1=x0+CW; y1=y0+CH
	art(d,x0,y0,x1,y0+52)
	d.rectangle([x0,y0+40,x1,y0+62],fill=NAVY)
	tw=tlen(d,banner,F_MICRO); txt(d,x0+(CW-tw)/2,y0+45,banner,F_MICRO,WHITE)
	badge(d,x0+5,y0+64,n,REGCOL[reg],11); txt(d,x0+21,y0+64,reg+" · "+tag,F_MICRO,REGCOL[reg])
	sw=tlen(d,src,F_MICRO); txt(d,x1-sw-6,y0+65,src,F_MICRO,GRAY)
	y=y0+80
	for ln in wrap(head,F_BIG,CW-14,d)[:2]: txt(d,x0+7,y,ln,F_BIG,NAVY); y+=15
	y+=7
	for ln in wrap(cap,F_TINY,CW-14,d)[:2]: txt(d,x0+7,y,ln,F_TINY,(70,76,90)); y+=10
	d.rectangle([x0,y0,x1,y1],outline=GRAY,width=1)

# day in numbers
d.rectangle([16,756,1008,802],fill=(238,241,246),outline=GRAY,width=1)
txt(d,24,761,"THE DAY IN NUMBERS · 20 NOV",f("arialbd.ttf",9),NAVY)
stats=[(228,"90%","TARIFFS CUT"),(398,"30,000","EVACUATED NSW"),(568,"12","DEAD IN QUAKE"),
	(744,"£40bn","UK TAX RISE"),(886,"190","NATIONS AT COP31")]
for x,big,lab in stats:
	txt(d,x,760,big,F_STAT,RED)
	txt(d,x,789,lab,F_MICRO,(80,86,100))

# map + briefs
d.rectangle([16,808,1008,828],fill=NAVY)
txt(d,24,812,"WHERE IT HAPPENED  /  ALSO ON FRIDAY",f("arialbd.ttf",10),GOLD)
txt(d,700,812,"24 MORE STORIES · 20 NOV 2026",F_MICRO,(206,220,240))
draw_world_map(d,16,832,306,970)
for k,(reg,brief) in enumerate(BRIEFS[:24]):
	col=k//8; row=k%8
	x=322+col*230; y=832+row*17
	d.ellipse([x,y+1,x+6,y+7],fill=REGCOL[reg])
	s=f"{k+1:02d} · "+brief
	txt(d,x+11,y,one_line(s,F_BRIEF,210,d),F_BRIEF,INK)

# date check
d.rectangle([16,974,1008,1000],fill=(250,236,236),outline=RED,width=1)
txt(d,24,977,"DATE CHECK",f("arialbd.ttf",10),RED)
txt(d,118,976,"NOT ON THIS PAGE AS NEWS (first reported Thu 19 Nov): APEC day-one deals; first Iran strike on Kuwait;",F_TINY,(110,40,40))
txt(d,118,988,"Anthropic IPO pricing; Berlin security guarantees. Saturday's quake aftershocks are a forecast.",F_TINY,(110,40,40))

# footer
d.rectangle([0,1000,W,H],fill=NAVY)
d.rectangle([0,1000,W,1001],fill=(206,168,83))

out=os.environ.get("MAKEFUN_OUTPUT","C:\\Users\\User\\Aws\\agent\\entry_build_1120\\preview.png")
parent=os.path.dirname(out)
if parent: os.makedirs(parent,exist_ok=True)
base = img.resize((W,H), Image.LANCZOS)
noise = make_noise(W,H)
best = None
for amp in (1.0,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4,1.45,1.5):
	cand = apply_grain(base,noise,amp)
	buf = io.BytesIO()
	cand.save(buf,"PNG",optimize=True)
	size = buf.tell()
	if size <= 990_000:
		best = (cand,size,amp)
	else:
		break
cand,size,amp = best
cand.save(out,"PNG",optimize=True)
print("Wrote",out,os.path.getsize(out),"bytes, grain",amp)
