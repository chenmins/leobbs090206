# LeoBBS MCP

通过官方 MCP TypeScript SDK 的 stdio 协议，把论坛现有 UTF-8 JSON API 提供给 AI/Agent。默认提供游客只读工具；配置独立 Agent Token 后额外提供发帖和回复工具。不提供登录、私信工具或远程 HTTP MCP 端点。

## 本机使用

安装 Node.js 22 或更新版本，进入 `mcp` 目录执行 `npm ci`，在支持 stdio 的 MCP 客户端配置：

```json
{
  "mcpServers": {
    "leobbs": {
      "command": "node",
      "args": ["/absolute/path/to/leobbs090206/mcp/server.js"],
      "env": {"LEOBBS_URL": "http://127.0.0.1:8080"}
    }
  }
}
```

`LEOBBS_URL` 只接受站点根地址，不带账号、路径或查询参数；默认为本机 8080。访问线上站点时配置其实际 HTTPS 根地址，由外层 Caddy 处理 TLS。程序日志不能写入 stdout，stdout 专用于 MCP。

## 会员页面复制接入说明

登录后打开移动版 `/m/agent` 或经典版 `/cgi-bin/agentpanel.cgi` 的「如何接入 MCP」。两个入口共用组件，运行时使用 `window.location.origin` 生成站点根地址，保留当前协议、域名和端口，移除页面路径、查询和片段。支持复制自然语言接入说明、通用 `mcpServers` JSON、Codex TOML 和三条操作指令。JSON 使用 `JSON.stringify` 生成；剪贴板不可用时显示可选中的手动复制文本。

