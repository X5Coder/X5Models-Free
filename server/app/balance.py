"""Per-upstream-account balance tracking — v9.1.

Rules (user spec):
- Every upstream Cline account starts with $0.50 of paid credit (local estimate).
- First paid failure caused by money (HTTP 402 / insufficient_credits) =>
  paid_dead=1, never tried again for PAID requests. FREE still tries it.
- Each paid request iterates ALL accounts marked as having balance
  (paid_dead=0, gone=0), keeps going until one succeeds or all are done.
  Only then return an error — and the end-user error is always generic
  ('Come back later'), never "account N is empty".
- Upstream returns the request cost at the end (usage.cost) =>
  automatically deducted from that account's $0.50. Balance <= ~0 => paid_dead.
- Deleted accounts ("user account has been deleted") => gone=1, skipped
  for both paid and free.
- FREE renews daily: on first free failure the account is blocked for that
  tier for 24h (free_blocked_until), other accounts are tried. After 24h it
  becomes eligible again. A free success clears the block.
"""
import time
from . import db as D

PAID_START = 0.50
FREE_BLOCK_MS = 86400000  # 24h
PAID_DEAD_EPS = 0.005  # balance at/below this => treated as empty


def _now():
    return int(time.time() * 1000)


def ensure(email):
    """Create a state row for a new account (never overwrites existing)."""
    if not email:
        return
    with D._lock:
        c = D._connect()
        c.execute(
            'INSERT OR IGNORE INTO acc_state '
            '(email, paid_balance, paid_dead, gone, free_blocked_until, paid_spent) '
            'VALUES (?,?,?,?,?,?)',
            (email, PAID_START, 0, 0, 0, 0.0))
        c.commit()


def ensure_all(emails):
    for e in emails or []:
        ensure(e)


def get_state(email):
    ensure(email)
    with D._lock:
        c = D._connect()
        r = c.execute('SELECT * FROM acc_state WHERE email=?', (email,)).fetchone()
        if not r:
            return {'email': email, 'paid_balance': PAID_START, 'paid_dead': 0,
                    'gone': 0, 'free_blocked_until': 0, 'paid_spent': 0.0}
        return {'email': r['email'], 'paid_balance': r['paid_balance'],
                'paid_dead': r['paid_dead'], 'gone': r['gone'],
                'free_blocked_until': r['free_blocked_until'],
                'paid_spent': r['paid_spent']}


def all_states():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT * FROM acc_state').fetchall()
        return {r['email']: {'paid_balance': r['paid_balance'], 'paid_dead': bool(r['paid_dead']),
                             'gone': bool(r['gone']), 'free_blocked_until': r['free_blocked_until'],
                             'paid_spent': r['paid_spent']} for r in rows}


def mark_paid_dead(email):
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET paid_dead=1 WHERE email=?', (email,))
        c.commit()


def mark_gone(email):
    """Permanently deleted upstream account — skip for paid AND free."""
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET gone=1 WHERE email=?', (email,))
        c.commit()


def block_free(email):
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET free_blocked_until=? WHERE email=?',
                  (_now() + FREE_BLOCK_MS, email))
        c.commit()


def unblock_free(email):
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET free_blocked_until=0 WHERE email=?', (email,))
        c.commit()


def deduct(email, cost):
    """Subtract the upstream-reported request cost from the $0.50 balance."""
    try:
        cost = float(cost or 0)
    except Exception:
        return get_state(email)['paid_balance']
    if cost <= 0:
        return get_state(email)['paid_balance']
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET paid_balance=paid_balance-?, paid_spent=paid_spent+? '
                  'WHERE email=?', (cost, cost, email))
        c.execute('UPDATE acc_state SET paid_dead=1 WHERE email=? AND paid_balance<=?',
                  (email, PAID_DEAD_EPS))
        c.commit()
        r = c.execute('SELECT paid_balance FROM acc_state WHERE email=?', (email,)).fetchone()
        return float(r['paid_balance']) if r else 0.0


def reset_account(email):
    """Admin: give the account a fresh $0.50 and clear all flags."""
    ensure(email)
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET paid_balance=?, paid_dead=0, gone=0, '
                  'free_blocked_until=0, paid_spent=0 WHERE email=?', (PAID_START, email))
        c.commit()


def reset_all_paid():
    with D._lock:
        c = D._connect()
        c.execute('UPDATE acc_state SET paid_balance=?, paid_dead=0, paid_spent=0', (PAID_START,))
        c.commit()


# ---------- upstream response classification ----------

def is_insufficient(code, body):
    """Money failure: HTTP 402 or insufficient_credits / insufficient balance text."""
    try:
        if int(code or 0) == 402:
            return True
    except Exception:
        pass
    b = str(body or '').lower()
    return ('insufficient_credits' in b) or ('insufficient balance' in b)


def is_deleted(body):
    b = str(body or '').lower()
    return ('user account has been deleted' in b) or ('account has been deleted' in b)


def extract_cost(usage):
    """Dollars charged by upstream for this request (usage.cost). 0 if none/free."""
    try:
        u = usage or {}
        return float(u.get('cost') or 0)
    except Exception:
        return 0.0
