import test from 'node:test'
import assert from 'node:assert/strict'
import { readAgentResponse } from '../src/agentResponse.js'

test('HTML errors describe status without displaying the server response', async () => {
  for (const status of [200,404,500,502]) {
    const response=new Response('<!DOCTYPE html><body>private diagnostic</body>',{status,headers:{'Content-Type':'text/html'}})
    await assert.rejects(readAgentResponse(response),error=>error.message.includes(`HTTP ${status}`) && !error.message.includes('private diagnostic') && !error.message.includes('Unexpected token'))
  }
})
test('JSON errors retain the original forum error and valid data is unchanged', async () => {
  const body={error:{message:'请先登录论坛'}}
  assert.deepEqual(await readAgentResponse(new Response(JSON.stringify(body),{status:401,headers:{'Content-Type':'application/json; charset=utf-8'}})),body)
  assert.deepEqual(await readAgentResponse(new Response('{"items":[]}',{headers:{'Content-Type':'application/json'}})),{items:[]})
})
test('malformed JSON gives a bounded diagnostic', async () => {
  for (const raw of ['{"broken":', 'null', '[]']) {
    await assert.rejects(readAgentResponse(new Response(raw,{headers:{'Content-Type':'application/json'}})),/响应格式错误.*HTTP 200/)
  }
})
