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

exec "$@"
