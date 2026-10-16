/************************************************************
 * skrept Worker v8.0 — TRUE streaming passthrough (no buffering)
 *  - يشاور على سيرفر Python (BACKEND_URL) بدل GAS
 *  - أي رد SSE من السيرفر يتحول مباشرة للمستخدم chunk-by-chunk
 *    بدون انتظار وبدون قراءة كاملة (response.body.pipeTo)
 *  - أي رد JSON عادي يتحول كما هو
 *  - CORS مفتوح + يقبل التوكن من Authorization header أو ?key=
 ************************************************************/

const BACKEND_URL = 'https://YOUR-SERVER-DOMAIN'; // skrept-py on VPS via 443+SSL (CF allows only 80/443)
const WORKER_KEY = 'PUT-YOUR-WORKER-KEY-HERE'; // must match WORKER_KEY env on server

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': '*',
};

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    // keep /v1/... path as-is so OpenAI clients work: /v1/models, /v1/chat/completions
    const target = new URL(BACKEND_URL + url.pathname + url.search);

    // مرر الهيدرات المهمة كما هي (Authorization + Content-Type) + مفتاح الوركر
    const headers = new Headers();
    const auth = request.headers.get('Authorization');
    if (auth) headers.set('Authorization', auth);
    const ct = request.headers.get('Content-Type');
    headers.set('Content-Type', ct || 'application/json');
    headers.set('X-Worker-Key', WORKER_KEY);

    const init = {
      method: request.method,
      headers,
      // مرر body الـ request مباشرة كـ stream (بدون قراءة/انتظار)
      body: request.method === 'POST' || request.method === 'PUT' ? request.body : undefined,
      redirect: 'follow',
    };

    const upstream = await fetch(target.toString(), init);

    // مرر هيدرات الـ upstream (خصوصاً text/event-stream) + CORS
    const outHeaders = new Headers(CORS);
    const uctype = upstream.headers.get('Content-Type');
    if (uctype) outHeaders.set('Content-Type', uctype);

    // SSE حقيقي: pipe مباشر من upstream للمستخدم — أول chunk يوصل
    // من السيرفر يتبعت فوراً للمستخدم بدون أي تخزين
    return new Response(upstream.body, {
      status: upstream.status,
      headers: outHeaders,
    });
  },
};
