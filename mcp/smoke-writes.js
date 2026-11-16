// Creates test posts: invoke only from the isolated Docker integration harness.
import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
if (process.env.LEOBBS_WRITE_TEST !== 'isolated') throw new Error('Use the isolated Agent integration harness')
const client = new Client({ name: 'isolated-write-test', version: '1' })
try {
  await client.connect(new StdioClientTransport({ command: process.execPath, args: ['server.js'], env: { ...process.env } }))
  const call = async (name, args) => {
    const result = await client.callTool({ name, arguments: args })
    assert.ok(!result.isError, JSON.stringify(result))
    return result.structuredContent
  }
  assert.equal((await client.listTools()).tools.length, 6)
  const topicArgs = { boardId: 1, title: 'MCP 发布测试 ' + randomUUID().slice(0, 8), body: '[b]MCP 中文正文[/b]', idempotencyKey: randomUUID() }
  const topic = await call('create_topic', topicArgs)
  const replay = await call('create_topic', topicArgs)
  assert.equal(replay.topicId, topic.topicId)
  assert.equal(replay.replayed, true)
  const replyArgs = { boardId: 1, topicId: topic.topicId, body: '[quote]MCP 回复内容[/quote]', idempotencyKey: randomUUID() }
  const reply = await call('reply_topic', replyArgs)
  assert.equal(reply.floor, 2)
  assert.equal((await call('reply_topic', replyArgs)).replayed, true)
  const read = await call('get_topic', { boardId: 1, topicId: topic.topicId })
  assert.equal(read.items.length, 2)
  assert.ok(read.items[0].body.includes('MCP 中文正文'))
  assert.ok(read.items[1].body.includes('MCP 回复内容'))
  assert.equal(read.items[0].author, 'leoadmin')
  console.log('PASS: real MCP create/reply/read, account identity, UBB and replay without duplicate posts')
} finally { await client.close() }
