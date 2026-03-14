# Tavily Key Generator + API Proxy

批量注册 Tavily 账户获取 API Key，并通过代理网关池化管理，对外提供统一 API 端点。

## 两个模块

| 模块 | 说明 |
|------|------|
| **Key Generator**（根目录） | 自动批量注册 Tavily 账户，获取 API Key |
| **API Proxy**（`proxy/`） | 将多个 Key 池化，统一出口 + Web 控制台 |

---

## API Proxy（代理网关）

将多个 Tavily API Key 池化，对外暴露统一端点和 Token，附带 Web 管理控制台。

### Proxy 功能

- **Key 池化轮询**：Round-robin 分配请求，连续失败 3 次自动禁用
- **Token 管理**：多个访问 Token，每个独立配额（小时/日/月限制）
- **用量统计**：实时查看成功/失败次数、延迟、配额使用情况
- **Web 控制台**：可视化管理 Key、Token 和用量
- **批量导入**：支持从 `api_keys.md` 格式文本批量导入 Key
- **兼容 Tavily 官方 API**：客户端只需改 base URL

### Docker 部署

```bash
cd proxy/
cp .env.example .env
# 编辑 .env 中的 ADMIN_PASSWORD
docker compose up -d
```

服务运行在 `http://localhost:9874`，访问 `/console` 进入管理控制台。

### 使用方式

1. 访问 `http://localhost:9874/console`，输入管理密码登录
2. 导入 Tavily API Key（支持单个添加或从 `api_keys.md` 批量导入）
3. 创建 Token，复制 Token ID
4. 在应用中调用代理：

```bash
curl -X POST http://localhost:9874/api/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "hello world"}'
```

### Proxy API 参考

**代理端点**（需要 Token 认证）：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/search` | 代理 Tavily Search API |
| POST | `/api/extract` | 代理 Tavily Extract API |

**管理端点**（需要 `X-Admin-Password` 请求头）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/console` | Web 管理控制台 |
| GET | `/api/stats` | 用量统计概览 |
| GET/POST | `/api/keys` | 列出/添加 Key |
| DELETE | `/api/keys/{id}` | 删除 Key |
| PUT | `/api/keys/{id}/toggle` | 启用/禁用 Key |
| GET/POST | `/api/tokens` | 列出/创建 Token |
| DELETE | `/api/tokens/{id}` | 删除 Token |

---

## Key Generator（批量注册）

自动批量注册 Tavily 账户并获取 API Key。

### Generator 功能

- Playwright 浏览器自动化，全流程无人值守
- 自动解决 Cloudflare Turnstile 验证码（CapSolver API）
- 自动接收验证邮件并完成邮箱验证
- 可插拔邮箱后端：Cloudflare Email Worker / DuckMail
- 批量注册，结果自动保存

## 快速开始

```bash
git clone https://github.com/skernelx/tavily-key-generator.git
cd tavily-key-generator
pip install -r requirements.txt
playwright install firefox
cp config.example.py config.py
# 编辑 config.py 填写配置
python main.py
```

## 配置说明

### 验证码（必配）

Tavily 注册页使用 Cloudflare Turnstile 验证码。本工具提供两种解决方式：

| 模式 | 配置值 | 成本 | 成功率 | 说明 |
|------|--------|------|--------|------|
| **CapSolver** | `"capsolver"` | ~$0.001/次 | **高** | **推荐**，稳定可靠，支持后台模式 |
| 浏览器点击 | `"browser"` | 免费 | 低 | 依赖 stealth 补丁，容易被检测，仅供尝试 |

**推荐使用 CapSolver**，注册即送余额，每次解决不到 1 分钱：

```python
CAPTCHA_SOLVER = "capsolver"
CAPSOLVER_API_KEY = "CAP-xxx"   # 从 capsolver.com 获取
```

如果想先试试免费模式（必须前台运行，成功率不高）：

```python
CAPTCHA_SOLVER = "browser"
HEADLESS = False                # 免费模式必须前台运行
```

### 邮箱后端（必配）

需要一个能接收邮件的后端来获取验证链接，二选一：

**方案 A：Cloudflare Email Worker**（自建，免费）

需要自己的域名 + Cloudflare Email Worker（catch-all 模式）。

```python
EMAIL_PROVIDER = "cloudflare"
EMAIL_DOMAIN = "example.com"
EMAIL_PREFIX = "tavily"
EMAIL_API_URL = "https://mail.example.com"
EMAIL_API_TOKEN = "your-token"
```

**方案 B：DuckMail**（第三方临时邮箱）

```python
EMAIL_PROVIDER = "duckmail"
DUCKMAIL_API_BASE = "https://api.duckmail.sbs"
DUCKMAIL_BEARER = "dk_xxx"
DUCKMAIL_DOMAIN = "duckmail.sbs"
```

### 自动上传到 Proxy（可选）

注册成功后自动将 API Key 推送到 Proxy 网关，无需手动导入：

```python
PROXY_AUTO_UPLOAD = True
PROXY_URL = "http://localhost:9874"       # Proxy 地址（支持远程）
PROXY_ADMIN_PASSWORD = "your-password"    # Proxy 管理密码
```

Generator 和 Proxy 不在同一台机器时，填远程地址即可，如 `http://your-server:9874`。

## 输出

注册成功的账户保存在 `api_keys.md`，同时自动上传到 Proxy（如已配置）：

```
邮箱,密码,API Key,时间;
```

## FAQ

**浏览器启动失败？**
运行 `playwright install firefox`。

**验证码失败？**
切换到 `CAPTCHA_SOLVER = "capsolver"`，免费浏览器模式成功率较低。

**收不到验证邮件？**
Cloudflare 模式检查 Worker 是否部署正确；DuckMail 模式检查 API Key 是否有效。

## License

MIT
