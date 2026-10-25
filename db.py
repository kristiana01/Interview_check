import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent TEXT NOT NULL,
    role TEXT NOT NULL,
    company TEXT NOT NULL DEFAULT '',
    held_on TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS tags (
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (interview_id, tag)
);
"""


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init(path):
    con = connect(path)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
