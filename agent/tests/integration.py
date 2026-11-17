"""Exercise real Apache + legacy writes in disposable copies of initialized data.

Run from repository root: python3 agent/tests/integration.py --image leobbs-agent-test:local
No requests are sent to the existing forum container. Tokens are never printed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('--image', default='leobbs-agent-test:local')
parser.add_argument('--source', default='persist')
parser.add_argument('--keep-on-failure', action='store_true')
args = parser.parse_args()
work = Path(tempfile.mkdtemp(prefix='leobbs-agent-integration-'))
name = 'leobbs-agent-test-' + uuid.uuid4().hex[:8]
passed = False

def docker(*args):
    return subprocess.check_output(['docker', *args], stderr=subprocess.PIPE).decode()

def cli(*args):
    return json.loads(docker('exec', '-u', 'www-data', name, 'python3', '/opt/leobbs-agent/token-cli.py', *args))

def request(path, payload=None, token=None, key=None, method=None):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = 'Bearer ' + token
    if key: headers['Idempotency-Key'] = key
    req = Request(origin + path, data=data, headers=headers, method=method)
    try: response = urlopen(req, timeout=45)
    except HTTPError as error: response = error
    with response:
        raw = response.read()
        return response.status, json.loads(raw) if 'application/json' in response.headers.get('Content-Type', '') else raw

def fresh_key(): return uuid.uuid4().hex

def clear_limits(member):
    f = member.read_bytes().split(b'\t')
    f[14] = b'0'
    member.write_bytes(b'\t'.join(f))
    (root / 'data/onlinedata.cgi').write_bytes(b'')

def check(status, expected, data):
    assert status == expected, (status, data)

try:
    shutil.copytree(Path(args.source) / 'cgi-bin', work / 'cgi-bin')
    shutil.copytree(Path(args.source) / 'non-cgi', work / 'non-cgi')
    root = work / 'cgi-bin'
    # Keep classic rendered images on the disposable origin, not the source site.
    settings=root/'data/boardinfo.cgi'
    settings.write_bytes(re.sub(rb"\$imagesurl\s*=\s*['\"][^'\"]*['\"]", b"$imagesurl = '/non-cgi'", settings.read_bytes()))
    # Ensure no inherited Agent credentials are copied into the test deployment.
    shutil.rmtree(root / 'data/agent', ignore_errors=True)
    styles = root / 'data/styles.cgi'
    raw = styles.read_bytes()
    # Disable outbound email only in this isolated test copy.
    raw = re.sub(rb'\$emailfunctions\s*=\s*[\'\"][^\'\"]*[\'\"]', b'$emailfunctions = "off"', raw)
    raw += b'\n$emailfunctions="off"; $floodcontrol="on"; $floodcontrollimit=30; 1;\n'
    styles.write_bytes(raw)
    member = next(p for p in root.glob('members*/*/cccc.cgi') if p.parent.name != 'old')
    clear_limits(member)
    docker('run', '-d', '--name', name, '-p', '127.0.0.1::80', '-e', 'LEOBBS_MOBILE_PUBLIC_BOARDS=1',
           '-v', str(root) + ':/var/www/html/cgi-bin', '-v', str(work / 'non-cgi') + ':/var/www/html/non-cgi', args.image)
    origin = 'http://' + docker('port', name, '80/tcp').strip()
    for attempt in range(30):
        try:
            status, data = request('/api/v1/home')
            if status == 200: break
        except (URLError, ConnectionError): pass
        time.sleep(0.2)
    else: raise AssertionError('Apache did not become ready')
    assert (root / 'post.cgi').read_bytes().count(b'# LEOBBS_AGENT_WRITE_LOCK') == 1
    assert (root / 'bbs.lib.pl').read_bytes().count(b'&leobbs_agent_error($banfreshtime)') == 1
    issued = cli('issue', '--user', 'cccc', '--boards', '1', '--scopes', 'topics:write,replies:write')
    token = issued['token']
    url = '/api/v1/boards/1/topics'
    payload = {'title': 'Agent 接口中文测试 ' + fresh_key()[:6], 'body': '[b]中文正文[/b]\n[quote]UBB 引用[/quote]', 'ubb': True}
    key = fresh_key()
    check(*[request(url, payload, key=key)[0], 401, 'missing auth'])
    status, data = request(url, {'title': '字符', 'body': '😀'}, token, fresh_key())
    check(status, 422, data)
    status, data = request(url, payload, token, 'bad')
    check(status, 400, data)
    status, data = request('/api/v1/boards/2/topics', payload, token, fresh_key())
    check(status, 403, data)
    # Parallel same-key writes must produce exactly one new topic.
    before = set((root / 'forum1').glob('*.thd.cgi'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: request(url, payload, token, key), range(4)))
    for status, data in results: check(status, 201, data)
    ids = {data['topicId'] for _, data in results}
    assert len(ids) == 1, results
    assert sum(not data['replayed'] for _, data in results) == 1
    assert len(set((root / 'forum1').glob('*.thd.cgi')) - before) == 1
    topic = ids.pop()
    status, detail = request(f'/api/v1/boards/1/topics/{topic}')
    check(status, 200, detail)
    assert '中文正文' in detail['items'][0]['body'] and '[b]' in detail['items'][0]['body']
    status, data = request(url, {**payload, 'body': 'changed'}, token, key)
    check(status, 409, data)
    assert data['error']['code'] == 'IDEMPOTENCY_CONFLICT'
    # Flood control is executed by the actual legacy writer, for a non-admin.
    reply_url = f'/api/v1/boards/1/topics/{topic}/replies'
    status, data = request(reply_url, {'body': '过快回复'}, token, fresh_key())
    check(status, 429, data)
    assert '灌水' in data['error']['message'] and data['error']['retryAfterSeconds'] > 0
    clear_limits(member)
    reply_key = fresh_key()
    status, data = request(reply_url, {'body': '[i]中文回复[/i]'}, token, reply_key)
    check(status, 201, data)
    assert data['floor'] == 2
    status, data = request(reply_url, {'body': '[i]中文回复[/i]'}, token, reply_key)
    assert status == 201 and data['replayed']
    assert len((root / f'forum1/{topic}.thd.cgi').read_bytes().splitlines()) == 2
    # Locked topic, private board, posting prohibition and banned account remain enforced.
    clear_limits(member)
    metadata = root / f'forum1/{topic}.pl'
    original = metadata.read_bytes()
    fields = original.split(b'\t'); fields[3] = b'closed'; metadata.write_bytes(b'\t'.join(fields))
    status, data = request(reply_url, {'body': 'locked test'}, token, fresh_key())
    check(status, 422, data)
    assert '锁定' in data['error']['message']
    metadata.write_bytes(original)
    board = root / 'forum1/foruminfo.cgi'; original = board.read_bytes()
    for index, value in [(8, b'yes'), (9, b'no')]:
        clear_limits(member)
        fields = original.split(b'\t'); fields[index] = value; board.write_bytes(b'\t'.join(fields))
        status, data = request(url, {**payload, 'title': '权限测试 ' + fresh_key()[:6]}, token, fresh_key())
        check(status, 422, data)
        board.write_bytes(original)
    fields = member.read_bytes().split(b'\t'); fields[3] = b'banned'; member.write_bytes(b'\t'.join(fields))
    status, data = request(url, payload, token, fresh_key()); check(status, 403, data)
    fields[3] = b'me'; member.write_bytes(b'\t'.join(fields))
    # No credentials or journals can be downloaded via the public CGI tree.
    for path in ['tokens/' + issued['id'] + '.json', 'audit.jsonl']:
        status, _ = request('/cgi-bin/data/agent/' + path); assert status == 403
    for path in (root / 'data/agent').rglob('*'):
        if path.is_file(): assert token.encode() not in path.read_bytes()
    # Recreate Apache process: persisted result survives; hooks remain single copies.
    docker('restart', name)
    origin = 'http://' + docker('port', name, '80/tcp').strip()
    for attempt in range(30):
        try:
            status, data = request(url, payload, token, key)
            if status == 201: break
        except (URLError, ConnectionError): pass
        time.sleep(0.2)
    check(status, 201, data); assert data['replayed'] and data['topicId'] == topic
    assert (root / 'post.cgi').read_bytes().count(b'# LEOBBS_AGENT_WRITE_LOCK') == 1
    # End-to-end MCP client -> stdio server -> Apache -> legacy post writer.
    admin = cli('issue', '--user', 'leoadmin', '--boards', '1', '--scopes', 'topics:write,replies:write')
    token_file = work / 'mcp-token'
    token_file.write_text(admin['token'])
    token_file.chmod(0o600)
    environment = dict(os.environ, LEOBBS_URL=origin, LEOBBS_TOKEN_FILE=str(token_file), LEOBBS_WRITE_TEST='isolated', LEOBBS_ICON_REPORT=str(work / 'icons.json'))
    subprocess.run([os.environ.get('LEOBBS_TEST_NODE', 'node'), 'smoke-writes.js'], cwd='mcp', env=environment, check=True)
    for row in json.loads((work / 'icons.json').read_text()):
        metadata = (root / f"forum1/{row['topicId']}.pl").read_bytes().split(b'\t')
        posts = (root / f"forum1/{row['topicId']}.thd.cgi").read_bytes().splitlines()
        assert metadata[10] == (row['icon'] + '.gif').encode()
        assert len(posts) == 2
        assert posts[0].split(b'\t')[7] == (row['icon'] + '.gif').encode()
        assert posts[1].split(b'\t')[7] == (row['replyIcon'] + '.gif').encode()
    token_file.unlink()
    cli('revoke', admin['id'])
    cli('revoke', issued['id'])
    status, data = request(url, payload, token, key); check(status, 401, data)
    print('PASS: isolated Apache writes, Chinese/UBB, concurrent idempotency, reply replay, flood control, locked/private/restricted/banned permissions, secret storage, persisted restart, revocation')
    passed = True
finally:
    if not passed and args.keep_on_failure:
        print('Debug container:', name, 'data:', work)
    else:
        subprocess.run(['docker', 'rm', '-f', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(work, ignore_errors=True)