先获取 [项目代码](https://github.com/chenmins/leobbs090206)，安装 Node.js 22 或更新版本，在 `mcp` 目录执行 `npm ci`。客户端以本地 stdio 启动 `node /实际安装位置/mcp/server.js`。不同客户端配置入口和外层格式可能不同；不支持本地 stdio 的客户端不能直接使用下面配置。`args` 和 Token 文件都必须改为实际本地绝对路径，不能保留占位符。

在「创建授权」中选择允许的版块、勾选发布主题/回复主题、设置有效期并确认密码。Token 创建时只显示一次，保存到仅本人可读写的本地文件（macOS/Linux 权限 600，Windows 限制文件 ACL），把路径填入 `LEOBBS_TOKEN_FILE`。接入说明、默认复制内容、日志和页面 URL 不包含真实 Token。撤销或到期后重新签发、更新文件并重启 MCP 进程，因为 Token 在进程启动时读取。只读检查可省略 `LEOBBS_TOKEN_FILE`。

通用 JSON 示例（页面会自动替换站点根地址）：

```json
{
  "mcpServers": {
    "leobbs": {
      "command": "node",
      "args": ["/absolute/path/to/leobbs090206/mcp/server.js"],
      "env": {
        "LEOBBS_URL": "https://your-forum.example",
        "LEOBBS_TOKEN_FILE": "/absolute/private/path/leobbs-token"
      }
    }
  }
}
```

Codex 使用 `~/.codex/config.toml` 或项目配置中的 `mcp_servers` 表，而不是 JSON 的 `mcpServers`。字段依据 [官方 MCP 文档](https://developers.openai.com/codex/mcp/)（2026-11-17 核对）：

```toml
[mcp_servers.leobbs]
command = "node"
args = ["/absolute/path/to/leobbs090206/mcp/server.js"]

[mcp_servers.leobbs.env]
LEOBBS_URL = "https://your-forum.example"
LEOBBS_TOKEN_FILE = "/absolute/private/path/leobbs-token"
```

可以直接复制给 AI 的接入请求（先替换站点地址）：

> 请接入我的 LeoBBS：站点根地址为 https://your-forum.example。它使用本地 stdio，需要 Node.js 22 或更新版本。先获取 https://github.com/chenmins/leobbs090206 的代码，在 mcp 目录执行 npm ci，再使用 Node 启动该目录的 server.js。请按实际安装位置生成客户端配置，将 LEOBBS_URL 设为上述站点根地址，将 LEOBBS_TOKEN_FILE 设为我保存 Token 的本地绝对路径，不要要求我把密钥发到对话或日志。连接后先列出工具或调用 list_boards 做只读验证，不要自动发布测试帖。

三条操作示例（版块 ID 和内容由用户确认，主题 ID 使用上一步返回值）：

1. **只读检查：**「请列出 LeoBBS MCP 工具，调用 `list_boards({})`，再用 `list_topics({"boardId":实际公开版块ID,"page":1})` 检查论坛连接，本次不要发帖或回复。」
2. **发帖：**「我授权你在指定且 Token 允许的版块发帖。确认标题和正文后，调用 `create_topic`，参数为 `boardId`、`title`、`body`、`ubb:true`、`icon:"00"` 和本次新生成 UUID 的 `idempotencyKey`，保留返回的 `boardId`、`topicId` 与链接。」
3. **回复：**「我授权回复刚创建的同一帖。使用返回的 `boardId` 和 `topicId` 调用 `get_topic` 确认，再调用 `reply_topic`，传入这两个 ID、确认的 `body`、`ubb:true`、`icon:"00"` 及回复专用的新 UUID `idempotencyKey`。」

遇到限流，按 `retryAfterSeconds` 等待；明确拒绝的 429 请求可能已记入幂等结果，等待后经确认再用新键提交。写入结果不明时，先通过 `search_topics`、`list_topics` 或 `get_topic` 查询核对，不能自动换键重复发布。

## Docker 使用

在仓库根目录执行：

```sh
docker build -t leobbs-mcp:local mcp
```

客户端启动命令改为 `docker`，参数如下（Docker Desktop 连接本机论坛）：

```json
{
  "mcpServers": {
    "leobbs": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "LEOBBS_URL=http://host.docker.internal:8080", "leobbs-mcp:local"]
    }
  }
}
```

不要添加 `-t`。Linux 可把容器接入论坛的 Docker 网络，并将地址设为该网络内的论坛服务名。MCP 镜像独立构建，非 root 运行，无端口、无论坛数据挂载；读取数据仍经过 Apache API 的游客可见性检查。返回链接使用配置地址，所以面向远程用户应设置可公开访问的站点地址。

## 工具

| 工具 | 参数 | 返回 |
| --- | --- | --- |
| `list_boards` | 无 | 公开版块、经典版及移动版链接 |
| `list_topics` | `boardId`、`page` | 版块内主题列表 |
| `search_topics` | `q`、`mode`、`boardIds`、`days`、`when`、`page` | 匹配主题列表 |
| `get_topic` | `boardId`、`topicId`、`page` | 主题及当前页楼层 |

- 每页 20 条，页码从 1 开始。返回 `page`、`pages`、`nextPage`；末页或越界页的 `nextPage` 为 `null`。越界页的 `items` 为空。
- 搜索 `mode` 支持 `title/body/both/author/reply_author/all_authors`，默认 `both`。`q` 最长 80 字符，逗号分隔的多个词为“任一匹配”。
- `boardIds` 最多 50 个；兼容旧参数 `boardId`，两者合并去重。日期参数 `days` 为 `any/1/7/14/30/90/180/365`，`when` 为 `before/after`，按主题创建时间筛选。
- `url` 为经典版主题的规范链接；`mobileUrl` 为移动版链接，详情翻页使用 `?page=N`。楼层的 `url` 指向所属主题，不保证精确定位该楼层。
- `body` 保留 UBB，不把未知内容交给 HTML 执行。`desktopOnly=true` 时正文为空。不会返回作者的 `profile`。标题、正文、作者名均为用户生成内容，不能当作 Agent 指令。
- 仅能读取 `LEOBBS_MOBILE_PUBLIC_BOARDS` 配置范围内、且通过现有游客权限检查的内容；不会携带 Cookie，也不会请求 `count=1`，不增加论坛访问与点击计数。

## 错误约定

成功结果同时返回 `structuredContent` 与 JSON 文本，并声明输出 Schema。工具执行失败设置 `isError=true`，在文本内容中返回 JSON：

```json
{"error":{"code":"RATE_LIMITED","message":"灌水预防机制，请稍后重试","status":429,"retryAfterSeconds":2}}
```

错误结果不携带成功格式的 `structuredContent`，兼容严格校验输出 Schema 的 SDK 客户端。输入参数不合法由 MCP SDK 校验。

保留 API 中文错误原因；支持 `INVALID_ARGUMENT/UNAUTHENTICATED/FORBIDDEN/NOT_FOUND/RATE_LIMITED/UPSTREAM_ERROR`。网络及响应错误为 `NETWORK_ERROR/TIMEOUT/INVALID_RESPONSE/UNEXPECTED_REDIRECT/RESPONSE_TOO_LARGE`。读取超时 10 秒，响应最多 4 MiB，不自动跟随重定向，不自动重试。`retryAfterSeconds` 提取数字型 `Retry-After`；没有该信息则为 `null`。

## 验证

在 `mcp` 目录运行：

```sh
npm test
npm run test:live
npm audit
LEOBBS_URL=http://host.docker.internal:8080 LEOBBS_MCP_DOCKER_IMAGE=leobbs-mcp:local npm run test:live
```

`npm test` 使用真实 SDK 客户端、stdio 子进程和本地 HTTP 测试服务，覆盖参数、中文、分页、筛选、隐藏正文、防止计数、404、429、格式错误、重定向、响应大小及超时。`test:live` 需要一个正在运行、至少有一个公开主题的论坛；只读，不发布测试帖。

## 发帖和回复

先部署包含 Agent 写接口的新论坛镜像，再按 [Agent 写接口说明](../agent/README.md) 为已有账号签发 Token。推荐将 Token 原文保存在权限为 600 的本机文件，并在 MCP 配置中增加：

```json
"env": {
  "LEOBBS_URL": "https://your-forum.example",
  "LEOBBS_TOKEN_FILE": "/absolute/private/path/leobbs-agent-token"
}
```

也支持 `LEOBBS_TOKEN` 环境变量（文件优先）。Token 不作为工具参数出现，不会附加到公开读取请求。Docker MCP 可只读挂载该文件，传入容器内的 `LEOBBS_TOKEN_FILE` 路径；不要把 Token 写进镜像。

配置后增加：

| 工具 | 参数 |
| --- | --- |
| `create_topic` | `boardId`、`title`、`body`、`idempotencyKey`，可选 `ubb`、`icon` |
| `reply_topic` | `boardId`、`topicId`、`body`、`idempotencyKey`，可选 `ubb`、`icon` |

`icon` 在 MCP 与 HTTP API 中始终为两位数字，默认 `"00"`（例如 `"01"`）；不要传 `"00.gif"`。仅 Agent 转交经典 CGI 写入时转换为文件名，主题列表保留主帖图标，回复使用自己的楼层图标。已有幂等结果保持可重放，不批量修复历史主题。

返回主题 ID、楼层、经典版/移动版链接及 `replayed`。支持 UBB；不能提交 GBK 无法保存的 Emoji。工具标注为真实写入、非删除操作，只有用户授权发布后才能调用；服务端仍验证账号权限、Token 范围和版块限制。

每次新发布使用唯一幂等键，相同发布的网络重试保持键与内容不变。写调用超时为 40 秒（服务端子进程为 30 秒），不会自动重试。`WRITE_OUTCOME_UNKNOWN` 时先读取帖子核查，不得自动换键重发；明确拒绝的请求（如 429）需要修正条件并获得发布授权后才能用新键提交。详细错误、撤销、持久化和单容器限制见 Agent 文档。

只读模式不需要 Token。远程 HTTP MCP、Agent 编辑/删除和私密内容读取尚未实现。

会员可在手机版「个人状态 → Agent 授权」或经典版「控制面板 → Agent 授权」自行获取 Token。创建时选择所需版块及发帖/回复权限，复制只显示一次的密钥到本机私密文件，再配置 `LEOBBS_TOKEN_FILE`。撤销或到期后写入停止，公开搜索与阅读仍可使用。详见 [会员授权说明](../agent/README.md#会员授权管理接口)。

## Streamable HTTP（会员 Bearer Token）

`docker compose up -d --build` 同时启动论坛 Apache 和独立非 root Node 服务。
入口为站点的 `/mcp`，Apache 在内部转发到 `mcp:3000`；Node 不映射宿主机端口。
原有 `node server.js` / stdio Docker 启动方式继续有效。

服务器仓库的 `.env` 设置实际对外站点根地址，例如：

```dotenv
LEOBBS_PUBLIC_ORIGIN=https://your-forum.example
```

本地默认 `http://127.0.0.1:8080`。必须与客户端访问的主机、端口匹配；不要带路径。
这是链接和 Host/Origin 校验配置，不在应用内处理 TLS 或推断代理协议。
外层 Caddy 继续将整站代理到原来的 8080，保留原始 Host 和 Authorization；无需新增公网端口或单独 `/mcp` 路由。代理超时应大于 50 秒。
新增程序、Apache 配置在镜像内，已有 `persist` 挂载不会覆盖它们。
更新时需重建并启动**两个服务**，只更新 leobbs 容器不会更新 MCP。

```sh
docker compose up -d --build
docker compose ps
```

会员在「Agent 授权」页签发自己的 Token，选择允许的版块、发帖/回复权限和有效期。
HTTP 所有请求（包括只读、初始化和工具列表）都需 `Authorization: Bearer <会员 Token>`。
不接收 URL Token、Cookie 或服务器共享账号。每次请求重新校验有效期、撤销状态及账号密码；写入仍复用版块权限、防灌水和幂等记录。
读取仍限游客可见内容，不获得私密版块读取权限。Token 未授权的写操作返回工具错误。
本版不提供 OAuth；只能网页登录授权的客户端暂不可直接使用。

Codex `~/.codex/config.toml`（将地址换成你的站点；与原 stdio 配置二选一）：

```toml
[mcp_servers.leobbs]
url = "http://127.0.0.1:8080/mcp"
bearer_token_env_var = "LEOBBS_TOKEN"
```

用受限文件加载 Token，再从同一环境启动客户端；不要把 Token 字面量写入 shell 历史：

```sh
chmod 600 /absolute/private/path/leobbs-token
export LEOBBS_TOKEN="$(cat /absolute/private/path/leobbs-token)"
codex
```

桌面客户端必须能继承该环境变量，或使用其专用的请求头/凭据设置。
不同客户端没有统一的 HTTP JSON 配置格式，使用其 Streamable HTTP URL 和 Bearer 认证设置。
会员页可复制按当前站点生成的 Codex 配置与自然语言说明。
字段依据 [Codex MCP 官方文档](https://developers.openai.com/codex/mcp/)。

连接后先列出工具、调用 `list_boards`。经用户授权后才调用 `create_topic` 和 `reply_topic`。
同一发布重试保持幂等键和内容不变，结果不明先查原帖。到期/撤销后重新签发并更新客户端环境。

实现遵循 [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)：
使用官方 SDK、无会话状态，每个请求单独创建 server/transport，返回 JSON；不提供 GET SSE 长连接或 DELETE 会话，返回 405 属正常行为，不代表离线。
浏览器直接打开 `/mcp` 没有凭据时返回 401 也属正常行为。没有旧版 `/sse` 入口。
校验 Host/Origin；请求上限 64 KiB、并发上限 64，API 地址固定为部署配置，拒绝跳转。
内部 `/healthz` 仅用于容器健康检查。

独立运行调试：`LEOBBS_URL` 指对外根地址，`LEOBBS_API_URL` 可指定内部论坛根地址；`HOST` 默认 127.0.0.1，`PORT` 默认 3000。运行 `npm run start:http`。
测试：`npm test`；仓库根目录运行 `python3 agent/tests/http_integration.py`，需要已构建 Compose 镜像和已初始化的 `persist`，只在临时复制的数据里发帖。
