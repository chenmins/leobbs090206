<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
const props = defineProps({ classic: Boolean })
const emit = defineEmits(['login'])
const origin = location.origin
const endpoint = '/cgi-bin/agenttokens.cgi'
const icons = '/non-cgi/images/'
const data = ref(null), error = ref(''), notice = ref(''), busy = ref(false), loading = ref(true)
const formOpen = ref(false), secret = ref(null), revokeTarget = ref(null), helpOpen = ref(false)
const name = ref(''), password = ref(''), scopes = ref(['topics:write', 'replies:write']), boards = ref([]), days = ref(30)
const secretField = ref(null), titleField = ref(null), loginRequired = ref(false)
const available = computed(() => (data.value?.boards || []).filter(b => scopes.value.every(s => b.scopes.includes(s))))
watch(available, list => { boards.value = boards.value.filter(id => list.some(b => b.id === id)) })
const revokeDialog = ref(null)
let previousFocus
watch(revokeTarget, async target => {
  if (target) { previousFocus = document.activeElement; await nextTick(); revokeDialog.value?.querySelector('button')?.focus() }
  else { await nextTick(); previousFocus?.focus() }
})
function dialogKeys(event) {
  if (event.key === 'Escape' && !busy.value) revokeTarget.value = null
  if (event.key !== 'Tab') return
  const buttons = [...revokeDialog.value.querySelectorAll('button:not(:disabled)')]
  if (!buttons.length) { event.preventDefault(); return }
  const first = buttons[0], last = buttons[buttons.length - 1]
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
}
const labels = { active: '有效', revoked: '已撤销', expired: '已过期', invalid: '密码变更，已失效' }
const date = value => value ? new Date(value * 1000).toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai', hour12: false}) : '尚未使用'
const scopeText = list => list.map(s => ({'topics:write':'发帖','replies:write':'回复','topics:read':'公开阅读'}[s] || s)).join('、')
const boardText = list => list.map(id => data.value?.boards.find(b => b.id === id)?.name || `版块 ${id}`).join('、')
async function load() {
  try {
    const response = await fetch(endpoint, { credentials: 'same-origin', cache: 'no-store' })
    const result = await response.json()
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) { secret.value = null; password.value = ''; data.value = null; loginRequired.value = true }
      throw new Error(result.error?.message || '暂时无法读取授权')
    }
    if (secret.value && secret.value.username !== result.username) secret.value = null
    data.value = result; loginRequired.value = false
  } catch (failure) { error.value = failure.message || '暂时无法连接论坛' }
  finally { loading.value = false }
}
async function openCreate() {
  error.value = ''; notice.value = ''; secret.value = null; formOpen.value = true
  await load(); await nextTick(); titleField.value?.focus()
}
function closeCreate() { formOpen.value = false; password.value = ''; error.value = '' }
async function mutate(payload) {
  const response = await fetch(endpoint, {method:'POST', credentials:'same-origin', cache:'no-store',
    headers:{'Content-Type':'application/json','X-CSRF-Token':data.value.csrf}, body:JSON.stringify(payload)})
  const result = await response.json()
  if (!response.ok) throw new Error(result.error?.message || '操作失败，请刷新列表核查')
  return result
}
async function create() {
  if (busy.value) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    secret.value = await mutate({action:'create', name:name.value, scopes:scopes.value, boards:boards.value, days:days.value, password:password.value})
    formOpen.value = false; name.value = ''; window.scrollTo(0,0)
  } catch (failure) { error.value = failure.message || '未收到结果，请刷新列表核查。若授权已创建但未取得 Token，请撤销后重新创建。' }
  finally { password.value = ''; busy.value = false; await load() }
}
async function revoke() {
  if (!revokeTarget.value || busy.value) return
  busy.value = true; error.value = ''; notice.value = ''
  try { await mutate({action:'revoke', id:revokeTarget.value.id}); notice.value = '授权已撤销，已发表的帖子不受影响。'; revokeTarget.value = null }
  catch (failure) { error.value = failure.message || '未收到结果，请刷新列表核查。' }
  finally { busy.value = false; await load() }
}
async function copySecret() {
  try { await navigator.clipboard.writeText(secret.value.token); notice.value = 'Token 已复制。请保存到本机私密文件。' }
  catch { secretField.value?.focus(); secretField.value?.select(); notice.value = '已选中 Token，请长按或使用系统复制。' }
}
function finish() { secret.value = null; notice.value = ''; load() }
function clearSensitive() { secret.value = null; password.value = '' }
function focusRefresh() { if (!busy.value) load() }
onMounted(() => { load(); window.addEventListener('pagehide', clearSensitive); window.addEventListener('focus', focusRefresh) })
onUnmounted(() => { clearSensitive(); window.removeEventListener('pagehide', clearSensitive); window.removeEventListener('focus', focusRefresh) })
</script>

