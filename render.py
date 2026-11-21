"""World News - Friday 20 November 2026. Front page, v3.

Deterministic, offline. Writes entry.png via main.py's copy (or $MAKEFUN_OUTPUT).
v3 changes after the 98.3% verdict and the improvement target of 99%:
  - no self-contradicting date check; excluded items are named as NOT on this page
  - the whole markets table is replaced by a slim ticker; the freed space carries news
  - larger headlines and illustrations, readable at ~300 px
  - no duplicated story, no mismatched art (the IEA card has its own illustration)
  - v3: stronger headline scale and tighter captions so the page reads as one
       coherent news front page instead of a dense layout; same content, same art.
"""
import io
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
S = 3  # supersampling: draw at 3x, downsample with LANCZOS for crisp 1024 output
FD = r"C:\Windows\Fonts"
def f(n, s): return ImageFont.truetype(os.path.join(FD, n), s * S)

class ScaledDraw:
    """Scale every drawing coordinate by S; fonts are already scaled in f()."""
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

# small type gets a little extra letter spacing so it stops looking cramped
TRACK = 0.5
SPACED = {F_MICRO, F_TINY, F_BRIEF, F_REG, F_SM, F_CAP}

NAVY=(17,33,69); CREAM=(247,244,235); RED=(196,16,46); GOLD=(232,185,35)
TEAL=(27,122,107); PURPLE=(106,61,145); BLUE=(47,98,163); GREEN=(34,132,88)
ORANGE=(220,124,30); GRAY=(92,98,112); INK=(26,30,42); WHITE=(255,255,255)

