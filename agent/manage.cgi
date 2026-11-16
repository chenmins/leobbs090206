#!/usr/bin/python3
"""Same-origin browser management; deliberately under /cgi-bin for legacy cookies."""
import json
import os
import sys
from urllib.parse import urlsplit
from management import MemberTokens
from service import ApiError

try:
    method = os.environ.get('REQUEST_METHOD', '')
    # Drain bounded POST bodies before auth rejection so Apache CGI can finish
    # the response instead of closing its input pipe with unread request bytes.
    raw = b''
    if method == 'POST':
        length = os.environ.get('CONTENT_LENGTH', '')
        if not length.isdigit() or len(length) > 5 or int(length) > 16384:
            raise ApiError(413, 'PAYLOAD_TOO_LARGE', '请求过大或不完整')
        raw = sys.stdin.buffer.read(int(length))
        if len(raw) != int(length): raise ApiError(400, 'INVALID_JSON', '请求不完整')
    service = MemberTokens()
    member = service.browser_member(os.environ.get('HTTP_COOKIE', ''))
    if method == 'GET':
        result, status = service.overview(member), 200
    elif method == 'POST':
        origin = os.environ.get('HTTP_ORIGIN')
        if os.environ.get('HTTP_SEC_FETCH_SITE') == 'cross-site' or (origin and urlsplit(origin).netloc != os.environ.get('HTTP_HOST')):
            raise ApiError(403, 'CSRF_INVALID', '不允许跨站提交授权操作')
        if os.environ.get('CONTENT_TYPE', '').split(';')[0].lower() != 'application/json':
            raise ApiError(415, 'INVALID_CONTENT_TYPE', '请使用 JSON 提交')
        try:
            def unique(pairs):
                data = {}
                for k, v in pairs:
                    if k in data: raise ValueError()
                    data[k] = v
                return data
            payload = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
        except (ValueError, UnicodeError, RecursionError): raise ApiError(400, 'INVALID_JSON', '请求格式无效')
        result = service.mutate(member, os.environ.get('HTTP_X_CSRF_TOKEN', ''), payload)
        status = 201 if payload.get('action') == 'create' else 200
    else: raise ApiError(405, 'METHOD_NOT_ALLOWED', '仅支持 GET 和 POST')
except ApiError as error:
    status, result = error.status, {'error': error.result()['error']}
except Exception:
    status, result = 500, {'error': {'code':'INTERNAL_ERROR', 'message':'授权管理暂不可用，请刷新列表确认操作结果'}}
print('Status: ' + str(status))
print('Content-Type: application/json; charset=utf-8')
print('Cache-Control: no-store, private')
print('X-Content-Type-Options: nosniff')
print('Cross-Origin-Resource-Policy: same-origin')
print('X-Frame-Options: DENY')
print()
print(json.dumps(result, ensure_ascii=False))
