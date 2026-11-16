#!/usr/bin/python3
from pathlib import Path
print('Content-Type: text/html; charset=utf-8')
print('Cache-Control: no-store')
print('X-Frame-Options: DENY')
print()
print(Path('/var/www/html/m/index.html').read_text())
