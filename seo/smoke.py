"""Verify the running Apache instance without cookies."""
import os
import re
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

base = os.environ.get("LEOBBS_URL", "http://127.0.0.1:8080")
for agent, expected in (("Mozilla Windows NT", "/cgi-bin/leobbs.htm"), ("Mozilla iPhone", "/m/")):
    from http.client import HTTPConnection
    address = urlsplit(base)
    connection = HTTPConnection(address.netloc, timeout=10)
    connection.request("GET", "/", headers={"User-Agent": agent, "X-Forwarded-Proto": "https"})
    with connection.getresponse() as response:
        assert response.status == 302
        assert response.getheader("Location") == expected
        assert urljoin("https://example.com/", expected).startswith("https://")
    connection.close()

with urlopen(base + "/robots.txt", timeout=10) as response:
    assert response.headers.get_content_type() == "text/plain"
    rules = response.read().decode("utf-8")
    for path in ("admin", "install", "loginout", "register", "messanger"):
        assert f"Disallow: /cgi-bin/{path}.cgi" in rules

with urlopen(base + "/sitemap.xml", timeout=10) as response:
    assert response.headers.get_content_type() == "application/xml"
    urls = [node.text for node in ET.fromstring(response.read().decode("utf-8")).iterfind(".//{*}loc")]
assert len(urls) == len(set(urls))
assert len({urlsplit(url).netloc for url in urls}) <= 1
for url in urls:
    path = urlsplit(url).path
    assert re.fullmatch(r"/cgi-bin/(leobbs|forums-\d+-0|topic-\d+-\d+-0-0-)\.htm", path)
    assert "Sitemap: " + urljoin(url, "/sitemap.xml") in rules
    for attempt in range(3):
        with urlopen(Request(base + path), timeout=10) as response:
            html = response.read().decode("gbk", errors="replace")
            assert response.status == 200
        if "服务器忙" not in html:
            break
        time.sleep(2)
    assert "</html>" in html.lower() and "服务器忙" not in html, path
print(f"SEO smoke checks passed ({len(urls)} public URLs)")
