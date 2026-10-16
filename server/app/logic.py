"""Token utilities + quota + short/modelmap — mirrors GAS sections 3-4."""
import time
import uuid
from datetime import datetime, timezone
from . import db as D
from . import tstore as T
from . import store as S
from .constants import DEF_SECRET, MODEL_MAP_STALE_MS, DAY_MS


def is_secret(params: dict) -> bool:
    sec = S.get_config().get('secret') or DEF_SECRET
    return params.get('key') == sec or params.get('admin') == sec or \
        params.get('secret') == sec or params.get('api_key') == sec


def tok_save_raw(t):
    return str(t or '')


def tok_send(t):
    t = str(t or '')
    return t if t.startswith('workos:') else 'workos:' + t


def extract_token(query: dict, body: dict) -> str:
    for k in ('key', 'api_key', 'token'):
        if query.get(k):
            return str(query[k])
    if query.get('auth'):
        a = str(query['auth'])
        return a[7:] if a.lower().startswith('bearer ') else a
    if not body:
        return ''
    for k in ('_tok', 'token', 'api_key'):
        if body.get(k):
            return str(body[k])
    return ''


def is_admin_tok(tk) -> bool:
    return tk == (S.get_config().get('secret') or DEF_SECRET)


def mint(email: str) -> str:
    old = T.tok_by_email(email)
    if old and T.tok_by_key(old):
        return old
    tk = 'sk-' + uuid.uuid4().hex[:24]
    now = int(time.time() * 1000)
    T.tok_save(tk, {'email': email, 'created': now, 'dayStart': now,
                    'freeUsed': 0, 'paidUsed': 0, 'calls': 0})
    return tk


def quota(cfg, t):
    now = int(time.time() * 1000)
    if now - t['dayStart'] > DAY_MS:
        t['dayStart'] = now
        t['freeUsed'] = 0
        t['paidUsed'] = 0
    return {'freeLeft': (cfg.get('freeLimit') or 1000000) - t['freeUsed'],
            'paidLeft': (cfg.get('paidLimit') or 200000) - t['paidUsed'],
            'resetAt': datetime.fromtimestamp((t['dayStart'] + DAY_MS) / 1000, tz=timezone.utc).isoformat()}


def validate_token(tk):
    if not tk:
        return {'ok': False, 'code': 'no_token', 'msg': 'missing token', 'stage': 1}
    if is_admin_tok(tk):
        return {'ok': True, 'isAdmin': True, 'stage': 2}
    t = T.tok_by_key(tk)
    if not t:
        return {'ok': False, 'code': 'bad_token', 'msg': 'invalid token', 'stage': 3}
    c = S.get_config()
    if tk in (c.get('blocked') or []):
        return {'ok': False, 'code': 'blocked', 'msg': 'token blocked', 'stage': 4}
    return {'ok': True, 'isAdmin': False, 'token': tk, 'entry': t, 'quota': quota(c, t), 'cfg': c, 'stage': 5}


def short_id(mid):
    s = str(mid or '')
    i = s.rfind('/')
    return s if i == -1 else s[i + 1:]


def get_model_map():
    m = D.jget('MODELMAP', None)
    if m and m.get('map') is not None and m.get('free') is not None and m.get('paid') is not None:
        return m
    return {'t': 0, 'map': {}, 'free': [], 'paid': []}


def save_model_map(free, paid):
    mp = {}
    for full in (free or []) + (paid or []):
        sh = short_id(full)
        if sh not in mp:
            mp[sh] = full
    m = {'t': int(time.time() * 1000), 'map': mp, 'free': free or [], 'paid': paid or []}
    D.jset('MODELMAP', m)
    return m


def lookup_in_map(inp, mm):
    if not inp or not mm:
        return ''
    if inp in mm['free']:
        return inp
    if inp in mm['paid']:
        return inp
    if inp in mm['map']:
        return mm['map'][inp]
    s = short_id(inp)
    if s != inp and s in mm['map']:
        return mm['map'][s]
    return ''
