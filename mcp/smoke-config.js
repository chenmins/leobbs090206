// Loads actual clipboard JSON from the isolated browser test. Substitute only
// documented local path placeholders; preserve the page-generated site origin.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
const config = JSON.parse(readFileSync(process.env.LEOBBS_COPIED_CONFIG, 'utf8')).mcpServers.leobbs
assert.equal(config.command, 'node')
assert.equal(config.env.LEOBBS_URL, process.env.LEOBBS_TEST_ORIGIN)
assert.equal(config.args[0], '/absolute/path/to/leobbs090206/mcp/server.js')
assert.equal(config.env.LEOBBS_TOKEN_FILE, '/absolute/private/path/leobbs-token')
config.args[0] = resolve('server.js')
config.env.LEOBBS_TOKEN_FILE = process.env.LEOBBS_TEST_TOKEN_FILE
const client = new Client({name:'clipboard-config-test', version:'1'})
try {
  await client.connect(new StdioClientTransport({...config, env:{...process.env, ...config.env}}))
  assert.equal((await client.listTools()).tools.length, 6)
  const result = await client.callTool({name:'list_boards', arguments:{}})
  assert.ok(!result.isError)
  assert.ok(result.structuredContent.boards.some(b=>b.id===1))
  console.log('PASS: copied JSON launches stdio MCP; tool discovery + read-only list_boards')
} finally { await client.close() }
