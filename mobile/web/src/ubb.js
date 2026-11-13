import { parse } from '@bbob/parser'
import { h } from 'vue'

const tags = {b: 'strong', i: 'em', u: 'u', s: 's', quote: 'blockquote', code: 'pre'}
const parserOptions = {contextFreeTags: ['code'], enableEscapeTags: false}

function safeUrl(value) {
  if (!/^(https?:\/\/|\/(?![/\\]))/i.test(value)) return
  try {
    const url = new URL(value, window.location.origin)
    if (['http:', 'https:'].includes(url.protocol) && !url.username && !url.password) return url.href
  } catch {
    return undefined
  }
}

function render(node, depth = 0) {
  if (typeof node === 'string') return node
  if (depth >= 32) return ''
  const tag = node.tag.toLowerCase()
  const attr = Object.values(node.attrs || {})[0] || ''
  const content = node.content || []
  const literal = content.map(item => typeof item === 'string' ? item : String(item)).join('')
  if (tag === 'code') return h('pre', [h('code', literal)])
  const children = content.map(item => render(item, depth + 1))
  if (tag === 'url') {
    const href = safeUrl(attr || literal.trim())
    return href ? h('a', {href, rel: 'ugc nofollow noopener', target: '_blank'}, children) : children
  }
  if (tag === 'img') {
    const src = safeUrl(literal.trim())
    return src ? h('img', {src, alt: '帖子图片', loading: 'lazy', referrerpolicy: 'no-referrer'}) : children
  }
  if (tag === 'color' && /^(#[0-9a-f]{3,8}|[a-z]{3,20})$/i.test(attr)) {
    return h('span', {style: {color: attr}}, children)
  }
  if (Object.hasOwn(tags, tag)) return h(tags[tag], children)
  return ['[' + tag + (attr ? '=' + attr : '') + ']', ...children, '[/' + tag + ']']
}

export default {
  props: {body: {type: String, required: true}, enabled: Boolean},
  render() {
    if (!this.enabled) return this.body
    try {
      return parse(this.body, parserOptions).map(node => render(node))
    } catch {
      return this.body
    }
  },
}
