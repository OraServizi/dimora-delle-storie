#!/usr/bin/env python3
"""Ultimo passaggio SEO su tutte le pagine (idempotente).

- title e description brevi (Google taglia oltre ~60 / ~158 caratteri)
- og:url, og:site_name, twitter:card su ogni pagina
- dati strutturati della home arricchiti (CIN, prenotazione, mappa)
- sitemap.xml con tutte le pagine
- toglie il pulsante IT / EN finché non c'è la traduzione

Va lanciato dopo gli altri generatori: storie.py, tempio.py e prenota.py lo richiamano da soli.
Uso: python3 tools/seo.py
"""
import datetime, glob, html, json, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.dimoradellestorie.com"
NOME = "Dimora delle Storie"
CIN = "IT090070C2000S8992"
GSC = '<meta name="google-site-verification" content="jhGrYVoggbXWwPBEhrQ1hidz6IVTA56Iq5drewmk0Lc">'  # Search Console: non togliere
e = html.escape

# pagina: (title, description). Le pagine non elencate restano come le genera il loro script.
META = {
    "index.html": ("Case vacanze a Tempio Pausania | Dimora delle Storie",
                   "Tre case vacanze di charme nel centro storico di Tempio Pausania: Loft dell'Antiquario, Suite del Viaggiatore e Antica Latteria 1930. Prenota diretto."),
    "loft-dell-antiquario.html": ("Loft dell'Antiquario — casa vacanze a Tempio Pausania",
                   "Loft di 45 mq all'ultimo piano nel centro storico di Tempio Pausania: velluto blu, peonie dipinte, bagno di 9 mq. Per 2 persone. Prenota diretto."),
    "suite-del-viaggiatore.html": ("Suite del Viaggiatore — suite a Tempio Pausania",
                   "Suite di 25 mq nel centro storico di Tempio Pausania: sabbia e oro, bagno di 9 mq, accesso alla sala da tè. Per 2 persone. Prenota diretto."),
    "antica-latteria-1930.html": ("Antica Latteria 1930 — casa vacanze a Tempio Pausania",
                   "Una vera latteria del 1930 nel centro storico di Tempio Pausania: 38 mq su due livelli, granito a vista, vasca con i piedini. Per 2 persone."),
    "la-dimora-intera.html": ("La Dimora intera: Loft e Suite per 4 a Tempio Pausania",
                   "Loft dell'Antiquario e Suite del Viaggiatore insieme, fino a 4 ospiti, nel centro storico di Tempio Pausania. Ideale per famiglie e amici."),
    "la-dimora.html": ("La Dimora: palazzetto del 1930 a Tempio Pausania",
                   "Un palazzetto del 1930 in Piazza Eleonora d'Arborea, nel centro storico di Tempio Pausania, con sala da tè, pianoforte e libreria."),
    "prenota.html": ("Prenota — Dimora delle Storie, Tempio Pausania",
                   "Prenota direttamente alla Dimora delle Storie a Tempio Pausania: scegli le date e vedi subito quali dimore sono libere."),
    "scrivi-la-tua-storia.html": ("Scrivi la tua storia | Dimora delle Storie",
                   "Avete soggiornato alla Dimora delle Storie a Tempio Pausania? Scrivete la vostra storia: le più belle entrano nel Libro delle Storie."),
    "storie.html": ("Il Libro delle Storie — Tempio Pausania e Gallura",
                   "Storie di Tempio Pausania e della Gallura, poesia e lingua gallurese: il Libro delle Storie della Dimora, da sfogliare come un libro."),
    "tempio-pausania.html": ("Tempio Pausania: cosa vedere nella Città di pietra",
                   "Tempio Pausania, la Città di pietra ai piedi del Limbara: cosa vedere a piedi nel centro storico, i dintorni, come arrivare da Olbia."),
    "storie/dove-dormire-a-tempio-pausania.html": ("Dove dormire a Tempio Pausania: il centro storico",
                   "Dove dormire a Tempio Pausania: perché scegliere il centro storico in granito, cosa vedere a piedi e come arrivare da Olbia."),
    "storie/leggenda-dell-antiquario.html": ("La leggenda dell'Antiquario | Dimora delle Storie",
                   "Vittorio Sanna, l'antiquario di Tempio Pausania che si innamorò del palazzetto di granito oggi Dimora delle Storie, e del suo loft di velluto blu."),
    "storie/leggenda-del-viaggiatore.html": ("La leggenda del Viaggiatore, esploratore del Limbara",
                   "Elia, l'esploratore arrivato a Tempio Pausania nel 1929 per studiare mufloni, falchi e grifoni del Monte Limbara: la storia della Suite del Viaggiatore."),
    "storie/leggenda-della-latteria.html": ("La leggenda della Latteria di Tempio | Dimora delle Storie",
                   "Caterina Pes e la latteria aperta nel 1930 di fronte alla Dimora, a Tempio Pausania: i bidoni dal Limbara, il grammofono e la vasca con i piedini."),
    "storie/leggenda-della-sala-da-te.html": ("La leggenda della sala da tè | Dimora delle Storie",
                   "Il pianoforte verticale, i giovedì dell'antiquario e le poesie lette ad alta voce, in italiano e in gallurese: la sala da tè della Dimora."),
}

