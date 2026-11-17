# Agent 写接口

API 随论坛的 Apache/Docker 镜像部署，复用经典版 `post.cgi` 的鉴权、权限、过滤、灌水限制和文件写入。首版支持创建主题和回复（含 UBB），不支持编辑、删除、附件上传或私密内容读取。

## 部署

在仓库根目录重新构建并启动论坛：

```sh
docker compose up -d --build
```

程序位于 `/opt/leobbs-agent`，不会被旧的 `persist/cgi-bin` 挂载覆盖。启动脚本在已有 `post.cgi` 中加入共享发帖锁，在 `bbs.lib.pl` 中加入刷新限流的结构化回调；补丁按标记去重，保留 GBK 编码和站点数据。若本地修改破坏了补丁定位点，启动会报错停止，避免静默遗漏。

Token、审计和幂等结果保存于 `persist/cgi-bin/data/agent`；Apache 禁止访问这个目录。目录权限 700、文件权限 600，属于 www-data。备份论坛时同时备份这个目录；丢失幂等记录后不能安全重试旧请求。

运行时锁位于容器内 `/run/leobbs-agent`，避免 Docker Desktop 挂载盘上的文件锁兼容问题。**同一份数据只支持一个论坛写服务容器**；不能让两个容器同时挂载并写入同一数据。重启不丢失已完成的幂等结果。

HTTPS 仍由外层 Caddy 负责，API 返回站内相对链接，不根据代理头拼接外部域名。线上客户端应使用 HTTPS 地址传递 Bearer Token。

## 签发、查看与撤销 Token

会员可以登录后自行创建和撤销自己的授权：手机版首页「个人状态 → Agent 授权」（`/m/agent`），经典版「控制面板 → Agent 授权」（`/cgi-bin/agentpanel.cgi`）。选择名称、允许的操作和版块、7/30/90/365 天有效期，再确认当前账号密码。Token 仅在创建成功时显示一次，离开页面后无法找回，丢失时请撤销并新建。列表显示到期时间、最近使用时间及状态。

管理员仍可使用下列 CLI；建议使用普通会员账号，并明确限制版块和操作。

```sh
docker compose exec -T -u www-data leobbs python3 /opt/leobbs-agent/token-cli.py issue \
  --user chenmin --boards 1 --scopes topics:write,replies:write --days 30

docker compose exec -T -u www-data leobbs python3 /opt/leobbs-agent/token-cli.py list

docker compose exec -T -u www-data leobbs python3 /opt/leobbs-agent/token-cli.py revoke TOKEN_ID
```

签发输出中的 `token` 只展示这一次，妥善保存，不要贴入帖子、日志或 Git。`id` 是非秘密的 Token 标识，用于撤销。数据库只保存 Token 的 SHA-256 摘要，不保存原文。Token 使用 256 位随机数，默认 30 天有效，最多 365 天；账号改密码后旧 Token 失效，禁言/屏蔽账号不能使用。

Token 绑定账号，不能通过请求中的用户名冒充他人。`topics:write` 允许创建主题，`replies:write` 允许回复；两者都必须匹配 Token 允许的版块，并继续通过经典版权限判断。保留 `topics:read` 范围供后续使用，当前公开读取不需要 Token，也不会因此获得私密版块读取权。

## HTTP 接口

```http
POST /api/v1/boards/1/topics
Authorization: Bearer leo_...
Idempotency-Key: 35ef7b11-773e-4f8d-a2fa-d9f9a6e196f1
Content-Type: application/json

{"title":"主题标题","body":"[b]中文正文[/b]","ubb":true,"icon":"00"}
```

```http
POST /api/v1/boards/1/topics/42/replies
Authorization: Bearer leo_...
Idempotency-Key: 452c8d95-1ceb-4154-b5e2-6f654c2f4f98
Content-Type: application/json

{"body":"回复内容","ubb":true}
```

标题 1–80 字符，正文 1–8000 字符，请求最多 64 KiB；经典论坛原有字节长度限制仍生效。`ubb` 默认 true，`icon` 默认 `00`（两位数字）。未知字段、重复 JSON 字段、无效 UTF-8、不可转换为 GBK 的字符会被拒绝，不会静默替换 Emoji。暂不接受用户、密码、隐藏帖、出售或上传参数。

成功返回 HTTP 201：

```json
{"boardId":1,"topicId":42,"floor":1,"url":"/cgi-bin/topic.cgi?forum=1&topic=42","mobileUrl":"/m/1/42?page=1","replayed":false}
```

错误返回非 2xx 状态和一致的 JSON：

```json
{"error":{"code":"RATE_LIMITED","message":"灌水预防机制已经使用，您必须再等待 12 秒钟才能再次发表！","retryAfterSeconds":12}}
```

