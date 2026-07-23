"""
HSK1 Flashcards - Backend API
Serve dados do vocabulário e áudio (gTTS) como uma API JSON.
O frontend (hospedado separadamente, ex: Hostgator) consome essa API via fetch().
"""

from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
import random
import json
import os

app = Flask(__name__)

# Libera CORS pro seu domínio do Hostgator poder chamar essa API.
# Troque "*" pelo seu domínio real em produção, ex: "https://seudominio.com.br"
CORS(app, resources={r"/api/*": {"origins": "*"}})

AUDIO_DIR = "audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

with open("vocabulario.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    flashcards = data["flashcards"]

# Indexa por hanzi pra busca rápida (usado na rota de áudio)
by_hanzi = {card["hanzi"]: card for card in flashcards}


@app.route("/api/word")
def get_word():
    """Retorna uma palavra aleatória do deck."""
    card = random.choice(flashcards)
    return jsonify({
        "hanzi": card["hanzi"],
        "pinyin": card["pinyin"],
        "significado": card["significado"],
        "audio_url": f"/api/audio/{card['hanzi']}"
    })


@app.route("/api/words")
def get_all_words():
    """Retorna o deck completo (útil pra pré-carregar no frontend, ou pro FSRS depois)."""
    return jsonify(flashcards)


@app.route("/api/audio/<hanzi>")
def get_audio(hanzi):
    """
    Serve o áudio pré-gerado do caractere.
    IMPORTANTE: o áudio é gerado ANTES do deploy (rode gerar_audios.py localmente)
    e enviado junto no repositório. Gerar via gTTS em tempo real no Render
    costuma bater rate limit (erro 429) do Google, por isso não fazemos isso aqui.
    """
    if hanzi not in by_hanzi:
        abort(404, description="Palavra não encontrada no deck")

    filename = os.path.join(AUDIO_DIR, f"{hanzi}.mp3")
    if not os.path.exists(filename):
        abort(404, description="Áudio ainda não foi gerado para essa palavra. Rode gerar_audios.py e faça novo deploy.")

    return send_file(filename, mimetype="audio/mpeg")


@app.route("/api/health")
def health():
    """Endpoint simples pra checar se a API está no ar (útil pro Render/UptimeRobot)."""
    return jsonify({"status": "ok", "total_palavras": len(flashcards)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
