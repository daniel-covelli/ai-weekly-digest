import threading

from flask import Flask, jsonify

from ai_daily_digest.__main__ import main

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/run", methods=["POST"])
def run():
    thread = threading.Thread(target=main)
    thread.start()
    return jsonify({"status": "started"}), 202
