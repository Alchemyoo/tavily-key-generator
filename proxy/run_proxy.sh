#!/bin/sh
set -e
cd /var/minis/workspace/tavily-key-generator/proxy
if [ -z "$ADMIN_PASSWORD" ]; then
  echo "Missing ADMIN_PASSWORD"
  echo "Set it first in Minis environment variables."
  exit 1
fi
exec python3 -m uvicorn server:app --host 0.0.0.0 --port 9874
