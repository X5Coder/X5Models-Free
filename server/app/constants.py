"""Constants — mirrors GAS section 1."""
DEF_SECRET = 'CHANGE-ME-min-8-chars'
CLINE_API = 'https://api.cline.bot/api/v1'
CACHE_TTL_MS = 30 * 60 * 1000
MODEL_MAP_STALE_MS = 5 * 60 * 1000
DAY_MS = 86400000

HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Cline/0.0.32 ai-sdk/openai-compatible/3.0.37 ai-sdk/provider-utils/5.0.30 runtime/bun/1.3.13',
    'http-referer': 'https://cline.bot',
    'x-client-type': 'cline-desktop',
    'x-client-version': '0.0.32',
    'x-core-version': '0.0.83',
    'x-is-multiroot': 'false',
    'x-platform': 'Cline Desktop',
}

VER = 'v9.1-20251017-balance'
