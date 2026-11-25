#!/usr/bin/env python3
"""Completa le pagine delle dimore: gallerie fotografiche con lightbox, testi
dell'Antica Latteria 1930, pagina /la-dimora (facciata, sala da tè, leggenda),
voce «La casa» nel menu. Idempotente: si può rilanciare."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storie_data import LEGGENDA_ANTIQUARIO as ANTIQUARIO, LEGGENDA_LATTERIA as LAT_LEGGENDA, LEGGENDA_VIAGGIATORE as VIAGGIATORE, LEGGENDA_SALA_TE as SALA_TE

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.dimoradellestorie.com"
e = html.escape
SERIF = "font-family:'Bodoni Moda',Georgia,serif"

def rd(p): return open(f"{SITE}/{p}", encoding="utf-8").read()
def wr(p, s): open(f"{SITE}/{p}", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ foto
P, L = "p", "l"   # verticale / orizzontale
FOTO = {
 "loft": [("01",L,"La parete delle peonie blu"),("02",L,"La testiera in velluto"),("03",P,"Il soggiorno"),
          ("04",L,"Il tavolo alla finestra"),("05",L,"Sotto il lampadario"),("06",L,"Il loft da un capo all'altro"),
          ("07",P,"L'angolo cottura"),("08",L,"Il caffè del mattino"),("09",L,"Il bagno di 9 mq"),
          ("10",L,"Velluto e cotone"),("11",P,"La zona notte"),("12",L,"Il lampadario")],
 "suite":[("01",L,"La testiera sabbia e oro"),("02",L,"Scrivania e TV"),("03",L,"Il letto"),("04",L,"La suite"),
          ("05",P,"La luce del primo piano"),("06",L,"Il bagno oro e pietra"),("07",L,"Velluto senape"),("08",P,"La doccia")],
 "te":  [("01",L,"Il pianoforte e il divano d'epoca"),("02",L,"La vetrina dei libri"),("03",L,"Il pianoforte verticale"),
         ("04",P,"Note"),("05",L,"Il divano a righe"),("06",L,"L'angolo del tè e del caffè"),("07",L,"Tazze e libri"),("08",L,"La vetrina")],
 "est": [("01",L,"Il vicolo di granito"),("02",P,"La facciata"),("03",L,"Il balcone in ferro battuto"),
         ("04",P,"Il portone azzurro"),("05",L,"La targa della Dimora"),("06",P,"Tra le case del centro storico")],
 "lat": [("01",L,"La vasca dietro la balaustra"),("02",L,"Il piano terra"),("03",L,"La camera sotto le travi"),
         ("04",L,"Un libro e un bicchiere di rosso"),("05",L,"Il soggiorno di granito"),("06",L,"Il giradischi"),
         ("07",L,"La scala e il lampadario"),("08",L,"I piedini della vasca"),("09",L,"Il letto"),
         ("10",P,"Il bidone del latte e i libri del Limbara"),("11",P,"Lo specchio barocco"),("12",P,"La doccia a colori"),
         ("13",L,"La lanterna"),("14",L,"Caffè e tè"),("15",P,"La chiave"),("16",P,"La facciata della Latteria"),("18",P,"La palazzina di fronte alla Dimora"),("19",P,"Il vicolo della Latteria")],
}
RIGHE = {
 "loft": [["01"],["03","02"],["04","05"],["07","06","11"],["09","10"],["08","12"]],
 "suite":[["01"],["05","02"],["03","04"],["08","06","07"]],
 "te":   [["01"],["04","02"],["03","05"],["06","07","08"]],
 "est":  [["02","01"],["03","04"],["05","06"]],
 "lat":  [["01"],["02","05"],["10","07"],["06","04","08"],["03","09"],["11","12","13"],["15","14"]],
 "latfuori": [["18","16","19"]],
}

# Foto scelte da Luca (cartella SCELTA FOTO, 23/11/2026): ordine e didascalie in foto_ordine.json, file /img/foto/g-<chiave>-NN.webp
_ORD = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto_ordine.json"), encoding="utf-8"))
FOTO = {k: [(n, o, c) for n, o, c in v] for k, v in _ORD.items()}
def _righe(nomi, schema=(2, 3)):
    r, i, j = [[nomi[0]]], 1, 0
    while i < len(nomi):
        n = schema[j % len(schema)]
        if len(nomi) - i - n == 1: n += 1
        r.append(nomi[i:i + n]); i += n; j += 1
    return r
RIGHE = {k: _righe([n for n, _, _ in v]) for k, v in FOTO.items()}
RIGHE["latfuori"] = [[n for n, _, _ in FOTO["latf"]]]
def n_foto(k): return len(FOTO[k])

def galleria(key, kicker, titolo, alt_pre):
    fk = "latf" if key == "latfuori" else key
    info = {n: (o, c) for n, o, c in FOTO[fk]}
    rows = []
    for riga in RIGHE[key]:
        figs = []
        for n in riga:
            o, c = info[n]
            ar = "2/3" if o == P else "3/2"
            grow = "0.6667" if o == P else "1.5"
            src = f"/img/foto/g-{fk}-{n}.webp"
            figs.append(f'<figure class="gf reveal" style="flex:{grow} 1 0;aspect-ratio:{ar}"><a href="{src}" data-cap="{e(c)}">'
                        f'<img src="{src}" alt="{e(alt_pre + " — " + c)}" loading="lazy" decoding="async" width="{1067 if o==P else 1600}" height="{1600 if o==P else 1067}"></a>'
                        f'<figcaption>{e(c)}</figcaption></figure>')
        rows.append('<div class="gr">' + "".join(figs) + '</div>')
    return (f'<div class="gal-head reveal"><span class="gal-k">{e(kicker)}</span>'
            f'<h2 class="gal-t">{e(titolo)}</h2></div><div class="gal" data-gal>' + "".join(rows) + '</div>')

CSS = '''<style id="galleria">
.gal-sec{padding:0 clamp(20px,4.5vw,64px) clamp(72px,9vw,120px)}
.gal-head{display:flex;flex-direction:column;gap:12px;border-top:1px solid rgba(239,232,220,.14);padding-top:44px;margin-bottom:36px}
.gal-k{font-size:11px;letter-spacing:.3em;color:#D4A65A}
.gal-t{margin:0;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(22px,3vw,40px);letter-spacing:.08em;line-height:1.2}
.gal{display:flex;flex-direction:column;gap:clamp(8px,1.1vw,16px)}
.gr{display:flex;gap:clamp(8px,1.1vw,16px)}
.gr>.gf:only-child{aspect-ratio:16/8!important;max-height:82vh}
.gf{position:relative;margin:0;min-width:0;overflow:hidden;background:#0B0E22;box-shadow:0 22px 60px rgba(0,0,0,.45)}
.gf a{display:block;width:100%;height:100%;cursor:zoom-in}
.gf img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 1.4s cubic-bezier(.2,.7,.1,1),filter 1.4s ease;filter:saturate(.92) brightness(.94)}
.gf:hover img{transform:scale(1.045);filter:saturate(1) brightness(1)}
.gf::after{content:"";position:absolute;inset:10px;border:1px solid rgba(226,183,106,0);transition:border-color .8s ease,inset .8s ease;pointer-events:none}
.gf:hover::after{inset:14px;border-color:rgba(226,183,106,.55)}
.gf figcaption{position:absolute;left:0;right:0;bottom:0;padding:40px 18px 14px;font-size:10.5px;letter-spacing:.22em;color:#EFE8DC;background:linear-gradient(180deg,rgba(8,10,24,0),rgba(8,10,24,.72));opacity:0;transform:translateY(8px);transition:opacity .6s ease,transform .6s ease;pointer-events:none}
.gf:hover figcaption{opacity:1;transform:none}
@media (hover:none){.gf figcaption{opacity:1;transform:none;padding:28px 10px 8px;font-size:9px;letter-spacing:.16em}}
@media (max-width:700px){.gr{flex-wrap:wrap}.gr>.gf{flex-basis:calc(50% - 6px)!important;aspect-ratio:auto!important;height:46vw}.gr>.gf:only-child,.gr>.gf:nth-child(3):last-child{flex-basis:100%!important;height:62vw}}
.lb{position:fixed;inset:0;z-index:200;display:none;align-items:center;justify-content:center;background:rgba(6,8,22,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
.lb.on{display:flex;animation:fade .5s ease both}
.lb img{max-width:min(92vw,1600px);max-height:80vh;box-shadow:0 30px 90px rgba(0,0,0,.6);animation:fade .6s ease both}
.lb p{position:absolute;left:0;right:0;bottom:4vh;margin:0;text-align:center;font-size:11px;letter-spacing:.28em;color:rgba(239,232,220,.8)}
.lb button{position:absolute;background:rgba(239,232,220,.06);border:1px solid rgba(239,232,220,.25);color:#EFE8DC;border-radius:999px;width:52px;height:52px;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .3s,border-color .3s}
.lb button:hover{background:rgba(212,166,90,.18);border-color:#D4A65A}
.lb .x{top:24px;right:24px}.lb .pv{left:clamp(10px,3vw,40px);top:50%;margin-top:-26px}.lb .nx{right:clamp(10px,3vw,40px);top:50%;margin-top:-26px}
.racconto{max-width:760px;margin:0 auto;padding:clamp(72px,9vw,120px) clamp(20px,4.5vw,64px);position:relative}
.racconto .k{display:block;text-align:center;font-size:11px;letter-spacing:.3em;color:#D4A65A;margin-bottom:16px}
.racconto h2{margin:0 0 44px;text-align:center;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(24px,3.4vw,44px);letter-spacing:.08em;line-height:1.2}
.racconto h2::after{content:"";display:block;width:64px;height:1px;margin:28px auto 0;background:linear-gradient(90deg,rgba(212,166,90,0),#D4A65A,rgba(212,166,90,0))}
.racconto p{margin:0 0 22px;font-size:18px;line-height:1.9;color:rgba(239,232,220,.86);text-transform:none!important;letter-spacing:normal!important}
.racconto p:first-of-type::first-letter{float:left;font-family:'Bodoni Moda',Georgia,serif;font-size:4.2em;line-height:.8;padding:8px 12px 0 0;color:#E2B76A}
.racconto .firma{margin-top:36px;text-align:center;font-family:'Bodoni Moda',Georgia,serif;font-style:italic;font-size:15px;letter-spacing:.12em;color:#8FA2E6}
.casa-sec{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(380px,100%),1fr));gap:clamp(32px,5vw,80px);padding:clamp(64px,8vw,110px) clamp(20px,4.5vw,64px) 40px;align-items:end}
.casa-sec h2{margin:0 0 20px;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(26px,3.6vw,48px);letter-spacing:.08em;line-height:1.15}
.casa-sec p{margin:0 0 18px;font-size:17px;line-height:1.8;color:rgba(239,232,220,.82)}
.riti{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:clamp(16px,2vw,28px)}
.rito{padding:32px 28px;border:1px solid rgba(226,183,106,.28);background:linear-gradient(180deg,rgba(15,17,40,.55),rgba(15,17,40,.25));box-shadow:0 22px 60px rgba(0,0,0,.35)}
.rito h3{margin:12px 0 14px;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(18px,1.7vw,22px);letter-spacing:.08em;color:#EFE8DC}
.rito p{margin:0;font-size:15px;line-height:1.75;color:rgba(239,232,220,.8)}
.te-cta{max-width:760px;margin:0 auto clamp(40px,5vw,72px);padding:40px clamp(20px,4.5vw,48px);text-align:center;border-top:1px solid rgba(226,183,106,.3);border-bottom:1px solid rgba(226,183,106,.3)}
.te-cta p{margin:14px 0 22px;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-size:clamp(16px,1.6vw,20px);letter-spacing:.06em;line-height:1.6;color:#EFE8DC}
.te-cta a{display:inline-flex;align-items:center;min-height:44px;padding:0 28px;border-radius:999px;background:#D4A65A;color:#0F111A;text-decoration:none;font-size:12px;font-weight:500;letter-spacing:.14em}
.dim-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:clamp(16px,2vw,28px);padding:0 clamp(20px,4.5vw,64px) clamp(80px,9vw,120px)}
.dim-card{position:relative;display:block;aspect-ratio:4/5;overflow:hidden;text-decoration:none;box-shadow:0 22px 60px rgba(0,0,0,.45)}
.dim-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform 1.6s cubic-bezier(.2,.7,.1,1)}
.dim-card:hover img{transform:scale(1.06)}
.dim-card::before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(8,10,24,0) 40%,rgba(8,10,24,.85))}
.dim-card span{position:absolute;z-index:2;left:24px;right:24px;bottom:24px;display:flex;flex-direction:column;gap:8px}
.dim-card small{font-size:10.5px;letter-spacing:.26em;color:#D4A65A}
.dim-card b{font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:clamp(20px,2vw,26px);letter-spacing:.08em;color:#EFE8DC}
</style>'''

LB = '''<div class="lb" role="dialog" aria-modal="true" aria-label="Galleria fotografica"><button class="x" aria-label="Chiudi">✕</button><button class="pv" aria-label="Foto precedente">‹</button><img alt=""><button class="nx" aria-label="Foto successiva">›</button><p></p></div>
<script>(()=>{const lb=document.querySelector('.lb');if(!lb)return;const im=lb.querySelector('img'),cp=lb.querySelector('p');let L=[],i=0,last;
const show=k=>{i=(k+L.length)%L.length;const a=L[i];im.src=a.getAttribute('href');im.alt=a.dataset.cap;cp.textContent=a.dataset.cap+'  ·  '+(i+1)+' / '+L.length;im.style.animation='none';im.offsetWidth;im.style.animation=''};
const close=()=>{lb.classList.remove('on');document.documentElement.style.overflow='';last&&last.focus()};
document.querySelectorAll('[data-gal]').forEach(g=>{const as=[...g.querySelectorAll('a')];as.forEach((a,k)=>a.addEventListener('click',ev=>{ev.preventDefault();last=a;L=as;show(k);lb.classList.add('on');document.documentElement.style.overflow='hidden';lb.querySelector('.x').focus()}))});
lb.querySelector('.x').onclick=close;lb.querySelector('.pv').onclick=()=>show(i-1);lb.querySelector('.nx').onclick=()=>show(i+1);
lb.addEventListener('click',ev=>{if(ev.target===lb)close()});
addEventListener('keydown',ev=>{if(!lb.classList.contains('on'))return;if(ev.key==='Escape')close();if(ev.key==='ArrowLeft')show(i-1);if(ev.key==='ArrowRight')show(i+1)});
let x0=null;lb.addEventListener('touchstart',ev=>x0=ev.touches[0].clientX,{passive:true});lb.addEventListener('touchend',ev=>{if(x0===null)return;const d=ev.changedTouches[0].clientX-x0;if(Math.abs(d)>40)show(i+(d<0?1:-1));x0=null});})();</script>'''

def put_css(s):
    s = re.sub(r'<style id="galleria">.*?</style>\n?', '', s, flags=re.S)
    return s.replace('</head>', CSS + '\n</head>', 1)

def put_block(s, block):
    """Inserisce (o sostituisce) il blocco tra </main> e <footer>."""
    s = re.sub(r'\n?<!--dimore-->.*?<!--/dimore-->\n?', '\n', s, flags=re.S)
    i = s.find('  <footer')
    return s[:i] + '<!--dimore-->\n' + block + '\n' + LB + '\n<!--/dimore-->\n' + s[i:]

# ------------------------------------------------------------------ menu
NAV_OLD = '<a href="/#dimore" style="text-decoration:none">Dimore</a><a href="/storie"'
NAV_NEW = '<a href="/#dimore" style="text-decoration:none">Dimore</a><a href="/la-dimora" style="text-decoration:none">La casa</a><a href="/storie"'
HOME_NAV_OLD = '<a href="#dimore" style="text-decoration:none">Dimore</a><a href="/storie"'
HOME_NAV_NEW = '<a href="#dimore" style="text-decoration:none">Dimore</a><a href="/la-dimora" style="text-decoration:none">La casa</a><a href="/storie"'

def nav(s):
    if '/la-dimora" style="text-decoration:none">La casa' in s: return s
    return s.replace(NAV_OLD, NAV_NEW).replace(HOME_NAV_OLD, HOME_NAV_NEW)

# ------------------------------------------------------------------ Antica Latteria 1930
LAT_KICK = "Due livelli · 38 mq · 2 ospiti · Tempio Pausania"
LAT_QUOTE = "«Il granito custodisce il fresco del mattino e il calore delle sere: qui il tempo scorre lento, come il latte versato a mano.»"
LAT_P = [
 "Nella palazzina di fronte alla Dimora, dove nel 1930 si vendeva davvero il latte, con la stessa facciata bianca e lo stesso portone azzurro delle altre dimore.",
 "Al piano terra il granito della casa è rimasto a vista: un divano, il tavolo, un giradischi con i vinili e un angolo cottura con piastra a induzione e macchina del caffè. Nel bagno, uno specchio barocco incorniciato dalla pietra e una doccia con luci colorate.",
 "Una scala bianca sale alla camera, sotto le travi di legno e il lampadario: il letto matrimoniale, un comò d'epoca, i fiori dipinti sulle pareti e, dietro una balaustra, la vasca con i piedini. Lo stile rustico ed elegante della Tempio di una volta.",
]
LAT_DOT = ["Camera matrimoniale al piano superiore", "Vasca freestanding con i piedini", "Doccia con luci colorate",
           "Angolo cottura a induzione e macchina del caffè", "Giradischi e selezione di vinili", "Smart TV",
           "Climatizzazione inverno/estate", "Wi-Fi", "Biancheria da letto e da bagno, linea cortesia"]

def racconto(kicker, titolo, paras, firma, rid):
    return (f'<section class="racconto reveal" id="{rid}"><span class="k">{e(kicker)}</span><h2>{e(titolo)}</h2>'
            + "".join(f"<p>{e(p)}</p>" for p in paras) + (f'<div class="firma">{firma}</div>' if firma else '') + '</section>')

def p_style(color="rgba(239,232,220,.82)"):
    return f'class="reveal" style="margin:0;font-size:17px;line-height:1.8;color:{color}"'

def latteria():
    s = rd("antica-latteria-1930.html")
    s = re.sub(r'(<span class="fd"[^>]*>)[^<]*(</span>)', lambda m: m.group(1) + e(LAT_KICK) + m.group(2), s, count=1)
    quote = (f'<p class="reveal" style="margin:0;{SERIF};font-style:italic;font-size:clamp(18px,1.92vw,25px);line-height:1.5;'
             f'color:#D4A65A;text-transform:uppercase;letter-spacing:.07em">{e(LAT_QUOTE)}</p>')
    paras = "".join(f'<p {p_style()}>{e(p)}</p>' for p in LAT_P)
    s = re.sub(r'(<div style="display:flex;flex-direction:column;gap:28px;max-width:640px">).*?(\s*<div class="reveal" style="display:flex;flex-wrap:wrap;gap:14px;margin-top:12px">)',
               lambda m: m.group(1) + quote + paras + m.group(2), s, count=1, flags=re.S)
    li = "".join(f'<li style="padding:14px 0;border-top:1px solid rgba(239,232,220,.14)">{e(d)}</li>' for d in LAT_DOT)
    s = re.sub(r'(<ul style="list-style:none;margin:0 0 56px;[^"]*">).*?(</ul>)', lambda m: m.group(1) + li + m.group(2), s, count=1, flags=re.S)
    desc = "Antica Latteria 1930: 38 mq su due livelli per 2 persone, nel centro storico di Tempio Pausania, granito a vista, travi in legno, vasca con i piedini e giradischi. Prenota direttamente."
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', s)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda m: m.group(1) + e(desc) + m.group(2), s)
    s = re.sub(r'("@type": "Accommodation", "name": "Antica Latteria 1930", "description": ")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s)
    s = re.sub(r'"amenityFeature": \[.*?\]', '"amenityFeature": ' + json.dumps(
        [{"@type": "LocationFeatureSpecification", "name": d, "value": True} for d in LAT_DOT], ensure_ascii=False), s, count=1, flags=re.S)
    fuori = ('''  <section class="casa-sec" style="padding-top:0">
    <div><span class="gal-k reveal" style="display:block;margin-bottom:16px">Fuori</span><h2 class="reveal">La palazzina di fronte</h2></div>
    <div><p class="reveal">La Latteria è nella palazzina proprio di fronte alla Dimora: facciata bianca, balcone in ferro battuto e portone azzurro, tra le case di granito del centro storico. Un ingresso tutto suo, a pochi passi dalla sala da tè.</p></div>
  </section>
  <section class="gal-sec" style="padding-top:12px"><div class="gal" data-gal>''' + galleria("latfuori", "", "", "Antica Latteria 1930").split('<div class="gal" data-gal>',1)[1] + '</section>\n')
    s = re.sub(r', "floorSize": \{[^}]*\}, "occupancy": \{[^}]*\}', '', s)
    s = re.sub(r'("amenityFeature": \[.*?\])', lambda m: m.group(1) + ', "floorSize": {"@type": "QuantitativeValue", "value": 38, "unitCode": "MTK"}, "occupancy": {"@type": "QuantitativeValue", "maxValue": 2}', s, count=1, flags=re.S)
    block = fuori + ('<section class="gal-sec">' + galleria("lat", f"Galleria · {n_foto('lat')} foto", "Dentro la Latteria", "Antica Latteria 1930") + '</section>\n'
             + racconto("Una leggenda della Dimora", "La leggenda della Latteria", LAT_LEGGENDA, '<a href="/storie/leggenda-della-latteria" style="color:#8FA2E6">Anche nel Libro delle Storie →</a>', "leggenda"))
    return put_block(put_css(s), block)

def loft():
    s = ospiti(rd("loft-dell-antiquario.html"), ">Ultimo piano · 45 mq · Tempio Pausania<", ">Ultimo piano · 45 mq · 2 ospiti · Tempio Pausania<")
    teaser = racconto("Una leggenda della Dimora", "La leggenda dell'Antiquario", ANTIQUARIO, '<a href="/storie/leggenda-dell-antiquario" style="color:#8FA2E6">Anche nel Libro delle Storie →</a>', "leggenda")
    block = '<section class="gal-sec">' + galleria("loft", f"Galleria · {n_foto('loft')} foto", "Dentro il loft", "Loft dell'Antiquario") + '</section>\n' + teaser
    return put_block(put_css(s), block)

def ospiti(s, kick_old, kick_new):
    s = s.replace(kick_old, kick_new)
    s = re.sub(r', "occupancy": \{[^}]*\}', '', s)
    return s.replace('"floorSize": {"@type": "QuantitativeValue", "value": 25, "unitCode": "MTK"}', '"floorSize": {"@type": "QuantitativeValue", "value": 25, "unitCode": "MTK"}, "occupancy": {"@type": "QuantitativeValue", "maxValue": 2}').replace('"floorSize": {"@type": "QuantitativeValue", "value": 45, "unitCode": "MTK"}', '"floorSize": {"@type": "QuantitativeValue", "value": 45, "unitCode": "MTK"}, "occupancy": {"@type": "QuantitativeValue", "maxValue": 2}')

def suite():
    s = ospiti(rd("suite-del-viaggiatore.html"), ">Primo piano · 25 mq · Tempio Pausania<", ">Primo piano · 25 mq · 2 ospiti · Tempio Pausania<")
    block = ('<section class="gal-sec">' + galleria("suite", f"Galleria · {n_foto('suite')} foto", "Dentro la suite", "Suite del Viaggiatore") + '</section>\n'
             + racconto("Una leggenda della Dimora", "La leggenda del Viaggiatore", VIAGGIATORE, '<a href="/storie/leggenda-del-viaggiatore" style="color:#8FA2E6">Anche nel Libro delle Storie →</a>', "leggenda"))
    return put_block(put_css(s), block)

# ------------------------------------------------------------------ /la-dimora

def la_dimora():
    tpl = rd("loft-dell-antiquario.html")
    tpl = re.sub(r'\n?<!--dimore-->.*?<!--/dimore-->\n?', '\n', tpl, flags=re.S)
    head_end = tpl.find('</head>'); hero = tpl.find('  <section style="position:relative;min-height:min(640px,78vh)')
    foot = tpl.find('  <footer')
    h = tpl[:head_end]
    title = "La Dimora — palazzetto del 1930 nel centro storico di Tempio Pausania"
    desc = "La Dimora delle Storie: un palazzetto del 1930 in Piazza Eleonora d'Arborea, nel centro storico di Tempio Pausania, con sala da tè, pianoforte e libreria."
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{e(desc)}">', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{BASE}/la-dimora">', h)
    h = re.sub(r'<meta property="og:type".*?<meta property="og:locale" content="it_IT">',
               f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
               f'<meta property="og:image" content="{BASE}/img/foto/est-01.webp"><meta property="og:locale" content="it_IT">', h, flags=re.S)
    ld = {"@context": "https://schema.org", "@type": "LodgingBusiness", "name": "Dimora delle Storie", "url": BASE, "description": desc,
          "image": [f"{BASE}/img/foto/est-01.webp", f"{BASE}/img/foto/te-01.webp"], "telephone": "+393791656864", "email": "info@dimoradellestorie.com",
          "address": {"@type": "PostalAddress", "streetAddress": "Piazza Eleonora d'Arborea 6", "addressLocality": "Tempio Pausania", "postalCode": "07029", "addressRegion": "SS", "addressCountry": "IT"},
          "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in ["Sala da tè", "Pianoforte", "Libreria con testi sulla Gallura", "Parcheggio gratuito nella piazza adiacente"]]}
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', h, flags=re.S)
    h = h.replace('url(fonts/', 'url(/fonts/').replace('href="fonts/', 'href="/fonts/').replace('href="img/', 'href="/img/')
    body_open = tpl[head_end:hero]
    header = re.search(r'    <header.*?</header>', tpl, flags=re.S).group(0).replace('src="img/', 'src="/img/')
    hero_html = f'''  <section style="position:relative;min-height:min(720px,86vh);overflow:hidden;display:flex;flex-direction:column">
    <img class="heroimg" src="/img/foto/est-01.webp" alt="La Dimora delle Storie tra le case di granito del centro storico di Tempio Pausania" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 40%">
    <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,17,26,.7) 0%,rgba(15,17,26,.15) 35%,#0F111A 100%)"></div>
{header}
    <div style="position:relative;flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:16px;padding:0 clamp(20px,4.5vw,64px) 56px">
      <span class="fd" style="font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#D4A65A">Piazza Eleonora d'Arborea · 1930 · Tempio Pausania</span>
      <h1 class="h1a" style="margin:0;{SERIF};font-weight:400;font-size:clamp(26px,5vw,71px);line-height:1.15;text-transform:uppercase;letter-spacing:.08em">La Dimora</h1>
    </div>
  </section>'''
    quote = (f'<p class="reveal" style="margin:0 0 28px;{SERIF};font-style:italic;font-size:clamp(18px,1.92vw,25px);line-height:1.5;'
             f'color:#8FA2E6;text-transform:uppercase;letter-spacing:.07em">«Ogni pietra di questo palazzetto racconta una storia, un legame con la città che lo circonda.»</p>')
    intro = f'''  <section class="casa-sec">
    <div>{quote}<h2 class="reveal">Un palazzetto del 1930</h2></div>
    <div><p class="reveal">Nel centro storico di Tempio Pausania, a pochi passi da Piazza Gallura, una residenza del 1930 restaurata con cura per unire il comfort di oggi al fascino della casa di una volta.</p>
    <p class="reveal">Tre dimore indipendenti, il Loft dell'Antiquario, la Suite del Viaggiatore e, nella palazzina di fronte, l'Antica Latteria 1930, e al centro della casa uno spazio comune: la sala da tè.</p></div>
  </section>'''
    facc = f'''  <section class="casa-sec" style="padding-top:clamp(40px,5vw,72px)">
    <div><span class="gal-k reveal" style="display:block;margin-bottom:16px">Fuori</span><h2 class="reveal">La facciata</h2></div>
    <div><p class="reveal">La facciata chiara tra le case di granito, i balconi in ferro battuto e il portone azzurro: è la Tempio di pietra, la «Città di pietra», che si vede dalla finestra.</p>
    <p class="reveal">Nella piazza adiacente ci sono parcheggi gratuiti.</p></div>
  </section>
  <section class="gal-sec" style="padding-top:12px"><div class="gal" data-gal>{galleria("est", "", "", "Dimora delle Storie").split('<div class="gal" data-gal>',1)[1]}</section>'''
    riti = [
        ("Il tè", "Il rito del pomeriggio", "Un tavolino d'epoca con il servizio da tè e da caffè, le tazze di porcellana e il tempo che rallenta. Il momento giusto per scegliere un libro dalla vetrina o pianificare la giornata."),
        ("Il pianoforte", "Il cuore della sala", "Il pianoforte verticale con i candelieri d'ottone è il centro della stanza. La musica è di casa a Tempio: qui è nato Gavino Gabriel, compositore e studioso dei canti della Gallura."),
        ("La poesia", "Versi da leggere la sera", "La Gallura ha una tradizione poetica antica: a Tempio è nato Don Baignu, Gavino Pes, tra i grandi poeti sardi del Settecento. Nel Libro delle Storie un capitolo intero è dedicato alla poesia."),
    ]
    riti_html = '<div class="riti">' + "".join(
        f'<div class="rito reveal"><span class="gal-k">{e(k)}</span><h3>{e(t)}</h3><p>{e(x)}</p></div>' for k, t, x in riti) + '</div>'
    te = f'''  <section class="casa-sec" id="sala-da-te">
    <div><span class="gal-k reveal" style="display:block;margin-bottom:16px">Tè · Poesia · Pianoforte</span><h2 class="reveal">La sala da tè</h2></div>
    <div><p class="reveal">Al centro della Dimora c'è la stanza più amata della casa: il pianoforte verticale, il divano d'epoca a righe, la vetrina con i libri su Tempio e sulla Gallura e un tavolino per il tè e il caffè.</p>
    <p class="reveal">È lo spazio comune degli ospiti, pensato per le ore lente: una tazza di tè, una poesia, una musica.</p></div>
  </section>
  <section class="gal-sec" style="padding-top:12px;padding-bottom:0">{riti_html}</section>
  <section class="gal-sec" style="padding-top:clamp(40px,5vw,72px)"><div class="gal" data-gal>{galleria("te", "", "", "Sala da tè").split('<div class="gal" data-gal>',1)[1]}</section>
{racconto("Una leggenda della Dimora", "La leggenda della sala da tè", SALA_TE, '<a href="/storie/leggenda-della-sala-da-te" style="color:#8FA2E6">Anche nel Libro delle Storie →</a>', "leggenda-sala-da-te")}
  <section class="te-cta reveal"><span class="gal-k">Il Libro delle Storie</span><p>Sfogliate le storie di Tempio e le poesie della Gallura con il pianoforte in sottofondo. E se avete una storia da raccontare, scrivetela per il Libro.</p><a href="/storie">Apri il libro →</a> <a href="/scrivi-la-tua-storia" style="background:transparent;color:#EFE8DC;border:1px solid rgba(239,232,220,.3);margin-left:8px">Scrivi la tua storia</a></section>'''
    cards = '''  <section class="casa-sec" style="padding-bottom:40px"><div><span class="gal-k reveal" style="display:block;margin-bottom:16px">Dove dormire</span><h2 class="reveal">Le dimore</h2></div><div></div></section>
  <div class="dim-cards">''' + "".join(
        f'<a class="dim-card reveal" href="/{slug}"><img src="/img/{img}" alt="{e(n)}" loading="lazy"><span><small>{e(k)}</small><b>{e(n)}</b></span></a>'
        for slug, img, n, k in [("loft-dell-antiquario", "loft.jpg", "Loft dell'Antiquario", "Ultimo piano · 45 mq"),
                                ("suite-del-viaggiatore", "suite.jpg", "Suite del Viaggiatore", "Primo piano · 25 mq"),
                                ("antica-latteria-1930", "latteria.jpg", "Antica Latteria 1930", "Due livelli · 38 mq")]) + '</div>'
    body = hero_html + "\n" + intro + "\n" + facc + "\n" + te + "\n" + cards + "\n<!--dimore-->\n" + LB + "\n<!--/dimore-->\n"
    return put_css(h + body_open + body + tpl[foot:])


# ------------------------------------------------------------------ navigazione: Home esplicita, nome accanto alla chiave, pagina attiva
NAV_CSS = """<style id="nav-chiara">
.brand{display:inline-flex;align-items:center;gap:14px;min-height:44px;text-decoration:none}
.brand b{font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:15px;letter-spacing:.16em;line-height:1.25;color:#EFE8DC}
.brand:hover b{color:#D4A65A}
.topnav a[aria-current]{color:#D4A65A;position:relative}
.topnav a[aria-current]::after{content:"";position:absolute;left:0;right:0;bottom:-5px;height:1px;background:#D4A65A}
@media (max-width:700px){.brand b{display:none}.topnav a[href="/"][aria-current]{display:none}.topnav{gap:13px!important;padding-left:18px!important;padding-right:18px!important}}
</style>"""
LOGO_RE = re.compile(r'<a href="(?:/|#)" aria-label="Dimora delle Storie[^"]*" style="[^"]*"><img src="(/?img/logo-icona\.svg)" alt="" style="[^"]*"></a>')
LINK = 'style="text-decoration:none"'

FOOT_ADDR = "<span>Piazza Eleonora d'Arborea 6<br>07029 Tempio Pausania (SS)</span>"
def cin(s):
    if "IT090070C2000S8992" in s: return s
    return s.replace(FOOT_ADDR, FOOT_ADDR + '<span style="font-size:12px;letter-spacing:.12em;color:rgba(239,232,220,.55)">CIN IT090070C2000S8992</span>')

def header_chiaro(s, attivo):
    s = re.sub(r'<style id="nav-chiara">.*?</style>\n?', '', s, flags=re.S).replace('</head>', NAV_CSS + '\n</head>', 1)
    s = LOGO_RE.sub(lambda m: f'<a class="brand" href="/" aria-label="Dimora delle Storie — torna alla home"><img src="{m.group(1)}" alt="" style="height:52px;width:auto;display:block"><b>Dimora<br>delle Storie</b></a>', s)
    s = s.replace(' aria-current="page"', '')
    for h in ['#dimore', '/#dimore']:
        s = s.replace(f'<a href="{h}" {LINK}>Dimore</a>', f'<a href="/" {LINK}>Home</a><a href="{h}" {LINK}>Dimore</a>') if f'<a href="/" {LINK}>Home</a><a href="{h}"' not in s else s
    if attivo:
        s = s.replace(f'<a href="{attivo}" {LINK}>', f'<a href="{attivo}" {LINK} aria-current="page">', 1)
    return s


# ------------------------------------------------------------------ /scrivi-la-tua-storia
def shell(slug, title, desc, og_img, ld, hero_img, hero_alt, kicker, h1, body, extra_css=""):
    tpl = rd("loft-dell-antiquario.html")
    tpl = re.sub(r'\n?<!--dimore-->.*?<!--/dimore-->\n?', '\n', tpl, flags=re.S)
    head_end = tpl.find('</head>'); hero = tpl.find('  <section style="position:relative;min-height:min(640px,78vh)'); foot = tpl.find('  <footer')
    h = tpl[:head_end]
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{e(desc)}">', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{BASE}/{slug}">', h)
    h = re.sub(r'<meta property="og:type".*?<meta property="og:locale" content="it_IT">',
               f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
               f'<meta property="og:image" content="{BASE}{og_img}"><meta property="og:locale" content="it_IT">', h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', h, flags=re.S)
    h = h.replace('url(fonts/', 'url(/fonts/').replace('href="fonts/', 'href="/fonts/').replace('href="img/', 'href="/img/')
    if extra_css: h += f'<style id="pagina">{extra_css}</style>\n'
    header = re.search(r'    <header.*?</header>', tpl, flags=re.S).group(0).replace('src="img/', 'src="/img/')
    hero_html = f"""  <section style="position:relative;min-height:min(560px,70vh);overflow:hidden;display:flex;flex-direction:column">
    <img class="heroimg" src="{hero_img}" alt="{e(hero_alt)}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.7">
    <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,17,26,.75) 0%,rgba(15,17,26,.25) 35%,#0F111A 100%)"></div>
{header}
    <div style="position:relative;flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:16px;padding:0 clamp(20px,4.5vw,64px) 56px">
      <span class="fd" style="font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#D4A65A">{e(kicker)}</span>
      <h1 class="h1a" style="margin:0;{SERIF};font-weight:400;font-size:clamp(26px,4.6vw,64px);line-height:1.15;text-transform:uppercase;letter-spacing:.08em">{e(h1)}</h1>
    </div>
  </section>"""
    return put_css(h + tpl[head_end:hero] + hero_html + "\n" + body + "\n" + tpl[foot:])

FORM_CSS = """
.scrivi{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(380px,100%),1fr));gap:clamp(40px,6vw,96px);padding:clamp(56px,7vw,96px) clamp(20px,4.5vw,64px) clamp(80px,9vw,120px);align-items:start}
.scrivi .intro p{margin:0 0 20px;font-size:17px;line-height:1.8;color:rgba(239,232,220,.82)}
.scrivi .intro ol{margin:8px 0 28px;padding:0;list-style:none;counter-reset:n}
.scrivi .intro li{counter-increment:n;position:relative;padding:16px 0 16px 52px;border-top:1px solid rgba(239,232,220,.14);font-size:15px;line-height:1.6;color:rgba(239,232,220,.8)}
.scrivi .intro li::before{content:counter(n,upper-roman);position:absolute;left:0;top:14px;font-family:'Bodoni Moda',Georgia,serif;font-size:20px;color:#D4A65A}
.modulo{position:relative;padding:clamp(24px,3vw,40px);border:1px solid rgba(226,183,106,.3);background:linear-gradient(180deg,rgba(15,17,40,.7),rgba(15,17,40,.4));box-shadow:0 30px 80px rgba(0,0,0,.4)}
.modulo h2{margin:0 0 24px;font-family:'Bodoni Moda',Georgia,serif;font-variation-settings:'opsz' 11;font-weight:400;font-size:clamp(20px,2vw,26px);letter-spacing:.08em}
.modulo label{display:block;margin:0 0 18px;font-size:11px;letter-spacing:.22em;color:rgba(239,232,220,.75)}
.modulo input[type=text],.modulo input[type=email],.modulo select,.modulo textarea{display:block;width:100%;box-sizing:border-box;margin-top:8px;padding:14px 16px;border:1px solid rgba(239,232,220,.22);border-radius:2px;background:rgba(5,7,20,.55);color:#EFE8DC;font:16px/1.6 'Inter',system-ui,sans-serif;letter-spacing:normal}
.modulo select{text-transform:none}.modulo option{background:#0F111A}
.modulo textarea{min-height:300px;resize:vertical}
.modulo input:focus,.modulo select:focus,.modulo textarea:focus{outline:none;border-color:#D4A65A;box-shadow:0 0 0 3px rgba(212,166,90,.18)}
.modulo .conta{display:block;margin-top:6px;text-align:right;font-size:11px;letter-spacing:.1em;color:rgba(239,232,220,.5)}
.modulo .check{display:flex;gap:12px;align-items:flex-start;font-size:13px;letter-spacing:.04em;line-height:1.6;text-transform:none!important;color:rgba(239,232,220,.8)}
.modulo .check *{text-transform:none!important}
.modulo .check input{margin-top:4px;width:18px;height:18px;accent-color:#D4A65A;flex:none}
.modulo .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.modulo button{margin-top:10px;min-height:52px;padding:0 36px;border:0;border-radius:999px;background:#D4A65A;color:#0F111A;font:500 13px 'Inter',sans-serif;letter-spacing:.16em;text-transform:uppercase;cursor:pointer}
.modulo button[disabled]{opacity:.6;cursor:wait}
.modulo .esito{margin:18px 0 0;font-size:14px;line-height:1.7;color:#E2B76A;text-transform:none!important;letter-spacing:.02em}
.grazie{text-align:center;padding:40px 10px}
.grazie h2{margin:0 0 16px}
.grazie p{font-size:16px;line-height:1.8;color:rgba(239,232,220,.85);text-transform:none!important;letter-spacing:normal!important}
.privacy{margin-top:22px;font-size:12px!important;line-height:1.7!important;color:rgba(239,232,220,.55)!important;text-transform:none!important;letter-spacing:normal!important}
"""

FORM_JS = r"""<script>(()=>{const f=document.getElementById('form-storia');if(!f)return;f.t.value=Date.now();
const ta=f.storia,ct=document.getElementById('conta');const up=()=>{ct.textContent=ta.value.length+' / 12000 caratteri'+(ta.value.length<200?' · minimo 200':'')};ta.addEventListener('input',up);up();
async function riduci(file){if(!file)return '';const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=ko;i.src=URL.createObjectURL(file)});
const s=Math.min(1,1600/Math.max(img.width,img.height)),c=document.createElement('canvas');c.width=Math.round(img.width*s);c.height=Math.round(img.height*s);c.getContext('2d').drawImage(img,0,0,c.width,c.height);return c.toDataURL('image/jpeg',.82)}
f.addEventListener('submit',async ev=>{ev.preventDefault();const es=document.getElementById('esito'),b=f.querySelector('button');es.textContent='';
if(f.storia.value.trim().length<200){es.textContent='La storia è un po\' breve: servono almeno 200 caratteri.';return}
b.disabled=true;b.textContent='Invio in corso…';
try{const dati={nome:f.nome.value,email:f.email.value,dimora:f.dimora.value,titolo:f.titolo.value,storia:f.storia.value,firma:f.firma.value,sito:f.sito.value,t:+f.t.value,
consenso_pubblicazione:f.consenso_pubblicazione.checked,consenso_privacy:f.consenso_privacy.checked,foto:f.foto.files[0]?await riduci(f.foto.files[0]):''};
const r=await fetch('/api/storia',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dati)});const j=await r.json().catch(()=>({}));
if(r.ok&&j.ok){f.innerHTML='<div class="grazie"><h2>Grazie!</h2><p>La vostra storia è arrivata alla Dimora. La leggeremo con cura e, se la pubblicheremo nel Libro delle Storie, vi scriveremo per avvisarvi.</p><p><a href="/storie" style="color:#E2B76A">Sfoglia il Libro delle Storie →</a></p></div>';f.scrollIntoView({behavior:'smooth',block:'start'});return}
throw new Error(j.errore||'errore')}catch(err){es.innerHTML='Non siamo riusciti a inviare la storia. Riprovate tra poco, oppure scriveteci a <a href="mailto:info@dimoradellestorie.com" style="color:#E2B76A">info@dimoradellestorie.com</a>.';b.disabled=false;b.textContent='Invia la storia'}})})();</script>"""

def form_html(cls="modulo reveal"):
    opts = "".join(f'<option>{e(x)}</option>' for x in ["Loft dell'Antiquario", "Suite del Viaggiatore", "Antica Latteria 1930", "Altro / non ancora ospite"])
    return f"""    <form class="{cls}" id="form-storia" novalidate>
      <h2>La vostra storia</h2>
      <label>Nome e cognome<input type="text" name="nome" required maxlength="80" autocomplete="name"></label>
      <label>Email (non sarà pubblicata)<input type="email" name="email" required maxlength="120" autocomplete="email"></label>
      <label>Dove avete soggiornato<select name="dimora">{opts}</select></label>
      <label>Titolo della storia<input type="text" name="titolo" required maxlength="120"></label>
      <label>La storia<textarea name="storia" required maxlength="12000" placeholder="C'era una volta, a Tempio…"></textarea><span class="conta" id="conta"></span></label>
      <label>Firma nel Libro (come volete apparire: nome, iniziali, un soprannome)<input type="text" name="firma" maxlength="80" placeholder="Es. Anna e Marco, Milano"></label>
      <label>Una foto, se volete (facoltativa)<input type="file" name="foto" accept="image/jpeg,image/png,image/webp" style="margin-top:8px;font-size:13px;text-transform:none"></label>
      <div class="hp" aria-hidden="true"><label>Non compilare<input type="text" name="sito" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="t">
      <label class="check"><input type="checkbox" name="consenso_pubblicazione" required><span>Sono l'autore di questa storia (e della foto, se presente) e acconsento alla sua pubblicazione nel Libro delle Storie e sui canali social della Dimora delle Storie, con la firma indicata e con eventuali piccole correzioni da me approvate.</span></label>
      <label class="check"><input type="checkbox" name="consenso_privacy" required><span>Ho letto l'informativa qui sotto e acconsento al trattamento dei miei dati per valutare e pubblicare la storia.</span></label>
      <button type="submit">Invia la storia</button>
      <p class="esito" id="esito" role="status" aria-live="polite"></p>
      <p class="privacy">Informativa: titolare del trattamento è Luca Cossu, Dimora delle Storie, Piazza Eleonora d'Arborea 6, 07029 Tempio Pausania (SS), info@dimoradellestorie.com. I dati inviati (nome, email, testo ed eventuale foto) sono usati solo per valutare e pubblicare la storia e per contattarvi in merito; l'email non viene mai pubblicata né ceduta a terzi. Potete chiedere in qualsiasi momento di correggere o rimuovere la storia e di cancellare i vostri dati scrivendo a info@dimoradellestorie.com.</p>
    </form>
"""

def scrivi():
    opts = "".join(f'<option>{e(x)}</option>' for x in ["Loft dell'Antiquario", "Suite del Viaggiatore", "Antica Latteria 1930", "Altro / non ancora ospite"])
    body = f"""  <section class="scrivi">
    <div class="intro">
      <p class="reveal" style="{SERIF};font-style:italic;font-size:clamp(18px,1.92vw,25px);line-height:1.5;color:#8FA2E6;text-transform:uppercase;letter-spacing:.07em">«E la prossima storia, magari, la scrivete voi.»</p>
      <p class="reveal">Il Libro delle Storie raccoglie le leggende della Dimora, le storie di Tempio e le poesie della Gallura. Ora ha un capitolo che aspetta voi: le storie degli ospiti.</p>
      <p class="reveal">Un ricordo del soggiorno, una passeggiata tra le piazze di granito, una giornata sul Limbara, un incontro, una poesia nata nella sala da tè: ogni storia vera, o inventata con il cuore, è benvenuta.</p>
      <ol class="reveal">
        <li>Scrivete la vostra storia nel modulo, con un titolo e, se volete, una foto.</li>
        <li>La leggiamo con cura: possiamo proporvi qualche piccola correzione, sempre con il vostro accordo.</li>
        <li>Se la pubblichiamo, entra nel Libro delle Storie con la firma che avete scelto, e vi scriviamo per avvisarvi.</li>
      </ol>
      <p class="reveal" style="font-size:15px;color:rgba(239,232,220,.65)">Grazie fin d'ora: ogni storia rende la Dimora un po' più vostra.</p>
    </div>
{form_html()}  </section>
{FORM_JS}"""
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Scrivi la tua storia — Il Libro delle Storie", "url": f"{BASE}/scrivi-la-tua-storia",
          "isPartOf": {"@type": "WebSite", "name": "Dimora delle Storie", "url": BASE}}
    return shell("scrivi-la-tua-storia", "Scrivi la tua storia — Il Libro delle Storie | Dimora delle Storie",
                 "Avete soggiornato alla Dimora delle Storie a Tempio Pausania? Scrivete la vostra storia: le più belle entrano nel Libro delle Storie.",
                 "/img/foto/te-01.webp", ld, "/img/foto/te-01.webp", "Il pianoforte e il divano della sala da tè", "Il Libro delle Storie · Gli ospiti", "Scrivi la tua storia", body, FORM_CSS)

CARTA_CSS = FORM_CSS + """
.foglio-modal{position:fixed;inset:0;z-index:400;display:none;align-items:flex-start;justify-content:center;overflow-y:auto;padding:4vh 16px;background:rgba(6,8,22,.86);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.foglio-modal.on{display:flex;animation:fade .5s ease both}
.foglio-modal .modulo{width:min(640px,100%);margin:auto;background:#F2EADC repeating-linear-gradient(180deg,rgba(0,0,0,0) 0,rgba(0,0,0,0) 31px,rgba(18,27,82,.08) 31px,rgba(18,27,82,.08) 32px);border:0;box-shadow:0 40px 90px rgba(0,0,0,.6),inset 0 0 60px rgba(120,90,40,.15);color:#121B52;animation:up 0.8s cubic-bezier(.2,.7,.1,1) both}
.foglio-modal .modulo h2{color:#121B52}
.foglio-modal .modulo label{color:#5A5650}
.foglio-modal .modulo input[type=text],.foglio-modal .modulo input[type=email],.foglio-modal .modulo select,.foglio-modal .modulo textarea{background:rgba(255,255,255,.55);border:0;border-bottom:1px solid rgba(18,27,82,.35);color:#121B52}
.foglio-modal .modulo textarea{background:transparent repeating-linear-gradient(180deg,rgba(0,0,0,0) 0,rgba(0,0,0,0) 25px,rgba(18,27,82,.14) 25px,rgba(18,27,82,.14) 26px);line-height:26px;font-family:'Bodoni Moda',Georgia,serif;font-size:17px;border-left:1px solid rgba(160,60,50,.4)}
.foglio-modal .modulo option{background:#F2EADC}
.foglio-modal .modulo .check,.foglio-modal .modulo .conta,.foglio-modal .privacy{color:#4A463F!important}
.foglio-modal .modulo button[type=submit]{background:#121B52;color:#F2EADC}
.foglio-modal .modulo .esito{color:#7A2E2A}
.foglio-modal .grazie p{color:#33302B}
.foglio-modal .grazie a{color:#121B52!important}
.foglio-x{position:fixed;top:18px;right:18px;z-index:410;width:48px;height:48px;border-radius:999px;border:1px solid rgba(239,232,220,.35);background:rgba(6,8,22,.6);color:#EFE8DC;font-size:20px;cursor:pointer}
"""

def libro_foglio(s):
    s = re.sub(r'<style id="foglio">.*?</style>\n?', '', s, flags=re.S).replace('</head>', f'<style id="foglio">{CARTA_CSS}</style>\n</head>', 1)
    s = re.sub(r'\n?<!--foglio-->.*?<!--/foglio-->\n?', '\n', s, flags=re.S)
    modal = (f'<!--foglio--><div class="foglio-modal" role="dialog" aria-modal="true" aria-label="Scrivi la tua storia"><button type="button" class="foglio-x" aria-label="Chiudi">✕</button>{form_html("modulo")}</div>{FORM_JS}'
             """<script>(()=>{const m=document.querySelector('.foglio-modal');if(!m)return;const x=m.querySelector('.foglio-x');let last;
const open=a=>{last=a;m.classList.add('on');document.documentElement.style.overflow='hidden';setTimeout(()=>{const n=m.querySelector('input[name=nome]');n&&n.focus()},300)};
const close=()=>{m.classList.remove('on');document.documentElement.style.overflow='';last&&last.focus()};
document.querySelectorAll('[data-foglio]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();ev.stopPropagation();open(a)}));
x.onclick=close;m.addEventListener('click',ev=>{if(ev.target===m)close()});addEventListener('keydown',ev=>{if(ev.key==='Escape'&&m.classList.contains('on'))close()});})();</script><!--/foglio-->""")
    return s.replace('</body>', modal + '\n</body>', 1)

# ------------------------------------------------------------------ esecuzione
wr("antica-latteria-1930.html", nav(latteria()))
wr("loft-dell-antiquario.html", nav(loft()))
wr("suite-del-viaggiatore.html", nav(suite()))
wr("la-dimora.html", nav(la_dimora()))
wr("scrivi-la-tua-storia.html", nav(scrivi()))
for p in ["index.html", "storie.html", "tempio-pausania.html", "storie/dove-dormire-a-tempio-pausania.html", "tools/storie.py"]:
    wr(p, nav(rd(p)))
idx = rd("index.html")
idx = idx.replace("[N] ospiti · [N] mq · [dotazioni]", "Vasca con i piedini · Giradischi · Climatizzazione · [N] ospiti")
idx = idx.replace("Vasca con i piedini · Giradischi · Climatizzazione · [N] ospiti", "Vasca con i piedini · Giradischi · Climatizzazione · 2 ospiti").replace("03 — GRANITO E LEGNO", "03 — DUE LIVELLI · 38 MQ")
idx = idx.replace("Tavolo per 4 · [N] ospiti", "Tavolo per 4 · 2 ospiti").replace("Climatizzazione · [N] ospiti", "Climatizzazione · 2 ospiti")
idx = idx.replace("[CIN / codice identificativo]", "CIN IT090070C2000S8992")
wr("index.html", idx)
sm = rd("sitemap.xml")
if "/la-dimora<" not in sm:
    sm = sm.replace("  <url><loc>https://www.dimoradellestorie.com/storie</loc>",
                    "  <url><loc>https://www.dimoradellestorie.com/la-dimora</loc><lastmod>2026-11-22</lastmod></url>\n  <url><loc>https://www.dimoradellestorie.com/storie</loc>")
    sm = re.sub(r'(antica-latteria-1930</loc><lastmod>)[^<]*', r'\g<1>2026-11-22', sm)
    wr("sitemap.xml", sm)
sm = rd("sitemap.xml")
if "/scrivi-la-tua-storia<" not in sm:
    sm = sm.replace("</urlset>", f"  <url><loc>{BASE}/scrivi-la-tua-storia</loc><lastmod>2026-11-22</lastmod></url>\n</urlset>")
for slug in ["leggenda-dell-antiquario", "leggenda-del-viaggiatore", "leggenda-della-sala-da-te", "leggenda-della-latteria"]:
    if f"/storie/{slug}<" not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{BASE}/storie/{slug}</loc><lastmod>2026-11-22</lastmod><priority>0.7</priority></url>\n</urlset>")
wr("sitemap.xml", sm)
import subprocess, glob
for t in ["storie.py", "tempio.py", "legali.py"]:
    subprocess.run([sys.executable, "-B", f"{SITE}/tools/{t}"], check=True, stdout=subprocess.DEVNULL)
ATTIVO = {"index.html": "/", "loft-dell-antiquario.html": "/#dimore", "suite-del-viaggiatore.html": "/#dimore",
          "antica-latteria-1930.html": "/#dimore", "la-dimora.html": "/la-dimora", "storie.html": "/storie",
          "tempio-pausania.html": "/tempio-pausania", "scrivi-la-tua-storia.html": "/storie"}
for p in ["index.html", "la-dimora.html", "loft-dell-antiquario.html", "suite-del-viaggiatore.html", "antica-latteria-1930.html",
          "storie.html", "tempio-pausania.html", "scrivi-la-tua-storia.html"] + [os.path.relpath(x, SITE) for x in glob.glob(f"{SITE}/storie/*.html")]:
    wr(p, cin(header_chiaro(nav(rd(p)), ATTIVO.get(p, "/storie"))))
wr("storie.html", libro_foglio(rd("storie.html")))
subprocess.run([sys.executable, "-B", f"{SITE}/tools/prenota.py"], check=True, stdout=subprocess.DEVNULL)  # prenotazioni Magellano
print("ok")
