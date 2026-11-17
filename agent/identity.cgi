#!/usr/bin/python3
"""Validate the forum's own Agent credential; never return secrets or account records."""
import json
import os
from service import AgentService, ApiError

try:
    if os.environ.get('REQUEST_METHOD') != 'GET':
        raise ApiError(405, 'METHOD_NOT_ALLOWED', '仅支持 GET')
    auth = os.environ.get('HTTP_AUTHORIZATION', '')
    record = AgentService().identity(auth[7:] if auth.startswith('Bearer ') else '')
    status, data = 200, {key: record[key] for key in ('scopes', 'boards', 'expires')}
except ApiError as error:
    status, data = error.status, {'error': error.result()['error']}
except Exception:
    status, data = 503, {'error': {'code': 'UNAVAILABLE', 'message': '授权服务暂不可用'}}
print(f'Status: {status}')
print('Content-Type: application/json; charset=utf-8')
print('Cache-Control: no-store')
if status == 401: print('WWW-Authenticate: Bearer')
if status == 405: print('Allow: GET')
print()
print(json.dumps(data, ensure_ascii=False))
