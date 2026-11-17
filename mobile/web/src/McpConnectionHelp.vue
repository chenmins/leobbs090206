<script setup>
import { nextTick, ref } from 'vue'
import { buildMcpConnection } from './mcpConnection.js'
defineProps({ open: Boolean })
const emit = defineEmits(['update:open'])
const copyIcon = '/non-cgi/images/copy.gif'
const connection = buildMcpConnection(window.location.origin)
const copyStatus = ref(''), manualCopy = ref(''), manualField = ref(null)
async function copy(text, label) {
  manualCopy.value = ''; copyStatus.value = ''
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value = `${label}已复制。请替换本地路径占位符。`
  } catch {
    // HTTP LAN sites and denied clipboard permissions still permit manual copy.
    manualCopy.value = text
    copyStatus.value = '浏览器不允许自动复制，已选中下方内容，请长按或按 Ctrl/Cmd+C 复制。'
    await nextTick(); manualField.value?.focus(); manualField.value?.select()
  }
}
</script>

<template>
  <details class="panel agent-help" :open="open" @toggle="emit('update:open', $event.currentTarget.open)">
    <summary class="row">如何接入 MCP</summary>
    <div class="row mcp-help-body">
      <p>当前站点：<strong class="mcp-origin">{{ connection.origin }}</strong></p>
      <p>使用本地 <b>stdio</b>，需要 <b>Node.js 22 或更新版本</b>。先获取<a href="https://github.com/chenmins/leobbs090206" target="_blank" rel="noopener noreferrer">项目代码</a>，在 <code>mcp</code> 目录执行 <code>npm ci</code>，由客户端使用 Node 启动该目录的 <code>server.js</code>。</p>
      <p>不同客户端配置入口可能不同；没有本地 stdio 支持的客户端无法直接套用。下面的绝对路径占位符必须换成你机器上的实际路径。手机可复制说明，交给运行 MCP 的电脑使用。</p>
      <section class="mcp-help-section">
        <h3>先签发自己的 Token</h3>
        <ol><li>点击「创建授权」，选择允许的版块，勾选发布主题和/或回复主题，设置有效期并确认账号密码。</li><li>Token 创建时只显示一次，保存到本地仅本人可读写的文件。macOS/Linux 设置权限 600，Windows 限制文件 ACL。</li><li>把文件的绝对路径填入 <code>LEOBBS_TOKEN_FILE</code>。撤销或到期后重新签发、更新文件，并重启 MCP 进程。</li></ol>
        <p>真实 Token 不要放进接入说明、对话、日志或页面 URL。以下复制内容只有路径占位符，不包含密钥。仅阅读公开帖子时，可省略 <code>LEOBBS_TOKEN_FILE</code>。</p>
      </section>
      <p class="mcp-copy-status" role="status" aria-live="polite">{{ copyStatus }}</p>
      <div v-if="manualCopy" class="mcp-manual"><label for="mcp-manual-copy">手动复制内容</label><textarea id="mcp-manual-copy" ref="manualField" :value="manualCopy" readonly rows="6" spellcheck="false" /></div>
      <section class="mcp-help-section">
        <h3>交给 Codex / AI agent 帮你配置</h3>
        <button type="button" @click="copy(connection.instructions, '接入说明')"><img :src="copyIcon" alt="">复制接入说明</button>
        <details class="mcp-snippet"><summary>查看接入说明</summary><pre data-testid="mcp-instructions">{{ connection.instructions }}</pre></details>
      </section>
      <section class="mcp-help-section">
        <h3>通用 MCP 客户端 JSON</h3>
        <button type="button" @click="copy(connection.json, 'JSON 配置')"><img :src="copyIcon" alt="">复制 JSON 配置</button>
        <pre data-testid="mcp-json">{{ connection.json }}</pre>
      </section>
      <section class="mcp-help-section">
        <h3>Codex TOML 配置</h3>
        <p>填写到 <code>~/.codex/config.toml</code> 或相应项目配置。字段见 <a href="https://developers.openai.com/codex/mcp/" target="_blank" rel="noopener noreferrer">Codex 官方 MCP 文档</a>。</p>
        <button type="button" @click="copy(connection.toml, 'TOML 配置')"><img :src="copyIcon" alt="">复制 TOML 配置</button>
        <details class="mcp-snippet"><summary>查看 TOML 配置</summary><pre data-testid="mcp-toml">{{ connection.toml }}</pre></details>
      </section>
      <section class="mcp-help-section">
        <h3>连接后可以这样对 AI 说</h3>
        <p>先只读检查连接。发帖和回复会实际写入论坛；请将示例中的版块、标题和正文替换为你确认的内容。</p>
        <div v-for="example in connection.examples" :key="example.title" class="mcp-example">
          <h4>{{ example.title }}</h4><p>{{ example.text }}</p>
          <button type="button" @click="copy(example.text, example.title)">复制「{{ example.title }}」</button>
        </div>
        <p>遇到限流按 <code>retryAfterSeconds</code> 等待。明确拒绝的 429 请求可能已有幂等记录，等待后经确认再以新键提交；若写入结果不明，先用 <code>search_topics</code> / <code>list_topics</code> / <code>get_topic</code> 核查，勿换键重复发布。</p>
      </section>
    </div>
  </details>
</template>

<style>
.mcp-help-body{overflow-wrap:anywhere}.mcp-help-body h3{font-size:16px;margin:0 0 10px;color:#102c8c}.mcp-help-body h4{font-size:14px;margin:0 0 7px}.mcp-help-body code{font-size:13px}.mcp-help-body ol{margin:8px 0;padding-left:22px}.mcp-help-body li{margin:7px 0}.mcp-help-section{border-top:1px solid #b8cae8;margin-top:16px;padding-top:14px}.mcp-snippet{margin-top:10px}.mcp-snippet summary{padding:6px 0}.mcp-example{background:#f1f5fc;border:1px solid #cbd9ef;padding:10px;margin:10px 0}.mcp-copy-status:not(:empty){padding:10px;background:#f3faf3;border:1px solid #9fb99e;color:#245b29}.mcp-manual textarea{display:block;width:100%;font:13px monospace;resize:vertical;margin-top:6px}.mcp-origin{word-break:break-all}
</style>
