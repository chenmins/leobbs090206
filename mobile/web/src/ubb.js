// The template renders these tokens as text in fixed HTML elements.
export function ubbTokens(body) {
  const pattern = /\[(b|i|u|quote|code)\]([\s\S]*?)\[\/\1\]/gi
  const tokens = []
  let offset = 0
  for (const match of body.matchAll(pattern)) {
    if (match.index > offset) tokens.push({tag: 'span', text: body.slice(offset, match.index)})
    const tag = match[1].toLowerCase()
    tokens.push({tag: {quote: 'blockquote', code: 'pre'}[tag] || tag, text: match[2]})
    offset = match.index + match[0].length
  }
  if (offset < body.length) tokens.push({tag: 'span', text: body.slice(offset)})
  return tokens
}
