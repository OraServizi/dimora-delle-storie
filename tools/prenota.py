#!/usr/bin/env python3
"""Prenotazioni Magellano nel sito: pulsante PRENOTA nell'intestazione di tutte
le pagine, calendarietto di disponibilità in ogni pagina alloggio, pagina
/prenota (scelta della dimora + calendario) e pagina /la-dimora-intera (Duplex:
Loft + Suite insieme). Idempotente: si può rilanciare (lo lancia anche dimore.py).

Codici Magellano (mail di Alessandro Marin, 23/11/2026):
  apikey YVQw8J6NyW · gruppi: Dimora delle Storie 16915, Antica Latteria 1930 18791
  alloggi: Loft 47201, Suite 47540, Duplex 48070, Latteria 50407
Le disponibilità di Duplex, Loft e Suite sono sincronizzate in Magellano."""
import glob, html, json, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.dimoradellestorie.com"
SERIF = "font-family:'Bodoni Moda',Georgia,serif"
e = html.escape
APIKEY = "YVQw8J6NyW"
WA = "https://wa.me/393791656864"
TEL = "+39 379 165 6864"

ALLOGGI = {   # chiave: (resourceID, realGroupID, ospiti max, nome, pagina)
    "loft":    (47201, 16915, 2, "Loft dell'Antiquario", "/loft-dell-antiquario"),
    "suite":   (47540, 16915, 2, "Suite del Viaggiatore", "/suite-del-viaggiatore"),
    "latteria":(50407, 18791, 2, "Antica Latteria 1930", "/antica-latteria-1930"),
    "intera":  (48070, 16915, 4, "La Dimora intera", "/la-dimora-intera"),
}
PAGINE_ALLOGGIO = {"loft-dell-antiquario.html": "loft", "suite-del-viaggiatore.html": "suite",
                   "antica-latteria-1930.html": "latteria"}

def rd(p): return open(f"{SITE}/{p}", encoding="utf-8").read()
def wr(p, s): open(f"{SITE}/{p}", "w", encoding="utf-8").write(s)

def blocco(s, tag, nuovo, dove):
    """Toglie il vecchio blocco <!--tag-->…<!--/tag--> e inserisce il nuovo davanti a `dove`."""
    s = re.sub(rf'<!--{tag}-->.*?<!--/{tag}-->\n?', '', s, flags=re.S)
    if nuovo is None: return s
    i = s.find(dove)
    if i < 0: return s
    return s[:i] + f'<!--{tag}-->{nuovo}<!--/{tag}-->\n' + s[i:]