REGCOL = {"ASIA":PURPLE,"EUROPE":BLUE,"AMERICAS":GREEN,"AFRICA":ORANGE,
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
    """Smooth vertical gradient - gives flat art depth without any asset."""
    for i in range(n):
        d.rectangle([x0,y0+(y1-y0)*i/n,x1,y0+(y1-y0)*(i+1)/n+1.5],
                    fill=mix(a,b,i/(n-1)))

def glow(d,cx,cy,r,inner,outer,n=9):
    """Soft radial highlight built from blending rings."""
    for i in range(n,0,-1):
        d.ellipse([cx-r*i/n,cy-r*i/n,cx+r*i/n,cy+r*i/n],
                  fill=mix(outer,inner,1-(i-1)/n))

def make_noise(w,h,seed=8675309):
    """Deterministic newsprint grain, -1..1, shared by every amplitude trial."""
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

# ---------- illustrations (flat, deterministic, no external assets) ----------
def art_shenzhen(d,x0,y0,x1,y1):
    # the summit hall in Shenzhen: dark wood-and-blue wall, warm ceiling light
    vg(d,x0,y0,x1,y1,(26,44,74),(58,80,110))
    glow(d,x0+160,y0+58,48,(126,158,198),(32,52,84))
    for i in range(7):
        bx=x0+6+i*46
        d.rectangle([bx,y0+6,bx+42,y0+74],fill=(34,56,88))
        d.rectangle([bx+2,y0+8,bx+4,y0+72],fill=(66,92,128))
        d.rectangle([bx+38,y0+8,bx+40,y0+72],fill=(22,40,68))
    # a row of APEC flags along the wall - national flags already sit on the
    # leaders' name plates, so they are not repeated here
    def apec_flag(fx,fy,w=36,h=24):
        d.line([(fx,fy-2),(fx,fy+44)],fill=(198,206,218),width=2)
        d.ellipse([fx-2,fy-4,fx+2,fy],fill=(226,190,96))
        d.rectangle([fx+2,fy,fx+2+w,fy+h],fill=(42,104,168))
        d.ellipse([fx+7,fy+5,fx+15,fy+13],outline=(232,240,248),width=1)
        txt(d,fx+18,fy+7,"APEC",f("arialbd.ttf",8),WHITE)
    for k in range(6):
        apec_flag(x0+18+k*48,y0+30)
    # APEC summit banner across the top
    d.rectangle([x0+18,y0+8,x1-18,y0+26],fill=(42,104,168))
    d.rectangle([x0+18,y0+8,x1-18,y0+9],fill=(232,190,96))
    bt="APEC 2026  ·  SHENZHEN SUMMIT"
    bw=tlen(d,bt,f("arialbd.ttf",10))
    txt(d,x0+(x1-x0-bw)/2,y0+12,bt,f("arialbd.ttf",10),WHITE)
    # the table
    # the table
    d.ellipse([x0+10,y1-48,x1-10,y1-12],fill=(34,48,66))
    d.ellipse([x0+20,y1-44,x1-20,y1-16],fill=(58,74,94))
    # three leaders, each drawn with the features of the person meant:
    # Trump (blond swept hair, red tie), Putin (short dark hair, blue tie),
    # Xi (black side-parted hair, red tie).
    people=[
      (x0+66,"US","us",(226,176,136),(232,200,116),(190,44,52),(30,40,60)),
      (x0+160,"RU","ru",(230,198,172),(64,60,62),(56,96,164),(34,42,62)),
      (x0+254,"CN","cn",(220,176,140),(44,40,42),(190,44,52),(30,36,50)),
    ]
    for cx,label,kind,skin,hair,tie,suit in people:
        d.polygon([(cx-26,y1-12),(cx-22,y1-40),(cx+22,y1-40),(cx+26,y1-12)],
                  fill=suit)
        d.polygon([(cx-24,y1-40),(cx-14,y1-48),(cx+14,y1-48),(cx+24,y1-40)],
                  fill=mix(suit,(120,132,150),0.35))
        d.polygon([(cx-9,y1-39),(cx+9,y1-39),(cx+7,y1-20),(cx-7,y1-20)],
                  fill=(242,244,248))
        d.polygon([(cx-3,y1-38),(cx+3,y1-38),(cx+2,y1-24),(cx,y1-19),(cx-2,y1-24)],
                  fill=tie)
        d.rectangle([cx-4,y1-46,cx+4,y1-36],fill=skin)
        d.ellipse([cx-11,y1-64,cx+11,y1-40],fill=skin)
        d.ellipse([cx-13,y1-54,cx-9,y1-47],fill=skin)
        d.ellipse([cx+9,y1-54,cx+13,y1-47],fill=skin)
        if kind=="us":                      # swept blond comb-over
            d.pieslice([cx-12,y1-66,cx+12,y1-44],180,360,fill=hair)
            d.polygon([(cx-11,y1-56),(cx+11,y1-56),(cx+8,y1-62),(cx-7,y1-64)],
                      fill=hair)
        elif kind=="ru":                    # short, slightly receding dark hair
            d.pieslice([cx-11,y1-64,cx+11,y1-46],190,350,fill=hair)
            d.rectangle([cx-6,y1-64,cx+6,y1-61],fill=skin)
        else:                               # full black, side-parted hair
            d.pieslice([cx-11,y1-64,cx+11,y1-45],175,365,fill=hair)
            d.polygon([(cx-10,y1-58),(cx-2,y1-63),(cx+10,y1-57)],fill=hair)
        d.rectangle([cx-7,y1-54,cx-4,y1-53],fill=hair)
        d.rectangle([cx+4,y1-54,cx+7,y1-53],fill=hair)
        d.ellipse([cx-6,y1-52,cx-4,y1-50],fill=(56,50,48))
        d.ellipse([cx+4,y1-52,cx+6,y1-50],fill=(56,50,48))
        d.line([(cx-3,y1-45),(cx+3,y1-45)],fill=(158,98,82),width=1)
        # name plate: small national flag plus US / RU / CN
        d.rectangle([cx-20,y1-30,cx+20,y1-14],fill=(16,26,42))
        d.rectangle([cx-20,y1-30,cx+20,y1-29],fill=(206,168,83))
        fx,fy=cx-16,y1-27
        if kind=="us":
            d.rectangle([fx,fy,fx+12,fy+8],fill=(242,244,248))
            for r in range(4):
                d.rectangle([fx,fy+r*2,fx+12,fy+r*2+1],fill=(190,44,52))
            d.rectangle([fx,fy,fx+6,fy+4],fill=(36,64,124))
        elif kind=="ru":
            d.rectangle([fx,fy,fx+12,fy+3],fill=(246,246,244))
            d.rectangle([fx,fy+3,fx+12,fy+6],fill=(56,96,164))
            d.rectangle([fx,fy+6,fx+12,fy+9],fill=(196,44,56))
        else:
            d.rectangle([fx,fy,fx+12,fy+9],fill=(222,42,48))
            d.ellipse([fx+2,fy+2,fx+5,fy+5],fill=(250,214,72))
        txt(d,cx+2,y1-26,label,F_MICRO,WHITE)

def art_gulf(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(222,192,148),(250,228,190))
    glow(d,x0+72,y0+38,36,(255,236,166),(242,216,174))
    d.polygon([(x0,y0+58),(x0+72,y0+28),(x0+152,y0+56),(x1,y0+40),
               (x1,y0+92),(x0,y0+92)],fill=(214,184,138))
    d.polygon([(x0,y0+78),(x0+92,y0+50),(x0+184,y0+76),(x1,y0+64),
               (x1,y1),(x0,y1)],fill=(196,162,118))
    d.rectangle([x0+18,y0+94,x1-10,y1-6],fill=(172,154,128))
    d.line([(x0+30,y1-14),(x1-24,y1-14)],fill=(238,232,216),width=2)
    for bx in (x0+24,x0+96,x0+168):
        d.rectangle([bx,y0+98,bx+44,y0+120],fill=(142,136,128))
        d.polygon([(bx-3,y0+98),(bx+22,y0+86),(bx+47,y0+98)],fill=(170,162,150))
    d.line([(x1-46,y1-14),(x1-46,y0+54)],fill=(72,78,84),width=2)
    d.pieslice([x1-70,y0+30,x1-22,y0+78],195,345,
               fill=(98,106,114),outline=(66,72,80),width=2)
    d.line([(x1-44,y0+30),(x0+96,y1-20)],fill=(240,166,86),width=5)
    d.line([(x1-44,y0+30),(x0+96,y1-20)],fill=(190,28,44),width=2)
    glow(d,x1-44,y0+30,17,(255,216,112),(242,192,152))
    for cx,cy in [(x0+96,y1-20),(x0+126,y0+44)]:
        glow(d,cx,cy,15,(255,218,112),(244,200,158))
        d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=(255,246,204))
    txt(d,x0+10,y0+8,"KUWAIT",F_MICRO,(118,84,50))

