"""FastAPI server — mirrors GAS sections 12-13 (router + doGet/doPost)."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from . import logic as L, svc, chat as CH, admin as A
from . import store as S, tstore as T, backup as B, balance as Bal
from .constants import VER
from .ui import ui_response
import time

app = FastAPI(title='skrept-py')

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['*'],
)

import os as _os
WORKER_KEY = _os.environ.get('WORKER_KEY', 'CHANGE-ME-worker-key')
WORKER_OPEN = {'/health', '/ver', '/openapi.json', '/docs'}


@app.middleware('http')
async def worker_gate(request: Request, call_next):
    # البوابة: /v1/* و /admin/* و /usage لازم X-Worker-Key (من الوركر فقط).
    # المفتوح دائمًا: /health /ver / الواجهات. الـ OPTIONS يعدي (CORS preflight).
    if request.method == 'OPTIONS':
        return await call_next(request)
    p = request.url.path
    gated = p.startswith(('/v1/', '/admin/', '/usage')) and not p.startswith(('/admin/ui', '/admin/backup.db'))
    if gated and request.headers.get('x-worker-key') != WORKER_KEY:
        return JSONResponse({'error': {'message': 'use the worker endpoint', 'type': 'forbidden', 'code': 'worker_only'}}, 403)
    return await call_next(request)


def qp(request: Request) -> dict:
    return dict(request.query_params)


def is_admin(request: Request) -> bool:
    return L.is_secret(qp(request))


def client_ip(request: Request, q: dict, body: dict) -> str:
    if q.get('_ip'):
        return str(q['_ip'])
    if body and body.get('_ip'):
        return str(body['_ip'])
    xf = request.headers.get('x-forwarded-for')
    if xf:
        return xf.split(',')[0].strip()
    return request.client.host if request.client else 'ip'


def rl(ip):
    if not svc.ip_limit(ip):
        return JSONResponse({'error': {'message': 'rate_limit: IP quota exceeded',
                                       'type': 'rate_limit', 'code': 'ip_rate_limit'}}, 429)
    return None


@app.get('/ver')
def ver():
    return {'ver': VER}


@app.get('/')
def root():
    import os as _o
    p = _o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))), 'pu', 'index.html')
    from fastapi import Response as _R
    with open(p, 'r', encoding='utf-8') as _f:
        return _R(content=_f.read(), media_type='text/html; charset=utf-8')


@app.get('/v1/models')
async def models(request: Request):
    r = rl(client_ip(request, qp(request), {}))
    if r:
        return r
    d, _ = CH.models_response(is_admin(request))
    return d


@app.get('/v1/models_refresh')
async def models_refresh(request: Request):
    svc.clear_models_cache()
    d, _ = CH.models_response(is_admin(request))
    return d


@app.get('/admin/ui')
def admin_ui(request: Request, admin: str = ''):
    tok = admin or qp(request).get('key', '')
    if not tok:
        auth = request.headers.get('authorization', '')
        if auth.lower().startswith('bearer '):
            tok = auth[7:].strip()
    if not L.is_secret({'admin': tok}):
        sec = S.get_config().get('secret') or ''
        import urllib.parse as _u
        return JSONResponse({'error': {'message': 'admin only — open /admin/ui?admin=' + _u.quote(sec, safe='') + ' (note: # must be %23) or paste the secret in the Unlock box'}}, 403)
    return ui_response(tok)


@app.get('/admin/export')
def a_export(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return A.api_export()


@app.get('/admin/config')
def a_config(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return A.api_config()


@app.get('/admin/live')
def a_live(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return A.api_live()


@app.get('/admin/backup_log')
def a_backup_log(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return {'log': B.get_backup_log()}


@app.get('/admin/error_log')
def a_error_log(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return {'log': svc.get_err_log()}


@app.get('/admin/cache_clear')
def a_cache_clear(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    svc.clear_models_cache()
    return {'cleared': True}


@app.get('/admin/backup.db')
def a_backup_db(admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    from . import db as D
    D.db().commit()
    return FileResponse(D.DB_PATH, filename='skrept-backup.db')


@app.get('/usage')
async def usage(request: Request):
    q = qp(request)
    r = rl(client_ip(request, q, {}))
    if r:
        return r
    tk = L.extract_token(q, {})
    v = L.validate_token(tk)
    if not v['ok']:
        return JSONResponse({'error': {'message': v['msg'], 'type': 'authentication_error', 'code': v['code']}}, 401)
    if v.get('isAdmin'):
        ac = S.get_accounts()
        tf = tp = 0
        for _, e in T.tok_all().items():
            tf += e.get('freeUsed', 0)
            tp += e.get('paidUsed', 0)
        return {'admin': True, 'unlimited': True, 'accounts': len(ac),
                'total_free_used': tf, 'total_paid_used': tp, 'total': tf + tp}
    t, qq, c = v['entry'], v['quota'], v['cfg']
    return {'email': t['email'], 'total_free_used': t['freeUsed'], 'total_paid_used': t['paidUsed'],
            'total': t['freeUsed'] + t['paidUsed'], 'free_left': qq['freeLeft'], 'paid_left': qq['paidLeft'],
            'reset_at': qq['resetAt'], 'limit_free': c.get('freeLimit') or 1000000,
            'limit_paid': c.get('paidLimit') or 200000}


@app.post('/v1/chat/completions')
async def chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({'error': {'message': 'invalid JSON body', 'type': 'invalid_request_error', 'code': 'bad_json'}}, 400)
    q = qp(request)
    r = rl(client_ip(request, q, body if isinstance(body, dict) else {}))
    if r:
        return r
    tk = L.extract_token(q, body)
    if not tk:
        auth = request.headers.get('authorization', '')
        if auth.lower().startswith('bearer '):
            tk = auth[7:].strip()
    v = L.validate_token(tk)
    if not v['ok']:
        if body.get('stream'):
            from fastapi.responses import StreamingResponse as _SR
            from .ustream import sse_data as _sse
            def _err():
                yield _sse({'error': {'message': v['msg'], 'type': 'authentication_error', 'code': v['code']}})
            return _SR(_err(), media_type='text/event-stream')
        return JSONResponse({'error': {'message': v['msg'], 'type': 'authentication_error', 'code': v['code']}}, 401)
    adm = is_admin(request)
    if body.get('stream'):
        ok, payload, code, requested, resolved, fr = CH.prepare(body, adm or v.get('isAdmin'), v.get('quota'))
        if not ok:
            from fastapi.responses import StreamingResponse as _SR2
            from .ustream import sse_data as _sse2
            def _err2(p=payload):
                yield _sse2(p)
            return _SR2(_err2(), media_type='text/event-stream')
        from fastapi.responses import StreamingResponse
        return StreamingResponse(CH.sse_generator(payload, requested, resolved, fr, tk, adm or v.get('isAdmin')),
                                 media_type='text/event-stream',
                                 headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
    d, code = CH.chat_response(body, adm, tk, v)
    return JSONResponse(d, code)


@app.post('/admin/add_account')
async def a_add(request: Request, admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    b = await request.json()
    if not (b.get('accessToken') and b.get('refreshToken') and b.get('expiresAtMs') and b.get('email')):
        return JSONResponse({'error': {'message': 'need accessToken refreshToken expiresAtMs email'}}, 400)
    S.upsert_account(b['email'], L.tok_save_raw(b['accessToken']), b['refreshToken'], int(b['expiresAtMs']))
    Bal.ensure(b['email'])  # fresh $0.50 balance row, never touches existing rows
    svc.clear_models_cache()
    return {'saved': b['email'], 'count': len(S.get_accounts()), 'token': L.mint(b['email'])}


@app.post('/admin/set')
async def a_set(request: Request, admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return A.api_set(await request.json())


@app.post('/admin/backup')
async def a_backup(request: Request, admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return A.api_backup()


@app.post('/admin/cleanup')
async def a_cleanup(request: Request, admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return S.cleanup_accounts()


@app.post('/admin/cache_clear')
async def a_cache_clear_p(request: Request, admin: str = ''):
    if not L.is_secret({'admin': admin}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    svc.clear_models_cache()
    return {'cleared': True}


@app.get('/health')
def health():
    return {'ok': True, 'ver': VER, 'accounts': len(S.get_accounts())}


# LAST route: secret-in-path UI (/go/<secret>) — avoids ? & # issues entirely
@app.get('/go/{secret}')
def admin_ui_path(secret: str):
    import urllib.parse as _u
    tok = _u.unquote(secret)
    if not L.is_secret({'admin': tok}):
        return JSONResponse({'error': {'message': 'admin only'}}, 403)
    return ui_response(tok)
