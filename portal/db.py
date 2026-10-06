import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL DEFAULT 'A',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    marks_obtained REAL NOT NULL CHECK (marks_obtained >= 0 AND marks_obtained <= 100),
    UNIQUE (student_id, subject)
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    with conn:
        conn.executescript(SCHEMA)
    conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
