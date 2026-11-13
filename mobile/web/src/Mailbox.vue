<script setup>
import { onMounted, ref, watch } from 'vue'

const emit = defineEmits(['read'])
const box = ref('inbox')
const items = ref([])
const page = ref(1)
const pages = ref(1)
const error = ref('')
const notice = ref('')
const busy = ref(false)
const to = ref('')
const title = ref('')
const message = ref('')
const classic = '/cgi-bin/messanger.cgi'

const contacts = ref([])
const contactName = ref('')
const contactBoxes = ['friend', 'block']

const composeFriends = ref([])
watch(box, async (current, _, onCleanup) => {
  if (current !== 'compose') return
  const request = new AbortController()
  onCleanup(() => request.abort())
  composeFriends.value = []
  try {
    const response = await fetch('/cgi-bin/friendlist.cgi?action=mobilelist', {
      cache: 'no-store', signal: request.signal,
    })
    if (response.ok) {
      const data = await response.json()
      if (!request.signal.aborted) composeFriends.value = data.names
    }
  } catch {
    // The recipient can still be entered manually.
  }
})

async function updateContacts(kind, action, name) {
  if (busy.value) return
  busy.value = true
  box.value = kind
  error.value = ''
  notice.value = ''
  contacts.value = []
  const endpoint = '/cgi-bin/' + kind + 'list.cgi'
  try {
    if (action) {
      const fields = new URLSearchParams({action, [action]: name})
      const encoded = await fetch('/api/v1/legacy-form', {method: 'POST', body: fields})
      const data = await encoded.json()
      if (!encoded.ok) throw new Error(data.error)
      const response = await fetch(endpoint, {method: 'POST', body: data.form,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
      if (!response.ok) throw new Error('名单操作失败，请重试。')
      await response.arrayBuffer()
    }
    const response = await fetch(endpoint + '?action=mobilelist', {cache: 'no-store'})
    if (!response.ok) throw new Error('无法读取名单，请确认登录状态。')
    contacts.value = (await response.json()).names
    const exists = contacts.value.some(entry => entry.toLowerCase() === name?.toLowerCase())
    if (action && exists !== (action === 'adduser')) throw new Error('名单未更新，请核对用户名。')
    if (action) contactName.value = ''
  } catch (failure) {
    error.value = failure.message
  } finally {
    busy.value = false
  }
}

async function load(nextBox, nextPage = 1) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  box.value = nextBox
  items.value = []
  try {
    const response = await fetch(classic + '?action=mobile' + nextBox + '&page=' + nextPage)
    if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
      throw new Error('无法读取站内信，请确认登录状态。')
    }
    const data = await response.json()
    items.value = data.items
    page.value = data.page
    pages.value = data.pages
  } catch (failure) {
    error.value = failure.message
  } finally {
    busy.value = false
  }
}

async function markRead(event, item) {
  if (!event.currentTarget.open || box.value !== 'inbox' || !item.unread || item.marking) return
  item.marking = true
  try {
    // Use the classic read action so both versions share the same read state.
    const response = await fetch(classic + '?action=read&msg=' + item.index, {cache: 'no-store'})
    if (!response.ok) throw new Error()
    const status = await fetch(classic + '?action=mobileinbox&page=' + page.value, {cache: 'no-store'})
    const data = await status.json()
    const updated = data.items.find(entry => entry.index === item.index &&
      entry.date === item.date && entry.title === item.title && entry.person === item.person)
    if (!updated || updated.unread) throw new Error()
    item.unread = 0
    emit('read')
  } catch {
    error.value = '未能更新已读状态，请关闭信件后重试。'
  } finally {
    item.marking = false
  }
}

function reply(item) {
  to.value = item.person
  title.value = ('回复：' + item.title).slice(0, 80)
  box.value = 'compose'
  error.value = ''
}

async function send() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    const fields = new URLSearchParams({action: 'send', touser: to.value, msgtitle: title.value,
      message: message.value, backup: 'yes'})
    const encoded = await fetch('/api/v1/legacy-form', {method: 'POST', body: fields})
    const result = await encoded.json()
    if (!encoded.ok) throw new Error(result.error)
    const response = await fetch(classic, {method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: result.form})
    const html = new TextDecoder('gbk').decode(await response.arrayBuffer())
    if (!response.ok || !html.includes('的短消息已经发出。')) {
      throw new Error('发送失败，请核对收件人和登录状态。')
    }
    to.value = title.value = message.value = ''
    notice.value = '站内信已发送。'
    busy.value = false
    await load('outbox')
  } catch (failure) {
    error.value = failure.message
  } finally {
    busy.value = false
  }
}

