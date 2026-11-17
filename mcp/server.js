import { createForumServer } from './forum-server.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { readFileSync } from 'node:fs'

const configuredUrl = new URL(process.env.LEOBBS_URL || 'http://127.0.0.1:8080')
if (!['http:', 'https:'].includes(configuredUrl.protocol) || configuredUrl.username || configuredUrl.password || configuredUrl.pathname !== '/' || configuredUrl.search || configuredUrl.hash) {
  throw new Error('LEOBBS_URL 必须是 HTTP(S) 站点根地址，不能包含账号、路径、查询参数或片段')
}
const origin = configuredUrl.origin
const token = process.env.LEOBBS_TOKEN_FILE ? readFileSync(process.env.LEOBBS_TOKEN_FILE, 'utf8').trim() : (process.env.LEOBBS_TOKEN || '')
if (token && !/^leo_[0-9a-f]{64}$/.test(token)) throw new Error('Agent Token 格式无效')
const server = createForumServer({ origin, token })
await server.connect(new StdioServerTransport())