<template>
  <div class="agent-page" :class="{'agent-desktop': classic}">
    <p class="crumb"><a :href="classic ? '/cgi-bin/leobbs.cgi' : '/m/'">首页</a> › {{ classic ? '控制面板' : '个人状态' }} › Agent 授权</p>
    <div class="agent-layout">
      <aside v-if="classic" class="panel agent-sidebar" aria-label="控制面板">
        <h2 class="bar">控制面板</h2>
        <a href="/cgi-bin/profile.cgi?action=modify"><img :src="icons+'profile.gif'" alt="">个人资料</a>
        <a href="/cgi-bin/friendlist.cgi"><img :src="icons+'friend.gif'" alt="">好友名单</a>
        <a href="/cgi-bin/blocklist.cgi"><img :src="icons+'blockpm.gif'" alt="">黑名单</a>
        <a href="/cgi-bin/agentpanel.cgi" aria-current="page"><img :src="icons+'profile.gif'" alt="">Agent 授权 <span>◀</span></a>
      </aside>
      <div class="agent-main">
        <p v-if="loading" class="panel row" role="status">正在读取授权…</p>
        <p v-if="error" class="panel row agent-error" role="alert">{{ error }} <button v-if="!busy" @click="error=''; load()">刷新</button></p>
        <p v-if="notice" class="panel row agent-notice" role="status">{{ notice }}</p>
        <section v-if="loginRequired" class="panel"><h1 class="bar">Agent 授权</h1><div class="row">登录后可以管理自己的 AI 授权。<button @click="emit('login')">登录论坛</button></div></section>
        <template v-if="data">
          <section v-if="secret" class="panel" aria-label="授权创建成功">
            <h1 class="bar"><img :src="icons+'yes.gif'" alt="">授权创建成功</h1>
            <div class="row agent-success">
              <p>已为「<b>{{ secret.name }}</b>」创建授权。</p>
              <p class="agent-warning">Token 仅显示这一次，请立即保存。</p>
              <label for="agent-secret">你的 Token</label>
              <textarea id="agent-secret" ref="secretField" :value="secret.token" readonly rows="3" spellcheck="false" autocomplete="off" />
              <button @click="copySecret"><img :src="icons+'copy.gif'" alt="">复制 Token</button>
              <dl class="agent-summary"><dt>账号</dt><dd>{{ secret.username }}</dd><dt>权限</dt><dd>{{ scopeText(secret.scopes) }}</dd><dt>版块</dt><dd>{{ boardText(secret.boards) }}</dd><dt>到期</dt><dd>{{ date(secret.expires) }}</dd></dl>
              <p>请保存到本机私密文件，不要发到帖子里。</p>
              <button @click="finish"><img :src="icons+'yes.gif'" alt="">已保存，返回列表</button>
            </div>
          </section>
          <section v-else-if="!formOpen || classic" class="panel">
            <h1 class="bar"><img :src="icons+'profile.gif'" alt="">我的 Agent 授权</h1>
            <div class="row agent-toolbar"><p>让你的 AI 以当前账号发帖和回复</p><div><button :disabled="busy" @click="openCreate"><img :src="icons+'newpost.gif'" alt="">创建授权</button><button class="agent-link" @click="helpOpen=!helpOpen">MCP 接入说明</button></div></div>
            <p v-if="!data.items.length" class="row agent-empty">还没有授权。创建后，你的 AI 就可以使用当前会员身份发帖或回复。</p>
            <table v-else class="agent-table"><thead><tr><th>授权名称</th><th>允许版块 / 权限</th><th>到期时间</th><th>最近使用</th><th>状态</th><th>操作</th></tr></thead>
              <tbody><tr v-for="item in data.items" :key="item.id" :class="{'agent-inactive':item.status!=='active'}">
                <td class="agent-name"><b>{{ item.name }}</b></td><td class="agent-permission">{{ boardText(item.boards) }}<small>{{ scopeText(item.scopes) }}</small></td>
                <td class="agent-expiry"><span class="mobile-label">到期：</span>{{ date(item.expires) }}</td><td class="agent-last"><span class="mobile-label">最近使用：</span>{{ date(item.lastUsed) }}</td>
                <td class="agent-status" :class="item.status">{{ labels[item.status] }}</td><td class="agent-action"><button v-if="item.status==='active'" :disabled="busy" @click="revokeTarget=item"><img :src="icons+'m_delete.gif'" alt="">撤销</button><span v-else>—</span></td>
              </tr></tbody>
            </table>
            <p class="row agent-info">公开帖子搜索和阅读无需 Token。权限变化后，实际发帖仍按论坛规则检查。</p>
          </section>
          <section v-if="formOpen && !secret" class="panel">
            <h1 class="bar"><img :src="icons+'edit.gif'" alt="">创建 Agent 授权</h1>
            <p class="row agent-info">当前账号：<b>{{ data.username }}</b></p>
            <form class="agent-form" @submit.prevent="create"><fieldset :disabled="busy">
              <label for="agent-name">授权名称</label><div><input id="agent-name" ref="titleField" v-model="name" maxlength="40" placeholder="例如：我的 Codex" required autocomplete="off"><small>例如：电脑名称或 AI 工具名称</small></div>
              <span id="agent-scopes-label">允许的操作</span><div role="group" aria-labelledby="agent-scopes-label" class="agent-checks"><label><input v-model="scopes" type="checkbox" value="topics:write">发布主题</label><label><input v-model="scopes" type="checkbox" value="replies:write">回复主题</label></div>
              <span id="agent-boards-label">允许的版块</span><div role="group" aria-labelledby="agent-boards-label" class="agent-board-options"><label v-for="board in available" :key="board.id"><input v-model="boards" type="checkbox" :value="board.id">{{ board.name }}</label><p v-if="!available.length">没有允许所选操作的版块。</p><small>只列出你有权操作的版块。灌水限制和锁帖规则仍生效。</small></div>
              <label for="agent-days">有效期</label><div><select id="agent-days" v-model="days"><option v-for="n in [7,30,90,365]" :key="n" :value="n">{{ n }} 天</option></select><small>到期后自动失效</small></div>
              <label for="agent-password">确认账号密码</label><div><input id="agent-password" v-model="password" type="password" autocomplete="current-password" maxlength="128" required><small>仅用于确认本次创建，不会交给 Agent。</small></div>
              <div class="agent-form-actions"><button :disabled="!scopes.length || !boards.length"><img :src="icons+'yes.gif'" alt="">{{ busy ? '创建中…' : '创建授权' }}</button><button type="button" @click="closeCreate"><img :src="icons+'no.gif'" alt="">取消</button></div>
            </fieldset></form>
          </section>
          <details class="panel agent-help" :open="helpOpen" @toggle="helpOpen=$event.currentTarget.open"><summary class="row">如何接入 MCP</summary><div class="row"><p>将 Token 原文保存到本机私密文件，在 MCP 配置中指定文件路径：</p><pre>{"env": {
  "LEOBBS_URL": "{{ origin }}",
  "LEOBBS_TOKEN_FILE": "/你的私密目录/leobbs-token"
}}</pre><p>这部分配置不包含 Token 原文。撤销后，AI 将不能继续使用此授权发帖或回复。</p></div></details>
        </template>
      </div>
    </div>
    <div v-if="revokeTarget" class="agent-overlay" @click.self="!busy && (revokeTarget=null)" @keydown="dialogKeys"><section ref="revokeDialog" class="panel agent-dialog" role="dialog" aria-modal="true" aria-labelledby="agent-revoke-heading"><h2 id="agent-revoke-heading" class="bar">撤销授权</h2><div class="row"><p>确定撤销「{{ revokeTarget.name }}」？</p><p>该 AI 将不能再使用此授权。已发表的帖子保留。</p><div class="agent-dialog-actions"><button :disabled="busy" @click="revoke"><img :src="icons+'m_delete.gif'" alt="">{{ busy ? '撤销中…' : '确认撤销' }}</button><button :disabled="busy" @click="revokeTarget=null">取消</button></div></div></section></div>
  </div>
