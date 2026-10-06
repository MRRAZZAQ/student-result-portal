from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/login")


def hash_password(password):
    return generate_password_hash(password)


def login_required(view):
    @wraps(view)
    def wrapped(**kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)

    return wrapped


@bp.before_app_request
def load_logged_in_user():
    g.user = session.get("user")
    g.is_admin = g.user == current_app.config["ADMIN_USER"]


@bp.route("/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if (
            username == current_app.config["ADMIN_USER"]
            and check_password_hash(current_app.config["ADMIN_PASSWORD_HASH"], password)
        ):
            session.clear()
            session["user"] = username
            target = request.args.get("next", "")
            if target.startswith("/") and not target.startswith("//"):
                return redirect(target)
            return redirect(url_for("results.dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
