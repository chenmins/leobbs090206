"""Verify built Agent code is readable by Apache but not writable, no forum writes.

Run after building with a 0600 service.py: python3 agent/tests/image_permissions.py IMAGE
"""
import subprocess
import sys
image = sys.argv[1] if len(sys.argv) > 1 else 'leobbs-agent-test:local'
program = '''import os, sys
from pathlib import Path
root = Path('/opt/leobbs-agent')
for path in [root, *root.rglob('*')]:
    assert os.access(path, os.R_OK), f'unreadable code: {path.name}'
    assert not os.access(path, os.W_OK), f'writable code: {path.name}'
    if path.is_dir(): assert os.access(path, os.X_OK)
assert os.access(root / 'write.cgi', os.X_OK)
sys.path.insert(0, str(root))
from service import AgentService
from management import MemberTokens
print('PASS: Apache user imports Agent modules; program permissions readable/not writable')
'''
subprocess.run(['docker','run','--rm','--user','www-data','--entrypoint','python3',image,'-c',program],check=True)
