// Read-only check. Credentials are read from a local file, never printed.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
const token=readFileSync(process.env.LEOBBS_TOKEN_FILE,'utf8').trim()
const client=new Client({name:'http-smoke',version:'1'})
try {
  await client.connect(new StreamableHTTPClientTransport(new URL(process.env.LEOBBS_MCP_HTTP),{requestInit:{headers:{Authorization:`Bearer ${token}`}}}))
  assert.equal((await client.listTools()).tools.length,6)
  const result=await client.callTool({name:'list_boards',arguments:{}})
  assert.ok(!result.isError)
  assert.ok(Array.isArray(result.structuredContent.boards))
  console.log('PASS: Streamable HTTP initialize, tools/list and read-only list_boards')
} finally {await client.close()}
