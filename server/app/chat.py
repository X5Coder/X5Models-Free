"""Chat passthrough — mirrors GAS section 11."""
import json
import time
import uuid
from . import svc, store as S, tstore as T, cline as C, logic as L, balance as B


def models_response(admin):
    pk = C.pick()
    if pk['err']:
        svc.log_err('no_accounts', pk['err'])
        return ({'error': {'message': pk['err'] if admin else 'Come back later',
                           'type': 'server', 'code': 'no_accounts'}}, 500)
    allm = svc.all_models(False)
    if not allm['free'] and not allm['paid']:
        svc.log_err('no_models', 'no models available')
        return ({'error': {'message': 'no models available' if admin else 'Come back later',
                           'type': 'server', 'code': 'no_models'}}, 500)
    now = int(time.time())
    d = [{'id': L.short_id(x), 'object': 'model', 'created': now, 'owned_by': 'cline',
          'permission': [], 'root': L.short_id(x), 'parent': None, 'full_id': x,
          'tier': 'free', 'label': svc.display_name(x, 'free'), 'quota': '1m/24h'} for x in allm['free']]
    for x in allm['paid']:
        d.append({'id': L.short_id(x), 'object': 'model', 'created': now, 'owned_by': 'cline',
                  'permission': [], 'root': L.short_id(x), 'parent': None, 'full_id': x,
                  'tier': 'paid', 'label': svc.display_name(x, 'paid'), 'quota': '200k/24h'})
    return ({'object': 'list', 'free_count': len(allm['free']), 'paid_count': len(allm['paid']),
             'total_count': len(d), 'cached': allm['cached'], 'cache_age_sec': allm['cache_age_sec'],
             'cache_ttl_sec': 1800, 'data': d}, 200)


INTERNAL_KEYS = ('_tok', 'token', 'api_key', '_ip')


def prepare(body, is_admin, qq):
    """Validate + resolve model + quota. Returns (ok, payload/requested/resolved/is_free/err,code)."""
    if not body.get('model') or not body.get('messages'):
        return (False, {'error': {'message': 'need model+messages', 'type': 'invalid_request_error',
                                  'code': 'bad_request', 'param': None}}, 400, None, None, None)
    # OpenAI official fields — pass through untouched (temperature, top_p, max_tokens,
    # max_completion_tokens, tools, tool_choice, response_format, stop, seed, user, etc.)
    requested = str(body['model'])
    resolved = svc.resolve_model(requested)
    fl = C.free_list()
    fr = C.is_free(resolved, fl)
    if not fl and fr:
        svc.log_err('no_free_models', 'free list unavailable')
        return (False, {'error': {'message': 'free list unavailable' if is_admin else 'Come back later',
                                  'type': 'server', 'code': 'no_free_models'}}, 500, None, None, None)
    if not is_admin and qq:
        if fr and qq['freeLeft'] <= 0:
            return (False, {'error': {'message': 'free quota done, resets ' + qq['resetAt'],
                                      'type': 'insufficient_quota', 'code': 'free_quota', 'param': None}}, 429, None, None, None)
        if (not fr) and qq['paidLeft'] <= 0:
            return (False, {'error': {'message': 'paid quota done, resets ' + qq['resetAt'],
                                      'type': 'insufficient_quota', 'code': 'paid_quota', 'param': None}}, 429, None, None, None)
    payload = dict(body)
    payload['model'] = resolved
    for k in INTERNAL_KEYS:
        payload.pop(k, None)
    return (True, payload, 200, requested, resolved, fr)


def charge(tk, is_admin, fr, total):
    if not is_admin and tk:
        m = T.tok_by_key(tk)
        if m:
            if fr:
                m['freeUsed'] += total
            else:
                m['paidUsed'] += total
            m['calls'] = (m.get('calls') or 0) + 1
            T.tok_save(tk, m)
def _tier_err(is_admin, fr, tried):
    """End-user error is ALWAYS generic — never 'account N is empty'."""
    if fr:
        msg = 'free quota cooling down, try again later'
    else:
        msg = 'no paid balance left, try again later'
    if is_admin:
        return ({'error': {'message': '%s (tried %d)' % (msg, tried),
                           'type': 'server_error', 'code': 'all_failed', 'param': None}}, 500)
    return ({'error': {'message': 'Come back later',
                       'type': 'server_error', 'code': 'all_failed', 'param': None}}, 500)


