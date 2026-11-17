import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer, request } from 'node:http'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
import { createHttpServer } from './http.js'

test('HTTP uses request credentials, enforces revocation and guards browser origins', async t => {
  const a = 'leo_' + 'a'.repeat(64), b = 'leo_' + 'b'.repeat(64)
  let revoked = false
  const writes = []
  const upstream = createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json')
    if (req.url === '/api/v1/agent/identity') {
      const valid = [a,b].includes(req.headers.authorization?.slice(7)) && !revoked
      res.statusCode = valid ? 200 : 401
      return res.end(JSON.stringify(valid ? {scopes:['topics:read','topics:write','replies:write']} : {error:{message:'invalid'}}))
    }
    if (req.method === 'POST') {
      writes.push(req.headers.authorization)
      req.resume()
      return res.end(JSON.stringify({boardId:1,topicId:2,floor:1,replayed:false}))
    }
    assert.equal(req.headers.authorization, undefined)
    res.end(JSON.stringify({boards:[{id:1,name:'public'}]}))
  })
  await new Promise(r => upstream.listen(0,'127.0.0.1',r))
  const app = createHttpServer({origin:'https://forum.example', apiOrigin:`http://127.0.0.1:${upstream.address().port}`, allowedHosts:['127.0.0.1']})
  await new Promise(r => app.listen(0,'127.0.0.1',r))
  t.after(() => {app.closeAllConnections(); app.close(); upstream.closeAllConnections(); upstream.close()})
  const url = `http://127.0.0.1:${app.address().port}/mcp`
  const clients = []
  async function connect(token) {
    const client = new Client({name:'test',version:'1'})
    clients.push(client)
    await client.connect(new StreamableHTTPClientTransport(new URL(url), {requestInit:{headers:{Authorization:`Bearer ${token}`}}}))
    return client
  }
  t.after(async () => {await Promise.all(clients.map(c=>c.close()))})
  assert.equal((await fetch(url,{method:'POST'})).status,401)
  const ca=await connect(a), cb=await connect(b)
  assert.equal((await ca.listTools()).tools.length,6)
  const boards=await ca.callTool({name:'list_boards',arguments:{}})
  assert.equal(boards.structuredContent.boards[0].url,'https://forum.example/cgi-bin/forums.cgi?forum=1')
  await Promise.all([ca,cb].map(c=>c.callTool({name:'create_topic',arguments:{boardId:1,title:'test',body:'test',idempotencyKey:'abcdefghijklmnop'}})))
  assert.deepEqual(new Set(writes),new Set([`Bearer ${a}`,`Bearer ${b}`]))
  assert.equal((await fetch(url,{method:'POST',headers:{Authorization:`Bearer ${a}`,Origin:'https://evil.example'}})).status,403)
  assert.equal(await new Promise(resolve => { const r=request(url,{method:'POST',headers:{Authorization:`Bearer ${a}`,Host:'evil.example'}},res=>{res.resume();resolve(res.statusCode)});r.end() }),403)
  assert.equal((await fetch(url+'?token=secret',{method:'POST'})).status,400)
  assert.equal((await fetch(url,{headers:{Authorization:`Bearer ${a}`}})).status,405)
  assert.equal((await fetch(url,{method:'POST',headers:{Authorization:`Bearer ${a}`,'Content-Type':'application/json'},body:'{'})).status,400)
  assert.equal((await fetch(url,{method:'POST',headers:{Authorization:`Bearer ${a}`,'Content-Type':'application/json'},body:'x'.repeat(65537)})).status,413)
  revoked=true
  await assert.rejects(()=>ca.listTools())
})
