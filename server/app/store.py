"""CONFIG + ACCOUNTS + TOKENS + USAGE + ROT — mirrors GAS _cfg/_accs/_toks/_au/_rot."""
import time
from . import db as D
from .constants import DEF_SECRET


def get_config():
    c = D.jget('CONFIG', None)
    if not c:
        c = {'secret': DEF_SECRET, 'freeLimit': 1000000, 'paidLimit': 200000,
             'ipLimit': 200,
             'tgToken': '',
             'tgChat': '',
             'aliases': {}, 'blocked': [], 'createdAt': int(time.time() * 1000)}
        D.jset('CONFIG', c)
    if c.get('blocked') is None:
        c['blocked'] = []
    if c.get('aliases') is None:
        c['aliases'] = {}
    return c


def set_config(c):
    D.jset('CONFIG', c)


def get_accounts():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT email, access_token, refresh_token, expires_at FROM accounts').fetchall()
        return [{'email': r['email'], 'accessToken': r['access_token'],
                 'refreshToken': r['refresh_token'], 'expiresAt': r['expires_at']} for r in rows]


def upsert_account(email, at, rt, exp):
    with D._lock:
        c = D._connect()
        c.execute('INSERT OR REPLACE INTO accounts VALUES (?,?,?,?)', (email, at, rt, exp))
        c.commit()


def delete_account(email):
    with D._lock:
        c = D._connect()
        c.execute('DELETE FROM accounts WHERE email=?', (email,))
        c.commit()


def cleanup_accounts():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT email, access_token, refresh_token FROM accounts').fetchall()
        rem = 0
        for r in rows:
            if not (r['email'] and r['access_token'] and r['refresh_token']):
                c.execute('DELETE FROM accounts WHERE email=?', (r['email'],))
                rem += 1
        c.commit()
        kept = c.execute('SELECT COUNT(*) n FROM accounts').fetchone()['n']
        return {'removed_fake': rem, 'kept': kept}
