# Tavily Proxy Quick Start

## 启动 Proxy

```bash
cd /var/minis/workspace/tavily-key-generator/proxy
./run_proxy.sh
```

## 添加 Tavily Key

```bash
curl -X POST http://127.0.0.1:9874/api/keys \
  -H "X-Admin-Password: $ADMIN_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{"key":"tvly-REPLACE_WITH_REAL_KEY"}'
```

## 创建访问 Token

```bash
curl -X POST http://127.0.0.1:9874/api/tokens \
  -H "X-Admin-Password: $ADMIN_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{"name":"default"}'
```

## 查看状态

```bash
curl -H "X-Admin-Password: $ADMIN_PASSWORD" http://127.0.0.1:9874/api/stats
curl -H "X-Admin-Password: $ADMIN_PASSWORD" http://127.0.0.1:9874/api/keys
curl -H "X-Admin-Password: $ADMIN_PASSWORD" http://127.0.0.1:9874/api/tokens
```

## Search API

```bash
curl -X POST http://127.0.0.1:9874/api/search \
  -H "Authorization: Bearer tvly-YOUR_PROXY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"latest AI news"}'
```

## Extract API

```bash
curl -X POST http://127.0.0.1:9874/api/extract \
  -H "Authorization: Bearer tvly-YOUR_PROXY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com"]}'
```
