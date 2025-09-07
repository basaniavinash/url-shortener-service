from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_expand_redirect_happy_path():
    # Create
    r = client.post("/v1/shorten", json={"url": "https://example.com"})
    assert r.status_code == 200, r.text
    data = r.json()
    sid = data["id"]
    assert len(sid) >= 6

    # Expand
    r2 = client.get(f"/v1/expand/{sid}")
    assert r2.status_code == 200
    assert r2.json()["long_url"].startswith("https://example.com")

    # Redirect (don’t follow external)
    r3 = client.get(f"/{sid}", allow_redirects=False)
    assert r3.status_code in (301, 302, 307, 308)
    assert r3.headers["location"].startswith("https://example.com")


def test_404_unknown_id():
    r = client.get("/nope", allow_redirects=False)
    assert r.status_code == 404
