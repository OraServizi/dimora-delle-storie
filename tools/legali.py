#!/usr/bin/env python3
"""Genera /privacy e /cookie (informativa privacy e cookie policy)."""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import storie as S  # riusa testa, menu, piede e stili

SITE, BASE, e, SERIF = S.SITE, S.BASE, S.e, S.SERIF
AGGIORNATA = "25 novembre 2026"
TITOLARE = "Luca Cossu, titolare di Dimora delle Storie"
SEDE = "Piazza Eleonora d'Arborea 6, 07029 Tempio Pausania (SS)"
EMAIL = "info@dimoradellestorie.com"

CSS = '''
@media (max-width:440px){.topnav{gap:16px!important;padding:10px 16px!important;font-size:12px!important}}
.l-sec{padding:clamp(40px,6vw,80px) clamp(20px,4.5vw,64px) clamp(80px,9vw,130px);max-width:860px;margin:0 auto}
.l-sec h1{margin:0 0 10px;'''+SERIF+''';font-weight:400;font-size:clamp(26px,4vw,46px);letter-spacing:.1em;text-transform:uppercase;line-height:1.15}
.l-sec .agg{margin:0 0 40px;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#8FA2E6}
.l-sec h2{margin:44px 0 12px;'''+SERIF+''';font-weight:400;font-size:clamp(17px,1.8vw,21px);letter-spacing:.1em;text-transform:uppercase;color:#E2B76A}
.l-sec p,.l-sec li{font-size:16px;line-height:1.8;color:rgba(239,232,220,.82)}
.l-sec ul{padding-left:20px;margin:0 0 12px}
.l-sec a{color:#E2B76A}
'''

PRIVACY = [
    ("Chi tratta i dati", [
        f"Titolare del trattamento è {TITOLARE}, {SEDE}. Per qualsiasi domanda sui vostri dati potete scrivere a <a href=\"mailto:{EMAIL}\">{EMAIL}</a>."]),
    ("Quali dati e perché", [
        "<strong>Navigazione.</strong> Il server che ospita il sito registra in modo automatico dati tecnici (indirizzo IP, data e ora, pagina richiesta, tipo di browser) necessari a far funzionare il sito e a proteggerlo da abusi. Base giuridica: legittimo interesse (art. 6.1.f GDPR).",
        "<strong>Richieste di informazioni.</strong> Se ci scrivete per email, WhatsApp o ci telefonate, usiamo i dati che ci date (nome, contatti, date del soggiorno) solo per rispondervi. Base giuridica: misure precontrattuali richieste da voi (art. 6.1.b).",
        "<strong>Verifica disponibilità e prenotazioni.</strong> Quando cercate le date sul sito, inviamo al nostro sistema di prenotazione solo le date e il numero di ospiti, senza dati personali. La prenotazione si completa sulle pagine del gestionale Magellano, che tratta i dati per nostro conto. Base giuridica: esecuzione del contratto (art. 6.1.b).",
        "<strong>Il Libro delle Storie.</strong> Se ci mandate una storia, riceviamo nome, email, la dimora in cui avete soggiornato, il testo, la firma ed eventualmente una foto. Li usiamo per valutare la storia e, se la pubblichiamo, per pubblicarla con la firma che avete scelto. Base giuridica: il vostro consenso (art. 6.1.a), che potete revocare in ogni momento chiedendoci di togliere la storia.",
        "<strong>Durante il soggiorno.</strong> Per legge registriamo i dati degli ospiti e li comunichiamo alla Questura (art. 109 TULPS, portale Alloggiati Web), e li usiamo per l'imposta di soggiorno e le statistiche turistiche. Base giuridica: obbligo di legge (art. 6.1.c)."]),
    ("Per quanto tempo", [
        "I dati delle richieste di informazioni per il tempo necessario a rispondere e, al massimo, per 24 mesi. Le storie non pubblicate le cancelliamo entro 12 mesi; quelle pubblicate restano online finché non ci chiedete di toglierle. I dati di prenotazione e di soggiorno per i tempi previsti dalle norme fiscali e di pubblica sicurezza. I dati tecnici di navigazione per pochi giorni, salvo necessità di accertare abusi."]),
    ("A chi li affidiamo", [
        "Non vendiamo né cediamo i vostri dati. Li trattano per nostro conto solo i fornitori che ci servono per lavorare:",
        "<ul><li>Vercel Inc. (ospitalità del sito), con server anche negli Stati Uniti, sulla base delle garanzie previste dal GDPR (decisione di adeguatezza UE-USA e clausole contrattuali standard);</li><li>Register.it (posta elettronica);</li><li>Magellano (gestionale delle prenotazioni);</li><li>le autorità pubbliche, quando la legge lo richiede.</li></ul>",
        "Se ci contattate con WhatsApp o seguite il nostro profilo Instagram, quei dati sono trattati anche da Meta secondo le sue informative."]),
    ("I vostri diritti", [
        "Potete chiederci in ogni momento di accedere ai vostri dati, correggerli, cancellarli, limitarne il trattamento, opporvi o riceverli in un formato leggibile (artt. 15-22 GDPR), e revocare un consenso già dato. Basta scrivere a <a href=\"mailto:"+EMAIL+"\">"+EMAIL+"</a>. Se ritenete che i vostri dati siano trattati in modo scorretto potete rivolgervi al Garante per la protezione dei dati personali (<a href=\"https://www.garanteprivacy.it\" rel=\"noopener\">garanteprivacy.it</a>)."]),
    ("Cookie", ["Il sito usa solo strumenti tecnici: i dettagli sono nella <a href=\"/cookie\">cookie policy</a>."]),
]

