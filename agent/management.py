"""Browser-owned Agent credentials. Never accepts a caller-supplied account."""
import hashlib
from http.cookies import SimpleCookie, CookieError
import json
import os
import re
import secrets
import subprocess
import time
from urllib.parse import unquote_to_bytes, quote_from_bytes
from service import AgentService, ApiError, atomic_json, digest

class MemberTokens(AgentService):
    def browser_member(self, header):
        try:
            cookies = SimpleCookie(); cookies.load(header)
            raw_name = unquote_to_bytes(cookies['amembernamecookie'].value.replace('+', ' '))
            supplied = unquote_to_bytes(cookies['apasswordcookie'].value.replace('+', ' '))
            member = self.member(raw_name.decode('gbk'))
            if not secrets.compare_digest(supplied, member['password']): raise ValueError()
            return member
        except (CookieError, KeyError, UnicodeError, ValueError):
            raise ApiError(401, 'LOGIN_REQUIRED', '请先登录论坛，再管理 Agent 授权')

    def web_state(self, member):
        directory = self.state / 'web'
        directory.mkdir(mode=0o700, exist_ok=True)
        path = directory / (member['account'] + '.json')
        state = json.loads(path.read_text()) if path.exists() else {}
        if state.get('fingerprint') != member['fingerprint']:
            state = {'fingerprint': member['fingerprint'], 'challenges': [], 'failures': []}
        state['challenges'] = [c for c in state['challenges'] if c['expires'] > time.time()]
        state['failures'] = [t for t in state['failures'] if t > time.time() - 600]
        return path, state

    def overview(self, member):
        with self.lock(member['account']):
            path, state = self.web_state(member)
            csrf = secrets.token_hex(32)
            state['challenges'] = state['challenges'][-9:] + [{'hash': digest(csrf.encode()), 'expires': int(time.time()) + 1800}]
            atomic_json(path, state)
            items = []
            for path in (self.state / 'tokens').glob('*.json'):
                record = json.loads(path.read_text())
                if record['account'] != member['account']: continue
                status = 'revoked' if record['revoked'] else 'expired' if record['expires'] <= time.time() else 'invalid' if record['fingerprint'] != member['fingerprint'] else 'active'
                items.append({**{k: record[k] for k in ['id', 'scopes', 'boards', 'created', 'expires']},
                              'name': record.get('name') or '命令行授权', 'lastUsed': record.get('lastUsed'), 'status': status})
        return {'username': member['username'], 'csrf': csrf, 'items': sorted(items, key=lambda x: -x['created']), 'boards': self.allowed_boards(member)}

    def allowed_boards(self, member):
        result = []
        for directory in sorted(self.root.glob('forum*')):
            match = re.fullmatch(r'forum([1-9][0-9]{0,9})', directory.name)
            if not match or not (directory / 'foruminfo.cgi').is_file(): continue
            env = {'PATH': '/usr/bin:/bin', 'AGENT_BOARD_ID': match[1],
                   'HTTP_COOKIE': 'amembernamecookie=' + quote_from_bytes(member['raw_name']) + '; apasswordcookie=' + quote_from_bytes(member['password'])}
            child = subprocess.run(['/usr/bin/perl', '/opt/leobbs-agent/board-permissions.pl'], env=env, cwd=self.root,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
            if child.returncode != 0: raise ApiError(503, 'PERMISSIONS_UNAVAILABLE', '暂时无法校验版块权限，请稍后重试')
            board = json.loads(child.stdout)
            if board and board.get('scopes'): result.append(board)
        return result

    def mutate(self, member, csrf, payload):
        if not isinstance(payload, dict): raise ApiError(400, 'INVALID_ARGUMENT', '请求格式无效')
        if not isinstance(csrf, str) or not re.fullmatch(r'[0-9a-f]{64}', csrf):
            raise ApiError(403, 'CSRF_INVALID', '页面已失效，请刷新后重试')
        with self.lock(member['account']):
            path, state = self.web_state(member)
            challenge = next((c for c in state['challenges'] if secrets.compare_digest(c['hash'], digest(csrf.encode()))), None)
            if not challenge: raise ApiError(403, 'CSRF_INVALID', '页面已失效或操作已提交，请刷新列表确认结果')
            action = payload.get('action')
            if action == 'revoke':
                if set(payload) != {'action', 'id'} or not isinstance(payload.get('id'), str) or not re.fullmatch(r'[0-9a-f]{64}', payload['id']):
                    raise ApiError(400, 'INVALID_ARGUMENT', '授权 ID 无效')
                target = self.state / 'tokens' / (payload['id'] + '.json')
                record = json.loads(target.read_text()) if target.exists() else {}
                if record.get('account') != member['account']: raise ApiError(404, 'NOT_FOUND', '授权不存在')
                state['challenges'].remove(challenge); atomic_json(path, state)
            elif action == 'create':
                if set(payload) != {'action', 'name', 'scopes', 'boards', 'days', 'password'}:
                    raise ApiError(400, 'INVALID_ARGUMENT', '创建参数无效')
                name = payload.get('name')
                if not isinstance(name, str) or not name.strip() or len(name) > 40 or re.search(r'[\x00-\x1f\x7f]', name):
                    raise ApiError(400, 'INVALID_ARGUMENT', '授权名称须为 1–40 字符')
                if type(payload['days']) is not int or payload['days'] not in [7, 30, 90, 365]:
                    raise ApiError(400, 'INVALID_ARGUMENT', '有效期请选择 7、30、90 或 365 天')
                scopes, boards = payload['scopes'], payload['boards']
                if not isinstance(scopes, list) or not scopes or any(s not in ['topics:write', 'replies:write'] for s in scopes):
                    raise ApiError(400, 'INVALID_SCOPE', '请选择发帖或回复权限')
                if not isinstance(boards, list) or not boards or len(boards) > 100 or any(type(b) is not int for b in boards):
                    raise ApiError(400, 'INVALID_BOARD', '请选择允许的版块')
                if len(state['failures']) >= 5: raise ApiError(429, 'PASSWORD_RATE_LIMITED', '密码确认失败过多，请 10 分钟后重试', 600)
                supplied = payload.get('password')
                try:
                    check = b'lEO' + hashlib.md5(supplied.encode('gbk')).hexdigest().encode('ascii') if isinstance(supplied, str) and 0 < len(supplied) <= 128 else b''
                except UnicodeError: check = b''
                if not secrets.compare_digest(check, member['password']):
                    state['failures'].append(int(time.time())); atomic_json(path, state)
                    raise ApiError(403, 'PASSWORD_INCORRECT', '账号密码不正确，请重新输入')
                allowed = {b['id']: b['scopes'] for b in self.allowed_boards(member)}
                if any(b not in allowed or not set(scopes) <= set(allowed[b]) for b in boards):
                    raise ApiError(403, 'FORBIDDEN', '所选版块不允许这些操作，请刷新后重新选择')
                # Consume before issuing: a lost response must never mint another secret on retry.
                state['challenges'].remove(challenge); state['failures'] = []; atomic_json(path, state)
                return self.issue(member['username'], scopes, boards, payload['days'] * 86400, name=name.strip())
            else: raise ApiError(400, 'INVALID_ACTION', '不支持此操作')
        self.revoke(payload['id'])
        return {'revoked': payload['id']}
