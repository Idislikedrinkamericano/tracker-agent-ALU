"""SQLite storage: companies + email events."""
import os
import sqlite3
from .classify import STATUS_PRECEDENCE, CATEGORY_TO_STATUS

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    name TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'unknown',
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS events (
    gmail_id TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT,
    sender TEXT,
    date TEXT,
    snippet TEXT
);
"""


def connect(base_dir):
    path = os.path.join(base_dir, "tracker.db")
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def _stronger(a, b):
    """Return the stronger of two statuses per precedence."""
    ia = STATUS_PRECEDENCE.index(a) if a in STATUS_PRECEDENCE else 99
    ib = STATUS_PRECEDENCE.index(b) if b in STATUS_PRECEDENCE else 99
    return a if ia <= ib else b


def add_event(conn, gmail_id, company, category, subject, sender, date, snippet):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM events WHERE gmail_id = ?", (gmail_id,))
    if cur.fetchone():
        return False  # already seen
    cur.execute(
        "INSERT INTO events VALUES (?,?,?,?,?,?,?)",
        (gmail_id, company, category, subject, sender, date, snippet),
    )
    new_status = CATEGORY_TO_STATUS.get(category, "unknown")
    cur.execute("SELECT status FROM companies WHERE name = ?", (company,))
    row = cur.fetchone()
    if row:
        status = _stronger(row[0], new_status)
        cur.execute("UPDATE companies SET status = ?, updated_at = ? WHERE name = ?",
                    (status, date, company))
    else:
        cur.execute("INSERT INTO companies VALUES (?,?,?)", (company, new_status, date))
    conn.commit()
    return True


def seed_companies(conn, names):
    cur = conn.cursor()
    for n in names:
        cur.execute("INSERT OR IGNORE INTO companies (name, status) VALUES (?, 'applied')", (n,))
    conn.commit()


def stats(conn):
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM companies GROUP BY status")
    return dict(cur.fetchall())


def recent_events(conn, limit=20):
    cur = conn.cursor()
    cur.execute(
        "SELECT company, category, subject, date FROM events "
        "ORDER BY rowid DESC LIMIT ?", (limit,))
    return cur.fetchall()


def companies_by_status(conn, status):
    cur = conn.cursor()
    cur.execute("SELECT name FROM companies WHERE status = ? ORDER BY name", (status,))
    return [r[0] for r in cur.fetchall()]
