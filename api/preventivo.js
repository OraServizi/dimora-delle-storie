// Preventivo in tempo reale da Magellano per le dimore della Dimora delle Storie.
// GET /api/preventivo?arrivo=AAAA-MM-GG&partenza=AAAA-MM-GG&ospiti=N
// Risponde { ok, prezzi: { "<resourceID>": { totale, soggiorno } } } solo per le dimore libere.
// Il browser non può interrogare bol.mainapps.com direttamente (CORS), quindi passa da qui.
const APIKEY = "YVQw8J6NyW";
const DIMORE = new Set([47201, 47540, 50407, 48070]); // Loft, Suite, Latteria, Duplex (escluso Palazzeddu)
const DATA = /^\d{4}-\d{2}-\d{2}$/;

module.exports = async (req, res) => {
  const { arrivo = "", partenza = "", ospiti = "2" } = req.query || {};
  const px = Math.max(1, Math.min(4, parseInt(ospiti, 10) || 2));
  if (!DATA.test(arrivo) || !DATA.test(partenza) || partenza <= arrivo) return res.status(400).json({ ok: false });
  const date = arrivo.replace(/-/g, "") + "-" + partenza.replace(/-/g, "");
  const url = `https://bol.mainapps.com/step1/all-geographicarea/all-typology/${date}/${px}/nc/?method=loadSecondaryData&apikey=${APIKEY}&lang=it`;
  try {
    const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 8000);
    const r = await fetch(url, { method: "POST", signal: ctrl.signal, headers: { "X-Requested-With": "XMLHttpRequest" } });
    clearTimeout(t);
    const j = await r.json();
    const prezzi = {};
    for (const u of (j.viewData && j.viewData.unitsForMap && j.viewData.unitsForMap.items) || []) {
      if (!DIMORE.has(u.unitID)) continue;
      const totale = u.priceWithAmenitiesAndPromotions ?? u.priceWithAmenities ?? u.priceValue;
      if (typeof totale === "number") prezzi[u.unitID] = { totale, soggiorno: u.priceValue };
    }
    res.setHeader("Cache-Control", "s-maxage=120, stale-while-revalidate=300");
    return res.status(200).json({ ok: true, prezzi });
  } catch (e) {
    return res.status(502).json({ ok: false });
  }
};
