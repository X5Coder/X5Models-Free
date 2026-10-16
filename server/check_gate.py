import sys
sys.path.insert(0, r'C:\Users\KIMO\Documents\sketx')
from fastapi.testclient import TestClient
from app.main import app, WORKER_KEY
from app import store, tstore
c = TestClient(app)
sec = store.get_config()['secret']
import urllib.parse as u
H = {'X-Worker-Key': WORKER_KEY}
assert c.get('/').status_code == 200, 'root blocked!'
print('1 / open: OK')
assert c.get('/go/' + u.quote(sec, safe='')).status_code == 200
print('2 UI open: OK')
print('3 OPTIONS:', c.options('/v1/chat/completions').status_code, '(handled by CORS)')
assert c.get('/v1/models').status_code == 403
assert c.get('/v1/models', headers=H).json().get('total_count') == 466
print('4 models gate: OK')
tk = list(tstore.tok_all())[0]
r = c.post('/admin/add_account', params={'admin': sec}, headers=H,
           json={'email': 'g@t.co', 'accessToken': 'A', 'refreshToken': 'R', 'expiresAtMs': 9999999999999})
assert r.status_code == 200, r.text[:150]
print('5 add_account via worker: OK', r.json())
import app.store as S
S.delete_account('g@t.co')
import sqlite3
sq = sqlite3.connect(r'C:\Users\KIMO\Documents\sketx\skrept.db')
sq.execute("DELETE FROM tokens WHERE email='g@t.co'"); sq.commit()
print('ALL OK')
