#!/usr/bin/env python3
"""Genera /tempio-pausania: video del drone (in arrivo) + guida della città."""
import os, sys, json, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import storie as S  # riusa testa, menu, piede e stili

SITE, BASE, e, SERIF = S.SITE, S.BASE, S.e, S.SERIF
VIDEO = "/img/tempio-drone.mp4"           # da caricare quando arriva il file
HAS_VIDEO = os.path.exists(SITE + VIDEO)

VEDERE = [
    ("Piazza San Pietro", "La Cattedrale, nata all'inizio del Duecento e riconsacrata nel 1839, l'Oratorio di Santa Croce e quello del Rosario: il cuore religioso della città."),
    ("Teatro del Carmine", "Il piccolo, elegante teatro cittadino, affacciato sulla stessa piazza."),
    ("Piazza Faber", "Dedicata a Fabrizio De André, con l'installazione progettata da Renzo Piano."),
    ("Fonti di Rinaggiu", "In fondo al viale alberato di Fonte Nuova, sorgenti note fin dall'epoca romana."),
    ("I palazzi di granito", "Facciate in blocchi di pietra grigia, in gran parte settecentesche: per questo Tempio è la «Città di pietra»."),
    ("La suppa cuata", "Il piatto simbolo della cucina gallurese, da assaggiare nei locali del centro."),
]
DINTORNI = [
    ("Monte Limbara", "Alle spalle della città. La cima di Punta Balistreri arriva a 1.359 metri; il sentiero «la sommità», lungo 12 km, attraversa i boschi e il giardino del Pavari."),
    ("Il mare della Gallura", "Le spiagge del nord Sardegna sono in media a una cinquantina di chilometri: si raggiungono in giornata."),
    ("Carrasciali Timpiesu", "A febbraio il Carnevale storico tempiese riempie le piazze del centro."),
]
ARRIVO = [
    ("In aereo", "Olbia Costa Smeralda è l'aeroporto più vicino, a circa 50 km (poco meno di un'ora in auto). Alghero è a circa 100 km."),
    ("In nave", "I porti di Olbia e Golfo Aranci sono a meno di un'ora di strada."),
    ("In autobus", "La linea ARST 602 collega Olbia e Tempio in circa un'ora e venti: verificate gli orari sul sito ARST."),
]

