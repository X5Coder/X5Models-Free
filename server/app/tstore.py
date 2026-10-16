"""TOKENS table helpers + ROT + USAGE — mirrors GAS _toks/_e2t/_au/_rot."""
from . import db as D


def tok_by_key(tk):
    with D._lock:
        c = D._connect()
        r = c.execute('SELECT * FROM tokens WHERE token=?', (tk,)).fetchone()
        if not r:
            return None
        return {'email': r['email'], 'created': r['created'], 'dayStart': r['day_start'],
                'freeUsed': r['free_used'], 'paidUsed': r['paid_used'], 'calls': r['calls']}


def tok_by_email(email):
    with D._lock:
        c = D._connect()
        r = c.execute('SELECT token FROM tokens WHERE email=?', (email,)).fetchone()
        return r['token'] if r else None


def tok_save(tk, e):
    with D._lock:
        c = D._connect()
        c.execute('INSERT OR REPLACE INTO tokens VALUES (?,?,?,?,?,?,?)',
                  (tk, e['email'], e['created'], e['dayStart'],
                   e.get('freeUsed', 0), e.get('paidUsed', 0), e.get('calls', 0)))
        c.commit()


def tok_all():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT * FROM tokens').fetchall()
        return {r['token']: {'email': r['email'], 'created': r['created'], 'dayStart': r['day_start'],
                             'freeUsed': r['free_used'], 'paidUsed': r['paid_used'],
                             'calls': r['calls']} for r in rows}


def usage_map():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT * FROM acc_usage').fetchall()
        return {r['email']: {'calls': r['calls'], 'tokens': r['tokens'], 'fails': r['fails']} for r in rows}


def usage_bump(email, tt, failed):
    with D._lock:
        c = D._connect()
        c.execute('INSERT INTO acc_usage VALUES (?,?,?,?) ON CONFLICT(email) DO UPDATE SET '
                  'calls=calls+1, tokens=tokens+excluded.tokens, fails=fails+excluded.fails',
                  (email, 1, tt or 0, 1 if failed else 0))
        c.commit()


def get_rot():
    return D.jget('ROT', {'i': 0})


def set_rot(r):
    D.jset('ROT', r)