# ------------------------------------------------------------------ stile
CSS = """<style id="prenota-css">
.btn-prenota{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:0 28px;border-radius:999px;background:#D4A65A;color:#0F111A!important;text-decoration:none;font:500 12px 'Inter',system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;box-shadow:0 10px 30px rgba(0,0,0,.3);transition:background .25s,transform .25s}
.btn-prenota:hover{background:#E2B76A;transform:translateY(-1px)}
.btn-prenota[aria-current]{background:transparent;color:#E2B76A!important;border:1px solid rgba(226,183,106,.6)}
@media (min-width:701px) and (max-width:1180px){.topnav{gap:18px!important;padding-left:20px!important;padding-right:20px!important}.btn-prenota{padding:0 22px}}
@media (max-width:700px){header:has(.btn-prenota){row-gap:14px!important}header .btn-prenota{order:2;margin-left:auto;min-height:40px;padding:0 18px;font-size:11px;letter-spacing:.16em}header .topnav{order:3;width:100%;box-sizing:border-box;justify-content:center}}
.cal-sec{padding:clamp(56px,7vw,96px) clamp(20px,4.5vw,64px);border-top:1px solid rgba(239,232,220,.1)}
.cal-head{max-width:760px;margin:0 0 36px}
.cal-head .k{display:block;margin-bottom:14px;font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#D4A65A}
.cal-head h2{margin:0 0 16px;font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:clamp(24px,3vw,40px);line-height:1.2;text-transform:uppercase;letter-spacing:.08em}
.cal-head p{margin:0;font-size:16px;line-height:1.8;color:rgba(239,232,220,.78)}
.cal-box{position:relative;padding:clamp(18px,3vw,40px);border:1px solid rgba(226,183,106,.28);background:linear-gradient(180deg,rgba(15,17,40,.72),rgba(15,17,40,.42));box-shadow:0 30px 80px rgba(0,0,0,.4)}
.cal-wait{margin:0;padding:60px 0;text-align:center;font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:rgba(239,232,220,.55)}
.cal-bar{display:flex;flex-wrap:wrap;gap:16px 24px;align-items:center;justify-content:space-between;margin-top:24px;padding-top:24px;border-top:1px solid rgba(239,232,220,.14)}
.cal-sel{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:rgba(239,232,220,.8)}
.cal-btn{min-height:52px;padding:0 40px;border:0;border-radius:999px;background:#D4A65A;color:#0F111A;font:500 13px 'Inter',system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase;cursor:pointer;transition:background .25s}
.cal-btn:hover{background:#E2B76A}
.cal-alt{margin:22px 0 0;font-size:14px;letter-spacing:.04em;color:rgba(239,232,220,.6)}
.cal-alt a{color:#E2B76A}
.cal-tabs{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 28px}
.cal-tabs button{min-height:44px;padding:0 22px;border:1px solid rgba(239,232,220,.22);border-radius:999px;background:transparent;color:#EFE8DC;font:400 12px 'Inter',system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;cursor:pointer}
.cal-tabs button[aria-pressed=true]{background:#EFE8DC;color:#0F111A;border-color:#EFE8DC}
.cal-tabs small{opacity:.6;margin-left:6px;letter-spacing:.08em}
/* calendarietto Magellano: usa le sue variabili CSS, ricolorate sulla Dimora */
.ml-cal{--calendar-bg:transparent;--header-month-txt:#EFE8DC;--header-week-txt:rgba(239,232,220,.5);--days-border:transparent;--element-hover:rgba(212,166,90,.2);--disabled-element-hover:transparent;--free-day:transparent;--not-selectable-day:transparent;--selected-day:rgba(212,166,90,.2);--selected-day-first-last:#D4A65A;--busy-day:transparent;--days-contrast-bg:transparent;color:#EFE8DC;font-family:'Inter',system-ui,sans-serif}
.ml-cal .ml-calendarWrapper{padding:0;border-radius:0;background:transparent}
.ml-cal .ml-calendar .cal-day{color:#EFE8DC;font-size:14px}
.ml-cal .ml-calendar .cal-day-block-booking{color:rgba(239,232,220,.45)}
.ml-cal .ml-calendar tbody tr td button.cal-day-selected-first,.ml-cal .ml-calendar tbody tr td button.cal-day-selected-last{color:#0F111A!important;font-weight:500}
.ml-cal .ml-calendar thead tr.month-title .month-name{font-family:'Bodoni Moda',Georgia,serif;font-weight:400;text-transform:uppercase!important;letter-spacing:.12em;font-size:16px}
.ml-cal .ml-calendar thead tr.day-week .day-name{font-size:11px;letter-spacing:.14em;text-transform:uppercase!important}
.ml-cal select{background:rgba(5,7,20,.6)!important;color:#EFE8DC!important;border:1px solid rgba(239,232,220,.25)!important;border-radius:2px}
.ml-cal option{background:#0F111A}
.ml-cal .ml-btn.prevMonth,.ml-cal .ml-btn.nextMonth{color:#E2B76A}
.ml-cal .legend-item{border-color:rgba(239,232,220,.35)!important;background:transparent!important}
.ml-cal .legend-title,.ml-cal .legend-label,.ml-cal .ml-bottom-label{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:rgba(239,232,220,.65)}
.ml-cal .ml-bottom-row{margin-top:18px;padding-top:22px;border-top:1px solid rgba(239,232,220,.14)}
.ml-cal .ml-checkin,.ml-cal .ml-checkout{font-family:'Bodoni Moda',Georgia,serif;font-size:18px;color:#EFE8DC}
.ml-cal .ml-confirm-booking{display:inline-flex!important;align-items:center;justify-content:center;min-height:52px;padding:0 44px!important;margin-top:18px;border:0!important;border-radius:999px!important;background:#D4A65A!important;color:#0F111A!important;font:500 13px 'Inter',system-ui,sans-serif!important;letter-spacing:.18em;text-transform:uppercase;text-decoration:none!important}
.ml-cal .ml-confirm-booking:hover{background:#E2B76A!important}
</style>"""

LOADER = """<script>(()=>{const box=document.getElementById('ml-cal');if(!box)return;
const sec=box.closest('[data-res]'),btn0=document.getElementById('cal-prenota'),sel=document.querySelector('.cal-sel');
const load=(src,css)=>new Promise((ok,ko)=>{const t=document.createElement(css?'link':'script');if(css){t.rel='stylesheet';t.href=src}else{t.src=src}t.onload=ok;t.onerror=ko;document.head.appendChild(t)});
const it=d=>d?d.split('-').reverse().join('/'):'';
let pronto=null;
const carica=()=>pronto||(pronto=load('https://bookingcalendar.mainapps.com/css/ml-calendar-bol.css',1)
  .then(()=>load('https://bookingcalendar.mainapps.com/js/jquery-2.1.4.min.js'))
  .then(()=>{window.$jma=jQuery.noConflict(true)})
  .then(()=>load('https://bookingcalendar.mainapps.com/js/safe/ml-calendar-bol.js')));
const avvia=()=>{const d=sec.dataset,now=new Date(),n=innerWidth<760?1:2;
  const b=document.getElementById('cal-prenota'),nb=b.cloneNode(true);b.replaceWith(nb);
  box.innerHTML='';sel&&(sel.textContent='Selezionate arrivo e partenza');
  $jma('#ml-cal').mlCalendar({apikey:'"""+APIKEY+"""',language:document.documentElement.lang==='en'?'en':'it',
    resourceID:+d.res,realGroupID:+d.grp,year:now.getFullYear(),month:now.getMonth()+1,calNumber:n,cols:n,
    calWrapper:'ml-m',startDay:1,scrollMonths:1,minYear:now.getFullYear(),minMonth:now.getMonth()+1,
    dataStart:null,dataEnd:null,dateFormat:'dd/mm/yyyy',pax:Math.min(2,+d.max),minPax:1,maxPax:+d.max,
    allowChildren:false,maxAge:17,submitSelector:'#cal-prenota',toolbar:1,monthTitle:1,legend:1,clickable:1,
    labels:{checkIn:'Arrivo',checkOut:'Partenza',nights:'Notti',book:'Prenota',pax:'Ospiti',children:'Bambini',childrenAge:'Età',
      selectable:'Libero',notSelectable:'Non selezionabile',notAvailable:'Occupato',legend:'Legenda'},
    onChange:(f,t,p)=>{if(!sel)return;sel.textContent=f&&t?('Dal '+it(f)+' al '+it(t)+(p?' · '+p+' ospiti':'')):f?('Arrivo '+it(f)+' · scegliete la partenza'):'Selezionate arrivo e partenza'}})};
const errore=()=>{box.innerHTML='<p class="cal-wait">Il calendario non si è caricato. Scriveteci su <a href="""+'"'+WA+'"'+""">WhatsApp</a> per verificare le date.</p>'};
const go=()=>carica().then(avvia).catch(errore);
document.querySelectorAll('.cal-tabs button').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('.cal-tabs button').forEach(x=>x.setAttribute('aria-pressed',x===t));
  Object.assign(sec.dataset,{res:t.dataset.res,grp:t.dataset.grp,max:t.dataset.max});history.replaceState(null,'','#'+t.dataset.k);go()}));
const k=location.hash.slice(1),tab=document.querySelector('.cal-tabs [data-k="'+k+'"]');if(tab){tab.click();return}
if(!('IntersectionObserver' in window)){go();return}
const io=new IntersectionObserver(es=>{if(es.some(x=>x.isIntersecting)){io.disconnect();go()}},{rootMargin:'600px'});io.observe(sec)})();</script>"""

