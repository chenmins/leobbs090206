// Read-only news-page regression. Photo responses/DOM fixtures never write posts.
const {chromium}=require(process.env.LEOBBS_PLAYWRIGHT || '/tmp/leobbs-mcp-tools/node_modules/playwright-core');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.LEOBBS_BROWSER || '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1100,height:850}});
  const origin=process.env.LEOBBS_URL || 'http://127.0.0.1:8080';
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',route=>new URL(route.request().url()).origin===origin ? route.continue() : route.abort());
  await page.goto(origin+'/cgi-bin/view.cgi?forum=1&topic='+(process.env.LEOBBS_TEST_TOPIC || '36'), {waitUntil:'domcontentloaded'});
  assert.equal(await page.evaluate(()=>typeof loadThreadFollow),'function','news page script must parse');
  assert.ok(!(await page.locator('body').innerText()).includes('targetTd.innerHTML'));
  assert.deepEqual(errors,[]);
  const code=page.locator('code').filter({hasText:'<p>'}).first();
  assert.equal(await code.innerText(),'<p>[br][/br]');
  const outside=await page.evaluate(()=>{const body=document.body.cloneNode(true);body.querySelectorAll('code').forEach(e=>e.remove());return body.textContent});
  assert.ok(!outside.includes('<p>第一段'));
  assert.ok(!outside.includes('[/br]同段换行'));
  if(process.env.LEOBBS_SCREENSHOT) await page.screenshot({path:process.env.LEOBBS_SCREENSHOT,fullPage:true});
  let mode='ok',requests=0;
  await page.route('**/getphotoinfo.cgi?**',route=>{
   requests++;
   const body=mode==='empty' ? Buffer.from('<html><body>  </body></html>') : Buffer.concat([Buffer.from('<html><body><div>'),Buffer.from('cdbcc6ac cfeacfb8 d0c5cfa2'.replaceAll(' ',''),'hex'),Buffer.from('</div><script>window.newsInjected=true;</script></body></html>')]);
   return route.fulfill({status:mode==='error'?503:200,contentType:'text/html; charset=gb2312',body});
  });
  await page.evaluate(()=>{
   const fixture=document.createElement('div');fixture.innerHTML='<img id="followImgtest" loaded="no"><div id="followtest" style="display:none"><div id="followTdtest"></div></div>';document.body.append(fixture);
  });
  const toggle=()=>page.evaluate(()=>loadThreadFollow(1,36,'test','jpg','fixture.jpg'));
  await toggle();await page.waitForFunction(()=>document.getElementById('followImgtest').getAttribute('loaded')==='yes');
  assert.equal(await page.locator('#followTdtest').innerText(),'图片详细信息');
  assert.equal(await page.locator('#followTdtest script').count(),0);
  assert.equal(await page.evaluate(()=>window.newsInjected),undefined);
  await toggle();assert.equal(await page.locator('#followtest').evaluate(e=>e.style.display),'none');
  await toggle();assert.equal(requests,1,'cached details must not fetch again');
  for(mode of ['empty','error']) {
   await toggle();await page.locator('#followImgtest').evaluate(e=>e.setAttribute('loaded','no'));await toggle();
   await page.waitForFunction(text=>document.getElementById('followTdtest').textContent.includes(text),mode==='empty'?'没有读取到':'读取失败');
  }
  assert.equal(await page.locator('#followImgtest').getAttribute('loaded'),'no');
  assert.deepEqual(errors,[]);
  console.log('PASS: news script syntax, no leaked JS, GBK photo details, script removal, expand/collapse/cache, empty/error states');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
