import os

from flask import Flask, render_template

from . import auth, db, metrics, results


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        DATABASE=os.path.join(app.instance_path, "results.sqlite3"),
        ADMIN_USER=os.environ.get("ADMIN_USER", "admin"),
        SESSION_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_HTTPONLY=True,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("ADMIN_PASSWORD_HASH"):
        app.config["ADMIN_PASSWORD_HASH"] = auth.hash_password(
            os.environ.get("ADMIN_PASSWORD", "admin123")
        )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    db.init_db(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(results.bp)
    app.register_blueprint(metrics.bp)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app
