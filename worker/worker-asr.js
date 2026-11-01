/*
  Habla ASR proxy — Cloudflare Worker (Groq Whisper)
  Version: v1.0
  Last Modified: 2026-10-31
  Changelog: v1.0 — receives recorded audio from the app and forwards it to Groq's Whisper
             speech-to-text (free tier), returning the transcript as JSON. Powers real Spanish
             pronunciation scoring on iPhone (recording works on iOS; the live speech API doesn't).
  Setup:
    1. Get a free Groq API key: https://console.groq.com/keys
    2. This Worker's Settings -> Variables and Secrets -> Add -> Secret
       Name: GROQ_API_KEY   Value: your gsk_... key
    3. Deploy. Name the Worker exactly "habla-asr" so the app's URL matches.
*/
export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "*",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    const json = (o, s) => new Response(JSON.stringify(o), { status: s || 200, headers: { ...cors, "Content-Type": "application/json" } });
    if (request.method !== "POST") return json({ error: "POST audio as multipart form-data" }, 405);
    if (!env.GROQ_API_KEY) return json({ error: "GROQ_API_KEY secret not set" }, 500);

    let inForm;
    try { inForm = await request.formData(); } catch (e) { return json({ error: "bad form-data" }, 400); }
    const file = inForm.get("file");
    const language = (inForm.get("language") || "es").toString();
    if (!file) return json({ error: "no audio file" }, 400);

    const fd = new FormData();
    fd.append("file", file, "clip");
    fd.append("model", "whisper-large-v3-turbo");
    fd.append("language", language);
    fd.append("response_format", "json");
    fd.append("temperature", "0");

    const r = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: { "Authorization": "Bearer " + env.GROQ_API_KEY },
      body: fd,
    });
    const body = await r.text(); // Groq returns {"text": "..."}
    return new Response(body, { status: r.status, headers: { ...cors, "Content-Type": "application/json" } });
  },
};