def sezione_calendario(chiave, kicker="Disponibilità", titolo="Scegliete le vostre date", testo=None, tabs=""):
    res, grp, mx, nome, _ = ALLOGGI[chiave]
    testo = testo or (f"Il calendario mostra in tempo reale le notti libere del {nome}. Selezionate arrivo e partenza, "
                      "poi «Prenota»: la prenotazione si conclude sul portale sicuro della Dimora, senza commissioni.")
    return (f'<section class="cal-sec" id="calendario" data-res="{res}" data-grp="{grp}" data-max="{mx}">'
            f'<div class="cal-head"><span class="k">{e(kicker)}</span><h2>{e(titolo)}</h2><p>{e(testo)}</p></div>{tabs}'
            '<div class="cal-box"><div id="ml-cal" class="ml-cal"><p class="cal-wait">Caricamento del calendario…</p></div>'
            '<button type="button" id="cal-prenota" hidden></button></div>'
            f'<p class="cal-alt">Preferite parlarne con noi? <a href="{WA}">WhatsApp</a> · <a href="tel:{TEL.replace(" ", "")}">{TEL}</a></p>'
            '</section>\n' + LOADER)

def comune(s, attivo=False):
    s = re.sub(r'<style id="prenota-css">.*?</style>\n?', '', s, flags=re.S).replace('</head>', CSS + '\n</head>', 1)
    cur = ' aria-current="page"' if attivo else ''
    btn = f'<a class="btn-prenota" href="/prenota"{cur}>Prenota</a>'
    s = re.sub(r'<!--pb-->.*?<!--/pb-->', '', s, flags=re.S)
    return re.sub(r'(<nav class="topnav".*?</nav>)', lambda m: m.group(1) + f'<!--pb-->{btn}<!--/pb-->', s, count=1, flags=re.S)

# ------------------------------------------------------------------ pagine alloggio
LINK_INTERA = (f'<!--li--><a href="/la-dimora-intera" style="text-decoration:none;display:flex;justify-content:space-between;'
               f'padding:18px 0;border-top:1px solid rgba(239,232,220,.18);{SERIF};font-size:18px;text-transform:uppercase;'
               'letter-spacing:.08em;color:#E2B76A"><span>La Dimora intera · 4 ospiti</span><span aria-hidden="true">→</span></a><!--/li-->')

def alloggio(p, chiave):
    s = comune(rd(p))
    s = blocco(s, "cal", "\n" + sezione_calendario(chiave) + "\n", "<!--dimore-->" if "<!--dimore-->" in s else "  <footer")
    s = s.replace(f'<a href="{WA}" style="text-decoration:none;background:#D4A65A', '<a href="#calendario" style="text-decoration:none;background:#D4A65A', 1)
    s = re.sub(r'<!--li-->.*?<!--/li-->', '', s, flags=re.S)
    if chiave in ("loft", "suite"):
        s = re.sub(r'(</a>)(\s*</aside>)', lambda m: m.group(1) + LINK_INTERA + m.group(2), s, count=1)
    wr(p, s)

# ------------------------------------------------------------------ template pagine nuove
def pagina(slug, title, desc, og_img, ld, hero_img, hero_alt, kicker, h1, body, extra_css="", hero_h="min(560px,70vh)"):
    tpl = rd("loft-dell-antiquario.html")
    for t in ["dimore", "cal", "pb", "li"]:
        tpl = re.sub(rf'\n?<!--{t}-->.*?<!--/{t}-->\n?', '\n' if t in ("dimore", "cal") else '', tpl, flags=re.S)
    tpl = re.sub(r'<script>\(\(\)=>\{const box=document.getElementById\(\'ml-cal\'\).*?</script>\n?', '', tpl, flags=re.S)
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
    header = re.search(r'    <header.*?</header>', tpl, flags=re.S).group(0).replace('src="img/', 'src="/img/').replace(' aria-current="page"', '')
    hero_html = f"""  <section style="position:relative;min-height:{hero_h};overflow:hidden;display:flex;flex-direction:column">
    <img class="heroimg" src="{hero_img}" alt="{e(hero_alt)}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.75">
    <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,17,26,.75) 0%,rgba(15,17,26,.25) 35%,#0F111A 100%)"></div>
{header}
    <div style="position:relative;flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:16px;padding:0 clamp(20px,4.5vw,64px) 56px">
      <span class="fd" style="font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#D4A65A">{e(kicker)}</span>
      <h1 class="h1a" style="margin:0;{SERIF};font-weight:400;font-size:clamp(26px,4.6vw,64px);line-height:1.15;text-transform:uppercase;letter-spacing:.08em">{e(h1)}</h1>
    </div>
  </section>"""
    return h + tpl[head_end:hero] + hero_html + "\n" + body + "\n" + tpl[foot:]

