(function () {
  if (!/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) return;

  const params = new URLSearchParams(location.search);
  const file = location.pathname.split('/').pop();
  const topic = /^topic-(\d+)-(\d+)-/.exec(file);
  const board = /^forums-(\d+)-/.exec(file);
  const boardId = topic?.[1] || board?.[1] || params.get('forum');
  const topicId = topic?.[2] || params.get('topic');
  let destination = '/m/';

  if (topic || board || file === 'forums.cgi' || file === 'topic.cgi') {
    if (!/^[1-9]\d*$/.test(boardId || '')) return;
    destination += boardId;
    if (topic || file === 'topic.cgi') {
      if (!/^[1-9]\d*$/.test(topicId || '')) return;
      destination += '/' + topicId;
    }
  } else if (!/^leobbs\.(cgi|htm)$/.test(file)) {
    return;
  }

  const key = 'leobbs-classic-until';
  try {
    if (Number(localStorage.getItem(key)) > Date.now()) return;
  } catch {}

  const viewport = document.createElement('meta');
  viewport.name = 'viewport';
  viewport.content = 'width=device-width, initial-scale=1';
  const previous = document.querySelector('meta[name="viewport"]');
  if (previous) previous.replaceWith(viewport);
  else document.head.append(viewport);

  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:grid;place-items:center;padding:16px;background:#12274399;box-sizing:border-box';
  const card = document.createElement('section');
  card.setAttribute('role', 'dialog');
  card.setAttribute('aria-modal', 'true');
  card.setAttribute('aria-label', '\u5207\u6362\u5230\u624b\u673a\u7248');
  card.style.cssText = 'width:min(100%,360px);box-sizing:border-box;border:1px solid #5279b3;background:#f4f8ff;color:#17395f;font:16px/1.5 sans-serif';
  const heading = document.createElement('div');
  heading.textContent = 'LeoBBS \u00b7 \u624b\u673a\u7248';
  heading.style.cssText = 'padding:10px 16px;background:linear-gradient(#5686c8,#315c99);color:white;font-weight:bold';
  const content = document.createElement('div');
  content.style.cssText = 'display:grid;gap:10px;padding:16px';
  const description = document.createElement('div');
  description.textContent = '\u4f7f\u7528\u624b\u673a\u7248\u9605\u8bfb\u5f53\u524d\u9875\u9762';
  const link = document.createElement('a');
  link.href = destination;
  link.textContent = '\u5207\u6362\u5230\u624b\u673a\u7248';
  link.style.cssText = 'display:block;padding:12px;text-align:center;background:#285b9f;color:white;font:bold 16px sans-serif;text-decoration:none';
  const dismiss = document.createElement('button');
  dismiss.type = 'button';
  dismiss.textContent = '\u7ee7\u7eed\u4f7f\u7528\u7ecf\u5178\u7248';
  dismiss.style.cssText = 'padding:12px;border:1px solid #5279b3;background:white;color:#17395f;font:16px sans-serif';
  const rootOverflow = document.documentElement.style.overflow;
  document.documentElement.style.overflow = 'hidden';
  const overflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  dismiss.onclick = function () {
    try { localStorage.setItem(key, String(Date.now() + 24 * 60 * 60 * 1000)); } catch {}
    if (previous) viewport.replaceWith(previous);
    else viewport.remove();
    document.body.style.overflow = overflow;
    document.documentElement.style.overflow = rootOverflow;
    overlay.remove();
  };
  overlay.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') dismiss.click();
    if (event.key === 'Tab') {
      event.preventDefault();
      (document.activeElement === link ? dismiss : link).focus();
    }
  });
  content.append(description, link, dismiss);
  card.append(heading, content);
  overlay.append(card);
  document.body.append(overlay);
  link.focus({preventScroll: true});
})();
