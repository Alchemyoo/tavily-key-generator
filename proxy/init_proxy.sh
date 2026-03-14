#!/bin/sh
set -e
cd /var/minis/workspace/tavily-key-generator/proxy

if [ -z "$ADMIN_PASSWORD" ]; then
  echo "Missing ADMIN_PASSWORD"
  echo "Set it in Minis environment variables first."
  exit 1
fi

# Start proxy if not already running
if ! wget -qO- http://127.0.0.1:9874/api/stats --header="X-Admin-Password: $ADMIN_PASSWORD" >/dev/null 2>&1; then
  nohup ./run_proxy.sh > proxy.log 2>&1 &
  echo $! > proxy.pid
  sleep 2
fi

echo "== Proxy stats =="
python3 manage_proxy.py stats || true

echo "\n== Tokens =="
python3 manage_proxy.py list-tokens || true

echo "\n== Keys =="
python3 manage_proxy.py list-keys || true

echo "\nTip: add a real Tavily key with:"
echo "python3 manage_proxy.py add-key tvly-YOUR_REAL_KEY"

echo "\nTip: create a new token with:"
echo "python3 manage_proxy.py create-token --name default"
