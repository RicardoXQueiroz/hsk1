"""
Roda esse script UMA VEZ na sua máquina local (não no Render).
Ele gera o mp3 de cada palavra do vocabulario.json e salva na pasta audio_cache/.
Depois, você sobe a pasta audio_cache/ inteira pro GitHub, junto com o resto do backend.

Como rodar:
    pip install gtts
    python gerar_audios.py
"""

import json
import os
import time
from gtts import gTTS

with open("vocabulario.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    flashcards = data["flashcards"]

os.makedirs("audio_cache", exist_ok=True)

total = len(flashcards)
for i, card in enumerate(flashcards, start=1):
    hanzi = card["hanzi"]
    filename = os.path.join("audio_cache", f"{hanzi}.mp3")

    if os.path.exists(filename):
        print(f"[{i}/{total}] Já existe: {hanzi}")
        continue

    try:
        tts = gTTS(text=hanzi, lang="zh")
        tts.save(filename)
        print(f"[{i}/{total}] Gerado: {hanzi}")
        time.sleep(1)  # pausa entre requisições pra não tomar rate limit também localmente
    except Exception as e:
        print(f"[{i}/{total}] ERRO em '{hanzi}': {e}")

print("\nConcluído! Confira a pasta audio_cache/ — deve ter um mp3 por palavra.")
