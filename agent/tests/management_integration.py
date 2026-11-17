"""Member UI/API integration against a disposable copy, never the running forum."""
import hashlib, json, os, re, shutil, subprocess, tempfile, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
work = Path(tempfile.mkdtemp(prefix='leobbs-member-test-'))
name = 'leobbs-member-test-' + uuid.uuid4().hex[:8]
def docker(*args): return subprocess.check_output(['docker', *args], stderr=subprocess.PIPE).decode().strip()
def req(payload=None, user='cccc', csrf=None, path='/cgi-bin/agenttokens.cgi', origin_header=None):
    headers={'Content-Type':'application/json'}
    if user: headers['Cookie']='amembernamecookie='+user+'; apasswordcookie='+hashed
    if csrf: headers['X-CSRF-Token']=csrf
    if origin_header: headers['Origin']=origin_header
    request=Request(origin+path, data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
    try: response=urlopen(request,timeout=30)
    except HTTPError as e: response=e
    raw=response.read()
    return response.status, json.loads(raw) if 'application/json' in response.headers.get('Content-Type','') else raw
try:
    for part in ['cgi-bin','non-cgi']: shutil.copytree(Path('persist')/part,work/part)
    root=work/'cgi-bin'; shutil.rmtree(root/'data/agent',ignore_errors=True)
    # Keep classic rendered images on the disposable origin, not the source site.
    settings=root/'data/boardinfo.cgi'
    settings.write_bytes(re.sub(rb"\$imagesurl\s*=\s*['\"][^'\"]*['\"]", b"$imagesurl = '/non-cgi'", settings.read_bytes()))
    password='isolated-password-123'; hashed='lEO'+hashlib.md5(password.encode()).hexdigest()
    for user in ['cccc','leoadmin']:
        member=next(p for p in root.glob('members*/*/'+user+'.cgi') if p.parent.name!='old')
        fields=member.read_bytes().split(b'\t'); fields[1]=hashed.encode(); member.write_bytes(b'\t'.join(fields))
    styles=root/'data/styles.cgi'; styles.write_bytes(styles.read_bytes()+b'\n$emailfunctions="off"; 1;\n')
    docker('run','-d','--name',name,'-p','127.0.0.1::80','-e','LEOBBS_MOBILE_PUBLIC_BOARDS=1','-v',str(root)+':/var/www/html/cgi-bin','-v',str(work/'non-cgi')+':/var/www/html/non-cgi','leobbs-agent-test:local')
    origin='http://'+docker('port',name,'80/tcp')
    for _ in range(40):
        try:
            status,data=req(user=None)
            if status==401: break
        except (URLError,ConnectionError): pass
        time.sleep(.2)
    assert status==401,(status,data)
    assert req(path='/api/v1/boards/1/topics', user=None)[0]==405  # imports must work before method rejection
    status,data=req(); assert status==200,(status,data)
    assert any(b['id']==1 for b in data['boards']),data
    csrf=data['csrf']; payload=dict(action='create',name='我的 AI 助手',scopes=['topics:write','replies:write'],boards=[1],days=30,password=password)
    assert req(payload,csrf='0'*64)[0]==403
    assert req(payload,csrf=csrf,origin_header='https://evil.example')[0]==403
    assert req({**payload,'password':'wrong'},csrf=csrf)[0]==403
    assert req({**payload,'username':'leoadmin'},csrf=csrf)[0]==400
    status,issued=req(payload,csrf=csrf); assert status==201,(status,issued)
    assert req(payload,csrf=csrf)[0]==403
    status,listed=req(); assert status==200 and len(listed['items'])==1
    assert issued['token'] not in json.dumps(listed)
    other=req(user='leoadmin')[1]; assert not other['items']
    assert req(dict(action='revoke',id=issued['id']),user='leoadmin',csrf=other['csrf'])[0]==404
    board=root/'forum1/foruminfo.cgi'; original=board.read_bytes(); f=original.split(b'\t'); f[8]=b'yes'; board.write_bytes(b'\t'.join(f))
    allforums=root/'data/allforums.cgi'; alloriginal=allforums.read_bytes()
    allforums.write_bytes(b'\n'.join(b'\t'.join(f).rstrip(b'\n') if line.startswith(b'1\t') else line for line in alloriginal.split(b'\n')))
    (root/'cache/forums1.pl').unlink(missing_ok=True)
    status,private=req(); assert status==200 and not any(b['id']==1 for b in private['boards']),(status,private)
    assert req(payload,csrf=private['csrf'])[0]==403
    board.write_bytes(original); allforums.write_bytes(alloriginal); (root/'cache/forums1.pl').unlink(missing_ok=True)
    # Child forums are postable; onlysub containers are a separate legacy flag.
    f=original.split(b'\t'); f[1]=b'childforum-999'
    board.write_bytes(b'\t'.join(f))
    allforums.write_bytes(b'\n'.join(b'\t'.join(f).rstrip(b'\n') if line.startswith(b'1\t') else line for line in alloriginal.split(b'\n')))
    (root/'cache/forums1.pl').unlink(missing_ok=True)
    status,child=req(); assert status==200 and any(b['id']==1 for b in child['boards'])
    board.write_bytes(original); allforums.write_bytes(alloriginal); (root/'cache/forums1.pl').unlink(missing_ok=True)
    for path in ['/m/agent','/cgi-bin/agentpanel.cgi']:
        status,raw=req(path=path); assert status==200 and b'/m/assets/' in raw,(path,status,raw[:100])
    # Exercise real rendered UI using only the disposable account.
    environment=dict(os.environ,LEOBBS_TEST_ORIGIN=origin,LEOBBS_TEST_HASH=hashed,LEOBBS_TEST_PASSWORD=password, LEOBBS_COPIED_CONFIG=str(work/'copied-mcp.json'))
    subprocess.run([os.environ.get('LEOBBS_TEST_NODE','node'),'agent/tests/member-ui.cjs'],env=environment,check=True)
    token_file=work/'clipboard-token'; token_file.write_text(issued['token']); token_file.chmod(0o600)
    environment['LEOBBS_TEST_TOKEN_FILE']=str(token_file)
    subprocess.run([os.environ.get('LEOBBS_TEST_NODE','node'),'smoke-config.js'],cwd='mcp',env=environment,check=True)
    token_file.unlink()
    csrf=req()[1]['csrf']; assert req(dict(action='revoke',id=issued['id']),csrf=csrf)[0]==200
    assert req()[1]['items'][0]['status']=='revoked'
    for p in (root/'data/agent').rglob('*'):
        if p.is_file(): assert issued['token'].encode() not in p.read_bytes()
    docker('restart',name); origin='http://'+docker('port',name,'80/tcp')
    for _ in range(40):
        try:
            status, result=req()
            if status==200: break
        except (URLError,ConnectionError): pass
        time.sleep(.2)
    assert status==200,(status,result)
    assert (root/'bbs.lib.pl').read_bytes().count(b'href=agentpanel.cgi')==1
    print('PASS: member ownership, cookies, CSRF/replay, password, permission changes, one-time secret, revoke, persistent deployment and browser flows')
finally:
    subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    shutil.rmtree(work,ignore_errors=True)
