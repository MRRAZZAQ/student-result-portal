import sqlite3

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from . import grades
from .auth import login_required
from .db import get_db

bp = Blueprint("results", __name__)

SUBJECT_FIELDS = [
    ("english", "English"),
    ("hindi", "Hindi"),
    ("mathematics", "Mathematics"),
    ("science", "Science"),
    ("social_science", "Social Science"),
]


def _marks_for(student_ids):
    if not student_ids:
        return {}
    placeholders = ",".join("?" * len(student_ids))
    rows = get_db().execute(
        f"SELECT student_id, subject, marks_obtained FROM marks "
        f"WHERE student_id IN ({placeholders})",
        student_ids,
    ).fetchall()
    grouped = {sid: [] for sid in student_ids}
    for row in rows:
        item = dict(row)
        value = item["marks_obtained"]
        item["marks_obtained"] = int(value) if value == int(value) else value
        grouped[item["student_id"]].append(item)
    return grouped


def _form_data():
    data = {
        "name": request.form.get("name", "").strip(),
        "roll_no": request.form.get("roll_no", "").strip(),
        "class_name": request.form.get("class_name", "").strip(),
        "section": request.form.get("section", "").strip() or "A",
        "marks": {},
    }
    for field, label in SUBJECT_FIELDS:
        raw = request.form.get(field, "").strip()
        if raw == "":
            continue
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"{label} marks must be a number.")
        if not 0 <= value <= 100:
            raise ValueError(f"{label} marks must be between 0 and 100.")
        data["marks"][label] = value
    return data


def _validate(data):
    errors = []
    if not data["name"]:
        errors.append("Name is required.")
    if not data["roll_no"]:
        errors.append("Roll number is required.")
    if not data["class_name"]:
        errors.append("Class is required.")
    if len(data["name"]) > 80:
        errors.append("Name is too long.")
    if len(data["roll_no"]) > 20:
        errors.append("Roll number is too long.")
    if not data["marks"]:
        errors.append("Enter marks for at least one subject.")
    return errors


@bp.route("/")
@login_required
def dashboard():
    search = request.args.get("q", "").strip()
    db = get_db()
    if search:
        students = db.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? "
            "ORDER BY name COLLATE NOCASE",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        students = db.execute("SELECT * FROM students ORDER BY name COLLATE NOCASE").fetchall()

    marks = _marks_for([s["id"] for s in students])
    rows = []
    for student in students:
        summary = grades.summarize(marks.get(student["id"], []))
        rows.append({"student": student, "summary": summary})

    passed = sum(1 for r in rows if r["summary"]["passed"])
    stats = {
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
    }
    return render_template("dashboard.html", rows=rows, stats=stats, search=search)


@bp.route("/students/new", methods=("GET", "POST"))
@login_required
def student_new():
    if request.method == "POST":
        try:
            data = _form_data()
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("student_form.html", data=request.form, subjects=SUBJECT_FIELDS)

        errors = _validate(data)
        if not errors:
            db = get_db()
            try:
                cur = db.execute(
                    "INSERT INTO students (name, roll_no, class_name, section) "
                    "VALUES (?, ?, ?, ?)",
                    (data["name"], data["roll_no"], data["class_name"], data["section"]),
                )
                _save_marks(cur.lastrowid, data["marks"])
                db.commit()
            except sqlite3.IntegrityError:
                errors.append(f"Roll number '{data['roll_no']}' already exists.")
            else:
                flash(f"Result added for {data['name']}.", "success")
                return redirect(url_for("results.student_detail", student_id=cur.lastrowid))

        for error in errors:
            flash(error, "error")
        return render_template("student_form.html", data=request.form, subjects=SUBJECT_FIELDS)

    return render_template("student_form.html", data={}, subjects=SUBJECT_FIELDS)


@bp.route("/students/<int:student_id>")
@login_required
def student_detail(student_id):
    student = get_db().execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    if student is None:
        abort(404)
    marks = _marks_for([student_id]).get(student_id, [])
    marks.sort(key=lambda m: _subject_order(m["subject"]))
    summary = grades.summarize(marks)
    return render_template(
        "student_detail.html", student=student, marks=marks, summary=summary
    )


@bp.route("/students/<int:student_id>/edit", methods=("GET", "POST"))
@login_required
def student_edit(student_id):
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        abort(404)

    existing = _marks_for([student_id]).get(student_id, [])
    existing_map = {m["subject"]: m["marks_obtained"] for m in existing}

    if request.method == "POST":
        try:
            data = _form_data()
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template(
                "student_form.html", data=request.form, student=student, subjects=SUBJECT_FIELDS
            )

        errors = _validate(data)
        if not errors:
            try:
                db.execute(
                    "UPDATE students SET name = ?, roll_no = ?, class_name = ?, section = ? "
                    "WHERE id = ?",
                    (data["name"], data["roll_no"], data["class_name"], data["section"], student_id),
                )
                db.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
                _save_marks(student_id, data["marks"])
                db.commit()
            except sqlite3.IntegrityError:
                errors.append(f"Roll number '{data['roll_no']}' already exists.")
            else:
                flash("Result updated.", "success")
                return redirect(url_for("results.student_detail", student_id=student_id))

        for error in errors:
            flash(error, "error")
        return render_template("student_form.html", data=request.form, student=student, subjects=SUBJECT_FIELDS)

    data = {
        "name": student["name"],
        "roll_no": student["roll_no"],
        "class_name": student["class_name"],
        "section": student["section"],
    }
    form_values = {k: v for k, v in data.items()}
    for field, label in SUBJECT_FIELDS:
        form_values[field] = existing_map.get(label, "")
    return render_template(
        "student_form.html", data=form_values, student=student, subjects=SUBJECT_FIELDS
    )


@bp.post("/students/<int:student_id>/delete")
@login_required
def student_delete(student_id):
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        abort(404)
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash(f"Deleted result for {student['name']}.", "success")
    return redirect(url_for("results.dashboard"))


def _save_marks(student_id, marks):
    db = get_db()
    for label, value in marks.items():
        db.execute(
            "INSERT INTO marks (student_id, subject, marks_obtained) VALUES (?, ?, ?)",
            (student_id, label, value),
        )


def _subject_order(subject):
    for index, (_, label) in enumerate(SUBJECT_FIELDS):
        if label == subject:
            return index
    return len(SUBJECT_FIELDS)
