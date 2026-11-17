"""Scoped Agent credentials and durable write orchestration for the legacy forum.

Only the Perl worker writes forum records. This module never edits post/member data.
"""
import fcntl
import hashlib
import html
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import tempfile
import time
from urllib.parse import urlencode, quote_from_bytes

ROOT = Path('/var/www/html/cgi-bin')
STATE = ROOT / 'data/agent'
WORKER = Path('/opt/leobbs-agent/legacy-worker.pl')

class ApiError(Exception):
    def __init__(self, status, code, message, retry=None):
        super().__init__(message)
        self.status, self.code, self.message, self.retry = status, code, message, retry

    def result(self):
        return {'status': self.status, 'error': {'code': self.code, 'message': self.message, 'retryAfterSeconds': self.retry}}


def atomic_json(path, data):
    """Flush before rename; a request must be durable before invoking the writer."""
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.tmp-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, separators=(',', ':'))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def digest(value):
    return hashlib.sha256(value).hexdigest()


class AgentService:
    def __init__(self, root=ROOT, state=STATE, worker=WORKER, lock_root=Path('/run/leobbs-agent')):
        self.root, self.state, self.worker = Path(root), Path(state), Path(worker)
        self.locks = Path(lock_root)
        for directory in [self.state, self.state / 'tokens', self.state / 'requests', self.locks]:
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)

    def member(self, username):
        if not isinstance(username, str) or not username or re.search(r'[\x00-\x1f/\\.<>"\';%&?=#:|]', username):
            raise ApiError(401, 'INVALID_ACCOUNT', '账号无效')
        try: raw_name = username.encode('gbk')
        except UnicodeError: raise ApiError(401, 'INVALID_ACCOUNT', '账号无效')
        name = raw_name.replace(b' ', b'_').lower()
        # Python's filesystem decoding preserves old GBK filenames with surrogateescape.
        filename = os.fsdecode(name + b'.cgi')
        for directory in sorted(self.root.glob('members*')):
            if not directory.is_dir(): continue
            candidates = [directory / filename] + [sub / filename for sub in directory.iterdir() if sub.is_dir() and sub.name != 'old']
            for path in candidates:
                if not path.is_file(): continue
                fields = path.read_bytes().split(b'\t')
                if len(fields) < 4 or fields[0].replace(b' ', b'_').lower() != name: continue
                if not fields[1] or fields[3] in (b'banned', b'masked'):
                    raise ApiError(403, 'ACCOUNT_DISABLED', '账号已被禁止发言或屏蔽')
                password = fields[1]
                if not password.startswith(b'lEO'):
                    password = b'lEO' + hashlib.md5(password).hexdigest().encode('ascii')
                return {'username': fields[0].decode('gbk'), 'raw_name': fields[0], 'password': password,
                        'fingerprint': digest(password), 'account': digest(name)}
        raise ApiError(401, 'INVALID_ACCOUNT', '账号不存在或已失效')

    def issue(self, username, scopes, boards, lifetime, name=None):
        member = self.member(username)
        if not scopes or not set(scopes) <= {'topics:read', 'topics:write', 'replies:write'}:
            raise ApiError(400, 'INVALID_SCOPE', '权限范围无效')
        if not boards or any(type(board) is not int or board < 1 or board > 9999999999 for board in boards):
            raise ApiError(400, 'INVALID_BOARD', '必须明确指定允许的版块')
        if type(lifetime) is not int or not 60 <= lifetime <= 365 * 86400:
            raise ApiError(400, 'INVALID_EXPIRY', '有效期须为 60 秒至 365 天')
        token = 'leo_' + secrets.token_hex(32)
        token_id = digest(token.encode('ascii'))
        record = {'id': token_id, 'username': member['username'], 'account': member['account'],
                  'fingerprint': member['fingerprint'], 'scopes': sorted(set(scopes)), 'boards': sorted(set(boards)),
                  'name': name, 'lastUsed': None, 'created': int(time.time()), 'expires': int(time.time()) + lifetime, 'revoked': False}
        atomic_json(self.state / 'tokens' / (token_id + '.json'), record)
        self.audit({'event': 'token_issued', 'tokenId': token_id, 'username': member['username']})
        return {**{k: record[k] for k in ['id', 'username', 'scopes', 'boards', 'expires', 'name']}, 'token': token}

    def revoke(self, token_id):
        if not re.fullmatch(r'[0-9a-f]{64}', token_id): raise ApiError(400, 'INVALID_TOKEN_ID', 'Token ID 无效')
        path = self.state / 'tokens' / (token_id + '.json')
        if not path.exists(): raise ApiError(404, 'NOT_FOUND', 'Token 不存在')
        # Revocation and writes use the same account lock: after this returns,
        # no request with this token can begin another legacy write.
        record = json.loads(path.read_text())
        with self.lock(record['account']):
            record = json.loads(path.read_text())
            record['revoked'] = True
            atomic_json(path, record)
            self.audit({'event': 'token_revoked', 'tokenId': token_id})

    def list_tokens(self):
        return [{k: record[k] for k in ['id', 'username', 'scopes', 'boards', 'created', 'expires', 'revoked']}
                for path in sorted((self.state / 'tokens').glob('*.json'))
                for record in [json.loads(path.read_text())]]

    def authenticate(self, token, board, scope):
        if not isinstance(token, str) or not re.fullmatch(r'leo_[0-9a-f]{64}', token):
            raise ApiError(401, 'UNAUTHENTICATED', '需要有效的 Agent Token')
        path = self.state / 'tokens' / (digest(token.encode('ascii')) + '.json')
        if not path.exists(): raise ApiError(401, 'UNAUTHENTICATED', 'Agent Token 无效')
        record = json.loads(path.read_text())
        if record['revoked'] or record['expires'] <= time.time():
            raise ApiError(401, 'UNAUTHENTICATED', 'Agent Token 已过期或撤销')
        member = self.member(record['username'])
        if not secrets.compare_digest(record['fingerprint'], member['fingerprint']):
            raise ApiError(401, 'UNAUTHENTICATED', '账号密码已变更，请重新签发 Token')
        if scope not in record['scopes'] or board not in record['boards']:
            raise ApiError(403, 'FORBIDDEN', 'Agent Token 不允许此操作或版块')
        return {**record, 'member': member}

    def lock(self, account):
        stream = open(self.locks / (account + '.lock'), 'a')
        os.chmod(stream.name, 0o600)
        fcntl.flock(stream, fcntl.LOCK_EX)
        return stream

    def audit(self, event):
        line = json.dumps({'time': int(time.time()), **event}, ensure_ascii=False) + '\n'
        fd = os.open(self.state / 'audit.jsonl', os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try: os.write(fd, line.encode('utf-8'))
        finally: os.close(fd)

    def validate(self, topic, key, payload):
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]{16,128}', key):
            raise ApiError(400, 'INVALID_IDEMPOTENCY_KEY', 'Idempotency-Key 须为 16–128 位字母、数字、下划线或连字符')
        allowed = {'body', 'ubb', 'icon'} | ({'title'} if topic is None else set())
        if not isinstance(payload, dict) or set(payload) - allowed:
            raise ApiError(400, 'INVALID_ARGUMENT', '请求含有不支持的字段')
        required = ['body'] + (['title'] if topic is None else [])
        for field in required:
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > (80 if field == 'title' else 8000):
                raise ApiError(400, 'INVALID_ARGUMENT', '标题须为 1–80 字符，正文须为 1–8000 字符')
            if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', value):
                raise ApiError(400, 'INVALID_ARGUMENT', '内容包含不支持的控制字符')
            try: value.encode('gbk')
            except UnicodeError: raise ApiError(422, 'UNSUPPORTED_ENCODING', '内容含有无法保存为 GBK 的字符（例如部分 Emoji）')
        if 'ubb' in payload and type(payload['ubb']) is not bool:
            raise ApiError(400, 'INVALID_ARGUMENT', 'ubb 必须是布尔值')
        if not isinstance(payload.get('icon', '00'), str) or not re.fullmatch(r'[0-9]{2}', payload.get('icon', '00')):
            raise ApiError(400, 'INVALID_ARGUMENT', 'icon 必须是两位数字')
        return {**payload, 'ubb': payload.get('ubb', True), 'icon': payload.get('icon', '00')}

    def write(self, token, board, topic, key, payload, remote_addr):
        scope = 'topics:write' if topic is None else 'replies:write'
        account = self.authenticate(token, board, scope)
        payload = self.validate(topic, key, payload)
        request_hash = digest(json.dumps([board, topic, payload], sort_keys=True, ensure_ascii=False).encode('utf-8'))
        record_path = self.state / 'requests' / (digest((account['account'] + ':' + key).encode()) + '.json')
        with self.lock(account['account']):
            account = self.authenticate(token, board, scope)
            token_path = self.state / 'tokens' / (account['id'] + '.json')
            token_record = json.loads(token_path.read_text())
            token_record['lastUsed'] = int(time.time())
            atomic_json(token_path, token_record)
            if record_path.exists():
                record = json.loads(record_path.read_text())
                if record['hash'] != request_hash:
                    raise ApiError(409, 'IDEMPOTENCY_CONFLICT', '同一个幂等键不能用于不同请求')
                if record['state'] != 'completed':
                    raise ApiError(409, 'WRITE_OUTCOME_UNKNOWN', '上次写入结果不确定，请先查找帖子或联系管理员，勿更换键自动重发')
                result = record['result']
                if 'data' in result: result['data']['replayed'] = True
                return result
            audit = {'username': account['username'], 'tokenId': account['id'], 'boardId': board, 'topicId': topic, 'operation': scope}
            self.audit({**audit, 'event': 'write_attempt'})
            record = {'hash': request_hash, 'state': 'pending', 'created': int(time.time())}
            atomic_json(record_path, record)
            try:
                result = self.run_legacy(account['member'], board, topic, payload, remote_addr)
                if result.get('status') == 201:
                    data = result['data']
                    if data['boardId'] != board or (topic is not None and data['topicId'] != topic): raise ValueError('unexpected target')
                    if not all(type(data[k]) is int and data[k] > 0 for k in ['boardId', 'topicId', 'floor']): raise ValueError('invalid identifiers')
                    data.update({'url': f"/cgi-bin/topic.cgi?forum={board}&topic={data['topicId']}",
                                 'mobileUrl': f"/m/{board}/{data['topicId']}?page={(data['floor'] - 1) // 20 + 1}", 'replayed': False})
                elif 'error' not in result or result.get('status') not in [403, 404, 422, 429]: raise ValueError('invalid result')
                record.update({'state': 'completed', 'result': result})
                atomic_json(record_path, record)
            except Exception:
                self.audit({**audit, 'event': 'write_unknown'})
                raise ApiError(409, 'WRITE_OUTCOME_UNKNOWN', '写入结果不确定，请先查找帖子或联系管理员，勿自动重发')
            saved = result.get('data', {})
            self.audit({**audit, 'event': 'write_completed', 'status': result['status'],
                        'topicId': saved.get('topicId', topic), 'floor': saved.get('floor')})
            return result

    def run_legacy(self, member, board, topic, payload, remote_addr):
        # The public API and idempotency hash retain the two-digit ID. Only the
        # legacy writer expects a filename, for both topic and reply records.
        fields = {'action': 'addnew' if topic is None else 'addreply', 'forum': str(board),
                  'inpost': payload['body'], 'posticon': payload['icon'] + '.gif', 'uselbcode': 'yes' if payload['ubb'] else 'no',
                  'inshowemoticons': 'yes', 'inwater': 'yes'}
        if topic is None: fields['intopictitle'] = payload['title']
        else: fields['topic'] = str(topic)
        encoded = urlencode({k: v.encode('gbk') for k, v in fields.items()}).encode('ascii')
        env = {'PATH': '/usr/bin:/bin', 'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': 'application/x-www-form-urlencoded',
               'CONTENT_LENGTH': str(len(encoded)), 'SCRIPT_FILENAME': str(self.root / 'post.cgi'), 'SCRIPT_NAME': '/cgi-bin/post.cgi',
               'REMOTE_ADDR': remote_addr, 'SERVER_NAME': 'localhost', 'SERVER_PORT': '80', 'HTTP_HOST': 'localhost',
               'HTTP_COOKIE': 'amembernamecookie=' + quote_from_bytes(member['raw_name']) + '; apasswordcookie=' + quote_from_bytes(member['password'])}
        child = subprocess.run(['/usr/bin/perl', str(self.worker)], input=encoded, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, cwd=self.root, env=env, timeout=30)
        if child.returncode != 0: raise RuntimeError('legacy worker failed')
        result = json.loads(child.stdout)
        if 'legacyError' in result:
            message = html.unescape(re.sub(r'<[^>]*>', '', result['legacyError'])).strip()
            retry = re.search(r'(?:等待|再等|请)\s*(\d+)\s*秒', message)
            status, code = (429, 'RATE_LIMITED') if '灌水' in message or '刷新' in message else (422, 'LEGACY_REJECTED')
            return {'status': status, 'error': {'code': code, 'message': message, 'retryAfterSeconds': int(retry[1]) if retry else None}}
        return result
