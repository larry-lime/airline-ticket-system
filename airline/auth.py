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

from airline.db import get_db
from airline.util import *

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        return redirect(url_for("auth.login")) if g.user is None else view(**kwargs)

    return wrapped_view


def user_is_logged_in():
    return g.user is not None


@bp.before_app_request
def load_logged_in_user():
    username = session.get("username")
    user_type = session.get("user_type")

    g.user_type = None if user_type is None else user_type

    if username is None:
        g.user = None
    else:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        if user_type == "booking_agent":
            query = """SELECT *
                       FROM booking_agent
                       JOIN booking_agent_work_for
                       ON booking_agent.username = booking_agent_work_for.email
                       WHERE username = '{}'
                    """
            cursor.execute(query.format(username))
        else:
            query = "SELECT * FROM {} where username = '{}'"
            cursor.execute(query.format(user_type, username))
        g.user = cursor.fetchone()
        cursor.close()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        session["username"] = username = request.form["username"]
        session["user_type"] = user_type = request.form["user_type"]
        session["password"] = generate_password_hash(request.form["password"])
        session["first_name"] = request.form["first_name"]
        session["last_name"] = request.form["last_name"]

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
        else:
            error = "Invalid user type."

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
            return redirect(url_for("airline.index"))

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
            query3 = """
            INSERT INTO permission (username, permission_type)
            VALUES('{}','read')
            """
            cursor.execute(query3.format(username))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        flash(error)

    return render_template("auth/airline_staff.html")


@bp.route("/register/agent", methods=("GET", "POST"))
def register_agent():
    airlines = get_airlines()
    if request.method == "POST":
        airline_name = request.form.get("airline_name")
        username = session["username"]
        password = session["password"]
        first_name = session["first_name"]
        last_name = session["last_name"]
        booking_agent_id = int(request.form["booking_agent_id"])

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        # Username is already taken
        query = "SELECT * FROM booking_agent WHERE username = '{}'"
        cursor.execute(query.format(username))
        data1 = cursor.fetchone()

        # User in the same airline has the same booking_agent_id
        query = """
                SELECT *
                FROM booking_agent as ba
                WHERE booking_agent_id = {}
                """
        cursor.execute(query.format(booking_agent_id, airline_name))
        data2 = cursor.fetchone()

        # TODO: Make it booking_agent_id + airline instead of just booking agent
        if airline_name is None:
            error = "Please select an airline."
        elif data1 is not None:
            error = f"User {username} is already registered."
        elif data2 is not None:
            # error = f"Booking agent ID {booking_agent_id} for {airline_name} airlines is already taken."
            error = f"Booking agent ID {booking_agent_id} is already taken."

        if error is None:
            # Insert into booking agent
            query = """
                    INSERT INTO booking_agent (username, password, first_name, last_name, booking_agent_id)
                    VALUES('{}','{}','{}','{}', {})
                    """
            cursor.execute(
                query.format(
                    username,
                    password,
                    first_name,
                    last_name,
                    booking_agent_id,
                )
            )
            conn.commit()
            # Insert into booking_agent_work_for
            query = """
                    INSERT INTO booking_agent_work_for (email, airline_name)
                    VALUES('{}','{}')
                    """
            cursor.execute(query.format(username, airline_name))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        flash(error)

    return render_template(
        "auth/booking_agent.html",
        airlines=airlines,
    )


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username: str = request.form["username"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM {} WHERE username = '{}'"
        cursor.execute(query.format(user_type, username))
        user = cursor.fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        else:
            session.clear()
            session["username"] = user["username"]
            session["user_type"] = user_type
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Goodbye!")
    return redirect(url_for("index"))
