<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue'
import ForumStats from './ForumStats.vue'
import Mailbox from './Mailbox.vue'
import UbbBody from './ubb.js'
import UbbEditor from './UbbEditor.vue'

const state = ref(null)
const shareOpen = ref(false)
const shareStatus = ref('')
const shareUrl = computed(() => new URL(topicLink(boardId.value, topicId.value), location.origin).href)

async function shareTopic() {
  shareStatus.value = ''
  if (navigator.share) {
    try {
      await navigator.share({title: state.value.topic.title, url: shareUrl.value})
      return
    } catch (error) {
      if (error.name === 'AbortError') return
    }
  }
  shareOpen.value = !shareOpen.value
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    shareStatus.value = '链接已复制'
  } catch {
    shareStatus.value = '请长按链接复制'
  }
}

const authorFloor = ref(null)
const onlineDuration = seconds => [Math.floor(seconds / 3600), Math.floor(seconds / 60) % 60, seconds % 60]
  .map(value => String(value).padStart(2, '0')).join(':')
const error = ref('')
const route = ref([])
let request

const searching = computed(() => route.value[0] === 'search')
const searchParams = new URLSearchParams(location.search)
const searchTerm = ref(searchParams.get('q') || '')
const searchBoards = ref([])
const selectedBoards = ref(searchParams.getAll('board'))
const searchDraft = ref(searchTerm.value)
const boardId = computed(() => searching.value ? '' : route.value[0])
function submitSearch(event) {
  const filters = new URLSearchParams(new FormData(event.currentTarget))
  const query = filters.get('q').trim()
  if (query) {
    filters.set('q', query)
    location.assign('/m/search?' + filters)
  }
}
function searchLink(index) {
  const filters = new URLSearchParams(searchParams)
  filters.set('page', index)
  return '/m/search?' + filters
}
const topicId = computed(() => route.value[1])
const page = computed(() => new URLSearchParams(location.search).get('page') || 1)
const boardLink = id => '/m/' + id
const topicLink = (board, topic) => boardLink(board) + '/' + topic
const pageLink = index => (topicId.value ? topicLink(boardId.value, topicId.value) : boardLink(boardId.value)) + '?page=' + index
const legacy = '/cgi-bin/'
const img = '/non-cgi/'
const date = new Intl.DateTimeFormat('zh-CN', {dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Shanghai'})
const formatDate = value => value ? date.format(value * 1000) : ''
const desktopTopic = computed(() => legacy + 'topic.cgi?forum=' + boardId.value + '&topic=' + topicId.value)

const mode = ref('')
const pendingAction = ref('')
const account = ref('')
const checkingAccount = ref(true)
const showMailbox = ref(false)
const initialMailbox = ref('inbox')
const mailboxKey = ref(0)
function openMailbox(box) {
  initialMailbox.value = box
  mailboxKey.value++
  showMailbox.value = true
  window.scrollTo(0, 0)
}
const unreadMail = ref(0)
const profile = ref(null)
let mailTimer
const username = ref('')
const password = ref('')
const title = ref('')
const body = ref('')
const useUbb = ref(true)
const formError = ref('')
const busy = ref(false)

const email = ref('')
const confirmation = ref('')
const agreed = ref(false)
const challenge = ref(null)
const code = ref('')
const registrationReady = ref(false)
const notice = ref('')

async function prepareRegistration() {
  registrationReady.value = false
  challenge.value = null
  code.value = ''
  try {
    const response = await fetch(legacy + 'register.cgi?action=agreed', {cache: 'no-store'})
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    if (mode.value !== 'register') return
    const document = new DOMParser().parseFromString(html, 'text/html')
    const form = document.querySelector('form[name="creator"]')
    if (!response.ok || !form || !document.querySelector('[name="password"]')) {
      throw new Error('请使用经典版注册，当前注册设置需要原版流程。')
    }
    const session = document.querySelector('[name="sessionid"]')?.value
    if (session) {
      const image = document.querySelector('img[src*="/verifynum/"]')?.getAttribute('src')
      const url = new URL(image || '', location.href)
      if (url.origin !== location.origin || !url.pathname.startsWith('/non-cgi/verifynum/')) {
        throw new Error('验证码无法加载，请使用经典版注册。')
      }
      challenge.value = {session, image: url.href}
    }
    registrationReady.value = true
  } catch (error) {
    if (mode.value === 'register') formError.value = error.message
  }
}

function scrollToComposer() {
  if (mode.value === 'addreply') {
    nextTick(() => document.getElementById('reply-composer')?.scrollIntoView({block: 'start'}))
  } else if (mode.value) window.scrollTo(0, 0)
}

function openForm(nextMode) {
  pendingAction.value = !account.value && ['addnew', 'addreply'].includes(nextMode) ? nextMode : ''
  mode.value = pendingAction.value ? 'login' : nextMode
  formError.value = pendingAction.value ? '请先登录，再发帖或回复。' : ''
  if (nextMode === 'register') {
    agreed.value = false
    prepareRegistration()
  }
  scrollToComposer()
}

const editFields = ref(null)
const editingTitle = ref(false)

async function editPost(url, post) {
  if (post.desktopOnly) {
    location.assign(url)
    return
  }
  if (busy.value) return
  busy.value = true
  formError.value = ''
  try {
    const response = await fetch(url, {cache: 'no-store'})
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    const doc = new DOMParser().parseFromString(html, 'text/html')
    const input = doc.querySelector('textarea[name="inpost"]')
    if (!response.ok || !input) throw new Error('无法打开编辑表单，请确认编辑权限。')
    const fields = {action: 'processedit', forum: boardId.value, topic: topicId.value, postno: post.floor}
    for (const name of ['posticon', 'inshowsignature', 'inshowemoticons', 'inshowchgfont', 'inwater', 'notify']) {
      const option = doc.querySelector('input[name="' + name + '"]:checked')
      if (option) fields[name] = option.value
    }
    const subject = doc.querySelector('input[name="newtopictitle"]')
    editingTitle.value = Boolean(subject)
    title.value = subject?.value || ''
    body.value = input.value
    useUbb.value = post.ubb
    editFields.value = fields
    openForm('processedit')
  } catch (failure) {
    notice.value = failure.message
  } finally {
    busy.value = false
  }
}

async function submit() {
  if (busy.value) return
  busy.value = true
  formError.value = ''
  const action = mode.value
  const login = action === 'login'
  const registering = action === 'register'
  if (['addnew', 'addreply', 'processedit'].includes(action) && (!body.value.trim() || body.value.length > 8000)) {
    formError.value = '请填写正文，最多 8000 个字符。'
    busy.value = false
    return
  }
  if (registering && (!registrationReady.value || !agreed.value || password.value !== confirmation.value)) {
    formError.value = '请确认两次密码一致，并同意注册条款。'
    busy.value = false
    return
  }
  let fields = login
    ? {action, inmembername: username.value, inpassword: password.value, CookieDate: '0'}
    : {action, forum: boardId.value, inpost: body.value, uselbcode: useUbb.value ? 'yes' : 'no'}
  if (registering) {
    fields = {action: 'addmember', inmembername: username.value.trim(), emailaddress: email.value.trim(),
      password: password.value, password2: confirmation.value, showemail: 'no'}
    if (challenge.value) Object.assign(fields, {sessionid: challenge.value.session, verifynum: code.value})
  }
  if (action === 'processedit') {
    fields = {...fields, ...editFields.value}
    if (editingTitle.value) fields.newtopictitle = title.value
  }
  if (action === 'addnew') fields.intopictitle = title.value
  if (action === 'addreply') fields.topic = topicId.value
  try {
    const encoded = await fetch('/api/v1/legacy-form', {method: 'POST', body: new URLSearchParams(fields)})
    const result = await encoded.json()
    if (!encoded.ok) throw new Error(result.error)
    const response = await fetch(legacy + (registering ? 'register.cgi' : login ? 'loginout.cgi' : action === 'processedit' ? 'editpost.cgi' : 'post.cgi'), {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: result.form,
    })
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    if (registering) {
      if (!response.ok || !html.includes('感谢您注册')) {
        const document = new DOMParser().parseFromString(html, 'text/html')
        const reason = [...document.querySelectorAll('li')].find(item => item.textContent.includes('对不起'))
        if (challenge.value) await prepareRegistration()
        throw new Error(reason?.textContent.trim() || '注册失败，请核对资料或使用经典版注册。')
      }
      await refreshAccount()
      password.value = ''
      confirmation.value = ''
      notice.value = account.value ? '注册成功，已登录。' : '注册成功，请按论坛要求查收邮件后登录。'
      mode.value = account.value ? '' : 'login'
    } else if (login) {
      if (!response.ok || !html.includes('感谢你登录')) throw new Error('登录失败，请核对用户名和密码')
      await refreshAccount()
      password.value = ''
      if (!account.value) throw new Error('登录状态未生效，请重试')
      mode.value = pendingAction.value
      scrollToComposer()
      pendingAction.value = ''
      formError.value = ''
    } else {
      if (!response.ok || !/(新主题发表成功|回复成功|编辑成功)/.test(html)) {
        const doc = new DOMParser().parseFromString(html, 'text/html')
        const reason = [...doc.querySelectorAll('li')].find(li => li.textContent.includes('对不起'))
        throw new Error(reason?.textContent.trim() || '提交失败，请确认已登录且有发帖权限')
      }
      const newTopic = html.match(/topic\.cgi\?forum=\d+&topic=(\d+)/)?.[1]
      if (action === 'addnew' && newTopic) location.assign(topicLink(boardId.value, newTopic))
      else location.reload()
    }
  } catch (failure) {
    formError.value = failure.message || '提交失败'
  } finally {
    busy.value = false
  }
}

async function refreshUnreadMail() {
  const member = account.value
  if (!member || document.hidden) return
  try {
    const response = await fetch(legacy + 'messanger.cgi?action=mobileinbox&summary=1', {cache: 'no-store'})
    const data = await response.json()
    if (response.ok && account.value === member) unreadMail.value = data.unread || 0
  } catch {
    // Keep the last successful count if the connection drops.
  }
}

async function loadProfile() {
  const member = account.value
  if (!member || profile.value) return
  try {
    const response = await fetch(legacy + 'loginout.cgi?action=mobileprofile', {cache: 'no-store'})
    const data = await response.json()
    if (response.ok && account.value === member) profile.value = data
  } catch {
    // A later expansion can retry loading the profile.
  }
}

const postActions = ref({})
let actionRequest = 0

async function loadPostActions() {
  const sequence = ++actionRequest
  postActions.value = {}
  if (!account.value || !topicId.value || !state.value?.topic) return
  try {
    const target = {forum: boardId.value, topic: topicId.value}
    const response = await fetch(legacy + 'delpost.cgi?' + new URLSearchParams({
      action: 'mobilepermissions', ...target,
    }), {cache: 'no-store'})
    if (!response.ok) return
    const allowed = await response.json()
    const actions = {}
    for (const [floor, permissions] of Object.entries(allowed)) {
      if (!/^[1-9][0-9]*$/.test(floor)) continue
      actions[floor] = {
        edit: permissions.canEdit ? legacy + 'editpost.cgi?' + new URLSearchParams({
          action: 'edit', ...target, postno: floor,
        }) : '',
        remove: permissions.canDelete === 1 || permissions === 1,
      }
    }
    if (sequence === actionRequest && account.value) postActions.value = actions
  } catch {
    // Classic permissions could not be loaded.
  }
}

async function deletePost(floor) {
  const topic = floor === 1
  if (busy.value || !window.confirm(topic ? '确定删除整个主题及其回复？' : '确定删除这条回复？')) return
  busy.value = true
  notice.value = ''
  try {
    const fields = new URLSearchParams({
      action: topic ? 'delete' : 'directdel', checked: 'yes', leavemessage: 'yes',
      forum: boardId.value, topic: topicId.value, postno: floor,
    })
    const response = await fetch(legacy + 'delpost.cgi', {method: 'POST', body: fields})
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    const message = new DOMParser().parseFromString(html, 'text/html').body.textContent
    if (!response.ok || !(topic ? /删除成功/ : /已删除\s*\d+\s*篇回复/).test(message)) {
      throw new Error('删除失败，请确认你仍有删除权限。')
    }
    if (topic) location.assign(boardLink(boardId.value))
    else {
      await load()
      notice.value = '回复已删除。'
    }
  } catch (failure) {
    notice.value = failure.message
  } finally {
    busy.value = false
  }
}

async function refreshAccount() {
  checkingAccount.value = true
  try {
    const response = await fetch(legacy + 'loginout.cgi?action=mobilestatus', {cache: 'no-store'})
    const text = new TextDecoder('gbk').decode(await response.arrayBuffer())
    account.value = response.ok ? text.match(/^LEOBBS_MEMBER:([^\r\n]+)$/)?.[1] || '' : ''
  } catch {
    account.value = ''
  } finally {
    checkingAccount.value = false
    unreadMail.value = 0
    if (account.value) refreshUnreadMail()
    loadPostActions()
  }
}

async function logout() {
  profile.value = null
  await fetch(legacy + 'loginout.cgi?action=logout')
  await refreshAccount()
}

async function load() {
  // Cancel the previous navigation so a slow response cannot overwrite the current page.
  request?.abort()
  const controller = new AbortController()
  request = controller
  // Convert old bookmarks before reading the current path.
  const oldRoute = location.hash.match(/^#\/(\d*)(?:\/(\d*))?(?:\/(\d+))?$/)
  if (oldRoute) {
    const [, board, topic, index] = oldRoute
    const path = topic ? topicLink(board, topic) : board ? boardLink(board) : '/m/'
    history.replaceState(null, '', path + (index ? '?page=' + index : ''))
  }
  route.value = location.pathname.slice('/m/'.length).split('/')
  state.value = null
  error.value = ''
  window.scrollTo(0, 0)
  if (searching.value && !searchTerm.value.trim()) {
    state.value = {items: [], pages: 1}
    fetch('/api/v1/home', {signal: controller.signal}).then(response => response.json()).then(data => { searchBoards.value = data.boards || [] }).catch(() => {})
    return
  }
  const path = searching.value ? '/search' : boardId.value
    ? '/boards/' + encodeURIComponent(boardId.value) + (topicId.value ? '/topics/' + encodeURIComponent(topicId.value) : '')
    : '/home'
  try {
    const response = await fetch('/api/v1' + path + '?' + (searching.value ? searchParams : new URLSearchParams({page: page.value})), {signal: controller.signal})
    const data = await response.json()
    if (!response.ok) throw new Error(data.error)
    if (!controller.signal.aborted) {
      state.value = data
      loadPostActions()
      if (searching.value) searchBoards.value = data.boards
    }
  } catch (failure) {
    if (!controller.signal.aborted) error.value = failure.message || '暂时无法读取论坛'
  }
}
function closeAuthorCard() {
  authorFloor.value = null
}

onMounted(() => {
  document.addEventListener('click', closeAuthorCard)
  refreshAccount()
  mailTimer = window.setInterval(refreshUnreadMail, 30000)
  window.addEventListener('focus', refreshUnreadMail)
  load()
})
onUnmounted(() => {
  document.removeEventListener('click', closeAuthorCard)
  window.clearInterval(mailTimer)
  window.removeEventListener('focus', refreshUnreadMail)
  request?.abort()
})
</script>

<template>
  <header class="shell">
    <div class="masthead">
      <a href="/m/" aria-label="LeoBBS 首页"><img :src="img + 'myimages/mainlogo.gif'" alt="LeoBBS"></a>
      <strong>雷傲极酷超级论坛</strong>
    </div>
    <nav aria-label="论坛导航">
      <a href="/m/" class="home-icon" aria-label="首页" title="首页"><img :src="img + 'images/homepage.gif'" alt="">首页</a>
      <a href="/m/search">搜索</a>
      <a :href="legacy + 'leobbs.htm'">桌面版</a>
      <button v-if="account" class="mail-toggle" :aria-expanded="showMailbox"
        :aria-label="unreadMail ? '站内信，' + unreadMail + ' 封未读' : '站内信'"
        :title="unreadMail ? unreadMail + ' 封未读站内信' : '站内信'"
        @click="showMailbox = !showMailbox; refreshUnreadMail()">
        <img :class="{'mail-unread': unreadMail}" :src="img + (unreadMail ? 'images/newmail.gif' : 'images/inboxnonew.gif')" alt="">
      </button>
      <span v-if="checkingAccount" class="nav-action" role="status">检测中…</span>
      <button v-else-if="!account" class="nav-action" @click="openForm('login')">登录</button>
      <span v-else class="account-nav">
        <span class="account-name">{{ account }}</span>
        <button class="nav-action" @click="logout">退出</button>
      </span>
    </nav>
  </header>

  <main>
    <Mailbox v-if="account && showMailbox" :key="mailboxKey" :initial-box="initialMailbox" @read="refreshUnreadMail" />
    <p v-if="notice" class="panel row" role="status">{{ notice }}</p>
    <Teleport defer to="#reply-composer" :disabled="mode !== 'addreply'">
    <form v-if="mode" class="panel compose" @submit.prevent="submit">
      <h2 class="bar">{{ {login: '登录', register: '注册', addnew: '发表主题', addreply: '回复', processedit: '编辑帖子'}[mode] }}</h2>
      <div class="row">
        <template v-if="mode === 'login'">
          <label>用户名<input v-model="username" autocomplete="username" required></label>
          <label>密码<input v-model="password" type="password" autocomplete="current-password" required></label>
        </template>
        <template v-else-if="mode === 'register'">
          <label>用户名<input v-model.trim="username" maxlength="12" autocomplete="username" required></label>
          <label>邮箱<input v-model.trim="email" type="email" autocomplete="email" required></label>
          <label>密码<input v-model="password" type="password" maxlength="20" autocomplete="new-password" required></label>
          <label>确认密码<input v-model="confirmation" type="password" maxlength="20" autocomplete="new-password" required></label>
          <label v-if="challenge">验证码
            <img :src="challenge.image" alt="注册验证码">
            <input v-model="code" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" required>
          </label>
          <button v-if="challenge" type="button" @click="prepareRegistration">换一张</button>
          <label><input v-model="agreed" type="checkbox" required> 我同意<a :href="legacy + 'register.cgi'" target="_blank" rel="noopener">论坛注册条款</a></label>
          <a :href="legacy + 'register.cgi'">经典版注册</a>
        </template>
        <template v-else>
          <label v-if="mode === 'addnew' || (mode === 'processedit' && editingTitle)">标题<input v-model.trim="title" maxlength="80" required></label>
          <UbbEditor v-model="body" v-model:enabled="useUbb" />
        </template>
        <p v-if="formError" role="alert">{{ formError }}</p>
        <button :disabled="busy || (mode === 'register' && !registrationReady)"><img v-if="['addnew', 'addreply', 'processedit'].includes(mode)" class="submit-icon" :src="img + 'images/yes.gif'" alt="">{{ busy ? '提交中…' : '提交' }}</button>
        <button type="button" :disabled="busy" @click="openForm('')"><img v-if="['addnew', 'addreply', 'processedit'].includes(mode)" class="submit-icon" :src="img + 'images/no.gif'" alt="">取消</button>
        <button v-if="mode === 'login'" type="button" :disabled="busy" @click="openForm('register')">注册</button>
      </div>
    </form>
    </Teleport>
    <section v-if="searching" class="panel">
      <h1 class="bar">搜索帖子</h1>
      <form class="row search-form" action="/m/search" @submit.prevent="submitSearch">
        <label for="search-title">帖子标题</label>
        <input id="search-title" v-model="searchDraft" name="q" type="search" maxlength="80" required>
        <button type="submit">搜索</button>
        <details class="search-options" :open="searchParams.has('mode')">
          <summary>高级搜索</summary>
          <label>搜索范围
            <select name="mode" :value="searchParams.get('mode') || 'title'">
              <option value="title">主题标题</option>
              <option value="body">帖子正文</option>
              <option value="both">标题和正文</option>
              <option value="author">主题作者</option>
              <option value="reply_author">回复作者</option>
              <option value="all_authors">主题和回复作者</option>
            </select>
          </label>
          <label>主题发表日期
            <select name="days" :value="searchParams.get('days') || 'any'">
              <option value="any">任何日期</option>
              <option v-for="days in [1, 7, 14, 30, 90, 180, 365]" :key="days" :value="days">{{ days }} 天</option>
            </select>
            <select name="when" aria-label="日期方向" :value="searchParams.get('when') || 'after'">
              <option value="after">之内</option><option value="before">之前</option>
            </select>
          </label>
          <fieldset v-if="searchBoards.length">
            <legend>搜索版块（未选时搜索所有公开版块）</legend>
            <label v-for="board in searchBoards" :key="board.id">
              <input v-model="selectedBoards" type="checkbox" name="board" :value="String(board.id)">
              {{ board.category }} › {{ board.name }}
            </label>
          </fieldset>
        </details>
      </form>
    </section>
    <p v-if="error" role="alert" class="panel row">{{ error }} <button @click="load">重试</button></p>
    <p v-else-if="!state" role="status" class="panel row">正在读取论坛…</p>
    <template v-else-if="searching">
      <section v-if="searchTerm.trim()" class="panel">
        <h2 class="bar">搜索结果</h2>
        <a v-for="topic in state.items" :key="topic.boardId + '-' + topic.id" class="row entry" :href="topicLink(topic.boardId, topic.id)">
          <img :src="img + 'posticons/' + topic.icon + '.gif'" alt="">
          <span><b>{{ topic.title }}</b><small>{{ topic.boardName }} · {{ topic.author }} · {{ formatDate(topic.updated) }}</small></span>
        </a>
        <p v-if="!state.items.length" class="row">没有找到匹配的帖子</p>
      </section>
      <nav v-if="state.pages > 1 || page > 1" class="panel pager" aria-label="搜索分页">
        <a v-if="page > 1" class="button" :href="searchLink(Number(page) - 1)">上一页</a>
        <span>{{ page }} / {{ state.pages }}</span>
        <a v-if="page < state.pages" class="button" :href="searchLink(Number(page) + 1)">下一页</a>
      </nav>
    </template>
    <template v-else-if="!boardId">
      <details v-if="account" class="panel" @toggle="$event.currentTarget.open && loadProfile()">
        <summary class="bar">个人状态 · {{ account }} · {{ unreadMail }} 封未读</summary>
        <div v-if="profile" class="row">
          <small>来自 {{ profile.address || '—' }} · 最后访问 {{ formatDate(profile.lastVisit) || '—' }}</small>
          <div class="profile-grid">
            <section><h3>我的财产</h3>
              <div>现金 <b>{{ profile.money }} {{ profile.currency || '雷傲元' }}</b></div>
              <div>存款 <b>{{ profile.deposit ?? '没开户' }}</b></div>
              <div>贷款 <b>{{ profile.loan || '没贷款' }}</b></div>
            </section>
            <section><h3>我的短消息</h3>
              <div><button class="profile-link" @click="openMailbox('inbox')">收件箱</button> <b>{{ profile.inbox }}</b></div>
              <div><button class="profile-link" @click="openMailbox('outbox')">发件箱</button> <b>{{ profile.outbox }}</b></div>
              <div>条数限制 <b>{{ profile.limit || '没有限制' }}</b></div>
            </section>
            <section><h3>我的文章</h3>
              <div>发表数 <b>{{ profile.posts }}</b></div>
              <div>回复数 <b>{{ profile.replies }}</b></div>
              <div>被删数 <b>{{ profile.deleted }}</b></div>
            </section>
          </div>
        </div>
      </details>
      <section v-for="category in [...new Set(state.boards.map(board => board.category))]" :key="category" class="panel">
        <h1 class="bar">◇ {{ category }}</h1>
        <a v-for="board in state.boards.filter(board => board.category === category)" :key="board.id" :href="boardLink(board.id)" class="row entry">
          <img :src="img + 'images/leobbs/foldernew.gif'" alt="">
          <span><b>{{ board.name }}</b><small>{{ board.description }}</small></span>
          <small class="counts">主题 {{ board.topics }}<br>回复 {{ board.posts }}</small>
        </a>
      </section>
      <p v-if="!state.boards.length" class="panel row">暂无开放的手机版版块</p>
      <section class="panel">
        <h2 class="bar">◇ 最新主题</h2>
        <a v-for="topic in state.latest" :key="topic.boardId + '-' + topic.id" class="row entry" :href="topicLink(topic.boardId, topic.id)">
          <img :src="img + 'posticons/' + topic.icon + '.gif'" alt="">
          <span><b>{{ topic.title }}</b><small>{{ topic.author }} · {{ formatDate(topic.updated) }}</small></span>
        </a>
        <p v-if="!state.latest.length" class="row">还没有主题</p>
      </section>
      <ForumStats :stats="state.stats" />
    </template>
    <template v-else>
      <div class="crumb"><a href="/m/">首页</a> › <a :href="boardLink(boardId)">{{ state.board.name }}</a><template v-if="topicId"> › 帖子详情</template></div>
      <section v-if="!topicId" class="panel">
        <div class="bar heading"><h1>{{ state.board.name }}</h1><button class="button" :disabled="checkingAccount" @click="openForm('addnew')"><img :src="img + 'images/edit.gif'" alt="">发帖</button></div>
        <p v-if="state.board.description" class="row intro">{{ state.board.description }}</p>
        <a v-for="topic in state.items" :key="topic.id" class="row entry" :href="topicLink(boardId, topic.id)">
          <img :src="img + 'posticons/' + topic.icon + '.gif'" alt="">
          <span><b>{{ topic.title }}</b><small>{{ topic.author }} · 回复 {{ topic.replies }} · {{ formatDate(topic.updated) }}</small></span>
        </a>
        <p v-if="!state.items.length" class="row">这一页没有主题</p>
      </section>
      <template v-else>
        <div class="bar panel heading">
          <h1>{{ state.topic.title }}</h1>
          <button class="button share-button" type="button" @click="shareTopic"><img :src="img + 'images/copy.gif'" alt="">分享</button>
        </div>
        <section v-if="shareOpen" class="panel row share-options" aria-label="分享帖子">
          <input :value="shareUrl" aria-label="帖子链接" readonly @focus="$event.target.select()">
          <button type="button" @click="copyShareLink">复制链接</button>
          <p v-if="shareStatus" role="status">{{ shareStatus }}</p>
        </section>
        <article v-for="post in state.items" :key="post.floor" class="panel post">
          <header class="byline">
            <button type="button" class="author-toggle" :style="{color: post.profile?.color || undefined}" :aria-expanded="authorFloor === post.floor"
              :aria-controls="'author-card-' + post.floor"
              @click.stop="authorFloor = authorFloor === post.floor ? null : post.floor">{{ post.author }}</button><small>{{ formatDate(post.created) }}</small>
            <b>{{ post.floor === 1 ? '楼主' : post.floor + ' 楼' }}</b>
          </header>
          <section v-if="authorFloor === post.floor" :id="'author-card-' + post.floor"
            class="author-card panel" :aria-label="post.author + '的资料'" @keydown.esc="authorFloor = null">
            <header class="bar heading"><strong>{{ post.author }}</strong>
            </header>
            <template v-if="post.profile">
              <div class="row author-fields">
                <div class="author-avatar">
                  <img :src="post.profile.avatar" :alt="post.author + '的头像'">
                </div>
                <div>头衔 <b>{{ post.profile.title }}</b></div>
                <div>等级 <a :href="legacy + 'lookinfo.cgi?action=style'">{{ post.profile.level || '—' }}</a>
                  <img v-if="post.profile.badge" :src="img + 'images/' + post.profile.badge" alt="">
                </div>
                <div>信息
                  <img v-if="post.profile.online" :src="img + 'images/online1.gif'" alt="当前在线">
                  <span v-else>未显示在线</span>
                  <img v-if="post.profile.roleIcon" :src="img + 'images/' + post.profile.roleIcon + '.gif'" :alt="post.profile.title">
                </div>
                <div>威望 <b>{{ post.profile.reputation }}</b>　积分 <b>{{ post.profile.points }}</b></div>
                <div>现金 <b>{{ post.profile.cash }} {{ post.profile.currency || '雷傲元' }}</b></div>
                <div>存款 <b>{{ post.profile.deposit ?? '没开户' }}</b></div>
                <div>贷款 <b>{{ post.profile.loan || '没贷款' }}</b></div>
                <div>来自 <b>{{ post.profile.location || '保密' }}</b>
                  <img :src="img + 'flags/' + post.profile.flag + '.gif'" alt="">
                </div>
                <div>发帖 <b>{{ post.profile.posts }}</b> 篇</div>
                <div>精华 <b>{{ post.profile.featured }}</b> 篇</div>
                <div>累计在线 <b>{{ onlineDuration(post.profile.onlineSeconds) }}</b></div>
                <div>注册 <b>{{ formatDate(post.profile.joined) || '—' }}</b></div>
                <div>造访 <b>{{ formatDate(post.profile.lastVisit) || '—' }}</b></div>
              </div>
            </template>
            <p v-else class="row">暂无会员资料</p>
          </section>
          <div class="body"><a v-if="post.desktopOnly" :href="desktopTopic">在经典版查看此楼内容</a><UbbBody v-else :body="post.body" :enabled="post.ubb" /></div>
          <footer v-if="postActions[post.floor]" class="row post-actions">
            <button v-if="postActions[post.floor].edit" type="button" @click="editPost(postActions[post.floor].edit, post)"><img :src="img + 'images/edit.gif'" alt="">编辑</button>
            <button v-if="postActions[post.floor].remove" type="button"
              @click="deletePost(post.floor)"><img :src="img + 'images/del.gif'" alt="">{{ post.floor === 1 ? '删除主题' : '删除回复' }}</button>
          </footer>
        </article>
        <div class="actions">
          <a :href="desktopTopic">经典版帖子</a>
          <button v-if="!['closed', 'pollclosed'].includes(state.topic.state)" class="button" :disabled="checkingAccount" @click="openForm('addreply')"><img :src="img + 'images/replynow.gif'" alt="">回复</button>
        </div>
      </template>
      <nav v-if="state.pages > 1 || page > 1" class="panel pager" aria-label="分页">
        <a v-if="page > 1" class="button" :href="pageLink(page - 1)">上一页</a>
        <span>{{ page }} / {{ state.pages }}</span>
        <a v-if="page < state.pages" class="button" :href="pageLink(Number(page) + 1)">下一页</a>
      </nav>
    </template>
    <div id="reply-composer"></div>
  </main>
  <footer>LeoBBS · 雷傲科技</footer>
</template>