onMounted(() => load('inbox'))
</script>

<template>
  <section class="panel compose">
    <h2 class="bar">站内信</h2>
    <div class="row mail-actions">
      <button :disabled="busy" :aria-current="box === 'inbox' ? 'page' : undefined" @click="load('inbox')"><img :src="'/non-cgi/images/inboxpm.gif'" alt="收件箱"></button>
      <button :disabled="busy" :aria-current="box === 'outbox' ? 'page' : undefined" @click="load('outbox')"><img :src="'/non-cgi/images/outboxpm.gif'" alt="发件箱"></button>
      <button :disabled="busy" :aria-current="box === 'compose' ? 'page' : undefined" @click="box = 'compose'; error = ''"><img :src="'/non-cgi/images/newpm.gif'" alt="撰写"></button>
      <button :disabled="busy" :aria-current="box === 'friend' ? 'page' : undefined" @click="updateContacts('friend')"><img :src="'/non-cgi/images/friendpm.gif'" alt="好友录"></button>
      <button :disabled="busy" :aria-current="box === 'block' ? 'page' : undefined" @click="updateContacts('block')"><img :src="'/non-cgi/images/blockpm.gif'" alt="黑名单"></button>
    </div>
    <p v-if="notice" class="row" role="status">{{ notice }}</p>
    <p v-if="error" class="row" role="alert">{{ error }}</p>
    <form v-if="box === 'compose'" class="row" @submit.prevent="send">
      <label>收件人<input v-model.trim="to" maxlength="12" required></label>
      <label>从好友录选择
        <select @change="to = $event.target.value || to" :value="composeFriends.includes(to) ? to : ''">
          <option value="">{{ composeFriends.length ? '选择好友' : '暂无可选好友' }}</option>
          <option v-for="name in composeFriends" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <label>主题<input v-model.trim="title" maxlength="80" required></label>
      <label>信件正文<textarea v-model="message" rows="6" maxlength="8000" required></textarea></label>
      <button :disabled="busy">发送</button>
    </form>
    <template v-else-if="contactBoxes.includes(box)">
      <form class="row" @submit.prevent="updateContacts(box, 'adduser', contactName)">
        <label>用户名<input v-model.trim="contactName" maxlength="12" required></label>
        <button :disabled="busy">添加{{ box === 'friend' ? '好友' : '到黑名单' }}</button>
      </form>
      <p v-if="!busy && !contacts.length && !error" class="row">名单为空。</p>
      <div v-for="name in contacts" :key="name" class="row mail-summary">
        <span class="mail-title">{{ name }}</span>
        <button v-if="box === 'friend'" :disabled="busy" @click="to = name; title = ''; message = ''; box = 'compose'">写信</button>
        <button :disabled="busy" @click="updateContacts(box, 'deluser', name)">移除</button>
      </div>
    </template>
    <template v-else>
      <p v-if="!busy && !error && !items.length" class="row">这个信箱还没有消息。</p>
      <details v-for="item in items" :key="box + '-' + page + '-' + item.index" class="row" @toggle="markRead($event, item)">
        <summary class="mail-summary">
          <img class="mail-status"
            :src="box === 'inbox' && item.unread ? '/non-cgi/images/unread.gif' : '/non-cgi/images/read.gif'"
            :alt="box === 'inbox' ? (item.unread ? '未读' : '已读') : ''">
          <span class="mail-title">{{ item.title }}</span>
          <small class="mail-person">{{ item.person }}</small>
        </summary>
        <div class="body">{{ item.body }}</div>
        <button v-if="box === 'inbox'" @click="reply(item)">回复站内信</button>
        <a :href="classic + '?action=' + (box === 'inbox' ? 'read' : 'outread') + '&msg=' + item.index">在经典版打开</a>
      </details>
      <div v-if="pages > 1" class="row mail-actions">
        <button :disabled="busy || page <= 1" @click="load(box, page - 1)">上一页</button>
        {{ page }} / {{ pages }}
        <button :disabled="busy || page >= pages" @click="load(box, page + 1)">下一页</button>
      </div>
    </template>
  </section>
</template>