CSS = '''
@media (max-width:440px){.topnav{gap:16px!important;padding:10px 16px!important;font-size:12px!important}}
.t-hero{position:relative;min-height:100svh;overflow:hidden;display:flex;flex-direction:column}
.t-hero video,.t-hero .t-ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.t-ph{background:radial-gradient(60% 50% at 50% 45%,rgba(150,170,240,.16),rgba(0,0,0,0) 70%)}
.t-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,10,24,.6) 0%,rgba(8,10,24,.1) 35%,rgba(8,10,24,.35) 70%,rgba(11,14,34,.95) 100%);pointer-events:none}
.t-hero>*{position:relative;z-index:1}
.t-title{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;text-align:center;gap:16px;padding:0 20px 14vh}
.t-k{font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:#8FA2E6}
.t-h1{margin:0;'''+SERIF+''';font-weight:400;font-size:clamp(30px,5.4vw,78px);line-height:1.1;letter-spacing:.1em;text-transform:uppercase;font-variation-settings:'opsz' 11;text-shadow:0 4px 40px rgba(0,0,0,.6)}
.t-sub{margin:0;'''+SERIF+''';font-style:italic;text-transform:uppercase;letter-spacing:.12em;font-size:clamp(12px,1.2vw,15px);color:rgba(239,232,220,.8);font-variation-settings:'opsz' 11}
.t-soon{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:rgba(239,232,220,.5);border:1px solid rgba(239,232,220,.18);border-radius:999px;padding:8px 16px}
.t-scroll{width:1px;height:64px;background:linear-gradient(#E2B76A,rgba(226,183,106,0));margin-top:20px;animation:tScroll 2.4s ease-in-out infinite}
@keyframes tScroll{0%{transform:scaleY(0);transform-origin:top}50%{transform:scaleY(1);transform-origin:top}51%{transform-origin:bottom}100%{transform:scaleY(0);transform-origin:bottom}}
.t-sec{padding:clamp(80px,11vw,150px) clamp(20px,4.5vw,64px);max-width:1240px;margin:0 auto}
.t-sec h2{margin:0 0 14px;'''+SERIF+''';font-weight:400;font-size:clamp(22px,2.6vw,36px);letter-spacing:.09em;text-transform:uppercase;line-height:1.2;font-variation-settings:'opsz' 11}
.t-sec .lead{margin:0 0 48px;max-width:62ch;font-size:17px;line-height:1.8;color:rgba(239,232,220,.78)}
.t-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));gap:1px;background:rgba(239,232,220,.12);border:1px solid rgba(239,232,220,.12)}
.t-card{background:rgba(9,12,32,.72);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);padding:34px 30px;display:flex;flex-direction:column;gap:12px;transition:background .5s}
.t-card:hover{background:rgba(18,27,82,.78)}
.t-card .n{'''+SERIF+''';color:#E2B76A;font-size:14px;letter-spacing:.1em}
.t-card h3{margin:0;'''+SERIF+''';font-weight:400;font-size:19px;letter-spacing:.08em;text-transform:uppercase;font-variation-settings:'opsz' 11}
.t-card p{margin:0;font-size:15px;line-height:1.75;color:rgba(239,232,220,.74)}
.t-band{background:linear-gradient(180deg,rgba(6,8,22,0),rgba(6,8,22,.75) 18%,rgba(6,8,22,.75) 82%,rgba(6,8,22,0))}
.t-rows{display:flex;flex-direction:column}
.t-row{display:grid;grid-template-columns:minmax(140px,220px) 1fr;gap:24px;padding:26px 0;border-top:1px solid rgba(239,232,220,.14)}
.t-row h3{margin:0;'''+SERIF+''';font-weight:400;font-size:16px;letter-spacing:.12em;text-transform:uppercase;color:#E2B76A}
.t-row p{margin:0;font-size:16px;line-height:1.75;color:rgba(239,232,220,.8)}
@media (max-width:600px){.t-row{grid-template-columns:1fr;gap:8px}}
.t-story{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(380px,100%),1fr));gap:40px;align-items:center}
.t-story a.card{display:block;text-decoration:none;padding:34px;border:1px solid rgba(226,183,106,.35);background:rgba(9,12,32,.7);border-radius:3px}
.t-story a.card span{font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:#8FA2E6}
.t-story a.card strong{display:block;margin:12px 0;'''+SERIF+''';font-weight:400;font-size:22px;letter-spacing:.08em;text-transform:uppercase;font-variation-settings:'opsz' 11}
.t-story a.card em{font-style:normal;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#E2B76A}
.t-final{text-align:center;display:flex;flex-direction:column;align-items:center;gap:22px}
.t-final .frame{width:min(860px,100%);aspect-ratio:16/9;border:1px solid rgba(226,183,106,.4);outline:1px solid rgba(226,183,106,.15);outline-offset:8px;display:grid;place-items:center;
 background:linear-gradient(rgba(6,8,22,.55),rgba(6,8,22,.55)),url(/img/loft.jpg) center/cover}
.t-final .frame span{font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:rgba(239,232,220,.75)}
.t-btn{text-decoration:none;background:#D4A65A;color:#0F111A!important;border-radius:999px;padding:18px 34px;font-size:13px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center}
.t-src{font-size:13px;line-height:1.7;color:rgba(239,232,220,.55);padding-top:0!important}
.t-src a{color:rgba(239,232,220,.7)}
@media (prefers-reduced-motion:reduce){.t-scroll{animation:none}}
'''

