#!/usr/bin/env python3
"""
generate_audio.py
Version: v2.0
Last Modified: 2026-10-31
Changelog:
    v2.0 — generalized to all Habla languages. Spanish (facebook/mms-tts-spa) + Igbo
           (nexusbert/igbo-mms-tts) via local MMS/VITS models. One .wav per phrase into
           audio/<lang>/, named by a hash matching the app. Skips clips that already exist.
    v1.0 — Igbo only (was generate_igbo_audio.py).

SETUP (Python 3.9+):  pip install -U transformers torch scipy numpy
RUN (from the root of your habla repo):  python generate_audio.py
First run downloads each model (~150MB) once. Then:
    git add audio && git commit -m "Audio clips" && git push
"""
import os, numpy as np
from transformers import pipeline
from scipy.io.wavfile import write as wav_write

# Must match the app clipId() exactly (djb2-xor, 32-bit).
def clip_id(s):
    x = 5381
    for ch in s:
        x = ((x * 33) & 0xFFFFFFFF) ^ (ord(ch) & 0xFFFFFFFF)
        x &= 0xFFFFFFFF
    return format(x, "08x")

LANGS = [
    {"code": "es", "model": "facebook/mms-tts-spa", "phrases": [
        "Hola",
        "Buenos días",
        "Buenas tardes",
        "Gracias",
        "De nada",
        "Sí, por favor",
        "No, gracias",
        "Adiós",
        "¿Cómo estás?",
        "Bien, gracias",
        "¿Cómo te llamas?",
        "Me llamo Steve",
        "Mucho gusto",
        "¿De dónde eres?",
        "Soy de Estados Unidos",
        "¿Hablas inglés?",
        "No entiendo",
        "¿Puedes repetir?",
        "Más despacio, por favor",
        "¿Cómo se dice...?",
        "Necesito ayuda",
        "Perdón",
        "Uno",
        "Dos",
        "Tres",
        "Cuatro",
        "Cinco",
        "Seis",
        "Siete",
        "Ocho",
        "Nueve",
        "Diez",
        "Una mesa para dos",
        "El menú, por favor",
        "Quisiera un café",
        "Agua, por favor",
        "Está delicioso",
        "La cuenta, por favor",
        "¿Dónde está el baño?",
        "A la izquierda",
        "A la derecha",
        "Todo recto",
        "¿Cuánto cuesta?",
        "Aquí y allí",
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
        "Hoy",
        "Mañana",
        "¿Qué tiempo hace?",
        "Hace calor",
        "Hace frío",
        "Hace sol",
        "Está lloviendo",
        "Hace buen día",
        "¿Qué hiciste?",
        "Comí",
        "Fui",
        "Ayer trabajé",
        "Estuvo bien",
        "Estuve allí",
        "¡Hola! Buenos días.",
        "Buenos días. Un café, por favor.",
        "¿Algo más?",
        "No, gracias. ¿Cuánto cuesta?",
        "Tres dólares.",
        "Aquí tiene. ¡Gracias!",
        "Hola, ¿cómo te llamas?",
        "Me llamo Steve. ¿Y tú?",
        "Soy Ana. Mucho gusto.",
        "Mucho gusto. ¿De dónde eres?",
        "Soy de México.",
        "¡Qué bien! Adiós.",
        "Perdón, ¿dónde está el baño?",
        "Todo recto, a la derecha.",
        "¿Puedes repetir, más despacio?",
        "A la derecha. Allí.",
        "¡Muchas gracias!",
    ]},
    {"code": "ig", "model": "nexusbert/igbo-mms-tts", "phrases": [
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
    ]},
]

total_new = 0
for spec in LANGS:
    code = spec["code"]
    out = os.path.join("audio", code)
    os.makedirs(out, exist_ok=True)
    todo = [p for p in spec["phrases"] if not os.path.exists(os.path.join(out, clip_id(p) + ".wav"))]
    if not todo:
        print("[" + code + "] all " + str(len(spec["phrases"])) + " clips already exist - skipping.")
        continue
    print("[" + code + "] loading " + spec["model"] + " (first run downloads ~150MB)...")
    tts = pipeline("text-to-audio", model=spec["model"])
    for i, phrase in enumerate(todo, 1):
        res = tts(phrase)
        audio = np.squeeze(np.asarray(res["audio"]))
        sr = int(res["sampling_rate"])
        pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
        path = os.path.join(out, clip_id(phrase) + ".wav")
        wav_write(path, sr, pcm)
        total_new += 1
        print("  [" + code + " " + str(i) + "/" + str(len(todo)) + "] " + phrase[:28].ljust(28) + " -> " + os.path.basename(path))

print("")
print("Done - " + str(total_new) + " new clip(s) written under audio/.")
print("Next: git add audio && git commit -m \"Audio clips\" && git push")
