import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user where id = '{}'"
        cursor.execute(query.format(user_id))
        g.user = cursor.fetchone() # a tuple with (id, name, password_hash)
        conn.commit()
        cursor.close()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        # Enforce required fields
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            query = "SELECT * FROM user WHERE username = '{}'"
            cursor.execute(query.format(username))
            data = cursor.fetchone()

            if data is not None:
                error = f"User {username} is already registered."
            else:
                query = "INSERT INTO user (username, password) VALUES('{}','{}')"
                cursor.execute(query.format(username, generate_password_hash(password)))
                conn.commit()
                cursor.close()
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM user WHERE username = '{}'"
        cursor.execute(query.format(username))
        user = cursor.fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user['id']
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