INTERA_CSS = """
.intera{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(420px,100%),1fr));gap:clamp(40px,6vw,96px);padding:96px clamp(20px,4.5vw,64px) 40px}
.intera p{margin:0 0 22px;font-size:17px;line-height:1.8;color:rgba(239,232,220,.82)}
.intera .q{font-family:'Bodoni Moda',Georgia,serif;font-style:italic;font-size:clamp(18px,1.9vw,25px);line-height:1.5;color:#E2B76A;text-transform:uppercase;letter-spacing:.07em}
.coppia{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:24px;align-content:start}
.coppia a{display:block;text-decoration:none;color:#EFE8DC}
.coppia img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;filter:saturate(.95)}
.coppia span{display:block;margin-top:14px;font-size:11px;letter-spacing:.26em;text-transform:uppercase}
.coppia b{display:block;margin-top:6px;font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:20px;text-transform:uppercase;letter-spacing:.08em}
.coppia .loft span{color:#8FA2E6}.coppia .suite span{color:#D4A65A}
"""

def la_dimora_intera():
    desc = ("La Dimora intera: il Loft dell'Antiquario e la Suite del Viaggiatore prenotati insieme, fino a 4 ospiti, "
            "nel centro storico di Tempio Pausania. Ideale per famiglie e amici. Prenota direttamente.")
    ld = {"@context": "https://schema.org", "@type": "Accommodation", "name": "La Dimora intera — Loft dell'Antiquario e Suite del Viaggiatore",
          "description": desc, "url": f"{BASE}/la-dimora-intera", "image": f"{BASE}/img/foto/est-02.webp",
          "address": {"@type": "PostalAddress", "streetAddress": "Piazza Eleonora d'Arborea 6", "addressLocality": "Tempio Pausania",
                      "postalCode": "07029", "addressRegion": "SS", "addressCountry": "IT"},
          "containedInPlace": {"@type": "LodgingBusiness", "name": "Dimora delle Storie", "url": BASE},
          "floorSize": {"@type": "QuantitativeValue", "value": 70, "unitCode": "MTK"},
          "occupancy": {"@type": "QuantitativeValue", "maxValue": 4}}
    body = f"""  <main class="intera">
    <div>
      <p class="q reveal">«Due storie sotto lo stesso tetto: il velluto blu dell'Antiquario e la sabbia e oro del Viaggiatore.»</p>
      <p class="reveal">Per chi viaggia in quattro, la Dimora si prenota tutta insieme: il Loft dell'Antiquario all'ultimo piano e la Suite del Viaggiatore al primo, due case complete con il proprio bagno, nello stesso palazzo del 1930 nel cuore del centro storico.</p>
      <p class="reveal">È la soluzione per una famiglia, per due coppie di amici o per chi desidera la Dimora tutta per sé, con la tranquillità di non dividere la casa con altri ospiti.</p>
      <div class="reveal" style="display:flex;flex-wrap:wrap;gap:14px;margin-top:12px">
        <a href="#calendario" style="text-decoration:none;background:#D4A65A;color:#0F111A;border-radius:999px;padding:18px 32px;font-size:13px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center">Verifica disponibilità</a>
        <a href="/la-dimora" style="text-decoration:none;border:1px solid rgba(255,255,255,.24);border-radius:999px;padding:18px 32px;font-size:13px;letter-spacing:.14em;text-transform:uppercase;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center">Scoprite la casa</a>
      </div>
    </div>
    <div class="coppia">
      <a class="loft reveal" href="/loft-dell-antiquario"><img src="/img/foto/loft-01.webp" alt="Loft dell'Antiquario, la parete delle peonie blu" loading="lazy"><span>Ultimo piano · 45 mq · 2 ospiti</span><b>Loft dell'Antiquario →</b></a>
      <a class="suite reveal" href="/suite-del-viaggiatore"><img src="/img/foto/suite-01.webp" alt="Suite del Viaggiatore, la testiera sabbia e oro" loading="lazy"><span>Primo piano · 25 mq · 2 ospiti</span><b>Suite del Viaggiatore →</b></a>
    </div>
  </main>
{sezione_calendario("intera", titolo="Le date per la Dimora intera", testo="Il calendario mostra le notti in cui Loft e Suite sono liberi insieme. Selezionate arrivo e partenza, poi «Prenota»: la prenotazione si conclude sul portale sicuro della Dimora, senza commissioni.")}"""
    s = pagina("la-dimora-intera", "La Dimora intera — Loft e Suite per 4 ospiti a Tempio Pausania", desc, "/img/foto/est-02.webp", ld,
               "/img/foto/est-02.webp", "La facciata della Dimora delle Storie, Tempio Pausania", "Loft + Suite · 70 mq · fino a 4 ospiti",
               "La Dimora intera", body, INTERA_CSS)
    wr("la-dimora-intera.html", comune(s))

