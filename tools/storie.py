#!/usr/bin/env python3
"""Genera /storie (il Libro delle Storie) e le pagine degli articoli /storie/<slug>."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storie_data import CAPITOLI, ARTICOLI, IN_ARRIVO

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.dimoradellestorie.com"
e = html.escape

loft = open(f"{SITE}/loft-dell-antiquario.html", encoding="utf-8").read()
HERO_START = loft.find('  <section style="position:relative;min-height:min(640px,78vh)')
FOOT_START = loft.find('  <footer')
HEAD_END = loft.find('</head>')
assert HERO_START > 0 and FOOT_START > 0

def absolutize(s):
    s = s.replace('src="img/', 'src="/img/').replace('href="img/', 'href="/img/')
    s = s.replace('url(fonts/', 'url(/fonts/').replace('href="fonts/', 'href="/fonts/')
    return s

def head(title, desc, canonical, og_img, jsonld, og_type="website"):
    h = loft[:HEAD_END]
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{e(desc)}">', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{canonical}">', h)
    h = re.sub(r'<meta property="og:type".*?<meta property="og:locale" content="it_IT">',
               f'<meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}">'
               f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{BASE}{og_img}">'
               f'<meta property="og:locale" content="it_IT">', h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>',
               '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + '</script>', h, flags=re.S)
    return h

BODY_OPEN = loft[HEAD_END:HERO_START]   # </head><body> + wrapper + pollen
FOOT = loft[FOOT_START:]

def header_html():
    return '''    <header style="position:relative;display:flex;flex-wrap:wrap;gap:20px;justify-content:space-between;align-items:center;padding:32px clamp(20px,4.5vw,64px)">
      <a href="/" aria-label="Dimora delle Storie — home" style="display:inline-flex;min-height:44px;align-items:center"><img src="/img/logo-icona.svg" alt="" style="height:52px;width:auto"></a>
      <nav class="topnav" style="display:flex;flex-wrap:wrap;gap:28px;align-items:center;font-size:13px;letter-spacing:.06em;padding:12px 28px;border-radius:999px;background:rgba(239,232,220,.08);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.18)">
        <a href="/#dimore" style="text-decoration:none">Dimore</a><a href="/storie" style="text-decoration:none">Storie</a><a href="/#tempio" style="text-decoration:none">Tempio</a><a href="/#prenota" style="text-decoration:none">Contatti</a>
      </nav>
    </header>'''

SERIF = "font-family:'Bodoni Moda',Georgia,serif"

# ------------------------------------------------------------------ pagine del libro
def cap(cid):
    return next(c for c in CAPITOLI if c["id"] == cid)

def page(inner, cls=""):
    return {"html": inner, "cls": cls}

pages = []
# 0 copertina
pages.append(page('''<div class="cover-frame"><img src="/img/logo-chiaro.svg" alt="" class="cover-logo">
<p class="cover-kicker">Dimora delle Storie</p><h2 class="cover-title">Il Libro<br>delle Storie</h2>
<p class="cover-sub">Tempio Pausania · Gallura</p><span class="cover-hint">Aprite il libro</span></div>''', "cover"))
# 1 ex libris
pages.append(page('''<div class="exlibris"><img src="/img/logo-icona.svg" alt="" width="64" height="64">
<p class="ex-k">Ex libris</p><p class="ex-t">Questo libro appartiene a chi passa da Tempio e ha voglia di ascoltarne le storie.</p>
<p class="ex-s">Sfogliatelo con un clic sul bordo delle pagine, con le frecce della tastiera o dall'indice qui accanto.</p></div>'''))
# 2 indice (compilato dopo, servono i numeri di pagina)
pages.append(None)
INDEX_POS = 2
cap_page = {}
art_page = {}
for c in CAPITOLI:
    cap_page[c["id"]] = len(pages)
    pages.append(page(f'''<div class="opener"><span class="op-n">Capitolo {c["n"]}</span><h2 class="op-t">{e(c["titolo"])}</h2>
<span class="op-rule" aria-hidden="true"></span><p class="op-i">{e(c["intro"])}</p></div>''', "opener-page"))
    if c["id"] == "dimore":
        pages.append(page('''<div class="pg"><span class="pg-k">Le tre case</span><h3 class="pg-t">Dove abitano le storie</h3>
<ul class="pg-list"><li><a href="/loft-dell-antiquario">Loft dell'Antiquario</a><span>Velluto blu · peonie · vetro</span></li>
<li><a href="/suite-del-viaggiatore">Suite del Viaggiatore</a><span>Sabbia · oro · sala da tè</span></li>
<li><a href="/antica-latteria-1930">Antica Latteria 1930</a><span>Granito · legno · vasca d'epoca</span></li></ul>
<p class="pg-p">Tre dimore in una residenza del 1930, nel cuore del centro storico di Tempio Pausania.</p></div>'''))
    for a in [a for a in ARTICOLI if a["cap"] == c["id"]]:
        art_page[a["slug"]] = len(pages)
        pages.append(page(f'''<article class="pg"><span class="pg-k">{e(c["titolo"])} · {e(a["data_it"])}</span>
<h3 class="pg-t"><a href="/storie/{a["slug"]}">{e(a["titolo"])}</a></h3><p class="pg-st">{e(a["sottotitolo"])}</p>
<p class="pg-p dropcap">{e(a["estratto"])}</p><a class="pg-more" href="/storie/{a["slug"]}">Leggi la storia →</a></article>'''))
    for t, d in IN_ARRIVO.get(c["id"], []):
        pages.append(page(f'''<div class="pg soon"><span class="pg-k">{e(c["titolo"])} · prossimamente</span>
<h3 class="pg-t">{e(t)}</h3><p class="pg-p">{e(d)}</p><span class="soon-seal" aria-hidden="true">In arrivo</span></div>'''))
# pagina finale
pages.append(page('''<div class="pg end"><span class="pg-k">Continua…</span><h3 class="pg-t">Le pagine si scrivono ogni settimana</h3>
<p class="pg-p">Nuove storie su Tempio, la Gallura, la poesia e la lingua gallurese. E la prossima, magari, la vivete voi.</p>
<a class="pg-more" href="https://wa.me/393791656864">Scriveteci su WhatsApp →</a></div>'''))
if len(pages) % 2 == 0:   # la quarta di copertina deve stare sul retro di un foglio
    pages.append(page('<div class="pg blank" aria-hidden="true"></div>'))
pages.append(page('<div class="cover-frame back"><img src="/img/logo-icona.svg" alt="" class="cover-logo small"><p class="cover-sub">dimoradellestorie.com</p></div>', "cover back-cover"))

idx = '<div class="pg"><span class="pg-k">Indice</span><h3 class="pg-t">Capitoli</h3><ol class="toc">'
for c in CAPITOLI:
    idx += f'<li><button type="button" data-go="{cap_page[c["id"]]}"><span class="toc-n">{c["n"]}</span><span class="toc-t">{e(c["titolo"])}</span><span class="toc-p">{cap_page[c["id"]]}</span></button></li>'
idx += '</ol></div>'
pages[INDEX_POS] = page(idx)

N = len(pages)
def face(i):
    p = pages[i]
    num = f'<span class="folio">{i}</span>' if 0 < i < N - 1 and "blank" not in p["html"] else ""
    side = "recto" if i % 2 == 0 else "verso"
    return f'<div class="face {side} {p["cls"]}" data-p="{i}">{p["html"]}{num}</div>'

leaves = ""
for k in range(N // 2):
    leaves += f'<div class="leaf" data-k="{k}" style="z-index:{N//2-k}"><div class="side front">{face(2*k)}</div><div class="side back">{face(2*k+1)}</div></div>'
deck = "".join(f'<div class="dpage">{face(i)}</div>' for i in range(N))

BOOK_CSS = r'''
@media (max-width:440px){.topnav{gap:16px!important;padding:10px 16px!important;font-size:12px!important}}
.storie-main{padding:12px clamp(16px,4.5vw,64px) 96px;display:flex;flex-direction:column;align-items:center;gap:28px}
.book-wrap{position:relative;width:min(1120px,100%,calc((100svh - 230px)*1.48));min-width:min(680px,100%)}
.book{position:relative;cursor:pointer;width:100%;aspect-ratio:1.48/1;perspective:2600px;transition:transform .9s cubic-bezier(.6,.05,.25,1)}
.book.closed-front{transform:translateX(-25%)}.book.closed-back{transform:translateX(25%)}
.leaf{position:absolute;top:0;left:50%;width:50%;height:100%;transform-origin:left center;transform-style:preserve-3d;transition:transform 1.15s cubic-bezier(.55,.08,.25,1)}
.leaf.flipped{transform:rotateY(-180deg)}
.leaf .side{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden}
.leaf .side.back{transform:rotateY(180deg)}
.face{position:absolute;inset:0;overflow:hidden;color:#1E2235;background:#F2EADC;
 background-image:radial-gradient(120% 90% at 50% 40%,rgba(255,255,255,.35),rgba(0,0,0,0) 60%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .45 0 0 0 0 .38 0 0 0 0 .28 0 0 0 .09 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
 padding:clamp(22px,4.2%,52px) clamp(22px,7%,64px);box-sizing:border-box;display:flex;flex-direction:column}
.face.recto{border-radius:2px 6px 6px 2px;box-shadow:inset 26px 0 40px -22px rgba(60,45,25,.38)}
.face.verso{border-radius:6px 2px 2px 6px;box-shadow:inset -26px 0 40px -22px rgba(60,45,25,.38)}
.face::after{content:"";position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 70px rgba(120,95,60,.16)}
.face.cover{color:#E2B76A;background:#121B52;background-image:radial-gradient(90% 70% at 30% 25%,rgba(143,162,230,.28),rgba(18,27,82,0) 60%),radial-gradient(80% 80% at 80% 90%,rgba(0,0,0,.45),rgba(0,0,0,0) 60%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='v'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.3' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .6 0 0 0 0 .65 0 0 0 0 .95 0 0 0 .16 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23v)'/%3E%3C/svg%3E");box-shadow:inset 10px 0 18px -8px rgba(0,0,0,.6),inset 0 0 0 1px rgba(226,183,106,.25)}
.face.cover::after{box-shadow:inset 0 0 90px rgba(0,0,0,.45)}
.cover-frame{position:absolute;inset:7%;border:1px solid rgba(226,183,106,.55);outline:1px solid rgba(226,183,106,.25);outline-offset:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:14px;padding:6%}
.cover-logo{width:42%;max-width:190px;filter:drop-shadow(0 2px 6px rgba(0,0,0,.5))}.cover-logo.small{width:22%}
.cover-kicker{margin:0;font-size:clamp(9px,1.1vw,12px);letter-spacing:.34em;text-transform:uppercase;opacity:.8}
.cover-title{margin:0;'''+SERIF+''';font-weight:400;font-size:clamp(20px,3.1vw,40px);line-height:1.2;letter-spacing:.1em;text-transform:uppercase;font-variation-settings:'opsz' 11;
 background:linear-gradient(100deg,#B8893F 0%,#F3D38F 35%,#C99A4E 55%,#F6DDA5 75%,#B8893F 100%);-webkit-background-clip:text;background-clip:text;color:transparent;background-size:220% 100%;animation:gild 7s ease-in-out infinite}
@keyframes gild{0%,100%{background-position:0% 0}50%{background-position:100% 0}}
.cover-sub{margin:0;font-size:clamp(9px,1vw,12px);letter-spacing:.28em;text-transform:uppercase;color:rgba(239,232,220,.7)}
.cover-hint{margin-top:10px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:rgba(239,232,220,.85);animation:hintp 2.6s ease-in-out infinite}
@keyframes hintp{0%,100%{opacity:.35}50%{opacity:1}}
.exlibris,.opener{margin:auto;text-align:center;display:flex;flex-direction:column;align-items:center;gap:14px;max-width:34ch}
.ex-k,.op-n,.pg-k{margin:0;font-size:clamp(9px,.9vw,11px);letter-spacing:.3em;text-transform:uppercase;color:#9A7434;font-weight:500}
.ex-t{margin:0;'''+SERIF+''';font-style:italic;font-size:clamp(15px,1.6vw,21px);line-height:1.5;font-variation-settings:'opsz' 11}
.ex-s{margin:0;font-size:clamp(11px,1vw,13px);line-height:1.6;color:#5A5650}
.op-t{margin:0;'''+SERIF+''';font-weight:400;font-size:clamp(22px,3vw,40px);letter-spacing:.08em;text-transform:uppercase;line-height:1.15;font-variation-settings:'opsz' 11}
.op-rule{width:64px;height:1px;background:#B8893F;position:relative}.op-rule::before{content:"";position:absolute;left:50%;top:50%;width:7px;height:7px;background:#B8893F;transform:translate(-50%,-50%) rotate(45deg)}
.op-i{margin:0;font-size:clamp(12px,1.15vw,15px);line-height:1.7;color:#4A4740}
.opener-page{background-image:radial-gradient(70% 55% at 50% 50%,rgba(18,27,82,.06),rgba(0,0,0,0) 70%),url("/img/peonia-base.jpg");background-size:auto,140%;background-position:center,center;background-blend-mode:normal,soft-light}
.opener-page.face{background-color:#EFE6D6}
.pg{display:flex;flex-direction:column;gap:12px;height:100%}
.pg-t{margin:0;'''+SERIF+''';font-weight:400;font-size:clamp(17px,2vw,27px);line-height:1.25;letter-spacing:.06em;text-transform:uppercase;font-variation-settings:'opsz' 11}
.pg-t a{text-decoration:none;color:inherit}.pg-t a:hover{color:#7A5A22}
.pg-st{margin:0;'''+SERIF+''';font-style:italic;font-size:clamp(13px,1.3vw,17px);color:#5A5650;font-variation-settings:'opsz' 11}
.pg-p{margin:0;font-size:clamp(12px,1.15vw,15px);line-height:1.75;color:#33302B}
.dropcap::first-letter{float:left;'''+SERIF+''';font-size:3.4em;line-height:.85;padding:4px 8px 0 0;color:#9A7434}
.pg-more{margin-top:auto;align-self:flex-start;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#121B52;text-decoration:none;border-bottom:1px solid #B8893F;padding-bottom:3px;min-height:24px}
.pg-list{list-style:none;margin:6px 0;padding:0}.pg-list li{display:flex;flex-direction:column;gap:2px;padding:12px 0;border-top:1px solid rgba(30,34,53,.14)}
.pg-list a{'''+SERIF+''';font-size:clamp(14px,1.4vw,18px);letter-spacing:.06em;text-transform:uppercase;color:#121B52;text-decoration:none;font-variation-settings:'opsz' 11}
.pg-list span{font-size:12px;color:#6A655C;letter-spacing:.04em}
.toc{list-style:none;margin:8px 0 0;padding:0}.toc li{border-top:1px solid rgba(30,34,53,.14)}
.toc button{all:unset;cursor:pointer;display:grid;grid-template-columns:3ch 1fr auto;gap:14px;align-items:baseline;width:100%;padding:clamp(10px,1.3vw,15px) 0;box-sizing:border-box;min-height:44px}
.toc button:hover .toc-t,.toc button:focus-visible .toc-t{color:#7A5A22}.toc button:focus-visible{outline:2px solid #B8893F;outline-offset:2px}
.toc-n{'''+SERIF+''';color:#9A7434;font-size:14px}.toc-t{'''+SERIF+''';font-size:clamp(14px,1.45vw,19px);letter-spacing:.07em;text-transform:uppercase;font-variation-settings:'opsz' 11}
.toc-p{font-size:12px;color:#6A655C}
.soon .pg-t{color:#5A5650}.soon-seal{margin-top:auto;align-self:flex-end;width:86px;height:86px;border-radius:50%;display:grid;place-items:center;text-align:center;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#7A2E2A;border:1.5px solid rgba(122,46,42,.6);box-shadow:inset 0 0 0 4px rgba(242,234,220,1),inset 0 0 0 5px rgba(122,46,42,.4);transform:rotate(-12deg);opacity:.75}
.folio{position:absolute;bottom:clamp(10px,2.4%,22px);left:0;right:0;text-align:center;font-size:11px;letter-spacing:.14em;color:#8A8478;'''+SERIF+'''}
.book-ui{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:center}
.bk-btn{all:unset;cursor:pointer;min-height:44px;min-width:44px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:0 20px;border-radius:999px;border:1px solid rgba(255,255,255,.2);background:rgba(239,232,220,.06);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#EFE8DC}
.bk-btn:hover{border-color:rgba(226,183,106,.6)}.bk-btn:focus-visible{outline:2px solid #E2B76A;outline-offset:3px}
.bk-btn[aria-pressed="true"]{border-color:#E2B76A;color:#E2B76A}
.bk-count{font-size:12px;letter-spacing:.14em;color:rgba(239,232,220,.7);min-width:9ch;text-align:center}
.click-l,.click-r{position:absolute;top:0;bottom:0;width:50%;z-index:200;cursor:pointer;background:none;border:0;padding:0}
.click-l{left:0;cursor:w-resize}.click-r{right:0;cursor:e-resize}
.book a,.book button{position:relative;z-index:300}
.book-shadow{position:absolute;left:4%;right:4%;bottom:-26px;height:40px;background:radial-gradient(50% 50% at 50% 50%,rgba(0,0,0,.55),rgba(0,0,0,0));filter:blur(6px);pointer-events:none}
.deck{display:none}
@media (max-width:820px){
 .book,.book-shadow,.click-l,.click-r{display:none}
 .deck{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;width:calc(100% + 32px);margin:0 -16px;padding:4px 16px 18px;box-sizing:border-box;scrollbar-width:none;-webkit-overflow-scrolling:touch}
 .deck::-webkit-scrollbar{display:none}
 .dpage{flex:0 0 84%;scroll-snap-align:center;position:relative;aspect-ratio:.7/1;filter:drop-shadow(0 14px 22px rgba(0,0,0,.45))}
 .dpage .face{border-radius:4px;padding:28px 24px}
 .pg-p{font-size:14px}.pg-t{font-size:20px}.op-t{font-size:26px}.cover-title{font-size:30px}
}
@media (prefers-reduced-motion:reduce){.leaf,.book{transition:none}.cover-title,.cover-hint{animation:none}}
.indice-seo{width:min(1120px,100%);border-top:1px solid rgba(239,232,220,.12);padding-top:40px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:28px}
.indice-seo h2{margin:0 0 8px;'''+SERIF+''';font-weight:400;font-size:15px;letter-spacing:.12em;text-transform:uppercase;color:rgba(239,232,220,.7);font-variation-settings:'opsz' 11}
.indice-seo a{color:#EFE8DC;text-decoration:none}.indice-seo a:hover{color:#E2B76A}
.indice-seo p{margin:6px 0 0;font-size:14px;line-height:1.6;color:rgba(239,232,220,.66)}
'''

AUDIO_JS = r'''
const Sound=(()=>{let ctx=null,amb=null,noise=null;
const get=()=>{if(!ctx){const C=window.AudioContext||window.webkitAudioContext;if(!C)return null;ctx=new C();
 const len=ctx.sampleRate*1.2;noise=ctx.createBuffer(1,len,ctx.sampleRate);const d=noise.getChannelData(0);let b=0;for(let i=0;i<len;i++){const w=Math.random()*2-1;b=(b+0.04*w)/1.04;d[i]=w*0.55+b*2.2;}}
 if(ctx.state==='suspended')ctx.resume();return ctx;};
function flip(strength=1){const c=get();if(!c)return;const t=c.currentTime;
 const s=c.createBufferSource();s.buffer=noise;s.playbackRate.value=0.9+Math.random()*0.25;
 const bp=c.createBiquadFilter();bp.type='bandpass';bp.Q.value=0.7;bp.frequency.setValueAtTime(3200,t);bp.frequency.exponentialRampToValueAtTime(700,t+0.55);
 const hp=c.createBiquadFilter();hp.type='highpass';hp.frequency.value=260;
 const g=c.createGain();g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(0.22*strength,t+0.05);
 g.gain.setValueAtTime(0.22*strength,t+0.16);g.gain.exponentialRampToValueAtTime(0.05*strength,t+0.42);g.gain.exponentialRampToValueAtTime(0.0001,t+0.72);
 s.connect(bp).connect(hp).connect(g).connect(c.destination);s.start(t,Math.random()*0.3,0.8);
 const s2=c.createBufferSource();s2.buffer=noise;const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=900;
 const g2=c.createGain();const t2=t+0.78;g2.gain.setValueAtTime(0.0001,t2);g2.gain.exponentialRampToValueAtTime(0.16*strength,t2+0.008);g2.gain.exponentialRampToValueAtTime(0.0001,t2+0.12);
 s2.connect(lp).connect(g2).connect(c.destination);s2.start(t2,0.5,0.14);}
function startAmb(){const c=get();if(!c||amb)return;const out=c.createGain();out.gain.value=0.0001;out.gain.exponentialRampToValueAtTime(0.5,c.currentTime+4);
 const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=1100;lp.Q.value=0.3;
 const dl=c.createDelay(2);dl.delayTime.value=0.42;const fb=c.createGain();fb.gain.value=0.38;const wet=c.createGain();wet.gain.value=0.35;
 dl.connect(fb).connect(dl);dl.connect(wet).connect(out);lp.connect(out);lp.connect(dl);out.connect(c.destination);
 const hz=m=>440*Math.pow(2,(m-69)/12);
 const chords=[[45,52,55,59,60],[41,48,52,57,64],[48,55,59,64,67],[43,50,55,59,62]];let ci=0;let voices=[];
 function chord(){const t=c.currentTime;voices.forEach(v=>{v.g.gain.cancelScheduledValues(t);v.g.gain.setValueAtTime(v.g.gain.value,t);v.g.gain.linearRampToValueAtTime(0,t+4);v.o.forEach(o=>o.stop(t+4.2));});
  voices=chords[ci%chords.length].map((m,i)=>{const g=c.createGain();g.gain.value=0;g.gain.linearRampToValueAtTime(0.018,t+4);
   const os=[-5,5].map(dt=>{const o=c.createOscillator();o.type=i<1?'sine':'triangle';o.frequency.value=hz(m);o.detune.value=dt;o.connect(g);o.start(t);return o;});g.connect(lp);return{g,o:os};});ci++;}
 const pent=[69,72,74,76,79,81,84];
 function bell(){const t=c.currentTime;const o=c.createOscillator();o.type='sine';o.frequency.value=hz(pent[Math.floor(Math.random()*pent.length)]);
  const o2=c.createOscillator();o2.type='sine';o2.frequency.value=o.frequency.value*2.01;const g=c.createGain();g.gain.setValueAtTime(0.0001,t);
  g.gain.exponentialRampToValueAtTime(0.03,t+0.01);g.gain.exponentialRampToValueAtTime(0.0001,t+2.6);const g2=c.createGain();g2.gain.value=0.25;
  o.connect(g);o2.connect(g2).connect(g);g.connect(lp);o.start(t);o2.start(t);o.stop(t+2.8);o2.stop(t+2.8);}
 chord();const i1=setInterval(chord,9000);let tb;(function loop(){bell();tb=setTimeout(loop,1800+Math.random()*3800);})();
 amb={out,stop(){const t=c.currentTime;out.gain.cancelScheduledValues(t);out.gain.setValueAtTime(out.gain.value,t);out.gain.exponentialRampToValueAtTime(0.0001,t+1.5);clearInterval(i1);clearTimeout(tb);setTimeout(()=>{voices.forEach(v=>v.o.forEach(o=>{try{o.stop()}catch(e){}}));out.disconnect();},1700);}};}
function stopAmb(){if(amb){amb.stop();amb=null;}}
return{flip,startAmb,stopAmb};})();
'''

BOOK_JS = r'''
(function(){
const store={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let sfx=store.get('dds-sfx')!=='0';let ambOn=false;
const bSfx=document.getElementById('bk-sfx'),bAmb=document.getElementById('bk-amb');
const syncBtns=()=>{bSfx.setAttribute('aria-pressed',sfx);bAmb.setAttribute('aria-pressed',ambOn);bAmb.querySelector('span').textContent=ambOn?'Atmosfera: sì':'Atmosfera: no';bSfx.querySelector('span').textContent=sfx?'Pagine: suono sì':'Pagine: suono no';};
bSfx.onclick=()=>{sfx=!sfx;store.set('dds-sfx',sfx?'1':'0');syncBtns();if(sfx)Sound.flip(.8);};
bAmb.onclick=()=>{ambOn=!ambOn;ambOn?Sound.startAmb():Sound.stopAmb();syncBtns();};
syncBtns();
const book=document.querySelector('.book');const leaves=[...book.querySelectorAll('.leaf')];const L=leaves.length;
const count=document.getElementById('bk-count');let cur=0;
function layout(){leaves.forEach((lf,k)=>{lf.classList.toggle('flipped',k<cur);});
 book.classList.toggle('closed-front',cur===0);book.classList.toggle('closed-back',cur===L);
 leaves.forEach((lf,k)=>{const vis=(k===cur-1)||(k===cur);lf.querySelectorAll('.side').forEach((s,j)=>{const show=(j===1&&k===cur-1)||(j===0&&k===cur);s.inert=!show;});});
 const l=cur*2-1,r=cur*2;count.textContent=cur===0?'Copertina':(cur===L?'Fine':(l+'–'+r));
 document.getElementById('bk-prev').disabled=cur===0;document.getElementById('bk-next').disabled=cur===L;}
function zfix(k,forward){const lf=leaves[k];lf.style.zIndex=L+5;setTimeout(()=>{leaves.forEach((x,j)=>{x.style.zIndex=j<cur?j+1:L-j;});},reduce?0:600);}
function go(to,withSound=true){to=Math.max(0,Math.min(L,to));if(to===cur)return;const fwd=to>cur;const steps=Math.abs(to-cur);
 let i=0;const step=()=>{const k=fwd?cur:cur-1;cur+=fwd?1:-1;zfix(k,fwd);layout();if(sfx&&withSound)Sound.flip(steps>1?.7:1);i++;if(i<steps)setTimeout(step,reduce?0:170);};step();}
const deck=document.querySelector('.deck');const dpages=[...deck.querySelectorAll('.dpage')];const NP=dpages.length;let last=0,tm;
const isDeck=()=>getComputedStyle(book).display==='none';
const dStep=()=>dpages.length>1?dpages[1].offsetLeft-dpages[0].offsetLeft:1;
function deckGo(i,smooth=true){i=Math.max(0,Math.min(NP-1,i));deck.scrollTo({left:dpages[i].offsetLeft-dpages[0].offsetLeft,behavior:(smooth&&!reduce)?'smooth':'auto'});}
function deckUI(){count.textContent=last===0?'Copertina':(last===NP-1?'Fine':(last+' / '+(NP-2)));
 document.getElementById('bk-prev').disabled=last===0;document.getElementById('bk-next').disabled=last===NP-1;}
deck.addEventListener('scroll',()=>{clearTimeout(tm);tm=setTimeout(()=>{const i=Math.round(deck.scrollLeft/dStep());if(i!==last){last=i;if(sfx)Sound.flip(.75);deckUI();}},90);},{passive:true});
function openPage(p,snd=true){if(isDeck())deckGo(p,snd);else go(Math.floor((p+1)/2),snd);}
document.getElementById('bk-prev').onclick=()=>isDeck()?deckGo(last-1):go(cur-1);
document.getElementById('bk-next').onclick=()=>isDeck()?deckGo(last+1):go(cur+1);
book.addEventListener('click',ev=>{if(ev.target.closest('a,button'))return;const r=book.getBoundingClientRect();const mid=r.left+r.width/2;go(ev.clientX<mid?cur-1:cur+1);});
document.addEventListener('keydown',ev=>{if(ev.target.closest('input,textarea'))return;const d=isDeck();
 if(ev.key==='ArrowRight')d?deckGo(last+1):go(cur+1);if(ev.key==='ArrowLeft')d?deckGo(last-1):go(cur-1);});
document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',ev=>{ev.stopPropagation();openPage(+b.dataset.go);}));
layout();if(isDeck())deckUI();
addEventListener('resize',()=>{isDeck()?deckUI():layout();});
const h=location.hash.match(/^#p(\d+)$/);if(h)setTimeout(()=>openPage(+h[1],false),400);
})();
'''

def storie_page():
    title = "Il Libro delle Storie — storie di Tempio Pausania e della Gallura | Dimora delle Storie"
    desc = "Il Libro delle Storie della Dimora: articoli su Tempio Pausania, la Gallura, la poesia e la lingua gallurese, da sfogliare come un libro."
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Il Libro delle Storie",
          "url": f"{BASE}/storie", "inLanguage": "it-IT",
          "publisher": {"@type": "LodgingBusiness", "name": "Dimora delle Storie", "url": BASE},
          "blogPost": [{"@type": "BlogPosting", "headline": a["titolo"], "url": f"{BASE}/storie/{a['slug']}", "datePublished": a["data"]} for a in ARTICOLI]}
    h = head(title, desc, f"{BASE}/storie", "/img/peonia-base.jpg", ld)
    h += f"<style>{BOOK_CSS}</style>\n"
    seo = '<section class="indice-seo" aria-label="Indice delle storie">'
    for c in CAPITOLI:
        arts = [a for a in ARTICOLI if a["cap"] == c["id"]]
        seo += f'<div><h2>{c["n"]} · {e(c["titolo"])}</h2>'
        if arts:
            for a in arts:
                seo += f'<p><a href="/storie/{a["slug"]}">{e(a["titolo"])}</a> — {e(a["estratto"])}</p>'
        else:
            seo += f'<p>{e(c["intro"])} Prime storie in arrivo.</p>'
        seo += '</div>'
    seo += '</section>'
    body = f'''  <section style="position:relative;overflow:hidden">
{header_html()}
    <div style="position:relative;text-align:center;padding:8px clamp(20px,4.5vw,64px) 8px;display:flex;flex-direction:column;align-items:center;gap:12px">
      <span style="font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#8FA2E6">Storie di Tempio · Gallura · Poesia</span>
      <h1 style="margin:0;{SERIF};font-weight:400;font-size:clamp(24px,3.4vw,46px);line-height:1.15;text-transform:uppercase;letter-spacing:.08em;font-variation-settings:'opsz' 11">Il Libro delle <em style="color:#E2B76A">Storie</em></h1>
    </div>
  </section>
  <main class="storie-main">
    <div class="book-wrap">
      <div class="book closed-front" role="region" aria-label="Il Libro delle Storie, da sfogliare">
        {leaves}
      </div>
      <div class="book-shadow" aria-hidden="true"></div>
      <div class="deck" role="region" aria-label="Il Libro delle Storie, da scorrere">{deck}</div>
    </div>
    <div class="book-ui">
      <button type="button" class="bk-btn" id="bk-prev" aria-label="Pagina precedente">←</button>
      <span class="bk-count" id="bk-count" aria-live="polite">Copertina</span>
      <button type="button" class="bk-btn" id="bk-next" aria-label="Pagina successiva">→</button>
      <button type="button" class="bk-btn" id="bk-sfx" aria-pressed="true"><span>Pagine: suono sì</span></button>
      <button type="button" class="bk-btn" id="bk-amb" aria-pressed="false"><span>Atmosfera: no</span></button>
    </div>
    {seo}
  </main>
'''
    foot = FOOT.replace('</body>', f'<script>{AUDIO_JS}{BOOK_JS}</script>\n</body>')
    return absolutize(h + BODY_OPEN + body + foot)

ARTICLE_CSS = '''
@media (max-width:440px){.topnav{gap:16px!important;padding:10px 16px!important;font-size:12px!important}}
.art{max-width:720px;margin:0 auto;padding:72px clamp(20px,4.5vw,64px) 96px;font-size:18px;line-height:1.85;color:rgba(239,232,220,.86)}
.art .lead{font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-size:clamp(20px,2.2vw,25px);line-height:1.6;color:#EFE8DC}
.art .lead::first-letter{float:left;font-size:3.6em;line-height:.8;padding:6px 10px 0 0;color:#E2B76A}
.art h2{font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(18px,1.9vw,23px);letter-spacing:.08em;text-transform:uppercase;color:#EFE8DC;margin:56px 0 8px}
.art p{margin:0 0 18px}.art ul{margin:0 0 18px;padding-left:20px}.art li{margin:0 0 10px}
.art a{color:#E2B76A;text-decoration-color:rgba(226,183,106,.4);text-underline-offset:3px}
.art strong{color:#EFE8DC;font-weight:500}
.fonti{margin-top:64px;padding-top:24px;border-top:1px solid rgba(239,232,220,.14);font-size:14px;line-height:1.7;color:rgba(239,232,220,.6)}
.fonti h3{font-size:11px;letter-spacing:.28em;text-transform:uppercase;font-weight:500;margin:0 0 8px;color:rgba(239,232,220,.7)}
.fonti a{color:rgba(239,232,220,.75)}
.art-nav{display:flex;flex-wrap:wrap;gap:12px;margin-top:48px}
.art-nav a{min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center;padding:0 24px;border-radius:999px;border:1px solid rgba(255,255,255,.2);font-size:12px;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;color:#EFE8DC}
.art-nav a.gold{background:#D4A65A;color:#0F111A;border-color:#D4A65A}
'''

def article_page(a):
    c = cap(a["cap"])
    url = f"{BASE}/storie/{a['slug']}"
    title = f"{a['titolo']} — {a['sottotitolo']} | Dimora delle Storie"
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["titolo"], "description": a["descrizione"],
          "datePublished": a["data"], "dateModified": a["data"], "inLanguage": "it-IT", "mainEntityOfPage": url,
          "image": f"{BASE}{a['img']}", "articleSection": c["titolo"],
          "author": {"@type": "Organization", "name": "Dimora delle Storie", "url": BASE},
          "publisher": {"@type": "LodgingBusiness", "name": "Dimora delle Storie", "url": BASE,
                        "address": {"@type": "PostalAddress", "streetAddress": "Piazza Eleonora d'Arborea 6", "postalCode": "07029", "addressLocality": "Tempio Pausania", "addressRegion": "SS", "addressCountry": "IT"}},
          "about": {"@type": "City", "name": "Tempio Pausania"}}
    h = head(title, a["descrizione"], url, a["img"], ld, "article") + f"<style>{ARTICLE_CSS}</style>\n"
    pnum = art_page[a["slug"]]
    fonti = "".join(f'<li><a href="{u}" rel="noopener">{e(t)}</a></li>' for t, u in a["fonti"])
    body = f'''  <section style="position:relative;min-height:min(560px,70vh);overflow:hidden;display:flex;flex-direction:column">
    <img src="{a['img']}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.55">
    <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,17,26,.75) 0%,rgba(15,17,26,.35) 40%,rgba(15,17,26,1) 100%)"></div>
{header_html()}
    <div style="position:relative;flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:14px;padding:0 clamp(20px,4.5vw,64px) 48px;max-width:960px">
      <span style="font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#8FA2E6"><a href="/storie" style="text-decoration:none">Il Libro delle Storie</a> · Capitolo {c["n"]} · {e(c["titolo"])}</span>
      <h1 style="margin:0;{SERIF};font-weight:400;font-size:clamp(24px,3.6vw,50px);line-height:1.18;text-transform:uppercase;letter-spacing:.07em;font-variation-settings:'opsz' 11">{e(a["titolo"])}</h1>
      <p style="margin:0;{SERIF};font-style:italic;font-size:clamp(17px,1.8vw,22px);color:rgba(239,232,220,.8);font-variation-settings:'opsz' 11">{e(a["sottotitolo"])}</p>
      <span style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:rgba(239,232,220,.55)"><time datetime="{a['data']}">{e(a["data_it"])}</time></span>
    </div>
  </section>
  <main class="art">
{a["corpo"]}
    <div class="art-nav"><a class="gold" href="https://wa.me/393791656864">Verifica disponibilità</a><a href="/storie#p{pnum}">Torna al libro</a></div>
    <aside class="fonti"><h3>Fonti</h3><ul>{fonti}</ul></aside>
  </main>
'''
    return absolutize(h + BODY_OPEN + body + FOOT)

os.makedirs(f"{SITE}/storie", exist_ok=True)
open(f"{SITE}/storie.html", "w", encoding="utf-8").write(storie_page())
for a in ARTICOLI:
    open(f"{SITE}/storie/{a['slug']}.html", "w", encoding="utf-8").write(article_page(a))
print("pagine libro:", N, "fogli:", N // 2, "articoli:", art_page)
