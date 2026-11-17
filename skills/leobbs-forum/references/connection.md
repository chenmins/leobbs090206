# LeoBBS MCP 接入

仅在未配置连接或排查连接时读取。先确认目标站点和客户端能力，不擅自覆盖已有 MCP 配置。

## Streamable HTTP（推荐远程连接）

将用户给的页面 URL 取 origin，保留协议、主机和端口，移除页面路径、查询和片段，再加 `/mcp`。
例如 `https://forum.example:8443/m/agent?x=1` 对应 `https://forum.example:8443/mcp`，不是页面 URL 本身。
不硬编码 leobbs.org，也不自动把 HTTP 改成 HTTPS。本地默认可使用 `http://127.0.0.1:8080/mcp`。

会员在「Agent 授权」页选择允许的版块、发帖/回复权限及有效期，确认密码后签发 Token。原文仅显示一次，应保存到仅本人可读写的本地文件（macOS/Linux 600；Windows 限制 ACL）。不要要求把真实 Token 发到聊天、写入 Skill、页面 URL 或日志。

Codex 的 `~/.codex/config.toml` 示例（地址需换成用户的真实站点）：

```toml
[mcp_servers.leobbs]
url = "https://forum.example:8443/mcp"
bearer_token_env_var = "LEOBBS_TOKEN"
```

客户端进程环境中的 `LEOBBS_TOKEN` 存实际 Token。可由用户从受限文件加载再启动客户端；不要在工具输出中打印值。桌面客户端是否继承 shell 环境取决于启动方式，应验证实际连接，不能仅凭配置文件就宣称成功。

其他客户端选择 Streamable HTTP，并使用 `Authorization: Bearer` 请求头；配置结构和环境变量展开语法因客户端而异，不编造通用 HTTP JSON。服务暂不支持 OAuth，也没有旧版 `/sse` 入口；`codex mcp login` 不是此服务的 Token 配置方式。

HTTP 初始化、列工具和只读查询都需要有效 Token；每次请求重新校验。浏览器直接打开 `/mcp` 得到 401 正常；带有效凭据的 GET 返回 405 也正常。用 MCP 客户端初始化、列工具、`list_boards` 验证，不以 GET 判断离线。

到期、撤销或改密码后，会员重新签发 Token 并更新客户端环境，重启连接。读取仍只提供游客可见内容。

## 本地 stdio（兼容原方式）

需要 Node.js 22+。获取项目代码 `https://github.com/chenmins/leobbs090206`，在 `mcp` 目录运行 `npm ci`。
由客户端运行 `node`，args 指向该目录下 `server.js` 的**实际绝对路径**。
设置 `LEOBBS_URL` 为论坛 origin；发帖时设置 `LEOBBS_TOKEN_FILE` 为本地受限 Token 文件的实际绝对路径。不要使用 `http-server.js` 作为 stdio 入口。

```json
{
  "mcpServers": {
    "leobbs": {
      "command": "node",
      "args": ["/absolute/path/to/leobbs090206/mcp/server.js"],
      "env": {
        "LEOBBS_URL": "https://forum.example:8443",
        "LEOBBS_TOKEN_FILE": "/absolute/private/path/leobbs-token"
      }
    }
  }
}
```

stdio 只读可省略 `LEOBBS_TOKEN_FILE`；配置 Token 后出现写工具。Token 文件更新后重启 MCP 进程。
两种方式选一种即可，避免把同一论坛重复配置成多个名称后操作错连接。
