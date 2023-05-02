import functools

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
    username = session.get("username")
    user_type = session.get("user_type")

    if username is None:
        g.user = None
    else:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM {} where username = '{}'"
        cursor.execute(query.format(user_type, username))
        g.user = cursor.fetchone()
        conn.commit()
        cursor.close()


# TODO: Finish this function along with register_customer, register_agent, and register_staff
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = session["username"] = request.form["username"]
        password = session["password"] = generate_password_hash(
            request.form["password"]
        )
        session["first_name"] = request.form["first_name"]
        session["last_name"] = request.form["last_name"]
        user_type = session["user_type"] = request.form["user_type"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        # Check if username is already registered
        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(user_type, username))
        data = cursor.fetchone()

        # If username is not registered, redirect to the appropriate registration page
        if data is not None:
            error = f"User {username} is already registered."
        elif user_type == "airline_staff":
            return redirect(url_for("auth.register_staff"))
        elif user_type == "booking_agent":
            return redirect(url_for("auth.register_agent"))
        elif user_type == "customer":
            return redirect(url_for("auth.register_customer"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("register/customer", methods=("GET", "POST"))
def register_customer():
    if request.method == "POST":
        username = session["username"]
        password = session["password"]
        first_name = session["first_name"]
        last_name = session["last_name"]
        building_number = request.form["building_number"]
        street = request.form["street"]
        city = request.form["city"]
        state = request.form["state"]
        phone_number = request.form["phone_number"]
        passport_number = request.form["passport_number"]
        passport_expiration = request.form["passport_expiration"]
        passport_country = request.form["passport_country"]
        date_of_birth = request.form["date_of_birth"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM customer WHERE username = '{}'"
        cursor.execute(query.format(username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            query = """
                    INSERT INTO customer (username, password, first_name, last_name, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                    VALUES('{}','{}','{}','{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                    """
            cursor.execute(
                query.format(
                    username,
                    password,
                    first_name,
                    last_name,
                    building_number,
                    street,
                    city,
                    state,
                    phone_number,
                    passport_number,
                    passport_expiration,
                    passport_country,
                    date_of_birth,
                )
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/customer.html")

@bp.route("/register/staff", methods=("GET", "POST"))
def register_staff():
    if request.method == "POST":
        username = session["username"]
        password = session["password"]
        first_name = session["first_name"]
        last_name = session["last_name"]
        date_of_birth = request.form["date_of_birth"]
        airline_name = request.form["airline_name"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM airline_staff WHERE username = '{}'"
        cursor.execute(query.format(username))
        data = cursor.fetchone()
        if data is not None:
            error = f"User {username} is already registered."
        else:
            # Insert airline_name into table airline if it does not exist
            query1 = "INSERT IGNORE INTO airline (airline_name) VALUES('{}')"
            cursor.execute(query1.format(airline_name.title()))
            query2 = """
                    INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name)
                    VALUES('{}','{}','{}','{}', '{}', '{}')
                    """
            cursor.execute(
                query2.format(
                    username,
                    password,
                    first_name,
                    last_name,
                    date_of_birth,
                    airline_name.title(),
                )
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

    return render_template("auth/booking_agent.html")


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
