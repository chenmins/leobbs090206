// Shared by mobile/classic member pages. Takes a URL only, never a Token.
export function buildMcpConnection(siteUrl) {
  const origin = new URL(siteUrl).origin
  const httpUrl = origin + '/mcp'
  const httpToml = `[mcp_servers.leobbs]
url = ${JSON.stringify(httpUrl)}
bearer_token_env_var = "LEOBBS_TOKEN"`
  const httpInstructions = `请帮我使用 Streamable HTTP 接入 LeoBBS MCP：${httpUrl}。使用会员 Agent Token 的 Bearer 鉴权，不使用 OAuth 登录。Codex 配置 url 为此地址，bearer_token_env_var 为 LEOBBS_TOKEN；启动 Codex 的进程环境必须设置该变量，可从仅本人可读的本地 Token 文件加载。不要把真实 Token 写入对话、URL、日志或复制配置。无需在客户端安装论坛源码或 Node.js。连接后先调用 list_boards 只读验证；只有我明确授权后才调用 create_topic 或 reply_topic。撤销或到期后重新签发，更新环境变量并重启客户端。写入结果不明先查询，不要换幂等键重复发帖。`
  const serverPath = '/absolute/path/to/leobbs090206/mcp/server.js'
  const tokenPath = '/absolute/private/path/leobbs-token'
  const env = { LEOBBS_URL: origin, LEOBBS_TOKEN_FILE: tokenPath }
  const json = JSON.stringify({ mcpServers: { leobbs: { command: 'node', args: [serverPath], env } } }, null, 2)
  // These values are an HTTP(S) origin and fixed POSIX path placeholders; JSON
  // string quoting also yields valid TOML basic strings for these values.
  const toml = `[mcp_servers.leobbs]
command = "node"
args = [${JSON.stringify(serverPath)}]

[mcp_servers.leobbs.env]
LEOBBS_URL = ${JSON.stringify(origin)}
LEOBBS_TOKEN_FILE = ${JSON.stringify(tokenPath)}`
  const instructions = `请帮我接入 LeoBBS MCP，论坛站点地址为 ${origin}。
这是在本机启动的 stdio MCP，需要 Node.js 22 或更新版本，不是远程 HTTP MCP 地址。请先获取项目代码 https://github.com/chenmins/leobbs090206，在项目的 mcp 目录执行 npm ci，再用 Node 启动该目录的 server.js。
请根据实际安装位置生成客户端配置：command 为 node，args 为 server.js 的本地绝对路径（示例 ${serverPath}）；env.LEOBBS_URL 为 ${origin}，env.LEOBBS_TOKEN_FILE 为我本机 Token 文件的绝对路径（示例 ${tokenPath}）。不要原样使用路径占位符。不同客户端配置入口不同，没有本地 stdio 支持的客户端不能直接使用此配置。
我会在会员 Agent 授权页选择允许的版块、勾选发布主题/回复主题权限、设置有效期并确认密码签发 Token。Token 只显示一次，应保存到仅本人可读写的本地文件（macOS/Linux 权限 600，Windows 限制文件 ACL），再填写文件路径。不要让我把真实 Token 发到对话、配置示例、日志或页面 URL 中。撤销或到期后需重新签发、更新本地文件并重启 MCP 进程。
连接后先列出工具，或调用 list_boards({}) 验证只读连接；不要为了测试连接自动发帖。纯只读使用可省略 LEOBBS_TOKEN_FILE。
仅在我明确授权发布后调用 create_topic 或 reply_topic。每次新发布生成唯一 idempotencyKey（例如 UUID），相同请求重试保持键与内容不变。遇到限流按 retryAfterSeconds 等待；若明确拒绝的 429 请求已记录，等待后经我确认再以新键提交。若 WRITE_OUTCOME_UNKNOWN 或写入结果不明，先通过 search_topics、list_topics 或 get_topic 查询核对，不能换键重复发布。`
  const examples = [
    { title: '1. 只读检查连接', text: '请先列出 LeoBBS MCP 工具，再调用 list_boards({}) 检查连接，并用 list_topics({"boardId":实际公开版块ID,"page":1}) 阅读主题列表。本次只读，不要创建主题或回复。' },
    { title: '2. 在已授权版块发帖', text: '我授权你在我指定且 Token 已允许的版块发布一篇主题。请先确认版块 ID、标题和正文；确定后调用 create_topic({"boardId":实际版块ID,"title":"确认的标题","body":"确认的正文","ubb":true,"icon":"00","idempotencyKey":"本次新生成的UUID"})，并保留返回的 boardId、topicId 和链接。限流按 retryAfterSeconds 等待；写入结果不明时先查询核对，避免重复发布。' },
    { title: '3. 回复刚发布的同一帖', text: '我授权你回复上一步创建的主题。使用刚返回的 boardId、topicId，先调用 get_topic({"boardId":返回的boardId,"topicId":返回的topicId,"page":1}) 确认是同一帖，再调用 reply_topic({"boardId":返回的boardId,"topicId":返回的topicId,"body":"确认的回复内容","ubb":true,"icon":"00","idempotencyKey":"本次回复新生成的UUID"})。不要猜主题 ID。限流按 retryAfterSeconds 等待；结果不明先查原帖，勿换键重复回复。' },
  ]
  return { origin, json, toml, instructions, examples, httpUrl, httpToml, httpInstructions }
}
