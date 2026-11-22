// Riceve una storia scritta da un ospite e la invia via email alla Dimora per l'approvazione.
// Variabili d'ambiente su Vercel: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, STORIE_TO.
const nodemailer = require("nodemailer");

const MAX = { nome: 80, email: 120, dimora: 60, titolo: 120, storia: 12000, firma: 80 };
const DIMORE = ["Loft dell'Antiquario", "Suite del Viaggiatore", "Antica Latteria 1930", "Altro / non ancora ospite"];

function pulisci(v, n) { return String(v || "").replace(/\r/g, "").trim().slice(0, n); }

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ ok: false }); }
  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch { b = {}; } }
  b = b || {};

  // antispam: campo nascosto compilato o invio troppo rapido
  if (b.sito) return res.status(200).json({ ok: true });
  if (Number(b.t || 0) && Date.now() - Number(b.t) < 8000) return res.status(200).json({ ok: true });

  const d = {
    nome: pulisci(b.nome, MAX.nome), email: pulisci(b.email, MAX.email), dimora: pulisci(b.dimora, MAX.dimora),
    titolo: pulisci(b.titolo, MAX.titolo), storia: pulisci(b.storia, MAX.storia), firma: pulisci(b.firma, MAX.firma),
  };
  const errori = [];
  if (!d.nome) errori.push("nome");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) errori.push("email");
  if (!d.titolo) errori.push("titolo");
  if (d.storia.length < 200) errori.push("storia");
  if (!b.consenso_pubblicazione || !b.consenso_privacy) errori.push("consensi");
  if (!DIMORE.includes(d.dimora)) d.dimora = "Non indicata";
  if (errori.length) return res.status(400).json({ ok: false, errori });

  const { SMTP_HOST = "authsmtp.securemail.pro", SMTP_PORT = "465", SMTP_USER, STORIE_TO } = process.env;
  // la password è stata salvata su Vercel come CLIENT_KEY: si accettano entrambi i nomi
  const SMTP_PASS = process.env.SMTP_PASS || process.env.CLIENT_KEY;
  if (!SMTP_USER || !SMTP_PASS) return res.status(503).json({ ok: false, errore: "invio non configurato" });

  const allegati = [];
  const m = /^data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$/.exec(String(b.foto || ""));
  if (m && m[2].length < 4_000_000) allegati.push({ filename: `foto-storia.${m[1] === "jpeg" ? "jpg" : m[1]}`, content: Buffer.from(m[2], "base64") });

  const testo = [
    "Nuova storia per il Libro delle Storie, da approvare.", "",
    `Titolo: ${d.titolo}`, `Firma nel Libro: ${d.firma || d.nome}`, `Dimora: ${d.dimora}`,
    `Autore: ${d.nome} <${d.email}>`, `Foto allegata: ${allegati.length ? "sì" : "no"}`,
    "Consenso alla pubblicazione e informativa privacy: accettati", `Inviata il: ${new Date().toLocaleString("it-IT", { timeZone: "Europe/Rome" })}`,
    "", "———", "", d.storia, "", "———",
    "Per approvarla, inoltra questa email o chiedi a Claude di pubblicarla nel capitolo «Le storie degli ospiti».",
    "Per rispondere all'autore basta rispondere a questa email.",
  ].join("\n");

  try {
    const t = nodemailer.createTransport({ host: SMTP_HOST, port: Number(SMTP_PORT), secure: Number(SMTP_PORT) === 465, auth: { user: SMTP_USER, pass: SMTP_PASS } });
    await t.sendMail({
      from: `"Il Libro delle Storie" <${SMTP_USER}>`, to: STORIE_TO || SMTP_USER, replyTo: `"${d.nome.replace(/"/g, "")}" <${d.email}>`,
      subject: `Nuova storia per il Libro: ${d.titolo}`, text: testo, attachments: allegati,
    });
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error("invio storia fallito", e && e.message);
    return res.status(502).json({ ok: false, errore: "invio non riuscito" });
  }
};
