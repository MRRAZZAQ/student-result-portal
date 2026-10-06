import os

import pytest

from portal import create_app
from portal.auth import hash_password


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": os.path.join(tmp_path, "test.sqlite3"),
            "ADMIN_USER": "admin",
            "ADMIN_PASSWORD_HASH": hash_password("secret123"),
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    client.post(
        "/login/",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=True,
    )
    return client


def login(client, username="admin", password="secret123"):
    return client.post("/login/", data={"username": username, "password": password})
