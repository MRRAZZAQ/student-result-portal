import time

from flask import Blueprint, Response, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

bp = Blueprint("metrics", __name__)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests handled",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
STUDENTS = Gauge("students_total", "Number of students in the portal")


@bp.before_app_request
def start_timer():
    request._start_time = time.perf_counter()


@bp.after_app_request
def record_request(response):
    start = getattr(request, "_start_time", None)
    endpoint = request.endpoint or "unmatched"
    labels = (request.method, endpoint, str(response.status_code))
    REQUESTS.labels(*labels).inc()
    if start is not None:
        LATENCY.labels(request.method, endpoint).observe(time.perf_counter() - start)
    return response


@bp.route("/health")
def health():
    return Response("flask_app_status 1\n", mimetype="text/plain")


@bp.route("/metrics")
def metrics():
    STUDENTS.set(_count_students())
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def _count_students():
    from .db import get_db

    try:
        row = get_db().execute("SELECT COUNT(*) AS n FROM students").fetchone()
        return row["n"]
    except Exception:
        return 0
