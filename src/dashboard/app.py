#!/usr/bin/env python3
"""
CleanBot live hotspot dashboard.

Usage:
  python src/dashboard/app.py            # runs on http://localhost:5001
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.dashboard.store import (
    get_all_events,
    get_events_since,
    get_max_id,
    get_stats,
    init_db,
    insert_event,
    seed_demo_data,
)

app = Flask(__name__)

init_db()
seed_demo_data()


# ── Pages ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Data API ─────────────────────────────────────────────────────────────────

@app.route("/api/events")
def api_events():
    return jsonify(get_all_events())


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/event", methods=["POST"])
def api_add_event():
    d = request.json or {}
    insert_event(
        lat        = float(d["lat"]),
        lng        = float(d["lng"]),
        class_name = str(d["class_name"]),
        confidence = float(d.get("confidence", 1.0)),
        action     = d.get("action"),
        bin_color  = d.get("bin_color"),
        priority   = d.get("priority"),
    )
    return jsonify({"ok": True})


# ── Server-Sent Events (live map updates) ────────────────────────────────────

@app.route("/api/stream")
def api_stream():
    def generate():
        # Start from current max so we only push genuinely NEW events
        last_id = get_max_id()
        while True:
            for event in get_events_since(last_id):
                yield f"data: {json.dumps(event)}\n\n"
                last_id = event["id"]
            time.sleep(2)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── RAG Q&A ──────────────────────────────────────────────────────────────────

@app.route("/api/ask", methods=["POST"])
def api_ask():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please enter a question."})
    try:
        from src.knowledge.rag import WasteRAG
        rag    = WasteRAG()
        answer = rag.answer(question, use_claude=False)
    except FileNotFoundError:
        answer = (
            "RAG index not built yet. Run:\n"
            "  python training/build_rag_index.py\n"
            "Then restart the dashboard."
        )
    except Exception as e:
        answer = f"Error: {e}"
    return jsonify({"answer": answer})


if __name__ == "__main__":
    print("CleanBot Dashboard → http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
