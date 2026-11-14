<script setup>
const props = defineProps({
  page: {type: Number, required: true},
  pages: {type: Number, required: true},
  link: {type: Function, required: true},
  label: {type: String, default: '分页'},
})

function jump(event) {
  window.location.assign(props.link(Number(event.target.value)))
}
</script>

<template>
  <nav class="panel page-strip" :aria-label="label">
    <a v-if="page > 1" :href="link(page - 1)" rel="prev">‹ 上一页</a>
    <span v-else class="page-edge">‹ 上一页</span>
    <label class="page-picker">
      <span>第 <b>{{ page }}</b> / {{ pages }} 页 ▾</span>
      <select aria-label="跳到页码" :value="page" @change="jump">
        <option v-if="page > pages" :value="page" disabled>第 {{ page }} 页</option>
        <option v-for="index in pages" :key="index" :value="index">第 {{ index }} 页</option>
      </select>
    </label>
    <a v-if="page < pages" :href="link(page + 1)" rel="next">下一页 ›</a>
    <span v-else class="page-edge">下一页 ›</span>
  </nav>
</template>
