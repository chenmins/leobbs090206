#!/usr/bin/python3
import json
import os
import re
import sys
from service import AgentService, ApiError


def main():
    if os.environ.get('REQUEST_METHOD') != 'POST':
        raise ApiError(405, 'METHOD_NOT_ALLOWED', '仅支持 POST')
    route = re.fullmatch(r'/api/v1/boards/([1-9][0-9]{0,9})/topics(?:/([1-9][0-9]{0,9})/replies)?', os.environ.get('REQUEST_URI', '').split('?')[0])
    if not route: raise ApiError(404, 'NOT_FOUND', '接口不存在')
    if os.environ.get('CONTENT_TYPE', '').split(';')[0].lower() != 'application/json':
        raise ApiError(415, 'UNSUPPORTED_MEDIA_TYPE', '请使用 application/json 和 UTF-8')
    length = os.environ.get('CONTENT_LENGTH', '')
    if not length.isdigit(): raise ApiError(411, 'LENGTH_REQUIRED', '缺少 Content-Length')
    if int(length) > 65536: raise ApiError(413, 'PAYLOAD_TOO_LARGE', '请求不得超过 64 KiB')
    raw = sys.stdin.buffer.read(int(length))
    if len(raw) != int(length): raise ApiError(400, 'INVALID_JSON', '请求不完整')
    try:
        def unique(pairs):
            value = {}
            for k, v in pairs:
                if k in value: raise ValueError('duplicate field')
                value[k] = v
            return value
        body = json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, RecursionError):
        raise ApiError(400, 'INVALID_JSON', '请求必须是有效的 UTF-8 JSON，且不能有重复字段')
    auth = os.environ.get('HTTP_AUTHORIZATION', '')
    token = auth[7:] if auth.startswith('Bearer ') else ''
    return AgentService().write(token, int(route[1]), int(route[2]) if route[2] else None,
                                os.environ.get('HTTP_IDEMPOTENCY_KEY', ''), body, os.environ.get('REMOTE_ADDR', '127.0.0.1'))

try:
    result = main()
except ApiError as error:
    result = error.result()
except Exception:
    # Never expose account records, cookies, tokens, paths or tracebacks in HTTP.
    result = ApiError(500, 'INTERNAL_ERROR', '写接口暂不可用，请稍后检查原请求结果').result()
status = result['status']
print(f'Status: {status}')
print('Content-Type: application/json; charset=utf-8')
print('Cache-Control: no-store')
print('X-Content-Type-Options: nosniff')
if status == 405: print('Allow: POST')
if status == 401: print('WWW-Authenticate: Bearer')
retry = result.get('error', {}).get('retryAfterSeconds')
if retry is not None: print(f'Retry-After: {int(retry)}')
print()
print(json.dumps(result.get('data') or {'error': result['error']}, ensure_ascii=False))
