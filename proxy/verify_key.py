#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
import time
from pathlib import Path

BASE_URL = os.environ.get("TAVILY_PROXY_URL", "http://127.0.0.1:9874").rstrip("/")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def admin_req(method, path, data=None):
    if not ADMIN_PASSWORD:
        print("Missing ADMIN_PASSWORD", file=sys.stderr)
        sys.exit(2)
    headers = {"Content-Type": "application/json", "X-Admin-Password": ADMIN_PASSWORD}
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {"raw": txt}


def token_req(path, token, data):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    req = urllib.request.Request(BASE_URL + path, data=json.dumps(data).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {"raw": txt}
    except Exception as e:
        return 599, {"detail": str(e)}


def ensure_proxy_up():
    try:
        code, _ = admin_req("GET", "/api/stats")
        if code == 200:
            return
    except Exception:
        pass

    script = Path(__file__).resolve().parent / "init_proxy.sh"
    if script.exists():
        subprocess.run(["/bin/sh", str(script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(10):
            time.sleep(1)
            try:
                code, _ = admin_req("GET", "/api/stats")
                if code == 200:
                    return
            except Exception:
                pass

    print("Proxy is not reachable.", file=sys.stderr)
    sys.exit(3)


def ensure_token(name="verify-temp"):
    code, data = admin_req("GET", "/api/tokens")
    if code == 200 and data.get("tokens"):
        return data["tokens"][0]["token"], False
    code, data = admin_req("POST", "/api/tokens", {"name": name})
    if code == 200 and data.get("token"):
        return data["token"]["token"], True
    print("Failed to create token", file=sys.stderr)
    print(json.dumps(data, ensure_ascii=False), file=sys.stderr)
    sys.exit(4)


def main():
    ap = argparse.ArgumentParser(description="Add and verify a Tavily key via proxy")
    ap.add_argument("key", help="Real Tavily API key starting with tvly-")
    ap.add_argument("--email", default="")
    ap.add_argument("--query", default="hello world")
    ap.add_argument("--keep-token", action="store_true")
    args = ap.parse_args()

    ensure_proxy_up()

    code, data = admin_req("POST", "/api/keys", {"key": args.key, "email": args.email})
    if code not in (200, 201):
        print(f"ADD_KEY_FAILED HTTP {code}")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(1)

    token, created = ensure_token()
    code, data = token_req("/api/search", token, {"query": args.query})

    result = {
        "add_key_http": 200,
        "verify_http": code,
        "token_used": token,
        "token_created": created,
        "ok": 200 <= code < 300,
        "response": data,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if 200 <= code < 300:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
