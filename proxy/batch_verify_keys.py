#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def extract_keys(text: str):
    import re
    return re.findall(r"tvly-[A-Za-z0-9\-_]{20,}", text)


def main():
    ap = argparse.ArgumentParser(description="Batch verify Tavily keys via proxy")
    ap.add_argument("file", help="Text file containing Tavily keys")
    ap.add_argument("--query", default="latest AI news")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(json.dumps({"ok": False, "error": "file_not_found", "file": args.file}, ensure_ascii=False))
        sys.exit(2)

    keys = extract_keys(p.read_text(encoding="utf-8", errors="replace"))
    keys = list(dict.fromkeys(keys))
    results = []

    for key in keys:
        proc = subprocess.run(
            [sys.executable, "verify_key.py", key, "--query", args.query],
            cwd=str(Path(__file__).resolve().parent),
            capture_output=True,
            text=True,
        )
        out = (proc.stdout or proc.stderr or "").strip()
        try:
            parsed = json.loads(out)
        except Exception:
            parsed = {"raw": out}
        results.append({
            "key_masked": key[:8] + "***" + key[-4:],
            "exit_code": proc.returncode,
            "ok": proc.returncode == 0,
            "result": parsed,
        })

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
