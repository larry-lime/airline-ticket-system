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

from airline.auth import login_required, user_is_logged_in
from airline.db import get_db
from airline.util import get_tickets, get_user_info, get_flight, get_purchases

bp = Blueprint("airline", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT airport_name, airport_city
            FROM airport
            """
    cursor.execute(query)
    airports = cursor.fetchall()
    cursor.close()

    purchases = get_purchases(g.user["username"], g.user_type) if user_is_logged_in() else None

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

        if error is None:
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

    return render_template(
        "airline/index.html",
        airports=airports,
        purchases=purchases,
    )


@bp.route("/search", methods=("GET", "POST"))
def search_results():
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

        if error is None:
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

    return render_template(
        "airline/results.html",
        going_to_airport=going_to_airport,
        leaving_from_airport=leaving_from_airport,
        departure_date=departure_date,
        return_date=return_date,
        flights=flights,
        airports=airports,
    )


@bp.route("/<int:id>/purchase", methods=("GET", "POST"))
@login_required
def purchase_ticket(id):
    flight = get_flight(id)
    tickets = get_tickets(id)

    if request.method == "POST":
        user_info = get_user_info(g.user["username"], g.user_type)
        ticket_id = request.form["ticket"]
        purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error = None

        conn = get_db()
        cursor = conn.cursor()
        query = """
                INSERT INTO purchases(ticket_id, customer_email, purchase_date)
                VALUES ({},'{}','{}')
                """
        cursor.execute(query.format(ticket_id, user_info["username"], purchase_date))
        conn.commit()
        cursor.close()

        # TODO: This should redirect to 'My Flights'
        if error is None:
            return redirect(url_for("airline.index"))

    return render_template(
        "airline/purchase_ticket.html", flight=flight, tickets=tickets
    )


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def refund(id):
    get_tickets(id)
    conn = get_db()
    cursor = conn.cursor()
    query = "DELETE FROM post WHERE id = '{}'"
    cursor.execute(query.format(id))
    conn.commit()
    cursor.close()
    return redirect(url_for("airline.index"))
