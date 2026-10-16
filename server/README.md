# skrept-py — نفس منطق GAS بالظبط، Python + SQLite (v9.1)

## التشغيل
```
pip install -r requirements.txt
python run.py
```

## Endpoints (نفس GAS)
- `GET /v1/models` — قائمة الموديلات (free + paid + cache 30min)
- `GET /v1/models_refresh` — مسح الكاش + تحديث
- `POST /v1/chat/completions` — OpenAI passthrough (tools + tool_calls) مع quota + rotation
  - `stream: false` → JSON عادي بصيغة OpenAI الرسمية
  - `stream: true` → SSE حقيقي لحظي (`text/event-stream` + `data: {...}` + `data: [DONE]`)، يمرر chunks الـ upstream مباشرة لحظة بلحظة
  - يقبل كل حقول OpenAI الرسمية (temperature/top_p/max_tokens/max_completion_tokens/tools/tool_choice/response_format/stop/seed/user/...) وتتمرر كما هي
  - يقبل التوكن عبر `?key=` أو `Authorization: Bearer` header (الرسمي)
- `GET /usage?key=sk-...` — استخدام التوكن
- `GET /ver` — النسخة
- `GET /health` — حالة سريعة

## الأرصدة (v9.1 — نظام 0.50$)
- كل حساب upstream يبدأ برصيد مدفوع `0.50$` (تقدير محلي في جدول `acc_state`).
- أول فشل مدفوع بسبب الفلوس (`402 insufficient_credits`) → `paid_dead=1` ولا يُجرَّب أبداً في المدفوع. المجاني يستمر عليه عادي.
- كل ريكوست مدفوع يجرّب **كل** الحسابات اللي عليها رصيد واحداً واحداً لحد ما ينجح أو يخلصوا كلهم — وساعتها فقط يرجع خطأ عام (`Come back later`) بدون ذكر أي حساب.
- التكلفة اللي يرجعها الـ upstream في الآخر (`usage.cost`) تتخصم تلقائياً من الـ `0.50`.
- الحساب المحذوف (`user account has been deleted`) → `gone=1` ويتخطَّى في المدفوع والمجاني.
- المجاني يتجدد يومياً: أول فشل → حظر 24 ساعة (`free_blocked_until`) ثم يُتاح ويُجرَّب من جديد. النجاح يفك الحظر.

## Admin (نفس GAS: ?admin=SECRET)
- `GET /admin/ui?admin=SECRET` — واجهة الإدارة
- `GET /admin/export` — dump الحسابات (للـ backup)
- `GET /admin/config` — الإعدادات
- `POST /admin/add_account?admin=SECRET` — `{email, accessToken, refreshToken, expiresAtMs}`
- `POST /admin/set?admin=SECRET` — `{freeLimit, paidLimit, ipLimit, secret, tgToken, tgChat, aliasSet:{id,name}, block, unblock, remove_email, reset_usage, reset_account:<email>, reset_all_paid:true}` — `reset_account` يرجّع الحساب لـ `0.50$` ويفك كل الحظر.
- `GET /admin/live` — الموديلات + `acc_states` (رصيد/حظر كل حساب) + call_log + error_log
- `POST /admin/backup?admin=SECRET` — يبعت ملف الـ .db على تليجرام
- `GET /admin/backup.db?admin=SECRET` — تحميل نسخة من ملف قاعدة البيانات مباشرة
- `POST /admin/cleanup?admin=SECRET` — حذف الحسابات الناقصة
- `POST /admin/cache_clear` + `GET /admin/cache_clear` — مسح كاش الموديلات

## التسجيل (سكربت المستخدم — بدل كود X5Coder الأصلي)
```
python start.py
python start.py --server http://YOUR-SERVER:8000 --secret YOUR-SECRET
```
- يعمل device-flow مع WorkOS، ثم `POST /auth/register` على api.cline.bot، ثم يبعت `{accessToken, refreshToken, expiresAtMs, email}` على `POST /admin/add_account?admin=SECRET` في سيرفرك.
- يطبع التوكن `sk-...` في الآخر.
- الكود الأصلي كان بيبعت على سيرفر GAS ثابت (base64 في `_G` + `_K`) — هنا بقى `--server` حر عشان يشاور على سيرفرك المحلي/المنشور.

## التخزين

- ملف واحد `skrept.db` (WAL mode = سريع) — النسخة الاحتياطية = نسخة من الملف نفسه.
- التوكن: `sk-...`، الأدمن = الـ secret.
- الـ quota: free = 1m/24h، paid = 200k/24h (تتصفر كل 24h).
- الـ rotation: أقل الحسابات استهلاكاً + round-robin على **كل** الحسابات المؤهلة (بدون حد top-3).
- قاعدة البيانات في `/app/data/skrept.db` (مجلد persistent داخل الكونتينر).

## محتويات المشروع الكامل
- `app/` — سيرفر FastAPI (الأرصدة في `app/balance.py`)
- `pu/index.html` — واجهة الويب (من GitHub، تُعرض على `/`)
- `start.py` — سكربت التسجيل للعميل (من GitHub: device-flow + register)
- `worker.js` — كود Cloudflare Worker (يتحط في داشبورد كلاود فلير)
