#!/bin/sh
set -e
cd /var/minis/workspace/tavily-key-generator/proxy

if [ -z "$1" ]; then
  echo "Usage: ./add_and_verify_key.sh tvly-REAL_KEY [query]"
  exit 1
fi

KEY="$1"
QUERY="${2:-latest AI news}"

./init_proxy.sh >/dev/null
python3 verify_key.py "$KEY" --query "$QUERY"
