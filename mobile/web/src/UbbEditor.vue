<script setup>
import { nextTick, ref } from 'vue'
import UbbBody from './ubb.js'
import ScEditor from './ScEditor.vue'

const enabled = defineModel('enabled', {type: Boolean})
const body = defineModel({type: String, required: true})
const editor = ref(null)
const useScEditor = ref(enabled.value)

function switchEditor() {
  useScEditor.value = !useScEditor.value
  if (useScEditor.value) enabled.value = true
}
const tools = [
  ['粗体', 'b', '', 'bold'], ['斜体', 'i', '', 'italic'], ['下划线', 'u', '', 'underline'], ['删除线', 's'],
  ['颜色', 'color', '#990000', 'fgcolor'], ['引用', 'quote'], ['代码', 'code'],
  ['链接', 'url', '', 'wlink'], ['带文字的链接', 'url', 'https://'], ['图片', 'img', '', 'img'],
]

async function insert(tag, attribute) {
  const field = editor.value
  const {selectionStart: start, selectionEnd: end} = field
  const opening = '[' + tag + (attribute ? '=' + attribute : '') + ']'
  const closing = '[/' + tag + ']'
  if (body.value.length + opening.length + closing.length > field.maxLength) {
    field.focus()
    return
  }
  body.value = body.value.slice(0, start) + opening + body.value.slice(start, end) + closing + body.value.slice(end)
  await nextTick()
  field.focus()
  field.setSelectionRange(start + opening.length, end + opening.length)
}
</script>

<template>
  <button class="editor-switch" type="button" :aria-pressed="useScEditor"
    @click="switchEditor">{{ useScEditor ? '切回经典工具栏' : '切换到富文本' }}</button>
  <ScEditor v-if="enabled && useScEditor" v-model="body" :enabled="enabled" />
  <template v-else>
  <div class="ubb-tools" role="group" aria-label="UBB 格式">
    <button v-for="[label, tag, attribute, icon] in tools" :key="label" type="button"
      :aria-label="label" :title="label" :disabled="!enabled" @click="insert(tag, attribute)">
      <img v-if="icon" :src="'/non-cgi/editor/images/' + icon + '.gif'" alt="">
      <s v-else-if="tag === 's'">S</s>
      <span v-else aria-hidden="true">{{ {quote: '❝', code: '</>', url: '↗+'}[tag] }}</span>
    </button>
  </div>
  <label>正文<textarea ref="editor" v-model="body" rows="6" maxlength="8000" required></textarea></label>
    <label><input v-model="enabled" type="checkbox">启用 UBB</label>
    <section class="panel" aria-label="正文预览">
      <h3 class="bar">实时预览</h3>
      <div v-if="body" class="body"><UbbBody :body="body" :enabled="enabled" /></div>
      <p v-else class="row">输入正文后即可预览。</p>
    </section>
  </template>
</template>
