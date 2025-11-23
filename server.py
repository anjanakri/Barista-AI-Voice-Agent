# from dotenv import load_dotenv
# import os

# load_dotenv()  # loads .env values

# MURF_API_KEY = os.getenv("MURF_API_KEY")
# print("Loaded Murf Key?", MURF_API_KEY is not None)
# print("Loaded key:", MURF_API_KEY)

import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
import requests

# Load .env
load_dotenv()
MURF_API_KEY = os.getenv("MURF_API_KEY")

app = Flask(__name__, template_folder="templates", static_folder="static")

# Create orders folder if not exists
ORDERS_DIR = "orders"
os.makedirs(ORDERS_DIR, exist_ok=True)

# -----------------------------
# ROUTE: SERVE FRONTEND
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
# ROUTE: SAVE ORDER AS JSON
# -----------------------------
@app.route("/save_order", methods=["POST"])
def save_order():
    order = request.json
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_{ts}.json"
    filepath = os.path.join(ORDERS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(order, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "ok", "file": filename})

# -----------------------------
# ROUTE: MURF TTS (SERVER SIDE)
# -----------------------------
@app.route("/tts", methods=["POST"])
def tts():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Murf Falcon API Endpoint (Doc: https://docs.murf.ai/)
    TTS_URL = "https://api.murf.ai/v1/speech/generate"

    headers = {
        "Authorization": f"Bearer {MURF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": text,
        "voice": "en-US-Neural-K",
        "format": "mp3"
    }

    response = requests.post(TTS_URL, json=payload, headers=headers, stream=True)

    if response.status_code != 200:
        return jsonify({"error": "Murf TTS failed", "details": response.text}), 500

    def generate():
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

    return Response(generate(), content_type="audio/mpeg")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Murf Key Loaded?", MURF_API_KEY is not None)
    app.run(host="0.0.0.0", port=5000, debug=True)
