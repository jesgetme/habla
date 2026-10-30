/*
  Habla TTS proxy — Cloudflare Worker
  Version: v1.0
  Last Modified: 2026-10-29
  Changelog: v1.0 — fetches Google Translate TTS server-side (bypasses the browser referer block
             that stops Igbo audio playing directly) and returns mp3 with CORS headers.
  Deploy: Cloudflare dashboard → Workers & Pages → Create → Worker → paste this → Deploy.
          Then copy the *.workers.dev URL and send it to Claude to wire into Habla.
*/
export default {
  async fetch(request) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const { searchParams } = new URL(request.url);
    const q = (searchParams.get("q") || "").slice(0, 200); // Google caps ~200 chars
    const tl = searchParams.get("tl") || "ig";
    const slow = searchParams.get("slow") === "1";
    if (!q) return new Response("missing q", { status: 400, headers: cors });

    const g = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=" +
      encodeURIComponent(tl) + (slow ? "&ttsspeed=0.3" : "") + "&q=" + encodeURIComponent(q);

    const r = await fetch(g, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://translate.google.com/",
      },
    });
    return new Response(r.body, {
      status: r.status,
      headers: { ...cors, "Content-Type": "audio/mpeg", "Cache-Control": "public, max-age=86400" },
    });
  },
};
