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
from datetime import timedelta
from pathlib import Path

from flask import Flask, Response, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.dashboard.store import (
    create_user,
    get_all_events,
    get_events_since,
    get_max_id,
    get_stats,
    get_user_by_email,
    get_user_by_id,
    init_db,
    insert_event,
    save_quote_request,
    seed_demo_data,
)

app = Flask(
    __name__,
    static_folder=str(Path(__file__).resolve().parents[2] / "Website_Layout"),
    static_url_path="/site",
)
app.secret_key = "change-me-to-a-secure-secret"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

init_db()
seed_demo_data()


# ── Pages ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/site")
def site_root():
    return redirect("/site/")


@app.route("/site/")
def site():
    return app.send_static_file("cleanbot.html")


@app.route("/api/session")
def api_session():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None})

    user = get_user_by_id(int(user_id))
    if not user:
        return jsonify({"user": None})

    return jsonify({"user": {"email": user["email"]}})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    if not email or not password:
        return jsonify({"ok": False, "error": "Email and password are required."}), 400

    if get_user_by_email(email) is not None:
        return jsonify({"ok": False, "error": "This email is already registered."}), 400

    password_hash = generate_password_hash(password)
    try:
        user_id = create_user(email=email, password_hash=password_hash)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500

    session["user_id"] = user_id
    session.permanent = remember
    return jsonify({"ok": True, "user": {"email": email}})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    if not email or not password:
        return jsonify({"ok": False, "error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"ok": False, "error": "Invalid email or password."}), 401

    session["user_id"] = user["id"]
    session.permanent = remember
    return jsonify({"ok": True, "user": {"email": email}})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return jsonify({"ok": True})


@app.route("/api/quote", methods=["POST"])
def api_quote():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    company = (data.get("company") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"ok": False, "error": "Name, email, and message are required."}), 400

    try:
        save_quote_request(name=name, email=email, company=company, message=message)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


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
