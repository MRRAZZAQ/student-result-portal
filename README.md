# Student Result Portal

A small web application for storing and publishing student exam results. Admins can log in, add results subject-wise, and the app calculates totals, percentage, grade and pass/fail automatically. Comes with a Docker Compose stack that includes Prometheus and Grafana for monitoring.

## Features

- Admin login (session based, password stored as a hash)
- Add / edit / delete student results with marks for 5 subjects
- Automatic total, percentage, grade (A+ to F) and pass/fail
- Pass rule: minimum 33 marks in every subject
- Dashboard with pass/fail stats and search by name or roll number
- Printable-style result sheet per student
- SQLite storage — data survives restarts
- `/health` and `/metrics` endpoints for Prometheus
- Gunicorn behind Docker, Flask dev server for local runs

## Tech stack

| Layer     | Choice                                    |
|-----------|-------------------------------------------|
| Backend   | Python 3.12, Flask 3                       |
| Database  | SQLite (stdlib `sqlite3`, no setup)        |
| Frontend  | Jinja2 templates + plain CSS, no framework |
| Metrics   | `prometheus_client`                        |
| Server    | Gunicorn (production), Flask (dev)         |
| Tests     | pytest                                     |
| Monitoring| Prometheus + Grafana via Docker Compose    |
| CI/CD     | GitHub Actions → Docker Hub                |

## Quick start (local)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 and log in with `admin` / `admin123`.

Change the credentials with environment variables:

```bash
set ADMIN_USER=myuser
set ADMIN_PASSWORD=mypassword
set SECRET_KEY=some-random-string
```

The database file is created at `instance/results.sqlite3` on first run.

## Run with Docker Compose

```bash
docker compose up --build
```

| Service    | URL                      | Notes                        |
|------------|--------------------------|------------------------------|
| Web app    | http://localhost:5000    | login: admin / admin123      |
| Prometheus | http://localhost:9090    | scrapes `/metrics` every 15s |
| Grafana    | http://localhost:3000    | admin / admin                |

Data is stored in the `results-data` volume so it survives `docker compose down`.

## Tests

```bash
pytest tests -v
```

Covers auth, form validation, grade calculation, CRUD flows and the health/metrics endpoints.

## Endpoints

| Method | Path                      | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/login/`                 | Admin login form               |
| POST   | `/login/`                 | Submit credentials             |
| POST   | `/login/logout`           | Log out                        |
| GET    | `/`                       | Dashboard (login required)     |
| GET    | `/students/new`           | Add result form                |
| POST   | `/students/new`           | Save a new result              |
| GET    | `/students/<id>`          | Result sheet                   |
| GET    | `/students/<id>/edit`     | Edit form                      |
| POST   | `/students/<id>/edit`     | Update result                  |
| POST   | `/students/<id>/delete`   | Delete result                  |
| GET    | `/health`                 | Liveness probe (plain text)    |
| GET    | `/metrics`                | Prometheus metrics             |

## Project structure

```
app.py                  entry point (python app.py)
portal/
  __init__.py           application factory
  auth.py               login/logout, session handling
  results.py            dashboard + student CRUD routes
  grades.py             grade and pass/fail logic
  db.py                 SQLite connection and schema
  metrics.py            /health and /metrics
  templates/            Jinja2 pages
  static/style.css      stylesheet
tests/                  pytest suite
Dockerfile              image for production
docker-compose.yml      app + Prometheus + Grafana
prometheus.yml          scrape config
.github/workflows/      CI: test, then push image on main
```

## CI/CD

Every push and pull request to `main` runs the test suite. When a push lands on `main`, the pipeline also builds the Docker image and pushes it to Docker Hub as `student-result-portal:latest` (plus a tag with the commit SHA). Required repository secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