SCHEDE = {  # chiave: (foto, dettagli)
    "loft": ("/img/loft.jpg", "Ultimo piano · 45 mq · 2 ospiti"),
    "suite": ("/img/suite.jpg", "Primo piano · 25 mq · 2 ospiti"),
    "latteria": ("/img/latteria.jpg", "Due livelli · 38 mq · 2 ospiti"),
    "intera": ("/img/foto/est-02.webp", "Loft + Suite · 70 mq · fino a 4 ospiti"),
}

CERCA_CSS = """
.cerca{padding:clamp(36px,5vw,64px) clamp(20px,4.5vw,64px) clamp(80px,9vw,120px)}
.cerca-form{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(200px,100%),1fr));gap:18px;align-items:end;padding:clamp(20px,3vw,36px);border:1px solid rgba(226,183,106,.3);background:linear-gradient(180deg,rgba(15,17,40,.72),rgba(15,17,40,.42));box-shadow:0 30px 80px rgba(0,0,0,.4)}
.cerca-form label{display:block;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:rgba(239,232,220,.7)}
.cerca-form input,.cerca-form select{display:block;width:100%;box-sizing:border-box;margin-top:10px;min-height:52px;padding:0 16px;border:1px solid rgba(239,232,220,.25);border-radius:2px;background:rgba(5,7,20,.6);color:#EFE8DC;font:16px 'Inter',system-ui,sans-serif;color-scheme:dark}
.cerca-form input:focus,.cerca-form select:focus{outline:none;border-color:#D4A65A;box-shadow:0 0 0 3px rgba(212,166,90,.18)}
.cerca-form option{background:#0F111A}
.cerca-form button{min-height:52px;border:0;border-radius:999px;background:#D4A65A;color:#0F111A;font:500 13px 'Inter',system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase;cursor:pointer}
.cerca-form button:hover{background:#E2B76A}
.cerca-msg{min-height:24px;margin:22px 0 0;font-size:14px;letter-spacing:.06em;color:#E2B76A}
.esiti{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:24px;margin-top:20px}
.esito{display:flex;flex-direction:column;border:1px solid rgba(239,232,220,.14);background:rgba(15,17,26,.55);transition:opacity .3s}
.esito img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}
.esito .c{display:flex;flex-direction:column;gap:10px;flex:1;padding:22px}
.esito .d{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:rgba(239,232,220,.6)}
.esito h3{margin:0;font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:21px;text-transform:uppercase;letter-spacing:.08em}
.esito .s{margin:auto 0 0;padding-top:12px;font-size:13px;letter-spacing:.1em;text-transform:uppercase}
.esito .s.ok{color:#E2B76A}.esito .s.no{color:rgba(239,232,220,.55)}
.esito a.p{display:inline-flex;align-items:center;justify-content:center;min-height:48px;margin-top:6px;border-radius:999px;background:#D4A65A;color:#0F111A;text-decoration:none;font:500 12px 'Inter',system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase}
.esito a.p:hover{background:#E2B76A}
.esito a.v{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:rgba(239,232,220,.7)}
.esito.off{opacity:.5}
.esito .prezzo{margin:0;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:rgba(239,232,220,.7)}
.esito .prezzo b{display:block;margin-bottom:2px;font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:28px;letter-spacing:.04em;color:#EFE8DC}
"""

