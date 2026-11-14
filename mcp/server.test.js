import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const requests = []
const board = { id: 1, name: '公开中文版块' }
const topic = { id: 2, title: '中文 UBB', author: '会员', replies: 1 }
// Real HTTP and stdio boundaries, with deterministic forum responses.
const http = createServer((req, res) => {
  requests.push({ url: req.url, cookie: req.headers.cookie })
  const url = new URL(req.url, 'http://localhost')
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  if (url.pathname.includes('/999')) {
    res.statusCode = 404
    return res.end(JSON.stringify({ error: '版块不存在' }))
  }
  if (url.searchParams.get('q') === 'busy') {
    res.statusCode = 429
    res.setHeader('Retry-After', '2')
    return res.end(JSON.stringify({ error: '灌水预防机制，请稍后重试' }))
  }
  if (url.searchParams.get('q') === 'slow') {
    const timer = setTimeout(() => res.end('{}'), 11000)
    res.on('close', () => clearTimeout(timer))
    return
  }
  if (url.searchParams.get('q') === 'oversized') return res.end(JSON.stringify({ data: 'a'.repeat(4 * 1024 * 1024) }))
  if (url.searchParams.get('q') === 'broken') return res.end('<html>服务器忙</html>')
  if (url.searchParams.get('q') === 'redirect') {
    res.statusCode = 302
    res.setHeader('Location', '/api/v1/home')
    return res.end()
  }
  if (url.searchParams.get('q') === 'shape') return res.end('{"items":null}')
  if (url.pathname.endsWith('/home')) return res.end(JSON.stringify({ boards: [board] }))
  const page = Number(url.searchParams.get('page') || 1)
  const paging = { page, pages: 2, items: page > 2 ? [] : [{ ...topic, boardId: 1 }] }
  if (url.pathname.endsWith('/topics/2')) paging.items = [{ floor: 1, author: '会员', body: '[b]中文[/b]', ubb: true, desktopOnly: false, profile: { cash: 123 } }, { floor: 2, author: '会员', body: '不得泄露的内容', desktopOnly: true }]
  res.end(JSON.stringify({ ...paging, board, topic }))
})
await new Promise(resolve => http.listen(0, '127.0.0.1', resolve))
const origin = `http://127.0.0.1:${http.address().port}`
const client = new Client({ name: 'test', version: '1.0.0' })
await client.connect(new StdioClientTransport({ command: process.execPath, args: ['server.js'], env: { ...process.env, LEOBBS_URL: origin } }))
test.after(async () => { await client.close(); await new Promise(resolve => http.close(resolve)) })
const call = (name, args = {}) => client.callTool({ name, arguments: args })

test('four tools declare output schemas and read-only annotations', async () => {
  const { tools } = await client.listTools()
  assert.deepEqual(tools.map(t => t.name).sort(), ['get_topic', 'list_boards', 'list_topics', 'search_topics'])
  for (const tool of tools) {
    assert.equal(tool.annotations.readOnlyHint, true)
    assert.ok(tool.outputSchema)
  }
})
test('browse boards and topics with canonical links and pagination', async () => {
  assert.equal((await call('list_boards')).structuredContent.boards[0].name, board.name)
  const result = await call('list_topics', { boardId: 1 })
  assert.equal(result.isError, undefined)
  assert.equal(result.structuredContent.nextPage, 2)
  assert.equal(result.structuredContent.items[0].url, `${origin}/cgi-bin/topic.cgi?forum=1&topic=2`)
  const empty = await call('list_topics', { boardId: 1, page: 3 })
  assert.deepEqual(empty.structuredContent.items, [])
  assert.equal(empty.structuredContent.nextPage, null)
})
test('search forwards UTF-8, multiple boards and date filters', async () => {
  await call('search_topics', { q: '中文', boardIds: [1, 2], days: '7', when: 'before', page: 2 })
  const url = new URL(requests.at(-1).url, origin)
  assert.equal(url.searchParams.get('q'), '中文')
  assert.deepEqual(url.searchParams.getAll('board'), ['1', '2'])
  assert.equal(url.searchParams.get('days'), '7')
  assert.equal(url.searchParams.get('when'), 'before')
})
test('topic excludes profiles and supplies per-floor source links', async () => {
  const { structuredContent: data } = await call('get_topic', { boardId: 1, topicId: 2 })
  assert.equal(data.items[0].body, '[b]中文[/b]')
  assert.equal(data.items[0].profile, undefined)
  assert.equal(data.items[1].body, '')
  assert.equal(data.items[1].desktopOnly, true)
  assert.ok(data.items[1].url.includes('topic=2'))
  const second = await call('get_topic', { boardId: 1, topicId: 2, page: 2 })
  assert.equal(second.structuredContent.mobileUrl, `${origin}/m/1/2?page=2`)
})
test('validation rejects invalid IDs and empty searches before HTTP', async () => {
  const before = requests.length
  for (const [name, args] of [['get_topic', { boardId: -1, topicId: 2 }], ['search_topics', { q: '  ' }]]) assert.equal((await call(name, args)).isError, true)
  assert.equal(requests.length, before)
})
test('API errors retain Chinese reasons and retry information', async () => {
  const missing = await call('get_topic', { boardId: 999, topicId: 2 })
  assert.equal(missing.isError, true)
  assert.equal(JSON.parse(missing.content[0].text).error.status, 404)
  assert.equal(JSON.parse(missing.content[0].text).error.message, '版块不存在')
  const busy = await call('search_topics', { q: 'busy' })
  assert.equal(JSON.parse(busy.content[0].text).error.retryAfterSeconds, 2)
  assert.equal(JSON.parse(busy.content[0].text).error.code, 'RATE_LIMITED')
})
test('HTML, malformed responses and redirects produce safe errors', async () => {
  for (const q of ['broken', 'shape', 'redirect']) {
    const result = await call('search_topics', { q })
    assert.equal(result.isError, true)
    assert.ok(JSON.parse(result.content[0].text).error.code)
    assert.ok(!result.content[0].text.includes('<html>'))
  }
})
test('reads never send cookies or increment counters', () => {
  for (const req of requests) {
    assert.equal(req.cookie, undefined)
    assert.equal(new URL(req.url, origin).searchParams.has('count'), false)
  }
})

test('oversized responses fail without leaking their body', async () => {
  const result = await call('search_topics', { q: 'oversized' })
  assert.equal(result.isError, true)
  assert.equal(JSON.parse(result.content[0].text).error.code, 'RESPONSE_TOO_LARGE')
})

test('slow upstream reports a retryable timeout', async () => {
  const result = await call('search_topics', { q: 'slow' })
  assert.equal(result.isError, true)
  assert.equal(JSON.parse(result.content[0].text).error.code, 'TIMEOUT')
})
