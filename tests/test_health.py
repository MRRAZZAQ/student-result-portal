def test_health_check(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert b"flask_app_status 1" in rv.data
    assert rv.mimetype == "text/plain"


def test_metrics_exposes_prometheus_format(client):
    rv = client.get("/metrics")
    assert rv.status_code == 200
    assert b"http_requests_total" in rv.data
    assert b"http_request_duration_seconds" in rv.data
    assert b"students_total" in rv.data


def test_metrics_counts_requests(client):
    client.get("/health")
    rv = client.get("/metrics")
    assert b'http_requests_total{' in rv.data
    assert b'endpoint="metrics.health"' in rv.data


def test_page_not_found(client):
    rv = client.get("/definitely-not-a-page")
    assert rv.status_code == 404
    assert b"404" in rv.data
