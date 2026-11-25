# Dimora delle Storie — sito

Home del nuovo sito di Dimora delle Storie (Tempio Pausania), direzione grafica "Granito e luce".

- `index.html` — la home (HTML/CSS statico, nessuna build)
- `img/` — foto delle dimore, livelli della peonia animata, logo

Pubblicato su Vercel come sito statico.

- `la-dimora.html` — la casa: facciata, sala da tè, leggenda dell'Antiquario
- `img/foto/` — foto del fotografo ottimizzate (webp 1600 px) per le gallerie
- `tools/dimore.py` — rigenera gallerie, testi della Latteria, pagina La Dimora e voce «La casa» del menu (`python3 tools/dimore.py`)
- `tools/seo.py` — ultimo passaggio SEO (title/description brevi, og:url, twitter:card, dati strutturati della home, sitemap). Parte da solo alla fine di `storie.py`, `tempio.py` e `prenota.py`; per un nuovo articolo aggiungere title e description in `META`.
- `tools/legali.py` — genera /privacy e /cookie (lanciato anche da `dimore.py`). I caratteri Inter sono ospitati in `fonts/`, niente Google Fonts.
