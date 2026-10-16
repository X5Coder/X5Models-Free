"""Upstream streaming via httpx + SSE passthrough helpers."""
import json
import httpx
from .constants import CLINE_API, HEADERS


def stream_api(path, token, payload):
    from .logic import tok_send
    h = dict(HEADERS)
    if token:
        h['Authorization'] = 'Bearer ' + tok_send(token)
    client = httpx.Client(timeout=None)
    req = client.build_request('POST', CLINE_API + path, headers=h, json=payload)
    r = client.send(req, stream=True)
    return client, r


def sse_data(obj) -> bytes:
    return ('data: ' + json.dumps(obj) + '\n\n').encode()


DONE = b'data: [DONE]\n\n'