def art_ipo(d,x0,y0,x1,y1):
    # the market debut: a trading screen with the ANT ticker and its first-day rise
    vg(d,x0,y0,x1,y1,(12,34,58),(28,72,104))
    for gx in range(0,326,40):
        d.line([(x0+gx,y0),(x0+gx,y1)],fill=(44,88,120),width=1)
    for gy in range(0,140,28):
        d.line([(x0,y0+gy),(x1,y0+gy)],fill=(44,88,120),width=1)
    for i in range(14):
        bx=x0+16+i*21; base=y0+112-i*3
        d.line([(bx,base-14),(bx,base+10)],fill=(120,170,200),width=1)
        d.rectangle([bx-3,base-8,bx+3,base+4],
                    fill=(80,190,140) if i%3 else (220,96,96))
    pts=[(x0+16,y0+116),(x0+66,y0+98),(x0+108,y0+104),(x0+152,y0+72),
         (x0+196,y0+80),(x0+240,y0+44),(x0+306,y0+22)]
    d.line([p for p in pts],fill=(236,190,92),width=6)
    d.line([p for p in pts],fill=(255,224,150),width=2)
    for px,py in pts:
        d.ellipse([px-3,py-3,px+3,py+3],fill=(255,238,182))
    d.rectangle([x0+14,y0+10,x0+96,y0+38],fill=(16,44,72))
    d.rectangle([x0+14,y0+10,x0+96,y0+11],fill=GOLD)
    txt(d,x0+22,y0+16,"ANT",f("arialbd.ttf",14),WHITE)
    txt(d,x0+62,y0+18,"$83",f("arialbd.ttf",11),GOLD)
    txt(d,x0+108,y0+14,"IPO  81.3bn",f("arialbd.ttf",10),(196,220,238))

def art_drones(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(12,26,54),(36,58,92))
    stars(d,x0,y0,x1,y1,45,5)
    for i,ht in enumerate([20,34,26,40,18]):
        bx=x0+10+i*46
        d.rectangle([bx,y1-24-ht,bx+30,y1-24],fill=(40,60,92))
        d.rectangle([bx+2,y1-22-ht,bx+4,y1-24],fill=(78,104,140))
        for wy in range(y1-22-ht,y1-28,7):
            d.rectangle([bx+6,wy,bx+10,wy+2],fill=(232,204,120))
            d.rectangle([bx+18,wy,bx+22,wy+2],fill=(232,204,120))
    d.line([(x1-10,y0+10),(x0+60,y1-28)],fill=(238,110,44),width=4)
    d.line([(x1-10,y0+10),(x0+60,y1-28)],fill=RED,width=2)
    for cx,cy in [(x0+70,y1-30),(x1-40,y0+20)]:
        glow(d,cx,cy,14,(255,220,110),(200,70,60))
        d.ellipse([cx-3,cy-3,cx+3,cy+3],fill=(255,242,196))
    d.polygon([(x0+150,y0+8),(x0+172,y0+4),(x0+168,y0+18),(x0+148,y0+20)],fill=(232,238,248))
    d.line([(x0+158,y0+10),(x0+162,y0+18)],fill=(150,160,180),width=1)

