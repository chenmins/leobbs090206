import test from 'node:test'
import assert from 'node:assert/strict'
import { buildMcpConnection } from '../src/mcpConnection.js'
for (const [url, origin] of [
  ['https://leobbs.org/m/agent?x=1#help', 'https://leobbs.org'],
  ['https://forum.example.net/cgi-bin/agentpanel.cgi?x=1#help', 'https://forum.example.net'],
  ['http://127.0.0.1:8080/m/agent', 'http://127.0.0.1:8080'],
]) test(`connection snippets preserve origin: ${origin}`, () => {
  const info = buildMcpConnection(url)
  const config = JSON.parse(info.json).mcpServers.leobbs
  assert.equal(info.origin, origin)
  assert.equal(config.command, 'node')
  assert.match(config.args[0], /^\/.*\/mcp\/server\.js$/)
  assert.equal(config.env.LEOBBS_URL, origin)
  assert.match(config.env.LEOBBS_TOKEN_FILE, /^\//)
  assert.match(info.toml, /\[mcp_servers.leobbs.env\]/)
  for (const text of [info.json, info.toml, info.instructions]) {
    assert.ok(text.includes(origin))
    assert.ok(!text.includes('/m/agent'))
    assert.ok(!text.includes('leo_'))
  }
  assert.match(info.instructions, /Node.js 22/)
  assert.match(info.instructions, /npm ci/)
  assert.match(info.instructions, /stdio/)
  assert.equal(info.examples.length, 3)
  assert.match(info.examples[0].text, /list_boards/)
  assert.match(info.examples[1].text, /create_topic/)
  assert.match(info.examples[2].text, /reply_topic/)
})
test('remote Codex configuration uses current origin and an environment variable only', () => {
  for (const origin of ['https://leobbs.org','https://forum.example.net','http://127.0.0.1:8080']) {
    const info=buildMcpConnection(origin+'/m/agent?x=1')
    assert.equal(info.httpUrl,origin+'/mcp')
    assert.ok(info.httpToml.includes('url = "'+origin+'/mcp"'))
    assert.ok(info.httpToml.includes('bearer_token_env_var = "LEOBBS_TOKEN"'))
    assert.ok(!info.httpToml.includes('leo_'))
  }
})
