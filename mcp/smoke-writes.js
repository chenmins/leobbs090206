// Creates test posts: invoke only from the isolated Docker integration harness.
import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { writeFileSync, readFileSync } from 'node:fs'
import { setTimeout as wait } from 'node:timers/promises'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
if (process.env.LEOBBS_WRITE_TEST !== 'isolated') throw new Error('Use the isolated Agent integration harness')
const client = new Client({ name: 'isolated-write-test', version: '1' })
try {
  await client.connect(process.env.LEOBBS_MCP_HTTP ? new StreamableHTTPClientTransport(new URL(process.env.LEOBBS_MCP_HTTP), {requestInit:{headers:{Authorization: 'Bearer ' + readFileSync(process.env.LEOBBS_TOKEN_FILE,'utf8').trim()}}}) : new StdioClientTransport({ command: process.execPath, args: ['server.js'], env: { ...process.env } }))
  const call = async (name, args) => {
    for (let attempt = 0; attempt < 3; attempt++) {
      const result = await client.callTool({ name, arguments: args })
      if (!result.isError) return result.structuredContent
      const error = JSON.parse(result.content[0].text).error
      // Only an explicit rate-limit rejection permits a fresh test request.
      // Unknown outcomes are never retried with a new key.
      if (error.code === 'RATE_LIMITED' && attempt < 2 && Number.isInteger(error.retryAfterSeconds) && error.retryAfterSeconds <= 60) {
        await wait(Math.max(1, error.retryAfterSeconds) * 1000)
        args.idempotencyKey = randomUUID()
        continue
      }
      assert.fail(JSON.stringify(result))
    }
  }
  assert.equal((await client.listTools()).tools.length, 6)
  const report = []
  const origin = process.env.LEOBBS_URL
  const html = async path => {
    const response = await fetch(new URL(path, origin))
    assert.equal(response.status, 200)
    return new TextDecoder('gbk').decode(await response.arrayBuffer())
  }
  for (const icon of ['00', '01']) {
    const title = 'MCP-icon-' + icon + '-' + randomUUID().slice(0, 8)
    // Omit 00 to test the public default; explicitly pass a real non-default.
    const topicArgs = { boardId: 1, title, body: '[b]MCP 中文正文[/b] ' + title, idempotencyKey: randomUUID(), ...(icon === '00' ? {} : {icon}) }
    const topic = await call('create_topic', topicArgs)
    const replay = await call('create_topic', topicArgs)
    assert.equal(replay.topicId, topic.topicId)
    assert.equal(replay.replayed, true)
    const replyIcon = icon === '00' ? '01' : '00'
    const replyArgs = { boardId: 1, topicId: topic.topicId, body: '[quote]MCP 回复内容[/quote] ' + title, idempotencyKey: randomUUID(), ...(replyIcon === '00' ? {} : {icon: replyIcon}) }
    const reply = await call('reply_topic', replyArgs)
    assert.equal(reply.floor, 2)
    assert.equal((await call('reply_topic', replyArgs)).replayed, true)
    const read = await call('get_topic', { boardId: 1, topicId: topic.topicId })
    assert.equal(read.items.length, 2)
    assert.ok(read.items[0].body.includes('MCP 中文正文'))
    assert.ok(read.items[1].body.includes('MCP 回复内容'))
    assert.equal(read.items[0].author, 'leoadmin')
    const listing = await html('/cgi-bin/forums.cgi?forum=1')
    const index = listing.indexOf(title)
    assert.ok(index >= 0, 'new topic must appear in classic list')
    const row = listing.slice(listing.lastIndexOf('<tr', index), listing.indexOf('</tr>', index) + 5)
    const sources = [...row.matchAll(/<img\b[^>]*\bsrc=["']?([^\s"'>]+)/gi)].map(m => m[1])
    const imageUrl = sources.map(src => new URL(src, origin)).find(url => url.pathname === `/non-cgi/posticons/${icon}.gif`)
    assert.ok(imageUrl, 'classic list must use the main topic icon filename: ' + icon)
    assert.equal(imageUrl.origin, new URL(origin).origin, 'test images must remain in the isolated deployment')
    const detail = await html(`/cgi-bin/topic.cgi?forum=1&topic=${topic.topicId}`)
    for (const value of [icon, replyIcon]) {
      assert.ok(detail.includes(`/posticons/${value}.gif`), 'classic floor icon missing')
      const image = await fetch(new URL(`/non-cgi/posticons/${value}.gif`, origin))
      assert.equal(image.status, 200)
      assert.equal(image.headers.get('content-type').split(';')[0], 'image/gif')
    }
    report.push({topicId: topic.topicId, icon, replyIcon, imageUrl: imageUrl.href})
  }
  if (process.env.LEOBBS_ICON_REPORT) writeFileSync(process.env.LEOBBS_ICON_REPORT, JSON.stringify(report))
  console.log('PASS: real MCP default/non-default topic + reply icons, classic list/floors, HTTP 200 image/gif, account identity, UBB and idempotency')
} finally { await client.close() }
