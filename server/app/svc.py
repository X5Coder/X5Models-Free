"""Models cache + resolve + logs + ip limit — GAS sections 5/7/9."""
import time
from datetime import datetime, timezone
from . import db as D
from . import logic as L
from . import cline as C
from .constants import CACHE_TTL_MS, MODEL_MAP_STALE_MS


def get_models_cache():
    c = D.jget('MODELS_CACHE', None)
    if not c:
        return None
    if not c.get('t') or (int(time.time() * 1000) - c['t']) > CACHE_TTL_MS:
        return None
    return c


def set_models_cache(free, paid):
    D.jset('MODELS_CACHE', {'t': int(time.time() * 1000), 'free': free or [], 'paid': paid or []})


def clear_models_cache():
    D.kv_delete('MODELS_CACHE')
    C.clear_free_cache()


def all_models(force=False):
    if force:
        clear_models_cache()
    c = get_models_cache()
    if c:
        return {'free': c['free'], 'paid': c['paid'], 'cached': True,
                'cache_age_sec': (int(time.time() * 1000) - c['t']) // 1000}
    fx = C.free_list_ex()
    pd = C.live_paid()
    set_models_cache(fx['list'], pd)
    L.save_model_map(fx['list'], pd)
    return {'free': fx['list'], 'paid': pd, 'cached': False, 'cache_age_sec': 0}


def resolve_model(inp):
    if not inp:
        return inp
    mm = L.get_model_map()
    hit = L.lookup_in_map(str(inp), mm)
    if hit:
        return hit
    if not mm.get('t') or (int(time.time() * 1000) - mm['t']) > MODEL_MAP_STALE_MS:
        try:
            allm = all_models(False)
            mm = L.save_model_map(allm['free'], allm['paid'])
            hit = L.lookup_in_map(str(inp), mm)
            if hit:
                return hit
        except Exception:
            pass
    return inp


def log_call(model, email, ok, tt):
    try:
        with D._lock:
            c = D._connect()
            c.execute('INSERT INTO call_log (at,model,email,ok,tokens) VALUES (?,?,?,?,?)',
                      (datetime.now(timezone.utc).isoformat(), str(model or '?'),
                       str(email or '?'), 1 if ok else 0, tt or 0))
            c.execute('DELETE FROM call_log WHERE id NOT IN (SELECT id FROM call_log ORDER BY id DESC LIMIT 40)')
            c.commit()
    except Exception:
        pass


def get_call_log():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT at,model,email,ok,tokens FROM call_log ORDER BY id DESC LIMIT 40').fetchall()
        return [{'at': r['at'], 'model': r['model'], 'email': r['email'],
                 'ok': bool(r['ok']), 'tokens': r['tokens']} for r in rows]


def log_err(code, detail):
    try:
        with D._lock:
            c = D._connect()
            c.execute('INSERT INTO err_log (at,code,detail) VALUES (?,?,?)',
                      (datetime.now(timezone.utc).isoformat(), code, str(detail or '')[:300]))
            c.execute('DELETE FROM err_log WHERE id NOT IN (SELECT id FROM err_log ORDER BY id DESC LIMIT 60)')
            c.commit()
    except Exception:
        pass


def get_err_log():
    with D._lock:
        c = D._connect()
        rows = c.execute('SELECT at,code,detail FROM err_log ORDER BY id DESC LIMIT 60').fetchall()
        return [{'at': r['at'], 'code': r['code'], 'detail': r['detail']} for r in rows]


def ip_limit(ip):
    from . import store as S
    lim = S.get_config().get('ipLimit') or 200
    ip = ip or 'unknown'
    now = int(time.time() * 1000)
    win = 60000
    with D._lock:
        c = D._connect()
        c.execute('DELETE FROM ip_log WHERE ts < ?', (now - win,))
        n = c.execute('SELECT COUNT(*) n FROM ip_log WHERE ip=?', (ip,)).fetchone()['n']
        if n >= lim:
            c.commit()
            return False
        c.execute('INSERT INTO ip_log (ip,ts) VALUES (?,?)', (ip, now))
        c.commit()
        return True


def display_name(mid, tier):
    from . import store as S
    full = str(mid or '')
    sh = L.short_id(full)
    a = S.get_config().get('aliases') or {}
    if a.get(full):
        return a[full]
    if a.get(sh):
        return a[sh]
    return sh + (' (free, 1m/24h)' if tier == 'free' else ' (paid, 200k/24h)')
