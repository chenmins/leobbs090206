// Apache/proxies may return HTML before CGI reaches its JSON error handler.
// Never expose that page (or its possible private diagnostics) to the member.
export async function readAgentResponse(response) {
  const status = `HTTP ${response.status}`
  if (response.redirected) {
    throw new Error(`授权接口发生了跳转（${status}），请刷新后重试；仍失败请联系管理员检查接口地址。`)
  }
  if (!(response.headers.get('content-type') || '').toLowerCase().includes('application/json')) {
    throw new Error(`授权接口异常（${status}），服务器未返回 JSON，请联系管理员检查 CGI 部署及错误日志。`)
  }
  let data
  try { data = await response.json() }
  catch { throw new Error(`授权接口响应格式错误（${status}），请稍后刷新或联系管理员。`) }
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error(`授权接口响应格式错误（${status}），请稍后刷新或联系管理员。`)
  }
  return data
}