def cerca_js():
    dati = json.dumps({k: {"res": v[0], "grp": v[1], "max": v[2], "nome": v[3], "url": v[4], "foto": SCHEDE[k][0], "det": SCHEDE[k][1]}
                       for k, v in ALLOGGI.items()}, ensure_ascii=False)
    return """<script>(()=>{const D=""" + dati + """,K='""" + APIKEY + """',API='https://adm.mainapps.com/api/booking/';
const f=document.getElementById('cerca'),out=document.getElementById('esiti'),msg=document.getElementById('cerca-msg');if(!f)return;
const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const giorno=s=>{const[a,b,c]=s.split('-').map(Number);return new Date(a,b-1,c)};
const it=s=>s.split('-').reverse().join('/');
const oggi=iso(new Date()),lim=new Date();lim.setFullYear(lim.getFullYear()+2);const max=iso(lim);f.arrivo.min=oggi;f.arrivo.max=max;f.partenza.max=max;
const valida=v=>/^\\d{4}-\\d{2}-\\d{2}$/.test(v)&&v>=oggi&&v<=max;
f.arrivo.addEventListener('change',()=>{if(!valida(f.arrivo.value))return;const m=giorno(f.arrivo.value);m.setDate(m.getDate()+1);f.partenza.min=iso(m);
  if(!f.partenza.value||f.partenza.value<=f.arrivo.value){m.setDate(m.getDate()+1);f.partenza.value=iso(m)}});
const notti=(a,b)=>{const L=[];for(let d=giorno(a);iso(d)<b;d.setDate(d.getDate()+1))L.push(iso(d));return L};
async function occupate(r,a,b){const da=giorno(a),ul=giorno(b);ul.setDate(ul.getDate()-1);
  const n=(ul.getFullYear()-da.getFullYear())*12+ul.getMonth()-da.getMonth()+1;
  const p=new URLSearchParams({apikey:K,language:'it',resourceID:r.res,realGroupID:r.grp,year:da.getFullYear(),month:da.getMonth()+1,calNumber:n,cols:n,startDay:1,
    minMonth:da.getMonth()+1,minYear:da.getFullYear(),maxMonth:12,maxYear:da.getFullYear()+2,dateFormat:'dd/mm/yyyy',pax:2,legend:0,toolbar:0,monthTitle:0,clickable:1});
  let h=await (await fetch(API+'LoadCalendar',{method:'POST',body:p})).text();try{h=JSON.parse(h)}catch(e){}
  const doc=new DOMParser().parseFromString(h,'text/html'),S=new Set();
  doc.querySelectorAll('button.cal-day[data-date]').forEach(x=>{const c=x.classList;if(c.contains('cal-day-block-booking')&&(!c.contains('cal-day-block-booking-last')||c.contains('cal-day-block-booking-first')))S.add(x.dataset.date)});
  return S}
async function minimo(r,a){try{const R=await (await fetch(API+'GetBookingRestriction?apikey='+K,{method:'POST',body:new URLSearchParams({FromDate:a,ToDate:a,ResourceID:r.res})})).json();
  const v=(R||[]).find(x=>x.StartDate.slice(0,10)<=a&&x.EndDate.slice(0,10)>=a);return v&&v.MinMinutes?Math.ceil(v.MinMinutes/1440):1}catch(e){return 1}}
const scheda=(r,stato,ok,link,pr)=>'<article class="esito'+(ok?'':' off')+'"><img src="'+r.foto+'" alt="'+r.nome+'" loading="lazy"><div class="c"><span class="d">'+r.det+'</span><h3>'+r.nome+'</h3>'
  +'<p class="s '+(ok?'ok':'no')+'">'+stato+'</p>'+(ok&&pr?'<p class="prezzo"><b>€ '+pr.totale.toLocaleString('it-IT')+'</b> totale, pulizia inclusa</p>':'')+(ok?'<a class="p" href="'+link+'">Prenota</a>':'')+'<a class="v" href="'+r.url+'">Scopri la dimora →</a></div></article>';
f.addEventListener('submit',async ev=>{ev.preventDefault();const a=f.arrivo.value,b=f.partenza.value,px=+f.ospiti.value;
  if(!a||!b){msg.textContent='Indicate le date di arrivo e di partenza.';return}
  if(b<=a){msg.textContent='La partenza deve essere successiva all\\'arrivo.';return}
  if(a<oggi){msg.textContent='La data di arrivo è già passata.';return}
  if(!valida(a)||!valida(b)){msg.textContent='Controllate l\\'anno delle date: si può prenotare fino al '+it(max)+'.';out.innerHTML='';return}
  const N=notti(a,b);msg.textContent='Verifico le disponibilità…';out.innerHTML='';
  history.replaceState(null,'','?arrivo='+a+'&partenza='+b+'&ospiti='+px);
  const P=fetch('/api/preventivo?arrivo='+a+'&partenza='+b+'&ospiti='+px).then(r=>r.ok?r.json():{}).then(j=>j.prezzi||{}).catch(()=>({}));
  try{const R=await Promise.all(Object.values(D).map(async r=>{
      if(px>r.max)return{r,ok:false,o:3,stato:'Fino a '+r.max+' ospiti'};
      const[S,mn]=await Promise.all([occupate(r,a,b),minimo(r,a)]);
      if(N.some(n=>S.has(n)))return{r,ok:false,o:2,stato:'Non disponibile in queste date'};
      if(N.length<mn)return{r,ok:false,o:1,stato:'Soggiorno minimo '+mn+' notti'};
      return{r,ok:true,o:0,stato:'Disponibile · '+N.length+(N.length==1?' notte':' notti'),
        link:'https://bol.mainapps.com/step2/'+r.res+'/'+a.replace(/-/g,'')+'-'+b.replace(/-/g,'')+'/'+px+'/nc/?apikey='+K+'&lang=it'}}));
    R.sort((x,y)=>x.o-y.o);const liberi=R.filter(x=>x.ok).length;
    msg.textContent=(liberi?(liberi==1?'Una dimora libera':liberi+' dimore libere'):'Nessuna dimora libera')+' dal '+it(a)+' al '+it(b)+' per '+px+(px==1?' ospite':' ospiti')+'.'+(liberi?'':(R.some(x=>x.o==1)&&!R.some(x=>x.o==2)?' In questo periodo il soggiorno minimo è di '+Math.max(...R.filter(x=>x.o==1).map(x=>+x.stato.match(/\\d+/)[0]))+' notti.':' Provate altre date o scriveteci: troveremo una soluzione.'));
    const PR=await P;out.innerHTML=R.map(x=>scheda(x.r,x.stato,x.ok,x.link,PR[x.r.res])).join('')}
  catch(e){msg.innerHTML='Non riusciamo a verificare le disponibilità in questo momento. Scriveteci su <a href=\""""+WA+"""\" style="color:#E2B76A">WhatsApp</a>.'}});
const q=new URLSearchParams(location.search);if(q.get('arrivo')){f.arrivo.value=q.get('arrivo');f.partenza.value=q.get('partenza')||'';if(q.get('ospiti'))f.ospiti.value=q.get('ospiti');f.requestSubmit()}})();</script>"""

