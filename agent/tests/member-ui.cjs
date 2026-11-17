// Run only through management_integration.py against its disposable data copy.
const {chromium}=require(process.env.LEOBBS_PLAYWRIGHT || '/tmp/leobbs-browser-tools/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.LEOBBS_BROWSER || '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',headless:true});
 try {
  const origin=process.env.LEOBBS_TEST_ORIGIN;
  const context=await browser.newContext({viewport:{width:390,height:844}});
  await context.addCookies(['amembernamecookie','apasswordcookie'].map((name,i)=>({name,value:i?process.env.LEOBBS_TEST_HASH:'cccc',domain:new URL(origin).hostname,path:'/cgi-bin'})));
  await context.grantPermissions(['clipboard-read','clipboard-write'], {origin});
  const page=await context.newPage(); const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const output=process.env.LEOBBS_SCREENSHOTS || '/tmp/leobbs-agent-screenshots';fs.mkdirSync(output,{recursive:true});
  async function check(label){
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' overflows');
   const missing=await page.locator('.agent-page img').evaluateAll(imgs=>imgs.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
   assert.deepEqual(missing,[],label+' broken icons');
   await page.screenshot({path:output+'/'+label+'.png',fullPage:true});
  }
  await page.goto(origin+'/m/agent');await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor(); await check('mobile-list');
  async function checkHelp(siteOrigin, saveConfig=false) {
   await page.getByRole('button',{name:'MCP 接入说明',exact:true}).click();
   const help=page.locator('.agent-help');
   await help.getByRole('button',{name:'复制 JSON 配置',exact:true}).click();
   const copied=await page.evaluate(()=>navigator.clipboard.readText());
   const config=JSON.parse(copied);
   assert.equal(config.mcpServers.leobbs.env.LEOBBS_URL,siteOrigin);
   assert.equal(config.mcpServers.leobbs.command,'node');
   assert.ok(!copied.includes('leo_'));
   assert.equal(copied,await help.locator('[data-testid="mcp-json"]').textContent());
   if(saveConfig && process.env.LEOBBS_COPIED_CONFIG) fs.writeFileSync(process.env.LEOBBS_COPIED_CONFIG,copied);
   for(const [button, testId] of [['复制接入说明','mcp-instructions'],['复制 TOML 配置','mcp-toml']]) {
    await help.getByRole('button',{name:button,exact:true}).click();
    const text=await page.evaluate(()=>navigator.clipboard.readText());
    assert.equal(text,await help.locator('[data-testid="'+testId+'"]').textContent());
    assert.ok(text.includes(siteOrigin));assert.ok(!text.includes('leo_'));
   }
   for(const button of await help.locator('.mcp-example button').all()) {
    await button.click();assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).length>40);
   }
   await check(siteOrigin===origin?'connection-help-local':'connection-help-'+new URL(siteOrigin).hostname);
   await page.getByRole('button',{name:'MCP 接入说明',exact:true}).click();
  }
  await checkHelp(origin,true);
  await page.getByRole('button',{name:'创建授权',exact:true}).click();
  await page.locator('#agent-name').fill('浏览器测试');
  await page.locator('.agent-board-options input').first().check();
  await check('mobile-create');
  await page.setViewportSize({width:320,height:740});await check('mobile-create-320');
  await page.locator('#agent-password').fill('bad');await page.locator('form').getByRole('button',{name:'创建授权',exact:true}).click();
  await page.getByRole('alert').filter({hasText:'账号密码不正确'}).waitFor();
  await page.locator('#agent-password').fill(process.env.LEOBBS_TEST_PASSWORD);await page.locator('form').getByRole('button',{name:'创建授权',exact:true}).click();
  await page.getByRole('heading',{name:'授权创建成功'}).waitFor();
  const testSecret=await page.locator('#agent-secret').inputValue();
  assert(testSecret.startsWith('leo_'));
  assert.ok(!(await page.locator('.agent-help').textContent()).includes(testSecret));
  // No screenshot of live test secret. Returning to list removes it from the DOM.
  await page.getByRole('button',{name:'已保存，返回列表'}).click();assert.equal(await page.locator('#agent-secret').count(),0);
  await page.getByRole('row').filter({hasText:'浏览器测试'}).getByRole('button',{name:'撤销',exact:true}).click();
  await page.getByRole('dialog').waitFor();await check('mobile-revoke');
  await page.getByRole('button',{name:'确认撤销',exact:true}).click();
  await page.getByRole('row').filter({hasText:'浏览器测试'}).getByText('已撤销',{exact:true}).waitFor();
  await page.setViewportSize({width:1280,height:900});await page.goto(origin+'/cgi-bin/agentpanel.cgi');await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor();await check('desktop-list');
  await page.getByRole('button',{name:'创建授权',exact:true}).click();await page.getByRole('heading',{name:'创建 Agent 授权'}).waitFor();await check('desktop-create');
  // Browsers receive the real built app via intercepted aliases. No request is
  // sent to either external host; all traffic is fulfilled by the isolated forum.
  for(const alias of ['https://leobbs.org','https://forum.example.net']) {
   await context.grantPermissions(['clipboard-read','clipboard-write'],{origin:alias});
   await context.addCookies(['amembernamecookie','apasswordcookie'].map((name,i)=>({name,value:i?process.env.LEOBBS_TEST_HASH:'cccc',domain:new URL(alias).hostname,path:'/cgi-bin'})));
   await context.route(alias+'/**',async route=>{
    const url=new URL(route.request().url());
    const response=await route.fetch({url:origin+url.pathname+url.search});
    await route.fulfill({response});
   });
   await page.goto(alias+'/m/agent?help=1#connection');
   await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor();
   await checkHelp(alias);
  }
  await page.goto(origin+'/cgi-bin/agentpanel.cgi');await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor();
  await checkHelp(origin);
  await page.getByRole('button',{name:'MCP 接入说明',exact:true}).click();
  await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw new Error('clipboard denied')}});
  await page.getByRole('button',{name:'复制 JSON 配置',exact:true}).click();
  assert.equal(JSON.parse(await page.locator('#mcp-manual-copy').inputValue()).mcpServers.leobbs.env.LEOBBS_URL,origin);
  assert.ok(await page.locator('#mcp-manual-copy').evaluate(e=>e.selectionEnd===e.value.length));
  await page.route('**/cgi-bin/agenttokens.cgi', route=>route.fulfill({status:500,contentType:'text/html',body:'<!DOCTYPE html><html><body>private server diagnostic</body></html>'}), {times:1});
  await page.reload();
  await page.getByRole('alert').filter({hasText:'HTTP 500'}).waitFor();
  const alert=await page.getByRole('alert').innerText();
  assert.ok(!alert.includes('Unexpected token') && !alert.includes('private server diagnostic'));
  assert.deepEqual(errors,[]);
  await context.clearCookies();await page.reload();await page.getByRole('button',{name:'登录论坛'}).waitFor();
  console.log('PASS: browser mobile 320/390 + desktop, create/password error/one-time secret/revoke/login state, icons and overflow');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
