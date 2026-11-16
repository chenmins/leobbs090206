import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('service', Path(__file__).parents[1] / 'service.py')
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        member = self.root / 'members/12/alice.cgi'
        member.parent.mkdir(parents=True)
        self.fields = ['alice', 'lEO' + 'a' * 32, '', 'me'] + [''] * 45
        member.write_bytes('\t'.join(self.fields).encode('gbk'))
        self.member = member
        self.api = service.AgentService(self.root, self.root / 'state', lock_root=self.root / 'locks')
        self.issued = self.api.issue('alice', ['topics:write', 'replies:write'], [1], 3600)
        self.token = self.issued['token']
        self.request = {'title': '中文主题', 'body': '[b]正文[/b]', 'ubb': True}

    def submit(self, key='request-12345678', payload=None, board=1):
        return self.api.write(self.token, board, None, key, self.request if payload is None else payload, '127.0.0.1')

    def test_token_stores_digest_and_revokes(self):
        for file in (self.root / 'state').rglob('*.json'):
            self.assertNotIn(self.token, file.read_text())
        self.assertEqual(self.api.authenticate(self.token, 1, 'topics:write')['username'], 'alice')
        self.api.revoke(self.issued['id'])
        with self.assertRaises(service.ApiError) as raised:
            self.submit()
        self.assertEqual(raised.exception.status, 401)

    def test_scopes_boards_expiration_and_password_change(self):
        with self.assertRaises(service.ApiError) as raised:
            self.api.authenticate(self.token, 2, 'topics:write')
        self.assertEqual(raised.exception.status, 403)
        with self.assertRaises(service.ApiError):
            self.api.authenticate(self.token, 1, 'admin')
        with patch.object(service.time, 'time', return_value=10**12):
            with self.assertRaises(service.ApiError): self.api.authenticate(self.token, 1, 'topics:write')
        self.fields[1] = 'lEO' + 'b' * 32
        self.member.write_bytes('\t'.join(self.fields).encode('gbk'))
        with self.assertRaises(service.ApiError): self.api.authenticate(self.token, 1, 'topics:write')

    def test_validation_and_gbk_before_writer(self):
        for body in [{}, {'title': 'x', 'body': '😀'}, {'title': 'x', 'body': 'ok', 'membername': 'admin'}, {'title': 'x', 'body': 'ok', 'ubb': 'yes'}]:
            with self.assertRaises(service.ApiError): self.submit(payload=body)
        with self.assertRaises(service.ApiError): self.submit(key='')

    def test_success_replays_without_second_write_and_conflict(self):
        result = {'status': 201, 'data': {'boardId': 1, 'topicId': 2, 'floor': 1}}
        with patch.object(self.api, 'run_legacy', return_value=result) as writer:
            first = self.submit()
            second = self.submit()
            self.assertEqual(first['data']['topicId'], 2)
            self.assertTrue(second['data']['replayed'])
            self.assertEqual(writer.call_count, 1)
            events = [json.loads(line) for line in (self.root / 'state/audit.jsonl').read_text().splitlines()]
            completed = next(event for event in events if event['event'] == 'write_completed')
            self.assertEqual(completed['topicId'], 2)
            self.assertEqual(completed['floor'], 1)
            with self.assertRaises(service.ApiError) as raised:
                self.submit(payload={**self.request, 'body': 'different'})
            self.assertEqual(raised.exception.code, 'IDEMPOTENCY_CONFLICT')

    def test_uncertain_result_blocks_retry(self):
        with patch.object(self.api, 'run_legacy', side_effect=RuntimeError('worker lost')) as writer:
            with self.assertRaises(service.ApiError) as raised: self.submit()
            self.assertEqual(raised.exception.code, 'WRITE_OUTCOME_UNKNOWN')
            with self.assertRaises(service.ApiError): self.submit()
            self.assertEqual(writer.call_count, 1)

    def test_classic_error_remains_json_and_retryable(self):
        result = {'status': 429, 'error': {'code': 'RATE_LIMITED', 'message': '灌水预防机制', 'retryAfterSeconds': 2}}
        with patch.object(self.api, 'run_legacy', return_value=result) as writer:
            self.assertEqual(self.submit()['status'], 429)
            self.assertEqual(self.submit()['error']['message'], '灌水预防机制')
            self.assertEqual(writer.call_count, 1)

if __name__ == '__main__': unittest.main()