def _handle_fail(cur, fr, code, body, fails):
    """Classify one upstream failure. Returns True if account is now
    permanently out for this tier (don't retry it in later requests)."""
    email = cur['email']
    if B.is_deleted(body):
        B.mark_gone(email)
        T.usage_bump(email, 0, True)
        return True
    if B.is_insufficient(code, body):
        B.mark_paid_dead(email)  # never again for paid...
        if fr:
            B.block_free(email)  # ...and cool down 24h for free, then retry
        else:
            T.usage_bump(email, 0, True)
        return True
    T.usage_bump(email, 0, True)
    if fr:
        B.block_free(email)  # first free failure => 24h, then eligible again
    return False


def chat_response(body, admin, tk, v):
    is_admin = (v.get('isAdmin') if v else admin)
    qq = v.get('quota') if v else None
    ok, payload, code, requested, resolved, fr = prepare(body, admin, qq)
    if not ok:
        return (payload, code)
    payload['stream'] = False
    order = C.candidates(fr)
    if not order:
        svc.log_err('no_accounts', 'no eligible accounts for tier')
        return _tier_err(is_admin, fr, 0)
    tried = 0
    for o in order:
        cur = next((a for a in S.get_accounts() if a['email'] == o['email']), None)
        if not cur:
            continue
        tried += 1
        rf = C.refresh(cur, S.get_accounts())
        if not rf['ok']:
            T.usage_bump(cur['email'], 0, True)
            continue
        rr = C.api('/chat/completions', 'post', cur['accessToken'], payload)
        if rr['code'] == 200:
            try:
                p = json.loads(rr['body']).get('data') or {}
            except Exception:
                T.usage_bump(cur['email'], 0, True)
                if fr:
                    B.block_free(cur['email'])
                continue
            ch = (p.get('choices') or [{}])[0]
            msg = ch.get('message') or {}
            has_c = bool(msg.get('content') and str(msg['content']))
            has_t = bool(msg.get('tool_calls'))
            if not has_c and not has_t:
                T.usage_bump(cur['email'], 0, True)
                if fr:
                    B.block_free(cur['email'])
                continue
            us = p.get('usage') or {}
            tot = us.get('total_tokens') or 0
            if not fr:
                B.deduct(cur['email'], B.extract_cost(us))  # auto-deduct $ cost from 0.50
            else:
                B.unblock_free(cur['email'])
            charge(tk, is_admin, fr, tot)
            T.usage_bump(cur['email'], tot, False)
            svc.log_call(resolved, cur['email'], True, tot)
            return ({'id': p.get('id') or ('chatcmpl-' + uuid.uuid4().hex[:8]),
                     'object': 'chat.completion', 'created': p.get('created') or int(time.time()),
                     'model': requested,
                     'choices': [{'index': 0, 'message': msg, 'finish_reason': ch.get('finish_reason') or 'stop'}],
                     'usage': us}, 200)
        else:
            svc.log_call(resolved, cur['email'], False, 0)
            _handle_fail(cur, fr, rr['code'], rr['body'], None)
            continue
    svc.log_err('all_failed', 'all %d eligible accounts failed' % len(order))
    return _tier_err(is_admin, fr, tried)


def sse_generator(payload, requested, resolved, fr, tk, is_admin):
    """Real-time SSE passthrough: streams upstream chunks live, rewrites model name.
    Falls back: if upstream has no stream support, does one non-stream call then
    replays it as SSE chunks (still valid SSE for any OpenAI client)."""
    from .ustream import stream_api, sse_data, DONE
    order = C.candidates(fr)
    if not order:
        svc.log_err('no_accounts', 'no eligible accounts for tier (stream)')
        yield sse_data({'error': {'message': 'Come back later',
                                  'type': 'server_error', 'code': 'all_failed'}})
        return
    tried = 0
    for o in order:
        cur = next((a for a in S.get_accounts() if a['email'] == o['email']), None)
        if not cur:
            continue
        tried += 1
        rf = C.refresh(cur, S.get_accounts())
        if not rf['ok']:
            T.usage_bump(cur['email'], 0, True)
            continue
        sp = dict(payload)
        sp['stream'] = True
        try:
            client, r = stream_api('/chat/completions', cur['accessToken'], sp)
        except Exception:
            T.usage_bump(cur['email'], 0, True)
            if fr:
                B.block_free(cur['email'])
            continue
        ok = yield from _stream_one(r, client, cur, sp, requested, resolved, fr, tk, is_admin)
        if ok:
            return
    svc.log_err('all_failed', 'all %d eligible accounts failed (stream)' % len(order))
    yield sse_data({'error': {'message': 'Come back later',
                              'type': 'server_error', 'code': 'all_failed'}})


