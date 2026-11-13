"""Run against the Compose instance with its initialized public board."""
import json
import os
import urllib.error
import urllib.request

root = os.environ.get("LEOBBS_URL", "http://127.0.0.1:8080")

def get(path, status=200):
    try:
        response = urllib.request.urlopen(root + path, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        assert response.status == status, (path, response.status)
        return response.headers, response.read()

headers, body = get("/api/v1/home")
assert headers.get_content_type() == "application/json"
home = json.loads(body)
board = next(board for board in home["boards"] if board["name"] == "站务公告区")
_, body = get(f'/api/v1/boards/{board["id"]}')
listing = json.loads(body)
assert listing["board"] == board
assert listing["page"] == 1
if listing["items"]:
    topic = listing["items"][0]
    _, body = get(f'/api/v1/boards/{board["id"]}/topics/{topic["id"]}')
    detail = json.loads(body)
    assert detail["topic"]["id"] == topic["id"]
    assert detail["items"][0]["floor"] == 1
    assert all("ip" not in post for post in detail["items"])
    _, body = get(f'/api/v1/boards/{board["id"]}/topics/{topic["id"]}?page=2')
    assert json.loads(body)["items"] == []
get(f'/api/v1/boards/{board["id"]}/topics/999999', 404)
get("/api/v1/boards/999999", 404)
get("/api/v1/boards/1?page=-1", 400)
for path in ("/m/", f'/m/{board["id"]}', f'/m/{board["id"]}/1?page=2'):
    _, body = get(path)
    assert b'id="app"' in body
print("Mobile HTTP smoke checks passed")