def rd(p): return open(os.path.join(SITE, p), encoding="utf-8").read()
def wr(p, s): open(os.path.join(SITE, p), "w", encoding="utf-8").write(s)

def pagine():
    return sorted([os.path.basename(x) for x in glob.glob(f"{SITE}/*.html")] +
                  [os.path.relpath(x, SITE) for x in glob.glob(f"{SITE}/storie/*.html")])

def meta(s, p):
    if p in META:
        t, d = META[p]
        s = re.sub(r'<title>.*?</title>', f'<title>{e(t)}</title>', s, count=1, flags=re.S)
        s = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{e(d)}">', s, count=1)
        s = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{e(d)}">', s, count=1)
        if p != "index.html":  # in home og:title resta il claim
            s = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{e(t)}">', s, count=1)
    # og:url / og:site_name / twitter:card subito dopo og:locale
    s = re.sub(r'<meta property="og:url"[^>]*>|<meta property="og:site_name"[^>]*>|<meta name="twitter:card"[^>]*>', '', s)
    m = re.search(r'<link rel="canonical" href="([^"]+)">', s)
    if m:
        extra = (f'<meta property="og:url" content="{m.group(1)}"><meta property="og:site_name" content="{NOME}">'
                 '<meta name="twitter:card" content="summary_large_image">')
        s = s.replace('<meta property="og:locale" content="it_IT">', '<meta property="og:locale" content="it_IT">' + extra, 1)
    # pulsante lingua senza traduzione
    s = re.sub(r'\n?\s*<a href="#"[^>]*>IT / EN</a>', '', s)
    return s

INTER = ("<style id=\"inter-font\">" + "".join(
    f"@font-face{{font-family:'Inter';font-style:normal;font-weight:{w};font-display:swap;src:url(/fonts/inter-latin-{w}-normal.woff2) format('woff2')}}"
    for w in (300, 400, 500)) + "</style>")
LEGALI = '<a href="/privacy" style="text-decoration:none">Privacy</a> · <a href="/cookie" style="text-decoration:none">Cookie</a>'

def locale(s):
    """Caratteri ospitati in casa (niente Google Fonts) e link a privacy e cookie nel piede."""
    s = re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>\n?', '', s)
    s = re.sub(r'<style id="inter-font">.*?</style>\n?', '', s, flags=re.S)
    s = s.replace('</head>', INTER + '\n</head>', 1)
    s = s.replace('<span>Privacy · Cookie</span>', f'<span>{LEGALI}</span>')
    if LEGALI not in s:
        s = s.replace('CIN IT090070C2000S8992</span></div>', f'CIN IT090070C2000S8992</span><span>{LEGALI}</span></div>', 1)
    return s

def home_jsonld(s):
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, flags=re.S)
    if not m: return s
    d = json.loads(m.group(2))
    if d.get("@type") != "LodgingBusiness": return s
    d["description"] = META["index.html"][1]
    d["geo"] = {"@type": "GeoCoordinates", "latitude": 40.90374, "longitude": 9.10500}
    d["identifier"] = {"@type": "PropertyValue", "propertyID": "CIN", "value": CIN}
    d["numberOfRooms"] = 3
    d["hasMap"] = "https://www.google.com/maps/search/?api=1&query=Piazza+Eleonora+d%27Arborea+6%2C+07029+Tempio+Pausania"
    d["potentialAction"] = {"@type": "ReserveAction", "target": f"{BASE}/prenota"}
    dentro = d.setdefault("containsPlace", [])
    if not any(x.get("url", "").endswith("/la-dimora-intera") for x in dentro):
        dentro.append({"@type": "Accommodation", "name": "La Dimora intera (Loft + Suite)", "url": f"{BASE}/la-dimora-intera"})
    return s[:m.start(2)] + json.dumps(d, ensure_ascii=False) + s[m.end(2):]

def sitemap(tutte):
    sm = rd("sitemap.xml")
    oggi = datetime.date.today().isoformat()
    for p in tutte:
        slug = p[:-5]
        url = BASE + ("/" if slug == "index" else "/" + slug)
        if f"<loc>{url}</loc>" not in sm:
            sm = sm.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{oggi}</lastmod></url>\n</urlset>")
    sm = sm.replace(f"<loc>{BASE}/storie</loc><changefreq>", f"<loc>{BASE}/storie</loc><lastmod>{oggi}</lastmod><changefreq>") \
        if f"<loc>{BASE}/storie</loc><changefreq>" in sm else sm
    wr("sitemap.xml", sm)

def main():
    tutte = pagine()
    for p in tutte:
        s = locale(meta(rd(p), p))
        if p == "index.html":
            s = home_jsonld(s)
            if GSC not in s: s = re.sub(r'(<meta name="description"[^>]*>)', lambda m: m.group(1) + "\n" + GSC, s, count=1)
        wr(p, s)
        t = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
        d = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
        if len(t) > 62 or len(d) > 160:
            print(f"attenzione {p}: title {len(t)} / description {len(d)} caratteri")
    sitemap(tutte)

if __name__ == "__main__":
    for t, d in META.values():
        assert len(t) <= 62 and len(d) <= 160, (len(t), len(d), t)
    main()
    print("seo ok")
