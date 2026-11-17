import { createServer } from 'node:http'
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js'
import { createForumServer } from './forum-server.js'

export function siteOrigin(value) {
  const url = new URL(value)
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.pathname !== '/' || url.search || url.hash) throw new Error('Expected an HTTP(S) site origin')
  return url.origin
}

export function createHttpServer({ origin, apiOrigin = origin, allowedHosts = [new URL(origin).host] }) {
  origin = siteOrigin(origin); apiOrigin = siteOrigin(apiOrigin)
  let active = 0
  return createServer({ requestTimeout: 15000, headersTimeout: 10000 }, async (req, res) => {
    res.setHeader('Cache-Control', 'no-store')
    res.setHeader('X-Content-Type-Options', 'nosniff')
    function fail(status, message) {
      res.writeHead(status, {'Content-Type':'application/json'})
      res.end(JSON.stringify({jsonrpc:'2.0',id:null,error:{code:-32000,message}}))
    }
    if (req.url === '/healthz') {res.writeHead(200); res.end('ok'); return}
    if (req.url?.includes('?')) return fail(400, 'Query parameters are not accepted')
    if (req.url !== '/mcp') return fail(404, 'Not found')
    // Host and browser Origin are independent checks. Never trust forwarded headers.
    if (!allowedHosts.includes(req.headers.host) && !allowedHosts.includes(req.headers.host?.replace(/:\d+$/, ''))) return fail(403, 'Host not allowed')
    if (req.headers.origin && req.headers.origin !== origin) return fail(403, 'Origin not allowed')
    const match = /^Bearer (leo_[0-9a-f]{64})$/.exec(req.headers.authorization || '')
    if (!match) {res.setHeader('WWW-Authenticate','Bearer'); return fail(401,'Valid member Agent Token required')}
    if (active >= 64) {res.setHeader('Retry-After','2'); return fail(503,'Server busy')}
    active++
    let server
    try {
      // First-party forum Tokens are checked on EVERY request, including tool discovery.
      const auth = await fetch(new URL('/api/v1/agent/identity',apiOrigin), {
        headers:{Authorization:`Bearer ${match[1]}`}, redirect:'error', signal:AbortSignal.timeout(10000),
      })
      await auth.body?.cancel()
      if (!auth.ok) {
        if (auth.status === 401 || auth.status === 403) {
          res.setHeader('WWW-Authenticate','Bearer'); return fail(401,'Agent Token expired, revoked or invalid')
        }
        return fail(503,'Authorization service unavailable')
      }
      if (req.method !== 'POST') {res.setHeader('Allow','POST'); return fail(405,'Stateless endpoint accepts POST only')}
      if (req.headers['content-type']?.split(';')[0].trim() !== 'application/json') return fail(415,'Expected application/json')
      if (Number(req.headers['content-length']) > 65536) return fail(413,'Request exceeds 64 KiB')
      let size=0; const chunks=[]
      for await (const chunk of req) {
        size += chunk.length
        if (size > 65536) {fail(413,'Request exceeds 64 KiB'); return}
        chunks.push(chunk)
      }
      let body
      try { body=JSON.parse(Buffer.concat(chunks).toString('utf8')) } catch {return fail(400,'Invalid JSON')}
      server=createForumServer({origin,apiOrigin,token:match[1]})
      const transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true})
      await server.connect(transport)
      await transport.handleRequest(req,res,body)
    } catch {
      if (!res.headersSent && !res.destroyed) fail(503,'MCP service unavailable')
    } finally {
      await server?.close()
      active--
    }
  })
}
