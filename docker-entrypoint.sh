#!/bin/sh
set -eu

seed_dir_if_missing() {
  src="$1"
  dst="$2"
  marker="$3"

  mkdir -p "$dst"
  if [ ! -e "$dst/$marker" ]; then
    cp -a "$src/." "$dst/"
  fi
}

seed_dir_if_missing /opt/leobbs-seed/cgi-bin/data /var/www/html/cgi-bin/data boardinfo.cgi
seed_dir_if_missing /opt/leobbs-seed/cgi-bin/members /var/www/html/cgi-bin/members index.html
seed_dir_if_missing /opt/leobbs-seed/cgi-bin/messages /var/www/html/cgi-bin/messages index.html
seed_dir_if_missing /opt/leobbs-seed/cgi-bin/boarddata /var/www/html/cgi-bin/boarddata index.html
seed_dir_if_missing /opt/leobbs-seed/non-cgi/usr /var/www/html/non-cgi/usr index.html
seed_dir_if_missing /opt/leobbs-seed/non-cgi/usravatars /var/www/html/non-cgi/usravatars index.html

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

chown -R www-data:www-data /var/www/html/cgi-bin/data /var/www/html/cgi-bin/members /var/www/html/cgi-bin/messages /var/www/html/cgi-bin/boarddata /var/www/html/non-cgi/usr /var/www/html/non-cgi/usravatars || true
chmod -R 777 /var/www/html/cgi-bin/data /var/www/html/cgi-bin/members /var/www/html/cgi-bin/messages /var/www/html/cgi-bin/boarddata /var/www/html/non-cgi/usr /var/www/html/non-cgi/usravatars || true

exec "$@"
