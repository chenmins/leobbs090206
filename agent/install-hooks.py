#!/usr/bin/python3
"""Idempotent small hooks for persisted classic source; preserve GBK bytes."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
post = root / 'post.cgi'
raw = post.read_bytes()
marker = b'# LEOBBS_AGENT_WRITE_LOCK'
if marker not in raw:
    anchor = b'use LBCGI;'
    if raw.count(anchor) != 1: raise SystemExit('post.cgi hook anchor not found; refusing unsafe upgrade')
    lock = b'''# LEOBBS_AGENT_WRITE_LOCK: serialize legacy and Agent posting across all boards.
open(my $leobbs_write_lock, '>>', '/run/leobbs-agent/post-write.lock') or die "post lock";
flock($leobbs_write_lock, 2) or die "post lock acquisition";

'''
    post.write_bytes(raw.replace(anchor, lock + anchor, 1))
# Upgrade the previous bind-mount lock location as well.
raw = post.read_bytes()
post.write_bytes(raw.replace(b"'/var/www/html/cgi-bin/lock/post-write.lock'", b"'/run/leobbs-agent/post-write.lock'"))
lib = root / 'bbs.lib.pl'
raw = lib.read_bytes()
marker = b'&leobbs_agent_error($banfreshtime)'
if marker not in raw:
    lines = raw.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if b'if (($thisprog eq "post.cgi")' in line and b'$banfreshtime' in line]
    if len(matches) != 1: raise SystemExit('refresh guard hook anchor not found; refusing unsafe upgrade')
    lines.insert(matches[0] + 1, b'                             &leobbs_agent_error($banfreshtime) if defined &leobbs_agent_error;\n')
    lib.write_bytes(b''.join(lines))

# These tiny deployment-owned entrypoints are safe to refresh in existing mounts.
import shutil
seed = Path('/opt/leobbs-seed/cgi-bin')
if seed.exists():
    for name in ['agenttokens.cgi', 'agentpanel.cgi']:
        shutil.copyfile(seed / name, root / name)
        (root / name).chmod(0o755)
# Add the member menu entry without transcoding the surrounding GBK source.
raw = lib.read_bytes()
if b'href=agentpanel.cgi' not in raw:
    anchor = b"linkset[1]='"
    if raw.count(anchor) != 1: raise SystemExit('control-panel menu anchor missing')
    link = '<div class=menuitems>&nbsp;<a href=agentpanel.cgi><font color=$menufontcolor>Agent 授权</font></a>&nbsp;</div>'.encode('gbk')
    lib.write_bytes(raw.replace(anchor, anchor + link, 1))
