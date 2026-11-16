import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1]))
from service import ApiError
from management import MemberTokens

class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.password = 'test-only-password'
        self.hashed = 'lEO' + hashlib.md5(self.password.encode()).hexdigest()
        for name in ['alice', 'bob']:
            path = self.root / ('members/12/' + name + '.cgi'); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('\t'.join([name, self.hashed, '', 'me'] + [''] * 45))
        self.api = MemberTokens(self.root, self.root / 'state', lock_root=self.root / 'locks')
        self.member = self.api.browser_member('amembernamecookie=alice; apasswordcookie=' + self.hashed)
        self.bob = self.api.browser_member('amembernamecookie=bob; apasswordcookie=' + self.hashed)
        self.mock = patch.object(self.api, 'allowed_boards', return_value=[{'id': 1, 'name': '公开区', 'scopes': ['topics:write', 'replies:write']}])
        self.mock.start(); self.addCleanup(self.mock.stop)

    def payload(self):
        return {'action': 'create', 'name': '我的 Codex', 'scopes': ['topics:write'], 'boards': [1], 'days': 30, 'password': self.password}

    def test_cookie_required_and_invalid_cookie_denied(self):
        for cookie in ['', 'amembernamecookie=alice', 'amembernamecookie=alice; apasswordcookie=bad']:
            with self.assertRaises(ApiError): self.api.browser_member(cookie)

    def test_owner_scope_and_only_once_secret(self):
        csrf = self.api.overview(self.member)['csrf']
        result = self.api.mutate(self.member, csrf, self.payload())
        self.assertTrue(result['token'].startswith('leo_'))
        self.assertEqual(self.api.overview(self.bob)['items'], [])
        listed = self.api.overview(self.member)
        self.assertEqual(listed['items'][0]['name'], '我的 Codex')
        self.assertNotIn(result['token'], json.dumps(listed))
        with self.assertRaises(ApiError): self.api.mutate(self.member, csrf, self.payload())
        with self.assertRaises(ApiError) as denied:
            self.api.mutate(self.bob, self.api.overview(self.bob)['csrf'], {'action':'revoke', 'id':result['id']})
        self.assertEqual(denied.exception.status, 404)
        self.api.mutate(self.member, listed['csrf'], {'action':'revoke', 'id':result['id']})
        self.assertEqual(self.api.overview(self.member)['items'][0]['status'], 'revoked')

    def test_csrf_password_and_privilege_rechecked(self):
        for mutate in [lambda p: p.update(password='bad'), lambda p:p.update(boards=[2]), lambda p:p.update(username='bob')]:
            payload = self.payload(); mutate(payload)
            with self.assertRaises(ApiError): self.api.mutate(self.member, self.api.overview(self.member)['csrf'], payload)
        with self.assertRaises(ApiError): self.api.mutate(self.member, '', self.payload())
        csrf = self.api.overview(self.member)['csrf']
        with self.assertRaises(ApiError): self.api.mutate(self.bob, csrf, self.payload())
        with patch('management.time.time', return_value=10**12):
            with self.assertRaises(ApiError): self.api.mutate(self.member, csrf, self.payload())
        self.assertEqual(self.api.list_tokens(), [])

    def test_old_cli_token_compatibility_and_last_use(self):
        token = self.api.issue('alice', ['topics:write'], [1], 3600)
        row = self.api.overview(self.member)['items'][0]
        self.assertEqual(row['name'], '命令行授权')
        with patch.object(self.api, 'run_legacy', return_value={'status':201,'data':{'boardId':1,'topicId':1,'floor':1}}):
            self.api.write(token['token'], 1, None, 'management-test-123', {'title':'测试', 'body':'正文'}, '127.0.0.1')
        self.assertIsNotNone(self.api.overview(self.member)['items'][0]['lastUsed'])

    def test_password_attempt_limit_and_password_change_invalidation(self):
        payload = self.payload(); payload['password'] = 'wrong'
        for _ in range(5):
            with self.assertRaises(ApiError) as denied:
                self.api.mutate(self.member, self.api.overview(self.member)['csrf'], payload)
            self.assertEqual(denied.exception.status, 403)
        with self.assertRaises(ApiError) as denied:
            self.api.mutate(self.member, self.api.overview(self.member)['csrf'], self.payload())
        self.assertEqual(denied.exception.status, 429)
        issued = self.api.issue('alice', ['topics:write'], [1], 3600)
        path = self.root / 'members/12/alice.cgi'
        path.write_text(path.read_text().replace(self.hashed, 'lEO' + hashlib.md5(b'new-password').hexdigest()))
        changed = self.api.member('alice')
        self.assertEqual(self.api.overview(changed)['items'][0]['status'], 'invalid')
        with self.assertRaises(ApiError): self.api.authenticate(issued['token'], 1, 'topics:write')
