<script setup>
defineProps({stats: {type: Object, required: true}})
const skin = '/non-cgi/images/leobbs/'
const onlineLegend = [
  ['ad', '论坛坛主'], ['smo', '论坛总版主'], ['cmo', '分类区版主'], ['mo', '论坛版主'],
  ['amo', '论坛副版主'], ['rz', '认证会员'], ['user', '普通会员'], ['guest', '客人或隐身会员'],
]
const peakTime = new Intl.DateTimeFormat('zh-CN', {
  dateStyle: 'short', timeStyle: 'short', timeZone: 'Asia/Shanghai',
})
const legend = [
  ['foldernew', '正规论坛有新帖'], ['folder', '正规论坛无新帖'],
  ['folderallnew', '开放论坛有新帖'], ['folderall', '开放论坛无新帖'],
  ['follownew', '评论论坛有新帖'], ['follow', '评论论坛无新帖'],
  ['rzfoldernew', '认证论坛有新帖'], ['rzfolder', '认证论坛无新帖'],
]
</script>

<template>
  <section class="panel">
    <h2 class="bar">论坛统计</h2>
    <ul class="row forum-stats">
      <li>最后注册会员 <b>{{ stats.lastMember || '—' }}</b></li>
      <li>注册会员总数 <a href="/cgi-bin/memberlist.cgi?a=5"><b>{{ stats.members }}</b></a> 人</li>
      <li>论坛主题总数 <b>{{ stats.topics }}</b> 篇</li>
      <li>论坛回复总数 <b>{{ stats.replies }}</b> 篇</li>
      <li>当前在线总数 <a href="/cgi-bin/whosonline.cgi"><b>{{ stats.online }}</b></a> 人</li>
      <li>昨 / 今日新帖 <b>{{ stats.yesterday }} / {{ stats.today }}</b> 篇</li>
      <li>历史最高一天发帖量 <b>{{ stats.peak }}</b> 篇</li>
    </ul>
  </section>
  <details class="panel" open>
    <summary class="bar">论坛在线统计（峰值 {{ stats.onlinePeak }} 人）</summary>
    <div class="row">
      <p v-if="stats.onlinePeakAt">峰值发生时间 {{ peakTime.format(stats.onlinePeakAt * 1000) }}</p>
      <p class="legend-item">
        <img :src="skin + 'online.gif'" alt="">
        <span>目前有 <a href="/cgi-bin/whosonline.cgi"><b>{{ stats.online }}</b></a> 人在线，其中注册会员 {{ stats.membersOnline }} 人，访客 {{ stats.guestsOnline }} 人。</span>
      </p>
      <p>论坛累计访问 {{ stats.visits }} 次，点击 {{ stats.clicks }} 次。</p>
      <p>在线图例</p>
      <div class="forum-legend">
        <span v-for="[icon, label] in onlineLegend" :key="icon" class="legend-item">
          <img :src="'/non-cgi/images/online' + icon + '.gif'" alt="">{{ label }}
        </span>
      </div>
    </div>
  </details>
  <section v-if="stats.birthdays" class="panel">
    <h2 class="bar">今日生日</h2>
    <p class="row legend-item"><img :src="skin + 'born.gif'" alt="">今天有 {{ stats.birthdays }} 位会员过生日</p>
  </section>
  <details class="panel">
    <summary class="bar">LeoBBS 论坛图例</summary>
    <div class="row forum-legend">
      <span v-for="[icon, label] in legend" :key="icon" class="legend-item">
        <img :src="skin + icon + '.gif'" alt="">{{ label }}
      </span>
    </div>
  </details>
</template>