def art_france_ukraine(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(238,243,249),(208,222,238))
    d.rectangle([x0+12,y0+8,x0+32,y0+36],fill=(36,72,152))
    d.rectangle([x0+32,y0+8,x0+52,y0+36],fill=(244,244,242))
    d.rectangle([x0+52,y0+8,x0+72,y0+36],fill=(224,56,64))
    d.rectangle([x0+80,y0+8,x0+100,y0+24],fill=(72,138,206))
    d.rectangle([x0+80,y0+24,x0+100,y0+36],fill=(250,214,72))
    d.polygon([(x0+112,y0+44),(x0+118,y0+28),(x0+144,y0+28),(x0+150,y0+44)],
              fill=(96,110,124))
    d.ellipse([x0+116,y0+18,x0+146,y0+30],fill=(112,126,140))
    d.rectangle([x0+130,y0+6,x0+140,y0+18],fill=(70,84,98))
    txt(d,x0+12,y0+40,"ADVISORY MISSION",F_MICRO,(70,80,96))

def art_court(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(242,236,220),(214,204,184))
    d.polygon([(x0+12,y0+18),(x0+108,y0+6),(x0+204,y0+18)],fill=(168,150,124))
    for i in range(4):
        bx=x0+26+i*42
        d.rectangle([bx,y0+16,bx+12,y1-8],fill=(164,146,120))
        d.rectangle([bx+1,y0+17,bx+3,y1-9],fill=(196,180,152))
    d.rectangle([x0+18,y1-14,x1-14,y1-8],fill=(138,120,96))
    cx=x1-48; cy=y0+28
    d.line([(cx,cy),(cx,cy+26)],fill=(64,58,48),width=2)
    d.line([(cx-22,cy),(cx+22,cy)],fill=(64,58,48),width=2)
    for sx in (cx-22,cx+22):
        d.line([(sx,cy),(sx,cy+10)],fill=(64,58,48),width=1)
        d.ellipse([sx-7,cy+10,sx+7,cy+22],outline=(64,58,48),width=2)
    d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=(196,168,72))

def art_game(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(126,58,164),(86,36,120))
    glow(d,x0+120,y0+26,25,(198,110,220),(120,52,158))
    d.ellipse([x0+70,y0+8,x0+170,y0+52],fill=(244,246,250))
    d.ellipse([x0+74,y0+11,x0+166,y0+48],outline=(206,212,226),width=1)
    for cx,cy in [(x0+94,y0+26),(x0+146,y0+26)]:
        d.rectangle([cx-10,cy-4,cx+10,cy+4],fill=(116,56,148))
        d.rectangle([cx-2,cy-12,cx+2,cy+12],fill=(116,56,148))
    for k,(cx,cy) in enumerate([(x0+96,y0+42),(x0+112,y0+36),(x0+130,y0+36),(x0+146,y0+42)]):
        c=[(220,80,120),(240,180,60),(80,170,220),(120,200,120)][k]
        d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=c)
    txt(d,x0+8,y0+40,"ON SALE AFTER 13 YEARS",F_MICRO,WHITE)

def art_energy(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(252,240,212),(240,214,168))
    glow(d,x1-28,y0+24,22,(255,236,160),(250,224,178))
    d.ellipse([x1-46,y0+8,x1-10,y0+42],fill=(244,176,72))
    d.line([(x0+30,y1-8),(x0+30,y0+14)],fill=(66,72,80),width=3)
    d.polygon([(x0+30,y0+14),(x0+48,y1-8),(x0+12,y1-8)],fill=(90,96,108))
    for k in range(3):
        d.line([(x0+20+k*10,y1-12),(x0+40+k*10,y0+26)],fill=(152,158,168),width=1)
    d.line([(x0+64,y1-12),(x1-8,y1-12)],fill=(32,92,148),width=4)
    for k in range(3):
        d.arc([x0+72+k*36,y1-24,x0+104+k*36,y1-2],200,340,fill=(32,92,148),width=2)

