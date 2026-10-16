"""Admin API — mirrors GAS section 16 (apiExport/apiLive/apiConfig/apiSet...)."""
from . import svc, store as S, tstore as T
from . import backup as B
from . import logic as L
from . import balance as Bal


def api_export():
    return B.dump_obj()


def api_live():
    allm = svc.all_models(False)
    d = [{'id': L.short_id(x), 'full_id': x, 'tier': 'free',
          'label': svc.display_name(x, 'free')} for x in allm['free']]
    d += [{'id': L.short_id(x), 'full_id': x, 'tier': 'paid',
           'label': svc.display_name(x, 'paid')} for x in allm['paid']]
    return {'free': allm['free'], 'free_count': len(allm['free']),
            'paid_count': len(allm['paid']), 'total_count': len(d),
            'cached': allm['cached'], 'live_models': d,
            'acc_states': Bal.all_states(),
            'call_log': svc.get_call_log(), 'error_log': svc.get_err_log()}


def api_config():
    c = S.get_config()
    return {'config': {'freeLimit': c.get('freeLimit'), 'paidLimit': c.get('paidLimit'),
                       'ipLimit': c.get('ipLimit'), 'tgChat': c.get('tgChat'),
                       'aliases': c.get('aliases'), 'blocked': c.get('blocked')}}


def api_set(b):
    b = b or {}
    nc = S.get_config()
    if b.get('secret') and len(str(b['secret'])) >= 8:
        nc['secret'] = str(b['secret'])
    if b.get('freeLimit') is not None:
        nc['freeLimit'] = max(1000, int(b['freeLimit']))
    if b.get('paidLimit') is not None:
        nc['paidLimit'] = max(1000, int(b['paidLimit']))
    if b.get('ipLimit') is not None:
        nc['ipLimit'] = max(10, int(b['ipLimit']))
    if b.get('tgToken'):
        nc['tgToken'] = str(b['tgToken'])
    if b.get('tgChat'):
        nc['tgChat'] = str(b['tgChat'])
    if b.get('aliasSet'):
        a = b['aliasSet']
        if a.get('name'):
            nc['aliases'][a['id']] = a['name']
        else:
            nc['aliases'].pop(a['id'], None)
    if b.get('block') is not None:
        bl = nc.get('blocked') or []
        if b['block'] not in bl:
            bl.append(b['block'])
        nc['blocked'] = bl
    if b.get('unblock') is not None:
        nc['blocked'] = [x for x in (nc.get('blocked') or []) if x != b['unblock']]
    if b.get('remove_email'):
        S.delete_account(b['remove_email'])
        svc.clear_models_cache()
    if b.get('reset_usage'):
        e = T.tok_by_key(b['reset_usage'])
        if e:
            import time
            e['freeUsed'] = 0
            e['paidUsed'] = 0
            import time as _t
            e['dayStart'] = int(_t.time() * 1000)
            T.tok_save(b['reset_usage'], e)
    if b.get('reset_account'):
        Bal.reset_account(str(b['reset_account']))
    if b.get('reset_all_paid'):
        Bal.reset_all_paid()
    S.set_config(nc)
    return {'saved': True}


def api_backup():
    return {'tg': B.tg_doc(B.dump_obj(), True)}


def api_cache_clear():
    svc.clear_models_cache()
    return {'cleared': True}