def _stream_one(r, client, cur, sp, requested, resolved, fr, tk, is_admin):
    from .ustream import sse_data, DONE
    try:
        ctype = r.headers.get('content-type', '')
        if r.status_code != 200 or 'text/event-stream' not in ctype:
            try:
                raw = r.read().decode(errors='replace')
            except Exception:
                raw = ''
            if B.is_deleted(raw):
                B.mark_gone(cur['email'])
                T.usage_bump(cur['email'], 0, True)
                svc.log_call(resolved, cur['email'], False, 0)
                return False
            if B.is_insufficient(r.status_code, raw):
                B.mark_paid_dead(cur['email'])
                if fr:
                    B.block_free(cur['email'])
                else:
                    T.usage_bump(cur['email'], 0, True)
                svc.log_call(resolved, cur['email'], False, 0)
                return False
            try:
                pj = json.loads(raw)
                p = pj.get('data') or pj
            except Exception:
                p = None
            if not p:
                T.usage_bump(cur['email'], 0, True)
                svc.log_call(resolved, cur['email'], False, 0)
                if fr:
                    B.block_free(cur['email'])
                return False
            ch = (p.get('choices') or [{}])[0]
            msg = ch.get('message') or {}
            if not ((msg.get('content') and str(msg['content'])) or msg.get('tool_calls')):
                T.usage_bump(cur['email'], 0, True)
                if fr:
                    B.block_free(cur['email'])
                return False
            cid = p.get('id') or ('chatcmpl-' + uuid.uuid4().hex[:8])
            ctime = p.get('created') or int(time.time())
            yield sse_data({'id': cid, 'object': 'chat.completion.chunk', 'created': ctime,
                            'model': requested,
                            'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})
            content = msg.get('content') or ''
            for i in range(0, len(content), 60):
                yield sse_data({'id': cid, 'object': 'chat.completion.chunk', 'created': ctime,
                                'model': requested,
                                'choices': [{'index': 0, 'delta': {'content': content[i:i + 60]},
                                             'finish_reason': None}]})
            if msg.get('tool_calls'):
                yield sse_data({'id': cid, 'object': 'chat.completion.chunk', 'created': ctime,
                                'model': requested,
                                'choices': [{'index': 0, 'delta': {'tool_calls': msg['tool_calls']},
                                             'finish_reason': None}]})
            yield sse_data({'id': cid, 'object': 'chat.completion.chunk', 'created': ctime,
                            'model': requested,
                            'choices': [{'index': 0, 'delta': {}, 'finish_reason': ch.get('finish_reason') or 'stop'}]})
            yield DONE
            us = p.get('usage') or {}
            tot = us.get('total_tokens') or 0
            if not fr:
                B.deduct(cur['email'], B.extract_cost(us))
            else:
                B.unblock_free(cur['email'])
            charge(tk, is_admin, fr, tot)
            T.usage_bump(cur['email'], tot, False)
            svc.log_call(resolved, cur['email'], True, tot)
            return True
        got_any = False
        total = 0
        cost = 0.0
        try:
            for line in r.iter_lines():
                if not line:
                    continue
                s = line.decode(errors='replace') if isinstance(line, bytes) else line
                s = s.strip()
                if not s.startswith('data:'):
                    continue
                data = s[5:].strip()
                if data == '[DONE]':
                    yield DONE
                    got_any = True
                    break
                try:
                    obj = json.loads(data)
                except Exception:
                    continue
                d = obj.get('data', obj)
                if isinstance(d, dict) and 'model' in d:
                    d['model'] = requested
                if isinstance(d, dict) and isinstance(d.get('usage'), dict):
                    total = d['usage'].get('total_tokens') or total
                    cost = B.extract_cost(d['usage']) or cost
                got_any = True
                yield ('data: ' + json.dumps(d) + '\n\n').encode()
        finally:
            try:
                r.close()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass
        if got_any:
            if not fr:
                B.deduct(cur['email'], cost)
            else:
                B.unblock_free(cur['email'])
            charge(tk, is_admin, fr, total)
            T.usage_bump(cur['email'], total, False)
            svc.log_call(resolved, cur['email'], True, total)
            return True
        T.usage_bump(cur['email'], 0, True)
        if fr:
            B.block_free(cur['email'])
        return False
    except Exception:
        try:
            r.close()
        except Exception:
            pass
        T.usage_bump(cur['email'], 0, True)
        svc.log_call(resolved, cur['email'], False, 0)
        if fr:
            B.block_free(cur['email'])
        return False
