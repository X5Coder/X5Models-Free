"""Dump object + Telegram backup — GAS sections 14-15. Backup returns the .db file."""
import os
import time
from datetime import datetime, timezone
import httpx
from . import db as D
from . import store as S
from . import tstore as T
from . import balance as Bal


def _state(a, now, u, blk):
    if blk:
        return 'blocked'
    if not a or not a.get('accessToken') or not a.get('refreshToken'):
        return 'broken'
    if a['expiresAt'] <= now - 86400000:
        return 'expired'
    if (u.get('fails') or 0) >= 5 and (u.get('calls') or 0) > 0 and ((u.get('fails') or 0) / (u.get('calls') or 0)) > 0.8:
        return 'failing'
    if a['expiresAt'] <= now:
        return 'refreshing'
    return 'live'


def dump_obj():
    accs = S.get_accounts()
    tks = T.tok_all()
    au = T.usage_map()
    c = S.get_config()
    now = int(time.time() * 1000)
    email2tok = {}
    for tk, e in tks.items():
        email2tok[e['email']] = tk
    states = Bal.all_states()
    out = []
    for a in accs:
        u = au.get(a['email']) or {'calls': 0, 'tokens': 0, 'fails': 0}
        tk = email2tok.get(a['email'], '')
        t = tks.get(tk) or {'freeUsed': 0, 'paidUsed': 0, 'dayStart': now, 'created': 0}
        blk = tk in (c.get('blocked') or [])
        st = states.get(a['email']) or {}
        out.append({
            'account': {'email': a['email'], 'valid': a['expiresAt'] > now,
                        'state': _state(a, now, u, blk)},
            'credentials': {'gateway_token': tk, 'accessToken': a['accessToken'],
                            'refreshToken': a['refreshToken'], 'expiresAt_ms': a['expiresAt']},
            'balance': {'paid_balance': st.get('paid_balance', 0.5),
                        'paid_dead': bool(st.get('paid_dead', False)),
                        'gone': bool(st.get('gone', False)),
                        'free_blocked_until': st.get('free_blocked_until', 0),
                        'paid_spent': st.get('paid_spent', 0.0)},
            'usage': {'free_used': t.get('freeUsed', t.get('free_used', 0)), 'free_limit': c.get('freeLimit') or 1000000,
                      'paid_used': t.get('paidUsed', t.get('paid_used', 0)), 'paid_limit': c.get('paidLimit') or 200000,
                      'total_used': t.get('freeUsed', t.get('free_used', 0)) + t.get('paidUsed', t.get('paid_used', 0)),
                      'reset_at': datetime.fromtimestamp((t.get('dayStart', now) + 86400000) / 1000, tz=timezone.utc).isoformat()},
            'stats': {'calls': u['calls'], 'routed_tokens': u['tokens'], 'fails': u['fails']},
            'blocked': blk})
    return {'date': datetime.now(timezone.utc).isoformat()[:10], 'ok': True, 'count': len(accs),
            'limits': {'free': c.get('freeLimit') or 1000000, 'paid': c.get('paidLimit') or 200000,
                       'ip': c.get('ipLimit') or 200},
            'accounts': out}


def tg_doc(obj, urgent=False):
    """Send the live SQLite .db file to Telegram (fast binary backup)."""
    try:
        c = S.get_config()
        if not c.get('tgToken') or not c.get('tgChat'):
            return {'ok': False, 'err': 'tg not configured'}
        date = datetime.now().strftime('%Y-%m-%d-%H%M')
        D.db().commit()
        for suffix in ('', '-wal'):
            try:
                D.db().execute('PRAGMA wal_checkpoint(TRUNCATE)' if False else 'SELECT 1')
            except Exception:
                pass
        path = D.DB_PATH
        with open(path, 'rb') as f:
            files = {'document': ('backup-%s.db' % date, f, 'application/x-sqlite3')}
            data = {'chat_id': str(c['tgChat']),
                    'caption': ('URGENT backup ' if urgent else 'Daily backup ') + date + ' | accounts: %d' % obj.get('count', 0)}
            r = httpx.post('https://api.telegram.org/bot%s/sendDocument' % c['tgToken'],
                           data=data, files=files, timeout=60.0)
        if r.status_code != 200:
            return {'ok': False, 'code': r.status_code, 'err': r.text[:300]}
        return {'ok': True, 'code': r.status_code}
    except Exception as e:
        return {'ok': False, 'err': str(e)[:200]}


def backup_log_push(ok: bool):
    try:
        with D._lock:
            c = D.db()
            c.execute('INSERT INTO backup_log (at,ok) VALUES (?,?)',
                      (datetime.now(timezone.utc).isoformat(), 1 if ok else 0))
            c.execute('DELETE FROM backup_log WHERE id NOT IN (SELECT id FROM backup_log ORDER BY id DESC LIMIT 30)')
            c.commit()
    except Exception:
        pass


def get_backup_log():
    with D._lock:
        c = D.db()
        rows = c.execute('SELECT at,ok FROM backup_log ORDER BY id DESC LIMIT 30').fetchall()
        return [{'at': r['at'], 'ok': bool(r['ok'])} for r in rows]
