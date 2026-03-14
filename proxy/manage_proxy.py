#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = os.environ.get("TAVILY_PROXY_URL", "http://127.0.0.1:9874")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def req(method, path, data=None, admin=True):
    url = BASE_URL.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if admin:
        if not ADMIN_PASSWORD:
            print("Missing ADMIN_PASSWORD", file=sys.stderr)
            sys.exit(2)
        headers["X-Admin-Password"] = ADMIN_PASSWORD
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            txt = resp.read().decode("utf-8", errors="replace")
            return resp.status, txt
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        return e.code, txt


def main():
    p = argparse.ArgumentParser(description="Manage Tavily Proxy")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats")
    sub.add_parser("list-keys")
    sub.add_parser("list-tokens")

    ak = sub.add_parser("add-key")
    ak.add_argument("key")
    ak.add_argument("--email", default="")

    aik = sub.add_parser("import-keys")
    aik.add_argument("file")

    ck = sub.add_parser("create-token")
    ck.add_argument("--name", default="default")

    dk = sub.add_parser("delete-key")
    dk.add_argument("id", type=int)

    tk = sub.add_parser("toggle-key")
    tk.add_argument("id", type=int)
    tk.add_argument("active", type=int, choices=[0, 1])

    dt = sub.add_parser("delete-token")
    dt.add_argument("id", type=int)

    cp = sub.add_parser("change-password")
    cp.add_argument("password")

    ts = sub.add_parser("test-search")
    ts.add_argument("token")
    ts.add_argument("query")

    te = sub.add_parser("test-extract")
    te.add_argument("token")
    te.add_argument("url")

    args = p.parse_args()

    if args.cmd == "stats":
        code, txt = req("GET", "/api/stats")
    elif args.cmd == "list-keys":
        code, txt = req("GET", "/api/keys")
    elif args.cmd == "list-tokens":
        code, txt = req("GET", "/api/tokens")
    elif args.cmd == "add-key":
        code, txt = req("POST", "/api/keys", {"key": args.key, "email": args.email})
    elif args.cmd == "import-keys":
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        code, txt = req("POST", "/api/keys", {"file": content})
    elif args.cmd == "create-token":
        code, txt = req("POST", "/api/tokens", {"name": args.name})
    elif args.cmd == "delete-key":
        code, txt = req("DELETE", f"/api/keys/{args.id}")
    elif args.cmd == "toggle-key":
        code, txt = req("PUT", f"/api/keys/{args.id}/toggle", {"active": args.active})
    elif args.cmd == "delete-token":
        code, txt = req("DELETE", f"/api/tokens/{args.id}")
    elif args.cmd == "change-password":
        code, txt = req("PUT", "/api/password", {"password": args.password})
    elif args.cmd == "test-search":
        url = BASE_URL.rstrip("/") + "/api/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {args.token}"}
        body = json.dumps({"query": args.query}).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as resp:
                code, txt = resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            code, txt = e.code, e.read().decode("utf-8", errors="replace")
    elif args.cmd == "test-extract":
        url = BASE_URL.rstrip("/") + "/api/extract"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {args.token}"}
        body = json.dumps({"urls": [args.url]}).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as resp:
                code, txt = resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            code, txt = e.code, e.read().decode("utf-8", errors="replace")
    else:
        p.error("unknown command")

    print(f"HTTP {code}")
    try:
        print(json.dumps(json.loads(txt), ensure_ascii=False, indent=2))
    except Exception:
        print(txt)
    sys.exit(0 if 200 <= code < 300 else 1)


if __name__ == "__main__":
    main()