def prenota():
    body = f"""  <main class="cerca">
    <div class="cal-head"><span class="k">Prenotazione diretta</span><h2>Quando arrivate?</h2><p>Indicate le date e il numero di ospiti: vi mostriamo subito quali dimore sono libere. Prenotando qui, direttamente con noi, non pagate commissioni.</p></div>
    <form class="cerca-form" id="cerca" novalidate>
      <label>Arrivo<input type="date" name="arrivo" required></label>
      <label>Partenza<input type="date" name="partenza" required></label>
      <label>Ospiti<select name="ospiti"><option value="1">1 ospite</option><option value="2" selected>2 ospiti</option><option value="3">3 ospiti</option><option value="4">4 ospiti</option></select></label>
      <button type="submit">Verifica disponibilità</button>
    </form>
    <p class="cerca-msg" id="cerca-msg" aria-live="polite"></p>
    <div class="esiti" id="esiti"></div>
    <p class="cal-alt">Preferite parlarne con noi? <a href="{WA}">WhatsApp</a> · <a href="tel:{TEL.replace(" ", "")}">{TEL}</a></p>
  </main>
{cerca_js()}"""
    desc = "Prenota direttamente alla Dimora delle Storie, Tempio Pausania: scegli le date e vedi subito le dimore libere tra Loft dell'Antiquario, Suite del Viaggiatore, Antica Latteria 1930 e la Dimora intera."
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Prenota — Dimora delle Storie", "url": f"{BASE}/prenota", "description": desc}
    s = pagina("prenota", "Prenota — Dimora delle Storie, Tempio Pausania", desc, "/img/loft.jpg", ld, "/img/loft.jpg",
               "Loft dell'Antiquario, Dimora delle Storie", "Prenotazione diretta · senza commissioni", "Prenota il tuo soggiorno", body, CERCA_CSS, hero_h="min(360px,46vh)")
    wr("prenota.html", comune(s, attivo=True))

# ------------------------------------------------------------------ home: collegamenti rimasti vuoti
LAB = "display:flex;flex-direction:column;gap:6px;padding:18px 24px;border-right:1px solid rgba(239,232,220,.18);font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:rgba(239,232,220,.78)"
INP = "background:transparent;border:0;color:#EFE8DC;font:300 16px 'Inter',sans-serif;padding:0;outline:none;color-scheme:dark;min-height:24px;width:100%"
APRI = "this.type='date';try{this.showPicker()}catch(e){}"
BOOKBAR = ('<label style="' + LAB + '">Arrivo<input type="text" name="arrivo" placeholder="Seleziona data" onfocus="' + APRI + '" style="' + INP + '"></label>'
           '<label style="' + LAB + '">Partenza<input type="text" name="partenza" placeholder="Seleziona data" onfocus="' + APRI + '" style="' + INP + '"></label>'
           '<label style="' + LAB + '">Ospiti<select name="ospiti" style="' + INP + ';cursor:pointer;-webkit-appearance:none;appearance:none">'
           '<option value="1" style="background:#0F111A">1 ospite</option><option value="2" selected style="background:#0F111A">2 ospiti</option>'
           '<option value="3" style="background:#0F111A">3 ospiti</option><option value="4" style="background:#0F111A">4 ospiti</option></select></label>'
           '<button type="submit" style="border:0;background:#D4A65A;color:#0F111A;font:500 13px \'Inter\',sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:20px 40px;cursor:pointer;min-height:56px">Verifica disponibilità</button>')
BOOKBAR_JS = """<!--bbjs--><script>(()=>{const f=document.querySelector('form.bookbar');if(!f)return;const a=f.arrivo,b=f.partenza;
const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');a.min=iso(new Date());
a.addEventListener('change',()=>{if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(a.value))return;const[y,m,d]=a.value.split('-').map(Number),n=new Date(y,m-1,d+1);b.type='date';b.min=iso(n);if(!b.value||b.value<=a.value){n.setDate(n.getDate()+1);b.value=iso(n)}});
f.addEventListener('submit',ev=>{if(!a.value||!b.value){ev.preventDefault();(a.value?b:a).focus()}})})();</script><!--/bbjs-->"""

def home():
    s = comune(rd("index.html"))
    s = re.sub(r'(<form class="fd bookbar")[^>]*?(style="[^"]*")>.*?</form>',
               lambda m: m.group(1) + ' action="/prenota" method="get" ' + m.group(2) + '>' + "\n      " + BOOKBAR + "\n    </form>", s, count=1, flags=re.S)
    s = re.sub(r'<!--bbjs-->.*?<!--/bbjs-->\n?', '', s, flags=re.S).replace('</body>', BOOKBAR_JS + '\n</body>', 1)
    for testo, href in [("Verifica disponibilità", "/prenota"), ("Scrivici su WhatsApp", WA), (TEL, "tel:+393791656864"),
                        ("info@dimoradellestorie.com", "mailto:info@dimoradellestorie.com"),
                        ("Instagram · @dimoradellestorie", "https://www.instagram.com/dimoradellestorie")]:
        s = re.sub(r'<a href="#"([^>]*>)' + re.escape(e(testo, quote=False)) + '</a>', lambda m: f'<a href="{href}"{m.group(1)}{e(testo, quote=False)}</a>', s)
    wr("index.html", s)

def sitemap():
    sm = rd("sitemap.xml")
    if "/la-dimora-intera<" not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{BASE}/la-dimora-intera</loc><lastmod>2026-11-23</lastmod></url>\n</urlset>")
    if "/prenota<" not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{BASE}/prenota</loc><lastmod>2026-11-23</lastmod></url>\n</urlset>")
    wr("sitemap.xml", sm)

