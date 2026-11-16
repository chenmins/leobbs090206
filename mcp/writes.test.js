import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const token = 'leo_' + 'a'.repeat(64)
const requests = []
const http = createServer(async (req, res) => {
  const chunks = []
  for await (const chunk of req) chunks.push(chunk)
  const body = JSON.parse(Buffer.concat(chunks).toString() || '{}')
  requests.push({ url: req.url, headers: req.headers, body })
  res.setHeader('Content-Type', 'application/json')
  if (req.method === 'GET') return res.end('{"boards":[]}')
  if (body.body === 'reject') {
    res.statusCode = 429
    return res.end(JSON.stringify({ error: { code: 'RATE_LIMITED', message: '灌水预防机制', retryAfterSeconds: 12 } }))
  }
  if (body.body === 'bad-json') return res.end('<html>bad upstream</html>')
  if (body.body === 'bad-shape') return res.end('{}')
  res.statusCode = 201
  res.end(JSON.stringify({ boardId: 1, topicId: 2, floor: req.url.endsWith('/replies') ? 21 : 1, replayed: false }))
})
await new Promise(resolve => http.listen(0, '127.0.0.1', resolve))
const origin = `http://127.0.0.1:${http.address().port}`
const client = new Client({ name: 'write-test', version: '1' })
await client.connect(new StdioClientTransport({ command: process.execPath, args: ['server.js'], env: { ...process.env, LEOBBS_URL: origin, LEOBBS_TOKEN: token } }))
test.after(async () => { await client.close(); await new Promise(resolve => http.close(resolve)) })
const call = (name, args = {}) => client.callTool({ name, arguments: args })
test('token enables two write tools with accurate annotations', async () => {
  const { tools } = await client.listTools()
  for (const name of ['create_topic', 'reply_topic']) {
    const tool = tools.find(t => t.name === name)
    assert.ok(tool)
    assert.equal(tool.annotations.readOnlyHint, false)
    assert.equal(tool.annotations.destructiveHint, false)
    assert.equal(tool.annotations.idempotentHint, true)
  }
})
test('create sends JSON, token and caller idempotency key, with canonical links', async () => {
  const result = await call('create_topic', { boardId: 1, title: '中文', body: '[b]正文[/b]', idempotencyKey: 'request-123456789' })
  assert.equal(result.isError, undefined)
  assert.equal(requests.at(-1).headers.authorization, `Bearer ${token}`)
  assert.equal(requests.at(-1).headers['idempotency-key'], 'request-123456789')
  assert.equal(requests.at(-1).body.title, '中文')
  assert.equal(result.structuredContent.url, `${origin}/cgi-bin/topic.cgi?forum=1&topic=2`)
})
test('reply returns correct mobile page and does not leak token to read calls', async () => {
  const result = await call('reply_topic', { boardId: 1, topicId: 2, body: '回复', idempotencyKey: 'reply-12345678901' })
  assert.equal(result.structuredContent.mobileUrl, `${origin}/m/1/2?page=2`)
  await call('list_boards')
  assert.equal(requests.at(-1).headers.authorization, undefined)
})
test('write requires idempotency key before HTTP and preserves API errors', async () => {
  const before = requests.length
  assert.equal((await call('create_topic', { boardId: 1, title: 'x', body: 'x' })).isError, true)
  assert.equal(requests.length, before)
  const failure = await call('reply_topic', { boardId: 1, topicId: 2, body: 'reject', idempotencyKey: 'reject-1234567890' })
  const error = JSON.parse(failure.content[0].text).error
  assert.equal(error.message, '灌水预防机制')
  assert.equal(error.retryAfterSeconds, 12)
  assert.ok(!failure.content[0].text.includes(token))
})

test('malformed write responses retain uncertain-outcome semantics', async () => {
  for (const body of ['bad-json', 'bad-shape']) {
    const result = await call('reply_topic', { boardId: 1, topicId: 2, body, idempotencyKey: 'uncertain-12345678' })
    assert.equal(result.isError, true)
    assert.equal(JSON.parse(result.content[0].text).error.code, 'WRITE_OUTCOME_UNKNOWN')
  }
})
