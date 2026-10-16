"""SQLite storage layer — mirrors GAS section 2. WAL + single connection + lock."""
import json
import sqlite3
import threading
import time
import os

DB_PATH = os.environ.get('SKREPT_DB', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skrept.db'))
LEGACY_DB = '/srv/data/skrept.db'  # pre-v9.1 path (ephemeral) — auto-migrate if present

_lock = threading.RLock()
_conn = None

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS accounts (
  email TEXT PRIMARY KEY,
  access_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS tokens (
  token TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  created INTEGER NOT NULL,
  day_start INTEGER NOT NULL,
  free_used INTEGER NOT NULL DEFAULT 0,
  paid_used INTEGER NOT NULL DEFAULT 0,
  calls INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_tokens_email ON tokens(email);
CREATE TABLE IF NOT EXISTS acc_usage (
  email TEXT PRIMARY KEY,
  calls INTEGER NOT NULL DEFAULT 0,
  tokens INTEGER NOT NULL DEFAULT 0,
  fails INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS acc_state (
  email TEXT PRIMARY KEY,
  paid_balance REAL NOT NULL DEFAULT 0.5,
  paid_dead INTEGER NOT NULL DEFAULT 0,
  gone INTEGER NOT NULL DEFAULT 0,
  free_blocked_until INTEGER NOT NULL DEFAULT 0,
  paid_spent REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ip_log (ip TEXT NOT NULL, ts INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS idx_ip ON ip_log(ip, ts);
CREATE TABLE IF NOT EXISTS call_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL, model TEXT NOT NULL, email TEXT NOT NULL,
  ok INTEGER NOT NULL, tokens INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS err_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL, code TEXT NOT NULL, detail TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS backup_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL, ok INTEGER NOT NULL);
"""


def _connect():
    global _conn
    with _lock:
        if _conn is None:
            if DB_PATH != LEGACY_DB and not os.path.exists(DB_PATH) and os.path.exists(LEGACY_DB):
                try:
                    import shutil
                    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
                    shutil.copy2(LEGACY_DB, DB_PATH)
                except Exception:
                    pass
            _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
            _conn.row_factory = sqlite3.Row
            _conn.executescript(SCHEMA)
            _conn.execute('PRAGMA synchronous=NORMAL')
            _conn.commit()
        return _conn


def db():
    return _connect()


def jget(key, default=None):
    with _lock:
        c = _connect()
        r = c.execute('SELECT v FROM kv WHERE k=?', (key,)).fetchone()
        if not r:
            return default
        try:
            return json.loads(r['v'])
        except Exception:
            return default


def jset(key, val):
    with _lock:
        c = _connect()
        c.execute('INSERT OR REPLACE INTO kv (k,v) VALUES (?,?)', (key, json.dumps(val)))
        c.commit()


def kv_delete(key):
    with _lock:
        c = _connect()
        c.execute('DELETE FROM kv WHERE k=?', (key,))
        c.commit()
