from tests.conftest import login


def test_login_page_loads(client):
    rv = client.get("/login/")
    assert rv.status_code == 200
    assert b"Admin Login" in rv.data


def test_login_success(client):
    rv = login(client)
    assert rv.status_code == 302
    assert rv.headers["Location"].endswith("/")


def test_login_wrong_password(client):
    rv = login(client, password="wrong")
    assert b"Invalid username or password" in rv.data


def test_dashboard_requires_login(client):
    rv = client.get("/")
    assert rv.status_code == 302
    assert "/login/" in rv.headers["Location"]


def test_dashboard_after_login(auth_client):
    rv = auth_client.get("/")
    assert rv.status_code == 200
    assert b"Results Dashboard" in rv.data


def test_logout(auth_client):
    rv = auth_client.post("/login/logout", follow_redirects=True)
    assert b"logged out" in rv.data
    rv = auth_client.get("/")
    assert rv.status_code == 302
