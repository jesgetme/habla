# Habla TTS proxy — deploy (free, ~3 min, no credit card)

This Cloudflare Worker gives Igbo its audio. Google blocks TTS requests made
directly from a web page, so this tiny proxy fetches the voice server-side
and hands it back to Habla.

## Steps
1. Make a free Cloudflare account: https://dash.cloudflare.com/sign-up  (no card)
2. Left sidebar → **Workers & Pages** → **Create** → **Create Worker**
3. Name it `habla-tts` → **Deploy** (deploys the starter)
4. Click **Edit code**, select all, delete, paste the contents of `worker.js`, **Deploy**
5. Copy the Worker URL at the top — looks like `https://habla-tts.<you>.workers.dev`
6. Send that URL to Claude — it gets wired into Habla and Igbo audio goes live.

## Test it yourself (optional)
Open in a browser (should play/download Igbo audio for "Ndeewo"):
`https://habla-tts.<you>.workers.dev/?tl=ig&q=Ndeewo`