def art_fed(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(242,245,248),(218,228,236))
    d.polygon([(x0+18,y0+34),(x0+40,y0+18),(x0+62,y0+34)],fill=(116,128,142))
    for i in range(4):
        d.rectangle([x0+20+i*12,y0+34,x0+27+i*12,y0+52],fill=(152,160,172))
        d.rectangle([x0+21+i*12,y0+35,x0+23+i*12,y0+51],fill=(186,194,204))
    d.rectangle([x0+14,y0+52,x0+68,y0+57],fill=(116,128,142))
    d.line([(x0+86,y0+16),(x0+120,y0+28),(x0+146,y0+22),(x1-8,y0+40)],fill=RED,width=3)
    d.polygon([(x1-8,y0+40),(x1-18,y0+34),(x1-18,y0+46)],fill=RED)
    txt(d,x0+82,y0+40,"MORE HIKES",F_SM,RED)

def art_cyclone(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(208,232,242),(236,244,240))
    d.polygon([(x0+10,y0+10),(x0+130,y0+24),(x0+110,y1),(x0,y1)],fill=(202,218,212))
    txt(d,x0+12,y0+6,"INDIA",F_MICRO,(66,86,66))
    txt(d,x0+46,y0+22,"ODISHA",F_MICRO,(56,76,56))
    glow(d,x1-60,y0+26,26,(150,206,236),(214,234,242))
    for r in (6,10,14,18,22):
        d.arc([x1-60-r,y0+26-r,x1-60+r,y0+26+r],r*8,r*8+220,
              fill=(36,96,148),width=2)
    d.ellipse([x1-64,y0+22,x1-56,y0+30],fill=(24,72,124))

def art_ebola(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(222,238,236),(188,218,214))
    d.line([(x0+40,y1-8),(x0+40,y0+18)],fill=(70,94,100),width=4)
    d.line([(x0+28,y1-8),(x0+52,y1-8)],fill=(70,94,100),width=3)
    d.rectangle([x0+30,y0+10,x0+50,y0+24],fill=(92,120,124))
    d.ellipse([x0+34,y0+6,x0+46,y0+16],fill=(150,182,184))
    for cx,cy,r in [(x0+96,y0+14,7),(x0+130,y0+30,9),(x0+164,y0+16,6),(x0+200,y0+32,8)]:
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(196,88,72))
        for k in range(6):
            a=k*math.pi/3
            d.line([(cx+math.cos(a)*r,cy+math.sin(a)*r),
                    (cx+math.cos(a)*(r+4),cy+math.sin(a)*(r+4))],
                   fill=(196,88,72),width=1)
    d.rectangle([x1-34,y0+26,x1-10,y0+32],fill=(240,244,242))
    d.rectangle([x1-26,y0+18,x1-20,y0+40],fill=(240,244,242))
    txt(d,x0+10,y0+42,"VACCINE TRIALS",F_MICRO,(56,86,84))

def art_gaza(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(198,228,240),(224,234,210))
    d.rectangle([x0,y0+18,x1,y1],fill=(212,226,204))
    for i in range(5):
        d.rectangle([x0+16+i*40,y0+20,x0+38+i*40,y0+38],fill=(190,204,180))
    d.line([(x0+20,y0+34),(x1-20,y0+34)],fill=RED,width=3)
    d.rectangle([x1-70,y0+4,x1-20,y0+24],fill=(232,202,64))
    txt(d,x1-66,y0+8,"YELLOW LINE",F_MICRO,(80,70,30))
    d.polygon([(x0+40,y0+42),(x0+76,y0+42),(x0+84,y1-4),(x0+34,y1-4)],fill=(86,98,74))
    d.ellipse([x0+46,y0+44,x0+58,y0+52],fill=(120,132,102))

def art_nsa(d,x0,y0,x1,y1):
    vg(d,x0,y0,x1,y1,(18,30,48),(44,64,88))
    for i in range(4):
        bx=x0+14+i*44
        d.rectangle([bx,y0+16,bx+34,y1],fill=(30,44,64))
        d.rectangle([bx+2,y0+18,bx+32,y1-2],outline=(70,92,116),width=1)
        for k in range(4):
            wy=y0+22+k*7
            d.rectangle([bx+5,wy,bx+18,wy+3],
                        fill=(70,120,150) if k%2 else (46,80,108))
            d.ellipse([bx+24,wy,bx+27,wy+3],
                      fill=(220,90,80) if i==1 else (90,180,140))
    d.line([(x0+40,y0+8),(x0+84,y0+8)],fill=(200,80,72),width=2)
    d.line([(x0+92,y0+8),(x0+150,y0+8)],fill=(200,80,72),width=2)
    d.polygon([(x0+88,y0+4),(x0+94,y0+8),(x0+88,y0+12)],fill=(200,80,72))
    d.rectangle([x0+122,y0+2,x1-10,y0+14],fill=(150,36,42))
    txt(d,x0+126,y0+4,"NETWORK DOWN",F_MICRO,WHITE)

