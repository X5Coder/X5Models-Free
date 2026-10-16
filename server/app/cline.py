"""Upstream Cline API + refresh + free/paid lists + pick/rotate — GAS section 8."""
import time
import httpx
from . import store as S
from . import tstore as T
from . import balance as B
from .constants import CLINE_API, HEADERS

_client = httpx.Client(timeout=30.0)


def api(path, method, token, payload=None):
    h = dict(HEADERS)
    if token:
        from .logic import tok_send
        h['Authorization'] = 'Bearer ' + tok_send(token)
    r = _client.request(method, CLINE_API + path, headers=h, json=payload)
    return {'code': r.status_code, 'body': r.text}


def refresh(a, all_accs):
    if a['expiresAt'] - int(time.time() * 1000) > 300000:
        return {'ok': True}
    try:
        rr = api('/auth/refresh', 'post', None, {'refreshToken': a['refreshToken'], 'grantType': 'refresh_token'})
        if rr['code'] == 200:
            import json
            d = json.loads(rr['body'])['data']
            from .logic import tok_save_raw
            from datetime import datetime
            a['accessToken'] = tok_save_raw(d['accessToken'])
            a['refreshToken'] = d['refreshToken']
            try:
                a['expiresAt'] = int(datetime.fromisoformat(str(d['expiresAt']).replace('Z', '+00:00')).timestamp() * 1000)
            except Exception:
                a['expiresAt'] = int(time.time() * 1000) + 3600000
            S.upsert_account(a['email'], a['accessToken'], a['refreshToken'], a['expiresAt'])
            return {'ok': True}
        return {'ok': False, 'err': 'refresh %d' % rr['code']}
    except Exception:
        return {'ok': False, 'err': 'refresh exc'}


_FREE_CACHE = None


def free_list_ex():
    global _FREE_CACHE
    if _FREE_CACHE:
        return _FREE_CACHE
    accs = [a for a in S.get_accounts() if a.get('email') and a.get('accessToken') and a.get('refreshToken')]
    B.ensure_all([a['email'] for a in accs])
    states = B.all_states()
    accs = [a for a in accs if not (states.get(a['email']) or {}).get('gone')]
    seen = {}
    free_ids = []
    last_err = ''
    for ac in accs:
        rf = refresh(ac, accs)
        if not rf['ok']:
            last_err = 'refresh ' + rf['err']
            continue
        rr = api('/ai/cline/recommended-models', 'get', ac['accessToken'])
        if rr['code'] != 200:
            last_err = 'models %d' % rr['code']
            continue
        try:
            import json
            data = json.loads(rr['body']).get('free') or []
        except Exception:
            continue
        for m in data:
            mid = m.get('id')
            if mid and mid not in seen:
                seen[mid] = True
                free_ids.append(mid)
    res = {'list': free_ids, 'err': '' if free_ids else (last_err or 'no accounts')}
    _FREE_CACHE = res
    return res


def free_list():
    return free_list_ex()['list']


def clear_free_cache():
    global _FREE_CACHE
    _FREE_CACHE = None


def live_paid():
    accs = [a for a in S.get_accounts() if a.get('email') and a.get('accessToken') and a.get('refreshToken')]
    B.ensure_all([a['email'] for a in accs])
    states = B.all_states()
    # skip accounts already known empty/deleted for the paid tier
    accs = [a for a in accs if not (states.get(a['email']) or {}).get('paid_dead')
            and not (states.get(a['email']) or {}).get('gone')]
    seen = {}
    all_ids = []
    for a in accs:
        if not refresh(a, accs)['ok']:
            continue
        rr = api('/models', 'get', a['accessToken'])
        if rr['code'] != 200:
            continue
        try:
            import json
            data = json.loads(rr['body']).get('data') or []
        except Exception:
            continue
        for m in data:
            mid = m.get('id')
            if not mid or mid in seen:
                continue
            seen[mid] = True
            all_ids.append(mid)
    try:
        fr = free_list()
    except Exception:
        fr = []
    return [x for x in all_ids if x not in fr]


def is_free(model, fl):
    if not model:
        return True
    if model in fl:
        return True
    if model.startswith('cline-free/'):
        return True
    if model == 'stealth/space-bunny-alpha':
        return True
    return False


def pick():
    all_a = [a for a in S.get_accounts() if a.get('email') and a.get('accessToken')]
    if not all_a:
        return {'err': 'no accounts registered', 'list': []}
    au = T.usage_map()
    scored = []
    for a in all_a:
        u = au.get(a['email']) or {'calls': 0, 'tokens': 0, 'fails': 0}
        scored.append((a, (u.get('tokens') or 0) + (u.get('fails') or 0) * 5000))
    scored.sort(key=lambda x: x[1])
    return {'err': '', 'list': [x[0] for x in scored[:min(3, len(scored))]]}


def rotated(lst):
    if not lst:
        return lst
    r = T.get_rot()
    n = len(lst)
    start = (r.get('i') or 0) % n
    r['i'] = ((r.get('i') or 0) + 1) % n
    T.set_rot(r)
    return [lst[(start + k) % n] for k in range(n)]


def candidates(is_free):
    """ALL eligible upstream accounts for this tier (no top-3 limit).

    Paid: every account with balance left (paid_dead=0, gone=0).
    Free: every non-deleted account whose 24h block has expired.
    Ordered by least usage first + rotation offset so load spreads.
    """
    all_a = [a for a in S.get_accounts() if a.get('email') and a.get('accessToken')]
    if not all_a:
        return []
    B.ensure_all([a['email'] for a in all_a])
    states = B.all_states()
    now = B._now()
    elig = []
    for a in all_a:
        st = states.get(a['email']) or {}
        if st.get('gone'):
            continue
        if is_free:
            if (st.get('free_blocked_until') or 0) > now:
                continue
        else:
            if st.get('paid_dead'):
                continue
        elig.append(a)
    if not elig:
        return []
    au = T.usage_map()
    scored = []
    for a in elig:
        u = au.get(a['email']) or {'calls': 0, 'tokens': 0, 'fails': 0}
        scored.append((a, (u.get('tokens') or 0) + (u.get('fails') or 0) * 5000))
    scored.sort(key=lambda x: x[1])
    ordered = [x[0] for x in scored]
    return rotated(ordered)