ESTERNI_CSS = """<style id="esterni-css">
.esterni{position:relative;padding:clamp(64px,8vw,120px) clamp(20px,4.5vw,64px);overflow:hidden;border-top:1px solid rgba(239,232,220,.1)}
.esterni .t{max-width:440px;margin:0 0 40px}
.esterni .t span{display:block;margin-bottom:12px;font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:#D4A65A}
.esterni .t h2{margin:0 0 14px;font-family:'Bodoni Moda',Georgia,serif;font-weight:400;font-size:clamp(22px,2.6vw,34px);line-height:1.25;text-transform:uppercase;letter-spacing:.08em}
.esterni .t p{margin:0 0 16px;font-size:15px;line-height:1.8;color:rgba(239,232,220,.75)}
.esterni .t a{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#E2B76A}
.esterni .f{display:grid;grid-template-columns:1.1fr .8fr 1.3fr;gap:clamp(12px,2vw,28px);align-items:start}
.esterni figure{margin:0;position:relative}
.esterni img{display:block;width:100%;object-fit:cover;box-shadow:0 30px 70px rgba(0,0,0,.45)}
.esterni figure:nth-child(1) img{aspect-ratio:3/4;object-position:center 30%}
.esterni figure:nth-child(2){margin-top:clamp(60px,9vw,140px)}
.esterni figure:nth-child(2) img{aspect-ratio:1/1}
.esterni figure:nth-child(3){margin-top:clamp(20px,3vw,40px)}
.esterni figure:nth-child(3) img{aspect-ratio:4/5;clip-path:inset(0 0 0 0 round 0)}
.esterni figcaption{margin-top:12px;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:rgba(239,232,220,.55)}
#dimore:has(+ #esterni),body:has(.esterni-home) #dimore{padding-bottom:40px!important}
.esterni-home{border-top:0;padding-top:40px;padding-bottom:clamp(100px,10vw,160px)}
@media (min-width:900px){.esterni{display:grid;grid-template-columns:minmax(260px,.7fr) 2fr;gap:clamp(40px,5vw,80px);align-items:center}.esterni .t{margin:0}}
@media (max-width:600px){.esterni .f{grid-template-columns:1fr 1fr}.esterni figure:nth-child(3){grid-column:1/-1;margin-top:0}.esterni figure:nth-child(3) img{aspect-ratio:16/10}.esterni figure:nth-child(2){margin-top:48px}}
</style>"""

ESTERNI = {  # pagina: (titolo, testo, [(foto, didascalia) x3])
    "dimora": ("Due palazzetti, uno di fronte all'altro",
               "La Dimora e l'Antica Latteria si guardano attraverso un vicolo di granito del centro storico: facciate bianche, portoni azzurri, balconi in ferro battuto.",
               [("g-home-facciata", "La facciata della Dimora"), ("g-est-02", "Il vicolo"), ("g-latf-01", "La palazzina della Latteria, di fronte")]),
    "latteria": ("La palazzina della Latteria",
                 "Di fronte alla Dimora, con la stessa facciata bianca e lo stesso portone azzurro: qui nel 1930 si vendeva davvero il latte.",
                 [("g-latf-01", "La facciata della Latteria"), ("g-latf-02", "La Latteria nel vicolo"), ("g-est-01", "La Dimora, di fronte")]),
}
PAGINE_ESTERNI = {"index.html": "dimora", "loft-dell-antiquario.html": "dimora", "suite-del-viaggiatore.html": "dimora",
                  "antica-latteria-1930.html": "latteria", "la-dimora-intera.html": "dimora", "prenota.html": "dimora"}

def esterni(p, k):
    tit, txt, foto = ESTERNI[k]
    figs = "".join(f'<figure class="reveal"><img src="/img/foto/{f}.webp" alt="{e(c)} — Dimora delle Storie, Tempio Pausania" loading="lazy" decoding="async"><figcaption>{e(c)}</figcaption></figure>' for f, c in foto)
    blk = (f'<section class="esterni"><div class="t reveal"><span>Gli esterni</span><h2>{e(tit)}</h2><p>{e(txt)}</p>'
           f'<a href="/la-dimora">Scoprite la casa →</a></div><div class="f">{figs}</div></section>\n')
    s = rd(p)
    s = re.sub(r'<style id="esterni-css">.*?</style>\n?', '', s, flags=re.S).replace('</head>', ESTERNI_CSS + '\n</head>', 1)
    dove = '  <section id="storie"' if p == "index.html" else "  <footer"
    if p == "index.html": blk = blk.replace('<section class="esterni">', '<section class="esterni esterni-home" id="esterni">')
    wr(p, blocco(s, "est", blk, dove))

if __name__ == "__main__":
    for p, k in PAGINE_ALLOGGIO.items(): alloggio(p, k)
    la_dimora_intera(); prenota(); home(); sitemap()
    for p, k in PAGINE_ESTERNI.items(): esterni(p, k)
    fatte = set(PAGINE_ALLOGGIO) | {"index.html", "la-dimora-intera.html", "prenota.html"}
    for p in [os.path.basename(x) for x in glob.glob(f"{SITE}/*.html")] + [os.path.relpath(x, SITE) for x in glob.glob(f"{SITE}/storie/*.html")]:
        if p not in fatte: wr(p, comune(rd(p)))
    import subprocess; subprocess.run([sys.executable, "-B", f"{SITE}/tools/seo.py"], check=True, stdout=subprocess.DEVNULL)  # ultimo passaggio SEO
    print("ok")
