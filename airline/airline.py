import datetime
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
from werkzeug.exceptions import abort

from airline.auth import login_required
from airline.db import get_db

bp = Blueprint("airline", __name__)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    INSERT INTO post (title, body, author_id)
                    VALUES ('{}', '{}', {})
                    """
            cursor.execute(query.format(title, body, g.user["id"]))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

    return render_template("airline/create.html")


def get_post(id, check_author=True):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT p.id, title, body, created, author_id, username
            FROM post p JOIN user u ON p.author_id = u.id
            WHERE p.id = '{}'
            """
    cursor.execute(query.format(id))
    post = cursor.fetchone()
    cursor.close()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT airport_name, airport_city
                FROM airport
                """
        cursor.execute(query)
        airports = cursor.fetchall()
        cursor.close()

    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        going_to_airport = session["going_to"] = request.form.get("going_to")
        leaving_from_airport = session["leaving_from"] = request.form.get(
            "leaving_from"
        )
        departure_date = session["departure_date"] = request.form.get("departure_date")
        return_date = session["return_date"] = request.form.get("return_date")

        if (
            going_to_airport is None
            or leaving_from_airport is None
            or departure_date is None
        ):
            error = "One or more fields are empty. Please fill out all fields."
        elif return_date is None:
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                )
            )
        else:  # User wants a return trip
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                    return_date=return_date,
                )
            )

        flash(error)

    return render_template("airline/index.html", airports=airports)


@bp.route("/search", methods=("GET", "POST"))
def search_results():
    if request.method == "GET":
        going_to_airport = request.args.get("going_to_airport")
        leaving_from_airport = request.args.get("leaving_from_airport")
        departure_date = request.args.get("departure_date")
        return_date = request.args.get("return_date")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT airport_name, airport_city
                FROM airport
                """
        cursor.execute(query)
        airports = cursor.fetchall()
        cursor.close()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None
        # TODO: Add a simple WHERE clause to the query below when we have enough sample data
        query = """
                SELECT airline_name,
                       flight_num,
                       departure_airport,
                       DATE_FORMAT(departure_time, '%h:%i %p') AS departure_time,
                       arrival_airport,
                       DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
                       price,
                       status,
                       airplane_id,
                       a1.airport_city as departure_city,
                       a2.airport_city as arrival_city 
                FROM flight as f
                JOIN airport as a1 on f.departure_airport = a1.airport_name
                JOIN airport as a2 on f.arrival_airport = a2.airport_name
                """
        cursor.execute(query)
        flights = cursor.fetchall()
        cursor.close()

        # TODO:
        # 1. Make the title the departure_time - arrival_time
        # 2. Under the title, show the departure city (departure_airport) - arrival city (arrival_airport)
        # 3. Under that, show the airline name
        # 4. Show how long the flight is (departure_time - arrival_time)
        # 5. In big letters, show the price of the flight

        # 6. Show the flight status (on time, delayed, cancelled)
        # 7. EXTRA: Above the big letters, show how many seats left

        return render_template(
            "airline/results.html",
            going_to_airport=going_to_airport,
            leaving_from_airport=leaving_from_airport,
            departure_date=departure_date,
            return_date=return_date,
            flights=flights,
            airports=airports,
        )
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        going_to_airport = session["going_to"] = request.form.get("going_to")
        leaving_from_airport = session["leaving_from"] = request.form.get(
            "leaving_from"
        )
        departure_date = session["departure_date"] = request.form.get("departure_date")
        return_date = session["return_date"] = request.form.get("return_date")

        if (
            going_to_airport is None
            or leaving_from_airport is None
            or departure_date is None
        ):
            error = "One or more fields are empty. Please fill out all fields."
        elif return_date is None:
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                )
            )
        else:  # User wants a return trip
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                    return_date=return_date,
                )
            )

        flash(error)


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    UPDATE post SET title = '{}', body = '{}'
                    WHERE id = '{}'
                    """
            cursor.execute(query.format(title, body, id))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

    return render_template("airline/update.html", post=post)


def get_flight(flight_num):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT airline_name,
                   flight_num,
                   departure_airport,
                   DATE_FORMAT(departure_time, '%h:%i %p') AS departure_time,
                   arrival_airport,
                   DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
                   price,
                   status,
                   airplane_id,
                   a1.airport_city as departure_city,
                   a2.airport_city as arrival_city 
            FROM flight as f
            JOIN airport as a1 on f.departure_airport = a1.airport_name
            JOIN airport as a2 on f.arrival_airport = a2.airport_name
            WHERE flight_num = '{}'
            """
    cursor.execute(query.format(flight_num))
    flight = cursor.fetchone()
    cursor.close()

    if flight is None:
        abort(404, f"Post id {flight_num} doesn't exist.")

    return flight

def get_tickets(flight_num):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT *
            FROM ticket
            NATURAL JOIN flight
            WHERE flight_num = '{}'
            """
    # Get all the available tickets for a given flight
    cursor.execute(query.format(flight_num))
    tickets = cursor.fetchall()
    cursor.close()

    return tickets

def get_user_info(username,user_type):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT *
            FROM {}
            WHERE username = '{}'
            """
    # Get all the available tickets for a given flight
    cursor.execute(query.format(user_type, username))
    user_info = cursor.fetchone()
    cursor.close()

    return user_info


@bp.route("/<int:id>/purchase", methods=("GET", "POST"))
@login_required
def purchase_ticket(id):
    flight = get_flight(id)
    tickets = get_tickets(id)

    if request.method == "POST":
        user_info = get_user_info(g.user["username"],g.user_type)
        ticket_id = request.form["ticket"]
        purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error = None

        conn = get_db()
        cursor = conn.cursor()
        query = """
                INSERT INTO purchases(ticket_id, customer_email, purchase_date)
                VALUES ({},'{}','{}')
                """
        cursor.execute(query.format(
            ticket_id,
            user_info['username'],
            purchase_date
            ))
        conn.commit()
        cursor.close()
        # TODO: This should redirect to 'My Flights'
        return redirect(url_for("airline.index"))

    return render_template("airline/purchase_ticket.html", flight=flight,tickets=tickets)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    conn = get_db()
    cursor = conn.cursor()
    query = "DELETE FROM post WHERE id = '{}'"
    cursor.execute(query.format(id))
    conn.commit()
    cursor.close()
    return redirect(url_for("airline.index"))