COOKIE = [
    ("In breve", [
        "Questo sito non usa cookie di profilazione né strumenti di statistica o pubblicità, e non mostra il banner dei cookie perché non serve: usa solo strumenti tecnici, che non richiedono consenso (art. 122 Codice privacy e Linee guida del Garante del 10 giugno 2021)."]),
    ("Cosa usiamo", [
        "<ul><li><strong>Memoria del browser (localStorage)</strong>: il Libro delle Storie ricorda l'ultima pagina che avete sfogliato, solo sul vostro dispositivo. Nessun dato viene inviato a noi.</li><li><strong>Caratteri tipografici</strong>: sono ospitati sul nostro sito, senza collegamenti a servizi esterni.</li></ul>"]),
    ("Siti esterni", [
        "I collegamenti a WhatsApp, Instagram e alle pagine di prenotazione di Magellano portano su siti di terzi, che possono usare cookie propri secondo le loro informative."]),
    ("Come gestirli", [
        "Potete cancellare la memoria del sito in qualsiasi momento dalle impostazioni del browser. Per il resto vale l'<a href=\"/privacy\">informativa privacy</a>."]),
]

def page(slug, titolo, h1, desc, sezioni):
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": titolo, "url": f"{BASE}/{slug}", "inLanguage": "it-IT"}
    h = S.head(titolo, desc, f"{BASE}/{slug}", "/img/loft.jpg", ld) + f"<style>{CSS}</style>\n"
    corpo = "".join(f"<h2>{e(t)}</h2>" + "".join(p if p.startswith("<ul>") else f"<p>{p}</p>" for p in ps) for t, ps in sezioni)
    body = f'''{S.header_html()}
  <section class="l-sec">
    <h1>{e(h1)}</h1>
    <p class="agg">Aggiornata il {AGGIORNATA}</p>
    {corpo}
  </section>
'''
    return S.absolutize(h + S.BODY_OPEN + body + S.FOOT)

open(f"{SITE}/privacy.html", "w", encoding="utf-8").write(page(
    "privacy", "Informativa privacy | Dimora delle Storie", "Informativa privacy",
    "Come Dimora delle Storie, a Tempio Pausania, tratta i dati di chi visita il sito, chiede informazioni, prenota o scrive una storia.", PRIVACY))
open(f"{SITE}/cookie.html", "w", encoding="utf-8").write(page(
    "cookie", "Cookie policy | Dimora delle Storie", "Cookie policy",
    "Il sito della Dimora delle Storie usa solo strumenti tecnici: nessun cookie di profilazione, statistica o pubblicità.", COOKIE))
print("privacy.html, cookie.html")

import subprocess as _sp; _sp.run([sys.executable, "-B", os.path.join(SITE, "tools", "seo.py")], check=True, stdout=_sp.DEVNULL)  # ultimo passaggio SEO
