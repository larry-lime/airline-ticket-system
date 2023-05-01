import functools
import logging

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

from airline.db import get_db

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
        g.user = cursor.fetchone()  # a tuple with (id, name, password_hash)
        conn.commit()
        cursor.close()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = g.username = request.form["username"]
        password = g.password = request.form["password"]
        first_name = g.first_name = request.form["first_name"]
        last_name = g.last_name = request.form["last_name"]
        user_type = g.user_type = request.form["user_type"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        # NOTE: I don't expect any errors so I comment this out
        # if not username:
        #     error = "Username is required."
        # elif not password:
        #     error = "Password is required."

        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(g.user_type, username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            current_app.logger.info("User %s registered", username)
            # query = """
            #         INSERT INTO {} (username, password, first_name, last_name)
            #         VALUES('{}','{}','{}','{}')
            #         """
            # cursor.execute(
            #     user_type,
            #     query.format(username, generate_password_hash(password)),
            #     first_name,
            #     last_name,
            # )
            # conn.commit()
            # cursor.close()
            if user_type == "customer":
                return redirect(url_for("auth.register_customer"))
            elif user_type == "booking_agent":
                return redirect(url_for("auth.register_agent"))
            elif user_type == "airling_staff":
                return redirect(url_for("auth.register_staff"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("register/customer", methods=("GET", "POST"))
def register_customer():
    if request.method == "POST":
        username = g.username
        password = g.password
        first_name = g.first_name
        last_name = g.last_name
        user_type = g.user_type

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(user_type, username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            query = """
                    INSERT INTO {} (username, password, first_name, last_name)
                    VALUES('{}','{}','{}','{}')
                    """
            cursor.execute(
                user_type,
                query.format(username, generate_password_hash(password)),
                first_name,
                last_name,
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/customer.html")

@bp.route("/register/staff", methods=("GET", "POST"))
def register_staff():
    if request.method == "POST":
        username = g.username
        password = g.password
        first_name = g.first_name
        last_name = g.last_name
        user_type = g.user_type

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(user_type, username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            query = """
                    INSERT INTO {} (username, password, first_name, last_name)
                    VALUES('{}','{}','{}','{}')
                    """
            cursor.execute(
                user_type,
                query.format(username, generate_password_hash(password)),
                first_name,
                last_name,
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/airline_staff.html")

@bp.route("/register/agent", methods=("GET", "POST"))
def register_agent():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        user_type = request.form["user_type"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(user_type, username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            query = """
                    INSERT INTO {} (username, password, first_name, last_name)
                    VALUES('{}','{}','{}','{}')
                    """
            cursor.execute(
                user_type,
                query.format(username, generate_password_hash(password)),
                first_name,
                last_name,
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/airline_staff.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_type = request.form["user_type"]
        current_app.logger.info(f"User type: {user_type}")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM user WHERE username = '{}'"
        cursor.execute(query.format(username))
        user = cursor.fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
