"""X5Coder register client — device flow + register + send to skrept-py server.
Usage:
  python register.py                              # local server 127.0.0.1:8000
  python register.py --server http://host:8000 --secret NEWSECRET
The admin secret defaults to the GAS default; override with --secret or SKREPT_SECRET env.
"""
import argparse
import base64
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import webbrowser

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

_W = "aHR0cHM6Ly9hcGkud29ya29zLmNvbQ=="
_C = "Y2xpZW50XzAxSzNBNTQxRk44VEEzRVBQSFREMjMyNUFS"
_DEFAULT_SECRET = "dlE3I0xtOUBYMiFwUjgkek40JmtUNg=="  # == GAS DEF_SECRET
_CHAT = "https://x5coder.github.io/X5Models-Free/"

_H = {
    "Content-Type": "application/json",
    "User-Agent": "Cline/0.0.32 ai-sdk/openai-compatible/3.0.37 ai-sdk/provider-utils/5.0.30 runtime/bun/1.3.13",
    "http-referer": "https://cline.bot",
    "x-client-type": "cline-desktop",
    "x-client-version": "0.0.32",
    "x-core-version": "0.0.83",
    "x-is-multiroot": "false",
    "x-platform": "Cline Desktop",
}


def _d(s):
    return base64.b64decode(s.encode()).decode()


def _f(u, d, t=30):
    q = urllib.request.Request(
        u, data=urllib.parse.urlencode(d).encode(), method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(q, timeout=t) as r:
            w = r.read().decode(errors="replace")
            try:
                return r.status, json.loads(w)
            except ValueError:
                return r.status, {"e": w[:200]}
    except urllib.error.HTTPError as e:
        w = e.read().decode(errors="replace")[:400]
        try:
            n = json.loads(w)
            if isinstance(n, dict) and isinstance(n.get("error"), str):
                try:
                    return e.code, json.loads(n["error"])
                except ValueError:
                    pass
            return e.code, n if isinstance(n, dict) else {"e": w[:200]}
        except ValueError:
            return e.code, {"e": w[:200]}



def _open_browser(u):
    try:
        if "ANDROID_ROOT" in os.environ or "com.termux" in sys.executable.lower() or os.path.exists("/system/bin/app_process"):
            return
        try:
            webbrowser.get("chrome").open(u)
        except Exception:
            webbrowser.open(u)
    except Exception:
        pass


def _send_account(server, secret, payload):
    url = server.rstrip("/") + "/admin/add_account?admin=" + urllib.parse.quote(secret)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:400]}


def main(server, secret):
    print(f"{YELLOW}Checking...{RESET}")
    c, v = _f(_d(_W) + "/user_management/authorize/device", {"client_id": _d(_C)})
    if c != 200 or not v.get("device_code"):
        print(f"{RED}Initialization error.{RESET}")
        return 1
    u = v.get("verification_uri_complete") or v["verification_uri"]
    print("\n" + "=" * 50)
    print(f"{BOLD}{CYAN}Please open the following link in Chrome:{RESET}")
    print(f"{GREEN}{u}{RESET}\n")
    print(f"{BOLD}User Code:{RESET} {YELLOW}{v['user_code']}{RESET}")
    print("=" * 50)
    print(f"{YELLOW}Waiting for authorization...{RESET}\n")
    _open_browser(u)
    n = max(1, int(v.get("interval", 5)))
    e = time.time() + int(v.get("expires_in", 300))
    t = None
    while time.time() <= e:
        c, t = _f(_d(_W) + "/user_management/authenticate",
                  {"grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                   "device_code": v["device_code"], "client_id": _d(_C)})
        if c == 200 and t.get("access_token"):
            break
        r = t.get("error", "") if isinstance(t, dict) else ""
        if r in ("authorization_pending", "access_denied") or "pending" in str(r).lower():
            time.sleep(n)
            continue
        if r == "slow_down":
            n += 1
            time.sleep(n)
            continue
        print(f"{RED}Authentication failed.{RESET}")
        return 1
    else:
        print(f"{RED}Session timed out.{RESET}")
        return 1
    if not t or not t.get("access_token"):
        print(f"{RED}Authentication failed.{RESET}")
        return 1
    d = json.dumps({"accessToken": t["access_token"], "refreshToken": t["refresh_token"]}).encode()
    q = urllib.request.Request("https://api.cline.bot/api/v1/auth/register", data=d, method="POST", headers=dict(_H))
    try:
        with urllib.request.urlopen(q, timeout=60) as r:
            g = json.load(r)["data"]
    except urllib.error.HTTPError as e:
        print(f"{RED}Error: {e.code}{RESET}")
        return 1
    except Exception:
        print(f"{RED}Failed to register account.{RESET}")
        return 1
    p = {"accessToken": g["accessToken"], "refreshToken": g["refreshToken"],
         "expiresAtMs": int(datetime.datetime.fromisoformat(g["expiresAt"].replace("Z", "+00:00")).timestamp() * 1000),
         "email": g["userInfo"]["email"]}
    code, o = _send_account(server, secret, p)
    if code != 200 or o.get("error"):
        print(f"{RED}Server rejected ({code}): {o}{RESET}")
        return 1
    k = o.get("token", "")
    print("\n" + "=" * 50)
    print(f"{BOLD}{CYAN}Server:{RESET}")
    print(f"{GREEN}{server}{RESET}\n")
    print(f"{BOLD}{CYAN}Account:{RESET} {GREEN}{p['email']}{RESET}\n")
    print(f"{BOLD}{CYAN}Token:{RESET}")
    print(f"{YELLOW}{k}{RESET}\n")
    print("=" * 50 + "\n")
    return 0


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser(description="Register a Cline account on your skrept-py server")
    _p.add_argument("--server", default="http://127.0.0.1:8000", help="skrept-py base URL")
    _p.add_argument("--secret", default=os.environ.get("SKREPT_SECRET") or _d(_DEFAULT_SECRET), help="admin secret")
    _a = _p.parse_args()
    sys.exit(main(_a.server, _a.secret))
