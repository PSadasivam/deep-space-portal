"""Rate limits must key on the visitor's address behind nginx, not on the proxy's (threat model WA-2)."""

import pytest

import app as portal_app
from app import app


@pytest.fixture
def client():
    was_enabled = portal_app.limiter.enabled
    portal_app.limiter.enabled = True
    portal_app.limiter.reset()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    portal_app.limiter.reset()
    portal_app.limiter.enabled = was_enabled


def _status(client, forwarded_for):
    return client.get("/api/status", headers={"X-Forwarded-For": forwarded_for}).status_code


def test_visitors_behind_the_proxy_get_separate_buckets(client):
    assert [_status(client, "203.0.113.1") for _ in range(10)] == [200] * 10
    assert _status(client, "203.0.113.1") == 429
    assert _status(client, "203.0.113.2") == 200


def test_spoofed_forwarded_for_entries_do_not_reset_the_limit(client):
    # nginx appends the real address last; a client can only prepend fake ones.
    for i in range(10):
        assert _status(client, f"198.51.100.{i}, 203.0.113.9") == 200
    assert _status(client, "198.51.100.99, 203.0.113.9") == 429
