#!/bin/sh
set -eu

seed_tree_if_missing() {
  src="$1"
  dst="$2"
  marker="$3"

  mkdir -p "$dst"
  if [ ! -e "$dst/$marker" ]; then
    cp -a "$src/." "$dst/"
  fi
}

seed_tree_if_missing /opt/leobbs-seed/cgi-bin /var/www/html/cgi-bin install.cgi
seed_tree_if_missing /opt/leobbs-seed/non-cgi /var/www/html/non-cgi index.html

# Upgrade the known news-mode inline-script bug in existing bind mounts.
# Copy only the response-parsing block, preserving other local CGI changes/GBK.
python3 - /var/www/html/cgi-bin/view.cgi /opt/leobbs-seed/cgi-bin/view.cgi <<'NEWS_VIEW_PATCH'
from pathlib import Path
import sys
view, seed = map(Path, sys.argv[1:])
if view.exists():
    raw = view.read_bytes()
    broken = br'html = html.replace(/<script[\s\S]*?<\/script>/ig, "");'
    if broken in raw:
        start = raw.index(b'return resp.text();')
        end = raw.index(b'targetTd.innerHTML = html;', start)
        source = seed.read_bytes().replace(b'\r\n', b'\n')
        first = source.index(b'return resp.arrayBuffer();')
        last = source.index(b'targetTd.innerHTML = html;', first)
        replacement = source[first:last]
        if b'\r\n' in raw: replacement = replacement.replace(b'\n', b'\r\n')
        view.write_bytes(raw[:start] + replacement + raw[end:])
    raw = view.read_bytes()
    marker = b'# LEOBBS_NEWS_UBB_COMPAT:'
    if marker not in raw:
        source = seed.read_bytes().replace(b'\r\n', b'\n')
        first = source.index(marker)
        last = source.index(b'# END_LEOBBS_NEWS_UBB_COMPAT', first) + len(b'# END_LEOBBS_NEWS_UBB_COMPAT')
        helper = source[first:last] + b'\n'
        if raw.count(br'&lbcode(\$post);') != 2:
            raise SystemExit('news UBB call anchors changed; refusing partial upgrade')
        if b'\r\n' in raw: helper = helper.replace(b'\n', b'\r\n')
        view.write_bytes(raw.replace(br'&lbcode(\$post);', br'&news_lbcode(\$post);') + (b'\r\n' if b'\r\n' in raw else b'\n') + helper)
NEWS_VIEW_PATCH

# Upgrade the refresh guard in existing installations while preserving local CGI edits.
perl -pi -e 'if (/if \(\(\(\$currenttime - \$savedtime\)/ && /\$thisprog eq "whosonline\.cgi"/) {
    s/if \(\(\(\$currenttime/if ((\$thisprog eq "post.cgi") \&\& ((\$currenttime/;
    s/\&\&\(\(\$thisprog eq "post\.cgi"\).*?\)\) \{/){/;
}' /var/www/html/cgi-bin/bbs.lib.pl

find /var/www/html/cgi-bin -type f -name "*.cgi" -exec chmod 755 {} \; || true
find /var/www/html/cgi-bin -type f -name "*.pl" -exec chmod 755 {} \; || true
find /var/www/html/cgi-bin -type f -name "*.pm" -exec chmod 644 {} \; || true

mkdir -p /var/www/html/cgi-bin/data
mkdir -p /var/www/html/cgi-bin/members/old
mkdir -p /var/www/html/cgi-bin/messages/in
mkdir -p /var/www/html/cgi-bin/messages/out
mkdir -p /var/www/html/cgi-bin/messages/main
mkdir -p /var/www/html/cgi-bin/messages/modscarddata
mkdir -p /var/www/html/cgi-bin/messages
mkdir -p /var/www/html/cgi-bin/boarddata
mkdir -p /var/www/html/non-cgi/usr
mkdir -p /var/www/html/non-cgi/usravatars
mkdir -p /var/www/html/non-cgi/myimages

chown -R www-data:www-data /var/www/html/cgi-bin /var/www/html/non-cgi || true
chmod -R 777 /var/www/html/cgi-bin/data /var/www/html/cgi-bin/members /var/www/html/cgi-bin/messages /var/www/html/cgi-bin/boarddata /var/www/html/cgi-bin/record /var/www/html/cgi-bin/search /var/www/html/cgi-bin/cache /var/www/html/cgi-bin/lock /var/www/html/cgi-bin/ftpdata /var/www/html/cgi-bin/memblock /var/www/html/cgi-bin/memfav /var/www/html/cgi-bin/memfriend /var/www/html/cgi-bin/sale /var/www/html/cgi-bin/ebankdata /var/www/html/cgi-bin/FileCount /var/www/html/cgi-bin/verifynum /var/www/html/non-cgi/usr /var/www/html/non-cgi/usravatars /var/www/html/non-cgi/myimages || true

mkdir -p /run/leobbs-agent
chown www-data:www-data /run/leobbs-agent
chmod 700 /run/leobbs-agent

# Upgrade only the two bounded hooks even when CGI sources are bind-mounted.
python3 /opt/leobbs-agent/install-hooks.py /var/www/html/cgi-bin
mkdir -p /var/www/html/cgi-bin/data/agent
chown -R www-data:www-data /var/www/html/cgi-bin/data/agent
find /var/www/html/cgi-bin/data/agent -type d -exec chmod 700 {} \;
find /var/www/html/cgi-bin/data/agent -type f -exec chmod 600 {} \;

exec "$@"