def page():
    title = "Tempio Pausania: cosa vedere nella Città di pietra | Dimora delle Storie"
    desc = "Tempio Pausania, la Città di pietra ai piedi del Limbara: cosa vedere a piedi nel centro storico, i dintorni, come arrivare da Olbia e dove dormire."
    ld = {"@context": "https://schema.org", "@type": "TouristDestination", "name": "Tempio Pausania",
          "url": f"{BASE}/tempio-pausania", "description": desc,
          "touristType": ["Cultura", "Natura", "Enogastronomia"],
          "includesAttraction": [{"@type": "TouristAttraction", "name": n} for n, _ in VEDERE[:4]] + [{"@type": "TouristAttraction", "name": "Monte Limbara"}]}
    h = S.head(title, desc, f"{BASE}/tempio-pausania", "/img/loft.jpg", ld)
    h += f"<style>{CSS}</style>\n"
    if HAS_VIDEO:
        media = f'<video autoplay muted loop playsinline preload="metadata" poster="/img/tempio-drone.jpg" aria-label="Il centro storico di Tempio Pausania"><source src="{VIDEO}" type="video/mp4"></video>'
        soon = ""
    else:
        media = '<div class="t-ph" aria-hidden="true"></div>'
        soon = '<span class="t-soon">Il video del centro storico dal drone arriva presto</span>'
    cards = "".join(f'<article class="t-card"><span class="n">{i+1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, (t, d) in enumerate(VEDERE))
    dint = "".join(f'<article class="t-card"><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in DINTORNI)
    arr = "".join(f'<div class="t-row"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in ARRIVO)
    art = S.ARTICOLI[0]
    fonti = " · ".join(f'<a href="{u}" rel="noopener">{e(t)}</a>' for t, u in art["fonti"])
    body = f'''  <section class="t-hero">
    {media}
{S.header_html()}
    <div class="t-title">
      <span class="t-k">Gallura · Sardegna</span>
      <h1 class="t-h1">Tempio Pausania</h1>
      <p class="t-sub">La Città di pietra ai piedi del Limbara</p>
      {soon}
      <span class="t-scroll" aria-hidden="true"></span>
    </div>
  </section>
  <section class="t-sec">
    <h2>Cosa vedere a piedi</h2>
    <p class="lead">Tempio sorge su un altopiano di granito a circa 566 metri, e conta circa 14 mila abitanti. Il centro storico si gira tutto a piedi partendo dalla Dimora, in piazza Eleonora d'Arborea: la sera, con la luce dei lampioni sulle facciate di pietra, è il momento più bello.</p>
    <div class="t-grid">{cards}</div>
  </section>
  <div class="t-band"><section class="t-sec">
    <h2>Il Limbara e i dintorni</h2>
    <p class="lead">Tra montagna e mare: una base tranquilla per scoprire tutta la Gallura.</p>
    <div class="t-grid">{dint}</div>
  </section></div>
  <section class="t-sec">
    <h2>Come arrivare</h2>
    <div class="t-rows">{arr}</div>
  </section>
  <section class="t-sec t-story">
    <div><h2>Dal Libro delle Storie</h2><p class="lead" style="margin:0">Le storie di Tempio, dei suoi personaggi e della Gallura, da sfogliare come un libro antico.</p></div>
    <a class="card" href="/storie/{art["slug"]}"><span>Capitolo II · Storie di Tempio</span><strong>{e(art["titolo"])}</strong><em>Leggi la storia →</em></a>
  </section>
  <section class="t-sec t-final">
    <h2>Dalla città alla Dimora</h2>
    <div class="frame" aria-hidden="true"><span>Dal cielo della Gallura fino alla vostra stanza · video in arrivo</span></div>
    <p class="lead" style="margin:8px 0 0;text-align:center">Tre dimore in una residenza del 1930, nel cuore del centro storico.</p>
    <a class="t-btn" href="/prenota">Verifica disponibilità</a>
  </section>
  <section class="t-sec t-src"><p>Fonti: {fonti}</p></section>
'''
    return S.absolutize(h + S.BODY_OPEN + body + S.FOOT)

open(f"{SITE}/tempio-pausania.html", "w", encoding="utf-8").write(page())
print("tempio-pausania.html", "video:" , HAS_VIDEO)
