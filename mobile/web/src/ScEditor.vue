<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import 'sceditor/minified/themes/default.min.css'
import contentStyle from 'sceditor/minified/themes/content/default.min.css?url'

const model = defineModel({type: String, required: true})
const props = defineProps({enabled: Boolean})
const field = ref(null)
const error = ref(false)
let instance

onMounted(async () => {
  try {
    await import('sceditor/minified/sceditor.min.js')
    await import('sceditor/minified/formats/bbcode.js')
    if (!field.value) return
    const api = window.sceditor
    api.create(field.value, {
      format: 'bbcode',
      style: contentStyle,
      width: '100%',
      height: 250,
      resizeEnabled: false,
      emoticonsEnabled: false,
      startInSourceMode: false,
      toolbar: 'bold,italic,underline,strike,color|quote,code|link,unlink,image|source',
    })
    instance = api.instance(field.value)
    const sync = () => {
      const value = instance.val()
      if (value !== model.value) model.value = value
    }
    instance.bind('valuechanged', sync)
    instance.getBody().addEventListener("input", sync);
    field.value.parentElement.addEventListener('input', sync)
    if (!props.enabled) instance.sourceMode(true)
  } catch {
    error.value = true
  }
})

watch(model, value => {
  if (instance && instance.val() !== value) instance.val(value)
})

onBeforeUnmount(() => {
  if (instance) model.value = instance.val();
  instance?.destroy()
  instance = undefined
})
</script>

<template>
  <div class="sc-editor">
    <label for="sc-body">正文</label>
    <textarea id="sc-body" ref="field" v-model="model" rows="6" maxlength="8000"></textarea>
    <p v-if="error" role="status">SCEditor 加载失败，可以继续输入 UBB 源码。</p>
  </div>
</template>
