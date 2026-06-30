from __future__ import annotations

import random
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "cleanbot.db"


def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  REAL    NOT NULL,
                lat        REAL    NOT NULL,
                lng        REAL    NOT NULL,
                class_name TEXT    NOT NULL,
                confidence REAL    NOT NULL,
                action     TEXT,
                bin_color  TEXT,
                priority   TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    REAL    NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS quote_requests (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL,
                company    TEXT,
                message    TEXT    NOT NULL,
                created_at REAL    NOT NULL
            )
        """)
        db.commit()


def insert_event(
    lat: float,
    lng: float,
    class_name: str,
    confidence: float,
    action: str | None = None,
    bin_color: str | None = None,
    priority: str | None = None,
) -> None:
    with get_db() as db:
        db.execute(
            """INSERT INTO events
               (timestamp, lat, lng, class_name, confidence, action, bin_color, priority)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (time.time(), lat, lng, class_name, confidence, action, bin_color, priority),
        )
        db.commit()


def get_all_events(limit: int = 500) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_max_id() -> int:
    with get_db() as db:
        row = db.execute("SELECT MAX(id) FROM events").fetchone()
        return row[0] or 0


def get_events_since(last_id: int) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM events WHERE id > ? ORDER BY id ASC", (last_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats() -> dict:
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        rows  = db.execute(
            "SELECT class_name, COUNT(*) as cnt FROM events GROUP BY class_name"
        ).fetchall()
        return {"total": total, "by_class": {r["class_name"]: r["cnt"] for r in rows}}


def create_user(email: str, password_hash: str) -> int:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.strip().lower(), password_hash, time.time()),
        )
        db.commit()
        return cursor.lastrowid


def get_user_by_email(email: str) -> dict | None:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def save_quote_request(name: str, email: str, company: str | None, message: str) -> int:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO quote_requests (name, email, company, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), email.strip(), company.strip() if company else None, message.strip(), time.time()),
        )
        db.commit()
        return cursor.lastrowid


def seed_demo_data() -> None:
    """Populate the DB with realistic-looking demo events if it is empty."""
    if get_stats()["total"] > 0:
        return

    rng = random.Random(42)
    base_lat, base_lng = 37.7749, -122.4194   # San Francisco

    classes = ["plastic", "metal", "paper", "bio_waste"]
    meta = {
        "plastic":   ("collect_recyclable", "blue"),
        "metal":     ("collect_recyclable", "blue"),
        "paper":     ("collect_recyclable", "blue"),
        "bio_waste": ("collect_compost",    "green"),
    }
    priorities = ["high", "high", "medium", "medium", "low"]

    # 5 hotspot zones around SF
    zones = [
        ( 0.010, -0.010),
        (-0.008,  0.012),
        ( 0.015,  0.005),
        (-0.002, -0.015),
        ( 0.006,  0.008),
    ]

    with get_db() as db:
        for _ in range(150):
            cls     = rng.choice(classes)
            act, bn = meta[cls]
            dz      = rng.choice(zones)
            lat     = base_lat + dz[0] + rng.gauss(0, 0.002)
            lng     = base_lng + dz[1] + rng.gauss(0, 0.002)
            conf    = rng.uniform(0.55, 0.99)
            ts      = time.time() - rng.uniform(0, 72 * 3600)
            pri     = rng.choice(priorities)
            db.execute(
                """INSERT INTO events
                   (timestamp, lat, lng, class_name, confidence, action, bin_color, priority)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (ts, lat, lng, cls, conf, act, bn, pri),
            )
        db.commit()
