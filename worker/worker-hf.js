/*
  Habla TTS proxy — v2.0 (HuggingFace / Meta MMS Igbo)
  Last Modified: 2026-10-29
  Changelog: v2.0 — switched backend from Google (blocks cloud IPs, unreliable) to Meta's open
             MMS Igbo model via HuggingFace Inference API. Reliable, purpose-built Igbo voice.
             Caches each phrase for a week. Token read from the HF_TOKEN Worker secret.
  Setup: add a Worker secret named HF_TOKEN (Settings → Variables and Secrets → Add → Secret),
         value = a free HuggingFace read token from https://huggingface.co/settings/tokens
*/
export default {
  async fetch(request, env) {
    const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, OPTIONS" };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const { searchParams } = new URL(request.url);
    const q = (searchParams.get("q") || "").slice(0, 200);
    if (!q) return new Response("missing q", { status: 400, headers: cors });

    // Cache first — each phrase is fetched once, then replays instantly.
    const cache = caches.default;
    const cacheKey = new Request(new URL(request.url).toString(), { method: "GET" });
    const cached = await cache.match(cacheKey);
    if (cached) return cached;

    if (!env.HF_TOKEN) return new Response("HF_TOKEN secret not set", { status: 500, headers: cors });

    let audio = null, ct = "audio/flac";
    for (let attempt = 0; attempt < 4; attempt++) {
      const r = await fetch("https://api-inference.huggingface.co/models/facebook/mms-tts-ibo", {
        method: "POST",
        headers: { "Authorization": "Bearer " + env.HF_TOKEN, "Content-Type": "application/json", "Accept": "audio/flac" },
        body: JSON.stringify({ inputs: q, options: { wait_for_model: true } }),
      });
      if (r.ok) { audio = await r.arrayBuffer(); ct = r.headers.get("content-type") || ct; break; }
      if (r.status === 503) { await new Promise(s => setTimeout(s, 3000)); continue; } // model warming up
      const msg = await r.text();
      return new Response("tts error " + r.status + ": " + msg.slice(0, 200), { status: 502, headers: cors });
    }
    if (!audio) return new Response("tts unavailable (model warming up — try again)", { status: 503, headers: cors });

    const resp = new Response(audio, { headers: { ...cors, "Content-Type": ct, "Cache-Control": "public, max-age=604800" } });
    await cache.put(cacheKey, resp.clone());
    return resp;
  },
};
