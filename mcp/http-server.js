import { createHttpServer, siteOrigin } from './http.js'
const origin=siteOrigin(process.env.LEOBBS_PUBLIC_ORIGIN || process.env.LEOBBS_URL || 'http://127.0.0.1:8080')
const apiOrigin=siteOrigin(process.env.LEOBBS_API_URL || origin)
const server=createHttpServer({origin,apiOrigin})
server.listen(Number(process.env.PORT || 3000), process.env.HOST || '127.0.0.1', () => console.error('LeoBBS Streamable HTTP MCP ready'))
for (const signal of ['SIGINT','SIGTERM']) process.on(signal, () => {
  server.close(() => process.exit(0))
  setTimeout(() => process.exit(0),45000).unref()
})
