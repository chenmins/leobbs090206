<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const state = ref(null)
const error = ref('')
const route = ref([])
let request

const boardId = computed(() => route.value[0])
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
  const path = boardId.value
    ? '/boards/' + encodeURIComponent(boardId.value) + (topicId.value ? '/topics/' + encodeURIComponent(topicId.value) : '')
    : '/home'
  try {
    const response = await fetch('/api/v1' + path + '?page=' + page.value, {signal: controller.signal})
    const data = await response.json()
    if (!response.ok) throw new Error(data.error)
    if (!controller.signal.aborted) state.value = data
  } catch (failure) {
    if (!controller.signal.aborted) error.value = failure.message || '暂时无法读取论坛'
  }
}
onMounted(() => {
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
      <a href="/m/"><img :src="img + 'images/gohome.gif'" alt="">首页</a>
      <a :href="legacy + 'search.cgi'">搜索</a>
      <a :href="legacy + 'loginout.cgi'">登录</a>
      <a :href="legacy + 'leobbs.htm'">桌面版</a>
    </nav>
  </header>

  <main>
    <p v-if="error" role="alert" class="panel row">{{ error }} <button @click="load">重试</button></p>
    <p v-else-if="!state" role="status" class="panel row">正在读取论坛…</p>
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
        <div class="bar heading"><h1>{{ state.board.name }}</h1><a class="button" :href="legacy + 'post.cgi?action=new&forum=' + boardId"><img :src="img + 'images/edit.gif'" alt="">发帖</a></div>
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
          <div class="body"><a v-if="post.desktopOnly" :href="desktopTopic">在经典版查看此楼内容</a><template v-else>{{ post.body }}</template></div>
        </article>
        <div class="actions">
          <a :href="desktopTopic">经典版帖子</a>
          <a v-if="!['closed', 'pollclosed'].includes(state.topic.state)" class="button" :href="legacy + 'post.cgi?action=reply&forum=' + boardId + '&topic=' + topicId"><img :src="img + 'images/replynow.gif'" alt="">回复</a>
        </div>
      </template>
      <nav v-if="state.pages > 1 || page > 1" class="panel pager" aria-label="分页">
        <a v-if="page > 1" class="button" :href="pageLink(page - 1)">上一页</a>
        <span>{{ page }} / {{ state.pages }}</span>
        <a v-if="page < state.pages" class="button" :href="pageLink(page + 1)">下一页</a>
      </nav>
    </template>
  </main>
  <footer>LeoBBS · 雷傲科技</footer>
</template>