</template>

<style>
.classic-agent #app{max-width:1200px}.classic-agent .masthead{min-height:90px}.agent-layout{display:block}.agent-main{min-width:0}.agent-page .bar{display:flex;align-items:center;gap:7px}.agent-page img{width:auto;height:auto;max-width:20px;max-height:20px;object-fit:contain;flex:none}.agent-page button{gap:6px;min-height:40px;font-size:14px}.agent-toolbar>div{display:flex;gap:12px;margin-top:12px;flex-wrap:wrap}.agent-link{border:0;background:none;text-decoration:underline}.agent-info{background:#edf3ff;color:#3d4860}.agent-empty{padding:22px 12px;color:#53627e}.agent-table{border-collapse:collapse;width:100%;font-size:14px}.agent-table th{background:#dce9fa;text-align:left}.agent-table th,.agent-table td{padding:10px;border:1px solid #b8cae8;overflow-wrap:anywhere}.agent-table th:first-child,.agent-table td:first-child{border-left:0}.agent-table th:last-child,.agent-table td:last-child{border-right:0}.agent-table tbody tr:nth-child(even){background:#f4f7fc}.agent-status{color:#606570}.agent-status.active{color:#24702a;font-weight:bold}.agent-inactive,.agent-inactive .agent-name{color:#697386}.agent-name{color:#102c8c}.agent-action button{padding:4px 7px;background:transparent;border:0;color:#971e22}.agent-page .mobile-label{display:none}.agent-error{color:#971e22}.agent-notice{color:#245b29;background:#f3faf3}.agent-form fieldset{margin:0;padding:14px;border:0;display:grid;gap:7px}.agent-form fieldset>label,.agent-form fieldset>span{font-weight:bold;margin-top:7px}.agent-form input:not([type=checkbox]),.agent-form select,.agent-success textarea{font:inherit;border:1px solid #7291c6;padding:9px;width:100%;border-radius:0;background:white;min-height:42px}.agent-form input[type=checkbox]{margin:0 7px 0 0;width:16px;height:16px}.agent-checks{display:flex;gap:18px;flex-wrap:wrap}.agent-checks label,.agent-board-options label{min-height:36px;display:flex;align-items:center}.agent-board-options{padding:8px;background:#f0f5ff;border:1px solid #cedcf5}.agent-form-actions{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}.agent-success>*+*{margin-top:14px}.agent-success label{display:block;font-weight:bold}.agent-success textarea{font-family:monospace;overflow-wrap:anywhere;word-break:break-all;resize:vertical}.agent-warning{border:1px solid #bc9730;background:#fff9dd;padding:10px;color:#594b1d}.agent-summary{display:grid;grid-template-columns:65px 1fr;border:1px solid #b8cae8}.agent-summary dt,.agent-summary dd{margin:0;padding:8px;border-bottom:1px solid #b8cae8;overflow-wrap:anywhere}.agent-summary dt{background:#e5eefc}.agent-help summary{cursor:pointer;color:#102c8c}.agent-help pre{font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere;padding:10px;background:#f1f5fc;border:1px solid #cbd9ef}.agent-help p{margin:6px 0}.agent-overlay{position:fixed;inset:0;background:#14294555;display:flex;align-items:center;justify-content:center;padding:16px;z-index:100}.agent-dialog{width:420px;max-width:100%;box-shadow:0 5px 20px #15264e44}.agent-dialog p+p{margin-top:10px;color:#535b6c}.agent-dialog-actions{display:flex;gap:12px;margin-top:20px}.agent-sidebar{align-self:start}.agent-sidebar a{display:flex;align-items:center;gap:9px;padding:14px;border-bottom:1px solid #b8cae8}.agent-sidebar a[aria-current]{background:#d6e5fb;font-weight:bold}.agent-sidebar a span{margin-left:auto}.agent-profile-link{display:block;border-top:1px solid #b8cae8;padding:11px 10px}.agent-profile-link img{vertical-align:middle;margin-right:6px}
@media(min-width:850px){.agent-desktop .agent-layout{display:grid;grid-template-columns:175px minmax(0,1fr);gap:12px}.agent-desktop .agent-form fieldset{grid-template-columns:130px 1fr;gap:14px}.agent-desktop .agent-form-actions{grid-column:2}.agent-desktop .agent-success{max-width:760px;margin:auto}.agent-desktop .agent-table .agent-name{width:18%}}
@media(max-width:849px){.agent-sidebar{display:none}.agent-table thead{display:none}.agent-table,.agent-table tbody{display:block}.agent-table tr{position:relative;display:grid;grid-template-columns:1fr auto;padding:12px;gap:6px;border-top:1px solid #b8cae8}.agent-table td{display:block;border:0;padding:0}.agent-table .agent-name{grid-column:1;grid-row:1;min-width:0}.agent-table .agent-status{grid-column:2;grid-row:1;text-align:right}.agent-table .agent-permission{grid-column:1/-1;grid-row:2}.agent-permission small{display:inline;margin-left:8px;font-size:inherit}.agent-table .agent-expiry{grid-column:1/-1;grid-row:3;font-size:13px}.agent-table .agent-last{grid-column:1;grid-row:4;font-size:12px;align-self:center;color:#53627e}.agent-table .agent-action{grid-column:2;grid-row:4;align-self:center}.agent-page .mobile-label{display:inline}.agent-table .agent-action button{min-height:34px}.agent-page .agent-table{font-size:15px}}
</style>
