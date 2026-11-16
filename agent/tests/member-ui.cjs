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
  const page=await context.newPage(); const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const output=process.env.LEOBBS_SCREENSHOTS || '/tmp/leobbs-agent-screenshots';fs.mkdirSync(output,{recursive:true});
  async function check(label){
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' overflows');
   const missing=await page.locator('.agent-page img').evaluateAll(imgs=>imgs.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
   assert.deepEqual(missing,[],label+' broken icons');
   await page.screenshot({path:output+'/'+label+'.png',fullPage:true});
  }
  await page.goto(origin+'/m/agent');await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor(); await check('mobile-list');
  await page.getByRole('button',{name:'创建授权',exact:true}).click();
  await page.locator('#agent-name').fill('浏览器测试');
  await page.locator('.agent-board-options input').first().check();
  await check('mobile-create');
  await page.setViewportSize({width:320,height:740});await check('mobile-create-320');
  await page.locator('#agent-password').fill('bad');await page.locator('form').getByRole('button',{name:'创建授权',exact:true}).click();
  await page.getByRole('alert').filter({hasText:'账号密码不正确'}).waitFor();
  await page.locator('#agent-password').fill(process.env.LEOBBS_TEST_PASSWORD);await page.locator('form').getByRole('button',{name:'创建授权',exact:true}).click();
  await page.getByRole('heading',{name:'授权创建成功'}).waitFor();
  assert((await page.locator('#agent-secret').inputValue()).startsWith('leo_'));
  // No screenshot of live test secret. Returning to list removes it from the DOM.
  await page.getByRole('button',{name:'已保存，返回列表'}).click();assert.equal(await page.locator('#agent-secret').count(),0);
  await page.getByRole('row').filter({hasText:'浏览器测试'}).getByRole('button',{name:'撤销',exact:true}).click();
  await page.getByRole('dialog').waitFor();await check('mobile-revoke');
  await page.getByRole('button',{name:'确认撤销',exact:true}).click();
  await page.getByRole('row').filter({hasText:'浏览器测试'}).getByText('已撤销',{exact:true}).waitFor();
  await page.setViewportSize({width:1280,height:900});await page.goto(origin+'/cgi-bin/agentpanel.cgi');await page.getByRole('heading',{name:'我的 Agent 授权'}).waitFor();await check('desktop-list');
  await page.getByRole('button',{name:'创建授权',exact:true}).click();await page.getByRole('heading',{name:'创建 Agent 授权'}).waitFor();await check('desktop-create');
  assert.deepEqual(errors,[]);
  await context.clearCookies();await page.reload();await page.getByRole('button',{name:'登录论坛'}).waitFor();
  console.log('PASS: browser mobile 320/390 + desktop, create/password error/one-time secret/revoke/login state, icons and overflow');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
