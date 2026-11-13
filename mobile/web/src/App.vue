<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ubbTokens } from './ubb.js'

const state = ref(null)
const error = ref('')
const route = ref([])
let request

const searching = computed(() => route.value[0] === 'search')
const searchTerm = ref(new URLSearchParams(location.search).get('q') || '')
const searchDraft = ref(searchTerm.value)
const boardId = computed(() => searching.value ? '' : route.value[0])
function submitSearch(event) {
  const query = String(new FormData(event.currentTarget).get('q') || '').trim()
  if (query) location.assign('/m/search?' + new URLSearchParams({q: query}))
}
const searchLink = index => '/m/search?' + new URLSearchParams({q: searchTerm.value, page: index})
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
const username = ref('')
const password = ref('')
const title = ref('')
const body = ref('')
const useUbb = ref(true)
const formError = ref('')
const busy = ref(false)

function openForm(nextMode) {
  pendingAction.value = !account.value && ['addnew', 'addreply'].includes(nextMode) ? nextMode : ''
  mode.value = pendingAction.value ? 'login' : nextMode
  formError.value = pendingAction.value ? '请先登录，再发帖或回复。' : ''
  if (nextMode) window.scrollTo(0, 0)
}

async function submit() {
  if (busy.value) return
  busy.value = true
  formError.value = ''
  const action = mode.value
  const login = action === 'login'
  const fields = login
    ? {action, inmembername: username.value, inpassword: password.value, CookieDate: '0'}
    : {action, forum: boardId.value, inpost: body.value, uselbcode: useUbb.value ? 'yes' : 'no'}
  if (action === 'addnew') fields.intopictitle = title.value
  if (action === 'addreply') fields.topic = topicId.value
  try {
    const encoded = await fetch('/api/v1/legacy-form', {method: 'POST', body: new URLSearchParams(fields)})
    const result = await encoded.json()
    if (!encoded.ok) throw new Error(result.error)
    const response = await fetch(legacy + (login ? 'loginout.cgi' : 'post.cgi'), {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: result.form,
    })
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    if (login) {
      if (!response.ok || !html.includes('感谢你登录')) throw new Error('登录失败，请核对用户名和密码')
      await refreshAccount()
      password.value = ''
      if (!account.value) throw new Error('登录状态未生效，请重试')
      mode.value = pendingAction.value
      pendingAction.value = ''
      formError.value = ''
    } else {
      if (!response.ok || !/(新主题发表成功|回复成功)/.test(html)) {
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
  }
}

async function logout() {
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
    return
  }
  const path = searching.value ? '/search' : boardId.value
    ? '/boards/' + encodeURIComponent(boardId.value) + (topicId.value ? '/topics/' + encodeURIComponent(topicId.value) : '')
    : '/home'
  try {
    const response = await fetch('/api/v1' + path + '?' + new URLSearchParams({page: page.value, ...(searching.value ? {q: searchTerm.value} : {})}), {signal: controller.signal})
    const data = await response.json()
    if (!response.ok) throw new Error(data.error)
    if (!controller.signal.aborted) state.value = data
  } catch (failure) {
    if (!controller.signal.aborted) error.value = failure.message || '暂时无法读取论坛'
  }
}
onMounted(() => {
  refreshAccount()
  load()
})
onUnmounted(() => {
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
      <span v-if="checkingAccount" class="nav-action" role="status">检测中…</span>
      <button v-else-if="!account" class="nav-action" @click="openForm('login')">登录</button>
      <button v-else class="nav-action" @click="logout">退出 {{ account }}</button>
    </nav>
  </header>

  <main>
    <form v-if="mode" class="panel compose" @submit.prevent="submit">
      <h2 class="bar">{{ {login: '登录', addnew: '发表主题', addreply: '回复'}[mode] }}</h2>
      <div class="row">
        <template v-if="mode === 'login'">
          <label>用户名<input v-model="username" autocomplete="username" required></label>
          <label>密码<input v-model="password" type="password" autocomplete="current-password" required></label>
        </template>
        <template v-else>
          <label v-if="mode === 'addnew'">标题<input v-model.trim="title" maxlength="80" required></label>
          <label>正文<textarea v-model="body" rows="6" maxlength="8000" required></textarea></label>
          <label><input v-model="useUbb" type="checkbox">启用 UBB</label>
        </template>
        <p v-if="formError" role="alert">{{ formError }}</p>
        <button :disabled="busy">{{ busy ? '提交中…' : '提交' }}</button>
        <button type="button" :disabled="busy" @click="openForm('')">取消</button>
      </div>
    </form>
    <section v-if="searching" class="panel">
      <h1 class="bar">搜索帖子</h1>
      <form class="row search-form" action="/m/search" @submit.prevent="submitSearch">
        <label for="search-title">帖子标题</label>
        <input id="search-title" v-model="searchDraft" name="q" type="search" maxlength="80" required>
        <button type="submit">搜索</button>
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
        <h1 class="bar panel">{{ state.topic.title }}</h1>
        <article v-for="post in state.items" :key="post.floor" class="panel post">
          <header class="byline">
            <strong>{{ post.author }}</strong><small>{{ formatDate(post.created) }}</small>
            <b>{{ post.floor === 1 ? '楼主' : post.floor + ' 楼' }}</b>
          </header>
          <div class="body"><a v-if="post.desktopOnly" :href="desktopTopic">在经典版查看此楼内容</a><template v-else><component :is="token.tag" v-for="(token, index) in (post.ubb ? ubbTokens(post.body) : [{tag: 'span', text: post.body}])" :key="index">{{ token.text }}</component></template></div>
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
  </main>
  <footer>LeoBBS · 雷傲科技</footer>
</template>
