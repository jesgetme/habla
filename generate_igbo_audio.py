#!/usr/bin/env python3
"""
generate_igbo_audio.py
Version: v1.0
Last Modified: 2026-10-29
Changelog: v1.0 — generates bundled Igbo audio clips for Habla using the local
           nexusbert/igbo-mms-tts model (Meta MMS / VITS). One .wav per phrase,
           named by a hash that matches the app, written to ./audio/ig/.
           Run once; commit the audio/ folder. No API, no key, no cost.

SETUP (Windows / Mac / Linux, Python 3.9+):
    pip install -U transformers torch scipy numpy
RUN  (from the root of your habla repo, so it writes ./audio/ig/):
    python generate_igbo_audio.py
First run downloads the model (~150 MB) once, then generates all clips in ~1 min on CPU.
"""
import os, numpy as np
from transformers import pipeline
from scipy.io.wavfile import write as wav_write

# Must match the app hash exactly (djb2-xor, 32-bit) so filenames line up.
def clip_id(s: str) -> str:
    x = 5381
    for ch in s:
        x = ((x * 33) & 0xFFFFFFFF) ^ (ord(ch) & 0xFFFFFFFF)
        x &= 0xFFFFFFFF
    return format(x, "08x")

PHRASES = [
    "Ndeewo",
    "Ụtụtụ ọma",
    "Ehihie ọma",
    "Daalụ",
    "Ọ dị mma",
    "Ee",
    "Mba",
    "Ka ọ dị",
    "Kedu ka ị mere?",
    "Adị m mma",
    "Kedu aha gị?",
    "Aha m bụ Steve",
    "Obi ụtọ izute gị",
    "Ebee ka i si?",
    "Esi m America",
    "Otu",
    "Abụọ",
    "Atọ",
    "Anọ",
    "Ise",
    "Isii",
    "Asaa",
    "Asatọ",
    "Itoolu",
    "Iri",
    "Ị na-asụ Bekee?",
    "Aghọtaghị m",
    "Biko kwughachi",
    "Biko jiri nwayọ",
    "Achọrọ m enyemaka",
    "Ndo",
    "Biko",
    "Mmiri",
    "Nri",
    "Achọrọ m mmiri",
    "Agụụ na-agụ m",
    "Ọ na-atọ ụtọ",
    "Nne",
    "Nna",
    "Enyi",
    "Nwa",
    "Nwoke",
    "Nwanyị",
    "Ndeewo! Kedu?",
    "Adị m mma. Daalụ.",
    "Aha m bụ Steve.",
    "Obi ụtọ izute gị.",
    "Ka ọ dị.",
    "Ndeewo. Achọrọ m mmiri.",
    "Ọ dị mma. Otu narị naira.",
    "Daalụ.",
    "Ọ dị mma.",
]

OUT = os.path.join("audio", "ig")
os.makedirs(OUT, exist_ok=True)

print(f"Loading Igbo TTS model (first run downloads ~150MB)…")
tts = pipeline("text-to-audio", model="nexusbert/igbo-mms-tts")

ok = 0
for i, phrase in enumerate(PHRASES, 1):
    out = tts(phrase)
    audio = np.squeeze(np.asarray(out["audio"]))
    sr = int(out["sampling_rate"])
    # float [-1,1] -> int16 PCM wav (universally playable in browsers)
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype(np.int16)
    path = os.path.join(OUT, clip_id(phrase) + ".wav")
    wav_write(path, sr, pcm)
    ok += 1
    print(f"  [{i:>2}/{len(PHRASES)}] {phrase[:30]:<30} -> {os.path.basename(path)}")

print(f"\nDone — {ok} clips written to {OUT}/")
print("Next: commit the audio/ folder and push.  git add audio && git commit -m \"Igbo audio clips\" && git push")