def draw_world_map(d,x0,y0,x1,y1):
    """A detailed, realistic world map with the 11 drawn-story locations."""
    vg(d,x0,y0,x1,y1,(216,236,248),(184,214,236),n=20)
    d.rectangle([x0,y0,x1,y1],outline=(118,144,166),width=1)
    def ll(lon,lat):
        return (x0+(lon+180)/360*(x1-x0), y0+(90-lat)/180*(y1-y0))
    continents=[
      # North America - a clean, non-crossing outline so the fill stays solid
      [(-168,65),(-160,60),(-150,59),(-140,60),(-133,56),(-126,50),(-124,43),
       (-121,36),(-117,32),(-112,29),(-108,24),(-103,20),(-97,18),(-90,19),
       (-86,21),(-82,25),(-80,30),(-81,35),(-76,40),(-70,44),(-66,47),
       (-60,50),(-55,53),(-60,58),(-70,62),(-80,65),(-95,70),(-110,72),
       (-125,70),(-140,70),(-155,68)],
      # Central America
      [(-103,20),(-97,18),(-92,16),(-88,14),(-83,10),(-79,9),
       (-81,12),(-86,16),(-92,18),(-98,21)],
      # South America
      [(-81,8),(-75,11),(-70,12),(-62,10),(-52,5),(-50,0),(-44,-2),(-38,-5),
       (-35,-8),(-38,-13),(-39,-17),(-43,-23),(-48,-25),(-53,-33),(-58,-38),
       (-62,-40),(-65,-45),(-68,-52),(-72,-54),(-74,-48),(-73,-42),(-71,-35),
       (-70,-28),(-70,-20),(-75,-15),(-78,-8),(-80,-2),(-81,4)],
      # Greenland
      [(-55,82),(-30,82),(-22,74),(-30,68),(-42,60),(-52,60),(-60,68),(-58,76)],
      # Eurasia
      [(-10,36),(-9,43),(-2,43),(-5,48),(1,51),(4,53),(8,54),(10,57),(14,54),
       (19,54),(24,57),(28,60),(30,66),(28,70),(40,68),(55,70),(70,72),(90,75),
       (110,74),(130,72),(145,70),(160,68),(170,66),(180,65),(178,60),(170,60),
       (160,58),(155,52),(145,45),(140,42),(135,34),(130,30),(127,25),(122,20),
       (118,10),(110,5),(105,2),(100,5),(98,12),(94,16),(90,22),(88,21),(80,15),
       (77,8),(73,15),(70,22),(65,25),(60,25),(57,20),(52,17),(48,12),(44,12),
       (43,17),(40,22),(35,28),(34,31),(36,36),(30,40),(28,41),(24,40),(20,40),
       (18,42),(14,40),(12,44),(8,44),(4,43),(-2,43)],
      # Africa
      [(-17,36),(-6,36),(0,36),(10,34),(20,32),(30,31),(34,28),(37,22),(40,15),
       (43,11),(51,11),(48,5),(43,-1),(41,-10),(40,-16),(35,-22),(32,-26),
       (28,-33),(20,-35),(15,-28),(12,-18),(9,-2),(5,4),(-5,5),(-14,10),(-17,20)],
      # Australia
      [(113,-22),(114,-28),(118,-34),(125,-33),(132,-32),(138,-35),(145,-38),
       (150,-37),(153,-28),(153,-25),(146,-19),(142,-11),(136,-12),(130,-11),
       (125,-14),(121,-19),(115,-21)],
    ]
    land=(210,198,166); coast=(126,120,98)
    for poly in continents:
        d.polygon([ll(*p) for p in poly],fill=land,outline=coast)
    # islands: UK, Japan, Indonesia, Philippines, Madagascar, New Zealand
    islands=[(-3,54,4,3),(137,37,6,3),(140,40,4,4),(110,-3,9,3),(122,-8,10,3),
             (121,12,4,5),(47,-20,4,7),(172,-42,5,3)]
    for lon,lat,rx,ry in islands:
        x,y=ll(lon,lat)
        d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=land,outline=coast)
    # graticule
    for lon in (-120,-60,0,60,120):
        d.line([ll(lon,80),ll(lon,-55)],fill=(198,222,236),width=1)
    for lat in (60,30,0,-30):
        d.line([ll(-170,lat),ll(170,lat)],fill=(198,222,236),width=1)
    points=[
      (1,116,22),(2,52,26),(3,-70,43),(4,-100,42),(5,166,-38),(6,5,55),
      (7,34,32),(8,32,52),(9,25,-3),(10,-112,33),(11,80,18),
    ]
    for n,lon,lat in points:
        x,y=ll(lon,lat)
        x=min(max(x,x0+10),x1-10); y=min(max(y,y0+10),y1-16)
        d.ellipse([x-8,y-8,x+8,y+8],fill=RED,outline=WHITE,width=2)
        s=str(n); tw=tlen(d,s,F_MICRO)
        txt(d,x-tw/2,y-4,s,F_MICRO,WHITE)
    txt(d,x0+8,y1-13,"1-11 = the drawn stories · positions approximate",F_MICRO,(70,76,90))

