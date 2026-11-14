import assert from 'node:assert/strict'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

// This smoke test only reads public data; it never creates posts or logs in.
const origin = new URL(process.env.LEOBBS_URL || 'http://127.0.0.1:8080').origin
const client = new Client({ name: 'leobbs-live-smoke', version: '1.0.0' })
const transport = process.env.LEOBBS_MCP_DOCKER_IMAGE
  ? new StdioClientTransport({ command: 'docker', args: ['run', '--rm', '-i', '-e', `LEOBBS_URL=${origin}`, process.env.LEOBBS_MCP_DOCKER_IMAGE] })
  : new StdioClientTransport({ command: process.execPath, args: ['server.js'], env: { ...process.env, LEOBBS_URL: origin } })
try {
  await client.connect(transport)
  const call = async (name, args = {}) => {
    const result = await client.callTool({ name, arguments: args })
    assert.ok(!result.isError, JSON.stringify(result))
    return result.structuredContent
  }
  assert.equal((await client.listTools()).tools.length, 4)
  const { boards } = await call('list_boards')
  assert.ok(boards.length, '测试需要至少一个已配置的公开版块')
  let testedTopic = false
  for (const board of boards) {
    const listing = await call('list_topics', { boardId: board.id })
    assert.equal(listing.board.id, board.id)
    if (!listing.items.length) continue
    const topic = listing.items[0]
    const detail = await call('get_topic', { boardId: board.id, topicId: topic.id })
    assert.equal(detail.topic.id, topic.id)
    assert.ok(detail.items.length)
    for (const post of detail.items) {
      assert.equal(post.profile, undefined)
      if (post.desktopOnly) assert.equal(post.body, '')
    }
    const search = await call('search_topics', { q: topic.title.slice(0, 30), mode: 'title', boardIds: [board.id], days: 'any' })
    assert.ok(search.items.some(item => item.id === topic.id && item.boardId === board.id))
    const empty = await call('get_topic', { boardId: board.id, topicId: topic.id, page: detail.pages + 1 })
    assert.deepEqual(empty.items, [])
    assert.equal(empty.nextPage, null)
    testedTopic = true
    break
  }
  assert.ok(testedTopic, '测试需要至少一个公开主题')
  const missing = await client.callTool({ name: 'list_topics', arguments: { boardId: 9999999999 } })
  assert.equal(missing.isError, true)
  assert.equal(JSON.parse(missing.content[0].text).error.code, 'NOT_FOUND')
  console.log('PASS: MCP handshake, four tools, public boards/topics, UTF-8 search, empty page and invisible board error')
} finally {
  await client.close()
}
