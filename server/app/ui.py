"""Admin UI loader — HTML lives in admin.html next to this file.
__SEC__ placeholder is replaced with the secret so the page auto-unlocks."""
import os
from fastapi import Response


def ui_response(secret=''):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin.html')
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()
    import json as _j
    html = html.replace('var SEC = window.__SEC ||', 'var SEC = ' + _j.dumps(secret) + ' ||')
    return Response(content=html, media_type='text/html; charset=utf-8')