| HTTP | code 示例 | 含义 |
| --- | --- | --- |
| 400 | INVALID_ARGUMENT / INVALID_JSON / INVALID_IDEMPOTENCY_KEY | 参数无效 |
| 401 | UNAUTHENTICATED / INVALID_ACCOUNT | Token 缺失、过期、撤销或账号凭据失效 |
| 403 | FORBIDDEN / ACCOUNT_DISABLED | Token 范围不允许或账号禁言 |
| 409 | IDEMPOTENCY_CONFLICT | 同一幂等键对应了不同请求 |
| 409 | WRITE_OUTCOME_UNKNOWN | 写入中断或结果无法确认，须核查 |
| 413 / 415 | PAYLOAD_TOO_LARGE / UNSUPPORTED_MEDIA_TYPE | 请求过大或非 JSON |
| 422 | UNSUPPORTED_ENCODING / LEGACY_REJECTED | GBK 不支持或经典版业务拒绝；message 保留具体原因 |
| 429 | RATE_LIMITED | 灌水/刷新限流；返回 Retry-After（可确定时） |
| 500 | INTERNAL_ERROR | 服务故障；不得盲目换键重试 |

经典版的主题不存在、主题锁定、私密版块、积分不足等业务拒绝统一返回 `LEGACY_REJECTED`，不会从 HTML 猜测成功。成功结果由私有 Perl worker 在经典版进入成功分支后生成并核对实际楼层。

## 幂等和审计

每次新发布使用新的 16–128 位幂等键（字母、数字、下划线或连字符，建议 UUID）。同账号下的键跨 Token 生效，作用域包含操作、目标、标题与正文。并发相同请求只执行一次；已完成请求以原 HTTP 状态和结果重放，成功时 `replayed=true`。更改内容而复用键返回 409。

确定被拒绝的请求也记录结果。比如 429 后，应等候指定时间，再由用户决定用新键重新提交；不能自动换键循环发帖。

在调用旧程序前先持久化 pending 记录。如果子进程超时、崩溃或结果无法验证，保留 pending 并返回 `WRITE_OUTCOME_UNKNOWN`。请通过读取主题、审计和论坛记录人工核查，**不要删除记录或换键自动重发**。不对经典多文件存储承诺事务性或自动回滚。幂等结果不自动过期；首版不提供强制清理/恢复接口。

审计 `audit.jsonl` 记录时间、Token ID、账号、目标、操作和结果，不记录 Token、Cookie、密码或正文。

## 测试

```sh
python3 -m unittest discover -s agent/tests
cd mcp && npm ci && npm test && cd ..
docker build -t leobbs-agent-test:local .
python3 agent/tests/integration.py --image leobbs-agent-test:local
```

集成测试将已有 `persist` 复制到临时目录，另起随机本机端口的容器，关闭副本的邮件功能，使用现有测试账号 `cccc` 和 `leoadmin`；测试后删除容器和副本。不会向正在运行的论坛发布测试帖。需 Node.js 22；可用 `LEOBBS_TEST_NODE` 指定 Node 可执行文件。`--source` 可指定初始化数据源；`--keep-on-failure` 保留失败副本供排查（默认清理）。

## 会员授权管理接口

`GET /cgi-bin/agenttokens.cgi` 使用现有登录 Cookie 返回当前会员的授权列表、可授权版块和一次性 `csrf`。列表仅包含 ID、名称、权限、版块、创建/到期/最近使用时间、状态，不返回 Token 摘要、密码或 Token 原文。

`POST /cgi-bin/agenttokens.cgi` 使用同一登录 Cookie、`Content-Type: application/json` 和 `X-CSRF-Token`：

```json
{"action":"create","name":"我的 AI 助手","scopes":["topics:write","replies:write"],"boards":[1],"days":30,"password":"当前账号密码"}
```

成功返回 201，包含只显示一次的 `token`；不能指定其他会员账号。撤销使用 `{"action":"revoke","id":"授权 ID"}`，成功返回 200。其他会员的 ID 返回 404。成功使用过或超过 30 分钟的 CSRF 令牌不能重放，重新 GET 获取新令牌。连续五次密码确认失败后十分钟内禁止继续尝试。所有响应禁止缓存；请求体和密钥不得记录进访问日志。

页面及管理接口位于 `/cgi-bin` 的入口支持经典版仅限该路径的 Cookie。Docker 启动会更新持久化目录内的两个入口，并幂等加入控制面板菜单。移动页及业务程序位于镜像目录，重新构建即可更新。

新增验证：`python3 agent/tests/management_integration.py` 在现有持久化数据的临时副本中测试 Cookie、CSRF、密码、权限变更、列表隔离、创建/撤销及浏览器布局；不向现有论坛发请求。浏览器脚本需要 playwright-core、Chromium/Edge，可用 `LEOBBS_PLAYWRIGHT`、`LEOBBS_BROWSER`、`LEOBBS_TEST_NODE` 指定位置。

图标兼容：MCP/HTTP 的 `icon` 保持两位数字（默认 `00`），Agent 在调用经典 CGI 的共享边界转换为 `00.gif` 等完整文件名。主帖写入主题索引及首楼，回复只设置其楼层图标，不替换主帖图标。幂等请求摘要继续使用两位编号，历史成功结果不重写、不批量迁移帖子。

额外回归：`node --test mobile/web/tests/mcpConnection.test.js` 校验站点根地址与配置生成；管理页集成测试复制实际 JSON 并通过 `mcp/smoke-config.js` 启动 stdio MCP，执行只读检查。发帖集成测试在临时数据中验证默认和非默认图标的主帖/回复存储，以及经典版图片 URL 的 HTTP 200 / image/gif。