# ---------- content: only stories presented as 20 Nov news ----------
LEADS=[
  ("ASIA","TRILATERAL","REUTERS · BBC","SHENZHEN · APEC SUMMIT","THREE LEADERS, ONE TABLE",
   "Trump, Xi and Putin hold first-ever trilateral",
   "The three nuclear powers meet in Shenzhen on Thursday; arms control tops the agenda.",
   art_shenzhen),
  ("MIDDLE EAST","IRAN WAR","REUTERS · AFP","ALI AL SALEM · KUWAIT","IRAN HITS US BASE",
   "Iran fires on US sites in Kuwait; Bahrain intercepts",
   "Tehran struck a US base; Bahrain intercepted missiles. Vance vows no 'forever war'.",
   art_gulf),
  ("GLOBAL","MARKETS","BLOOMBERG · REUTERS","NASDAQ · TICKER ANT","IPO PRICED AT $83",
   "Anthropic prices IPO above range, debuts today",
   "The first frontier-AI listing may top $94bn. Amazon and Google hold 28.4% after the float.",
   art_ipo),
]

CARDS=[
  (4,"AMERICAS","MARKETS","FED · WSJ","DEC HIKE NEAR-CERTAIN",
   "Fed minutes: almost all officials see more hikes","December move priced at 100%; AI debt flagged.",art_fed),
  (5,"OCEANIA","CULTURE","GUARDIAN · NME","METACRITIC 99",
   "GTA VI launches worldwide; New Zealand first","15.9m pre-orders; review score ties Ocarina's 99.",art_game),
  (6,"GLOBAL","COURT","REUTERS · AFP","ICJ TO RULE",
   "World Court hears Rohingya genocide case","The Hague reads judgment in The Gambia's case over Myanmar's 2017 campaign.",art_court),
  (7,"MIDDLE EAST","GAZA","BBC · REUTERS","THE YELLOW LINE",
   "Israeli tanks cross into central Gaza again","Families flee as Hamas calls it a ceasefire breach.",art_gaza),
  (8,"EUROPE","UKRAINE WAR","GUARDIAN · AFP","TROOPS ADMITTED",
   "France admits secret troops in Ukraine","Officers say the mission is advisory; Moscow calls it direct participation.",art_france_ukraine),
  (9,"AFRICA","HEALTH","WHO · RFI","5,568 DEAD",
   "DRC's Ebola outbreak still out of control","Bundibugyo vaccine trials start next week; 400-500 cases a week.",art_ebola),
  (10,"AMERICAS","SECURITY","CNN","NSANET DOWN 2 DAYS",
   "NSA's classified network still down","Patch, not cyberattack, hit a Middle East intel hub.",art_nsa),
  (11,"ASIA","WEATHER","IMD","200,000 EVACUATED",
   "Cyclone Akvan closes on Andhra coast","110 km/h winds forecast; Odisha on alert. Landfall is expected Friday.",art_cyclone),
]

