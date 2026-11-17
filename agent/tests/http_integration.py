"""Real Streamable HTTP + Apache writes on disposable persisted data, no production writes."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

name = 'leobbs-http-test-' + uuid.uuid4().hex[:8]
work = Path(tempfile.mkdtemp(prefix=name))
def docker(*args):
    return subprocess.check_output(['docker', *args], stderr=subprocess.PIPE).decode().strip()
def req(origin, token=None):
    headers = {'Authorization': 'Bearer ' + token} if token else {}
    try: response=urlopen(Request(origin+'/api/v1/agent/identity',headers=headers),timeout=10)
    except HTTPError as e: response=e
    with response: return response.status, json.loads(response.read())
try:
    for directory in ['cgi-bin','non-cgi']:
        shutil.copytree(Path('persist')/directory,work/directory)
    root=work/'cgi-bin'
    shutil.rmtree(root/'data/agent',ignore_errors=True)
    settings=root/'data/boardinfo.cgi'
    settings.write_bytes(re.sub(rb"\$imagesurl\s*=\s*['\"][^'\"]*['\"]",b"$imagesurl = '/non-cgi'",settings.read_bytes()))
    with (root/'data/styles.cgi').open('ab') as f: f.write(b'\n$emailfunctions="off"; 1;\n')
    docker('network','create',name)
    docker('run','-d','--name',name,'--network',name,'--network-alias','leobbs','-p','127.0.0.1::80',
        '-e','LEOBBS_MOBILE_PUBLIC_BOARDS=1','-v',str(root)+':/var/www/html/cgi-bin',
        '-v',str(work/'non-cgi')+':/var/www/html/non-cgi','leobbs090206-leobbs')
    origin='http://'+docker('port',name,'80/tcp')
    for _ in range(60):
        try:
            if req(origin)[0]==401: break
        except (URLError,ConnectionError,ValueError): pass
        time.sleep(.5)
    else: raise RuntimeError('Apache not ready')
    docker('run','-d','--name',name+'-mcp','--network',name,'--network-alias','mcp','--read-only',
        '-e','HOST=0.0.0.0','-e','LEOBBS_API_URL=http://leobbs','-e','LEOBBS_PUBLIC_ORIGIN='+origin,
        '--entrypoint','node','leobbs090206-mcp','http-server.js')
    def cli(*args): return json.loads(docker('exec','-u','www-data',name,'python3','/opt/leobbs-agent/token-cli.py',*args))
    issued=cli('issue','--user','leoadmin','--boards','1','--scopes','topics:write,replies:write')
    status, identity=req(origin,issued['token'])
    assert status==200 and identity['boards']==[1] and 'token' not in identity
    tokenfile=work/'token'; tokenfile.write_text(issued['token']); tokenfile.chmod(0o600)
    environment=dict(os.environ, LEOBBS_URL=origin, LEOBBS_TOKEN_FILE=str(tokenfile),LEOBBS_WRITE_TEST='isolated',LEOBBS_MCP_HTTP=origin+'/mcp')
    subprocess.run([os.environ.get('LEOBBS_TEST_NODE','node'),'smoke-writes.js'],cwd='mcp',env=environment,check=True)
    cli('revoke',issued['id'])
    assert req(origin,issued['token'])[0]==401
    # A revoked token is also refused at MCP discovery (not just at the writer).
    try:
        urlopen(Request(origin+'/mcp',data=b'{}',headers={'Authorization':'Bearer '+issued['token'],'Content-Type':'application/json'}))
        raise AssertionError('revoked token accepted')
    except HTTPError as e: assert e.code==401
    print('PASS: HTTP MCP through Apache, persisted-directory deployment, identity/revocation and isolated writes')
finally:
    for container in [name+'-mcp',name]:
        subprocess.run(['docker','rm','-f',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run(['docker','network','rm',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    shutil.rmtree(work)
