#!/bin/sh
set -e
cd /var/minis/workspace/tavily-key-generator/proxy

if [ -z "$1" ]; then
  echo "Usage: ./batch_add_and_verify.sh keys.txt [query]"
  exit 1
fi

FILE="$1"
QUERY="${2:-latest AI news}"

./init_proxy.sh >/dev/null
python3 batch_verify_keys.py "$FILE" --query "$QUERY"