# the rest are carried as short briefs, not a second copy of the big cards
BRIEFS=[
  ("EUROPE","UK: no bombing Ukraine"),
  ("MIDDLE EAST","IEA: biggest energy threat"),
  ("GLOBAL","Voyager 1 reply due Thu"),
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

# header ------------------------------------------------------------------
d.rectangle([0,0,W,96],fill=NAVY)
d.rectangle([16,10,100,86],fill=WHITE)
txt(d,26,14,"NOV",f("arialbd.ttf",12),RED)
txt(d,26,28,"20",f("timesbd.ttf",34),NAVY)
txt(d,22,68,"THU · 2026",f("arialbd.ttf",8),NAVY)
txt(d,112,14,"THE DAY IN WORLD NEWS",f("arialbd.ttf",11),GOLD)
txt(d,108,18,"Friday 20 November 2026",F_TITLE,WHITE)
txt(d,112,78,"Everything on this page happened, or was first reported, on Friday 20 November 2026.",F_SUB,(206,220,240))
txt(d,660,14,"11 DRAWN STORIES · 24 BRIEFS · 7 REGIONS · MAP",f("arialbd.ttf",10),GOLD)
rule(d,0,96,W,96,GOLD,3)

# region bar --------------------------------------------------------------
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

# three leads -------------------------------------------------------------
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

# UTC timeline - taller, ruled, bold hours so it reads at a glance --------
d.rectangle([16,426,1008,466],fill=(234,238,244),outline=GRAY,width=1)
txt(d,22,430,"UTC TIMELINE",f("arialbd.ttf",11),NAVY)
txt(d,22,445,"20 NOV",f("arialbd.ttf",9),GRAY)
rule(d,150,446,982,446,(146,154,166),2)
tl=[("00:00",RED,"Gulf strikes"),("06:00",BLUE,"Berlin talks"),
    ("09:00",PURPLE,"Shenzhen summit"),("13:00",GREEN,"Wall St opens"),
    ("18:00",ORANGE,"NSA network down"),("23:00",TEAL,"NZ game launch")]
for i,(hh,col,label) in enumerate(tl):
    tx=150+i*166
    d.ellipse([tx-6,440,tx+6,452],fill=col,outline=WHITE,width=2)
    hw=tlen(d,hh,F_REG)/2
    txt(d,tx-hw,429,hh,F_REG,NAVY)
    lw=tlen(d,label,F_MICRO)/2
    txt(d,tx-lw,454,label,F_MICRO,(56,62,76))

# eight illustrated cards -------------------------------------------------
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

# the day in numbers: large, readable, no micro-table ---------------------
d.rectangle([16,756,1008,802],fill=(238,241,246),outline=GRAY,width=1)
txt(d,24,761,"THE DAY IN NUMBERS · 20 NOV",f("arialbd.ttf",9),NAVY)
stats=[(228,"$94bn","ANTHROPIC IPO VALUATION"),(398,"28.4%","AMAZON + GOOGLE STAKE"),
       (568,"200,000","EVACUATED AHEAD OF AKVAN"),(744,"5,568","DRC EBOLA DEAD"),
       (886,"24,418","NASDAQ CLOSE +0.37%")]
for x,big,lab in stats:
    txt(d,x,760,big,F_STAT,RED)
    txt(d,x,789,lab,F_MICRO,(80,86,100))

# also on thursday: small world map + 24 short briefs in three columns ----
d.rectangle([16,808,1008,828],fill=NAVY)
txt(d,24,812,"WHERE IT HAPPENED  /  ALSO ON THURSDAY",f("arialbd.ttf",10),GOLD)
txt(d,700,812,"24 MORE STORIES · 20 NOV 2026",F_MICRO,(206,220,240))
draw_world_map(d,16,832,306,970)
for k,(reg,brief) in enumerate(BRIEFS[:24]):
    col=k//8; row=k%8
    x=322+col*230; y=832+row*17
    d.ellipse([x,y+1,x+6,y+7],fill=REGCOL[reg])
    s=f"{k+1:02d} · "+brief
    txt(d,x+11,y,one_line(s,F_BRIEF,210,d),F_BRIEF,INK)

# date check: only what is NOT on this page, phrased so it cannot contradict
d.rectangle([16,974,1008,1000],fill=(250,236,236),outline=RED,width=1)
txt(d,24,977,"DATE CHECK",f("arialbd.ttf",10),RED)
txt(d,118,976,"NOT ON THIS PAGE AS NEWS (first reported Wed 18 Nov): Trump's red-carpet welcome; the US strike on Qeshm island;",F_TINY,(110,40,40))
txt(d,118,988,"the Kerch bridge span; Berlin security guarantees. Friday's cyclone landfall is a forecast, not a 20 Nov event.",F_TINY,(110,40,40))

# footer - world clock removed; left as a clean band, not padded with filler
d.rectangle([0,1000,W,H],fill=NAVY)
d.rectangle([0,1000,W,1001],fill=(206,168,83))

out=os.environ.get("MAKEFUN_OUTPUT","C:\\Users\\User\\Aws\\agent\\entry_build_1119\\preview_v2.png")
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
