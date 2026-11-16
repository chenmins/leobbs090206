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

返回主题 ID、楼层、经典版/移动版链接及 `replayed`。支持 UBB；不能提交 GBK 无法保存的 Emoji。工具标注为真实写入、非删除操作，只有用户授权发布后才能调用；服务端仍验证账号权限、Token 范围和版块限制。

每次新发布使用唯一幂等键，相同发布的网络重试保持键与内容不变。写调用超时为 40 秒（服务端子进程为 30 秒），不会自动重试。`WRITE_OUTCOME_UNKNOWN` 时先读取帖子核查，不得自动换键重发；明确拒绝的请求（如 429）需要修正条件并获得发布授权后才能用新键提交。详细错误、撤销、持久化和单容器限制见 Agent 文档。

只读模式不需要 Token。远程 HTTP MCP、Agent 编辑/删除和私密内容读取尚未实现。

会员可在手机版「个人状态 → Agent 授权」或经典版「控制面板 → Agent 授权」自行获取 Token。创建时选择所需版块及发帖/回复权限，复制只显示一次的密钥到本机私密文件，再配置 `LEOBBS_TOKEN_FILE`。撤销或到期后写入停止，公开搜索与阅读仍可使用。详见 [会员授权说明](../agent/README.md#会员授权管理接口)。
