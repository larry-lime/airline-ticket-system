import pandas as pd
import json
import plotly
import plotly.express as px

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

from werkzeug.security import check_password_hash, generate_password_hash
from airline.auth import login_required, user_is_logged_in
from airline.db import get_db
from airline.util import *
from airline.search_util import *
from airline.staff_util import *
from airline.error_checking import *

bp = Blueprint("airline", __name__)


# TODO: Update this and populate this with content when the post() table is updated with actual content
@bp.route("/<int:post_id>/post", methods=("GET", "POST"))
def post(post_id):
    return render_template("airline/post.html", post_id=post_id)


@bp.route("/", methods=("GET", "POST"))
def index():
    airports = get_airports()
    delete_ticket_id = request.args.get("delete_ticket_id")
    username = g.user["username"] if user_is_logged_in() else None
    purchases = graphJSON = flights = None
    month_top_booking_agents = year_top_booking_agents = frequent_customers = None
    year_top_destinations = month_top_destinations = None
    posts = []

    if delete_ticket_id is not None:
        refund(delete_ticket_id)

    if g.user_type == "airline_staff":
        airline_name = g.user["airline_name"]
        flights = get_next_month_flights(airline_name)
        month_top_booking_agents = get_top_agents_of_month(airline_name)
        year_top_booking_agents = get_top_agents_of_year(airline_name)
        frequent_customers = top_customers(airline_name)
        year_top_destinations = top_destinations_of_year(airline_name)
        month_top_destinations = top_destinations_of_last_3_months(airline_name)

    elif g.user_type == "customer":
        purchases = (
            customer_get_purchases(username, g.user_type)
            if user_is_logged_in()
            else None
        )
        graphJSON = plot_customer_purchase_totals(username)

    elif g.user_type == "booking_agent":
        purchases = (
            booking_agent_get_purchases(g.user["booking_agent_id"])
            if user_is_logged_in()
            else None
        )

    if request.method == "POST":
        leaving_from_airport = request.form.get("leaving_from")
        going_to_airport = request.form.get("going_to")
        departure_date = request.form.get("departure_date")
        return_date = request.form.get("return_date")

        error = error_check_search(
            leaving_from_airport, going_to_airport, departure_date
        )

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
        flights=flights,
        graphJSON=graphJSON,
        posts=posts,
        purchases=purchases,
        month_top_booking_agents=month_top_booking_agents,
        year_top_booking_agents=year_top_booking_agents,
        frequent_customers=frequent_customers,
        year_top_destinations=year_top_destinations,
        month_top_destinations=month_top_destinations,
    )


@bp.route("/search", methods=("GET", "POST"))
def search_results():
    get_all_flights = request.args.get("search_all_flights")
    going_to_airport = request.args.get("going_to_airport")
    leaving_from_airport = request.args.get("leaving_from_airport")
    departure_date = request.args.get("departure_date")
    return_date = request.args.get("return_date")

    airports = get_airports()
    flights = []

    if get_all_flights is not None and get_all_flights == "True":
        flights = search_all_flights()

    elif g.user_type == "airline_staff":
        airline_name = g.user["airline_name"]
        flights = search_as_airline_staff(
            airline_name,
            going_to_airport,
            leaving_from_airport,
            departure_date,
            return_date,
        )
    else:
        flights = general_search(
            leaving_from_airport,
            going_to_airport,
            departure_date,
            return_date,
        )

    if request.method == "POST":
        error = None

        # TODO: Change this to not use session variables
        going_to_airport = request.form.get("going_to")
        leaving_from_airport = request.form.get("leaving_from")
        departure_date = request.form.get("departure_date")
        return_date = request.form.get("return_date")

        error = error_check_search(
            leaving_from_airport, going_to_airport, departure_date
        )

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
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT username
            FROM customer
            """
    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    flight = get_flight(id)
    tickets = get_tickets(id)

    if request.method == "POST":
        user_info = get_user_info(g.user["username"], g.user_type)
        ticket_id = request.form["ticket"]
        purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if g.user_type == "customer":
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    INSERT INTO purchases(ticket_id, customer_email, purchase_date)
                    VALUES ({},'{}','{}')
                    """
            cursor.execute(
                query.format(ticket_id, user_info["username"], purchase_date)
            )
            conn.commit()
            cursor.close()

        elif g.user_type == "booking_agent":
            booking_agent_id = g.user["booking_agent_id"]
            session["customer_email"] = customer_email = request.form["customer_email"]
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    INSERT INTO purchases(ticket_id, customer_email, purchase_date, booking_agent_id)
                    VALUES ({},'{}','{}','{}')
                    """
            cursor.execute(
                query.format(ticket_id, customer_email, purchase_date, booking_agent_id)
            )
            conn.commit()
            cursor.close()

        return redirect(url_for("airline.index"))

    return render_template(
        "airline/purchase_ticket.html",
        flight=flight,
        tickets=tickets,
        customers=customers,
    )


@bp.route("/continue_staff_action", methods=("GET", "POST"))
@login_required
def staff_action():
    username = g.user["username"]

    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT permission_type FROM permission WHERE username = '{}'"
        cursor.execute(query.format(username))
        permission_type = cursor.fetchone()
        cursor.close()

        staff_action = request.form.get("staff_action")

        if (
            permission_type["permission_type"] == "admin"
            and staff_action == "create_new_flight"
        ):
            return redirect(url_for("airline.add_flight"))
        elif (
            permission_type["permission_type"] == "write"
            or permission_type["permission_type"] == "admin"
        ) and staff_action == "change_status":
            return redirect(url_for("airline.change_status"))
        elif (
            permission_type["permission_type"] == "admin"
            and staff_action == "add_airplane"
        ):
            return redirect(url_for("airline.add_airplane"))
        elif (
            permission_type["permission_type"] == "admin"
            and staff_action == "add_new_airport"
        ):
            return redirect(url_for("airline.add_new_airport"))
        elif (
            permission_type["permission_type"] == "admin"
            and staff_action == "grant_new_permission"
        ):
            return redirect(url_for("airline.grant_new_permission"))
        elif (
            permission_type["permission_type"] == "admin"
            and staff_action == "add_booking_agent"
        ):
            return redirect(url_for("airline.add_booking_agent"))
        else:
            error = f"User {username} doesn't have the permission"

        flash(error)
    return render_template("airline/index.html")


@bp.route("/add_flight", methods=("GET", "POST"))
# search func.
def add_flight():
    if request.method == "POST":
        username = g.user["username"]
        airline_name = g.user["airline_name"]
        flight_num = request.form["flight_num"]
        departure_airport = request.form["departure_airport"]
        departure_time = request.form["departure_time"]
        arrival_airport = request.form["arrival_airport"]
        arrival_time = request.form["arrival_time"]
        price = request.form["price"]
        STATUS = request.form["STATUS"]
        airplane_id = request.form["airplane_id"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM flight WHERE flight_num = '{}'"
        cursor.execute(query.format(flight_num))
        flight_data = cursor.fetchone()
        if flight_data is not None:
            error = f"Flight has existed in the system"
        else:
            query = """
                INSERT INTO flight
                (flight_num, airline_name, departure_airport, 
                departure_time, arrival_airport, arrival_time, 
                price, STATUS, airplane_id) 
                VALUES ('{}','{}','{}',
                '{}','{}','{}',
                '{}','{}','{}') 
                """
            cursor.execute(
                query.format(
                    flight_num,
                    airline_name,
                    departure_airport,
                    departure_time,
                    arrival_airport,
                    arrival_time,
                    price,
                    STATUS,
                    airplane_id,
                )
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_flight.html")


@bp.route("/add_airplane", methods=("GET", "POST"))
# search func.
def add_airplane():
    if request.method == "POST":
        airline_name = g.user["airline_name"]
        airplane_id = request.form["airplane_id"]
        seats = request.form["seats"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM airplane WHERE airline_name = '{}' and\
              airplane_id = '{}'"
        cursor.execute(query.format(airline_name, airplane_id))
        data = cursor.fetchone()
        if data is not None:
            error = f"Airplane has existed in the system"
        else:
            query = """
                INSERT INTO airplane
                (airline_name, airplane_id, seats) 
                VALUES ('{}','{}','{}') 
                """
            cursor.execute(query.format(airline_name, airplane_id, seats))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_airplane.html")


@bp.route("/add_new_airport", methods=("GET", "POST"))
# search func.
def add_new_airport():
    if request.method == "POST":
        airport_name = request.form["airport_name"]
        airport_city = request.form["airport_city"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM airport WHERE airport_name = '{}' and\
              airport_city = '{}'"
        cursor.execute(query.format(airport_name, airport_city))
        data = cursor.fetchone()
        if data is not None:
            error = f"Airport has existed in the system"
        else:
            query = """
                INSERT INTO airport
                (airport_name, airport_city) 
                VALUES ('{}','{}') 
                """
            cursor.execute(query.format(airport_name, airport_city))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_new_airport.html")


@bp.route("/change_status", methods=("GET", "POST"))
# search func.
def change_status():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT flight_num
            FROM flight
            """
    cursor.execute(query)
    flight_nums = cursor.fetchall()
    cursor.close()
    error = None

    if request.method == "POST":
        flight_num = request.form["flight_num"]
        STATUS = request.form["STATUS"]
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM flight WHERE flight_num = '{}' and STATUS = '{}'"
        cursor.execute(query.format(flight_num, STATUS))
        data = cursor.fetchone()
        if data is not None:
            error = f"STATUS is the same"
        else:
            query = """
                UPDATE flight
                SET STATUS = '{}' 
                WHERE flight_num = '{}'
                """
            cursor.execute(query.format(STATUS, flight_num))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/change_status.html", flight_nums=flight_nums)


@bp.route("/grant_new_permission", methods=("GET", "POST"))
# search func.
def grant_new_permission():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT username
            FROM airline_staff
            """
    cursor.execute(query)
    usernames = cursor.fetchall()
    cursor.close()
    error = None

    if request.method == "POST":
        username = request.form["username"]
        permission_type = request.form["permission_type"]
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = (
            "SELECT * FROM permission WHERE username = '{}' and permission_type = '{}'"
        )
        cursor.execute(query.format(username, permission_type))
        data = cursor.fetchone()
        if data is not None:
            error = f"Permission is the same"
        else:
            query = """
                UPDATE permission
                SET permission_type = '{}' 
                WHERE username = '{}'
                """
            cursor.execute(query.format(permission_type, username))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/grant_new_permission.html", usernames=usernames)


@bp.route("/add_booking_agent", methods=("GET", "POST"))
# search func.
def add_booking_agent():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        booking_agent_id = request.form["booking_agent_id"]
        airline_name = request.form["airline_name"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM booking_agent WHERE username = '{}'"
        cursor.execute(query.format(username))
        data = cursor.fetchone()
        if data is not None:
            error = f"Booking agent has existed in the system"
        else:
            query = """
                INSERT INTO booking_agent
                (username, password,first_name,last_name,booking_agent_id) 
                VALUES ('{}','{}','{}','{}','{}') 
                """
            cursor.execute(
                query.format(
                    username,
                    generate_password_hash(password),
                    first_name,
                    last_name,
                    booking_agent_id,
                )
            )

            conn.commit()
            cursor.close()

            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            error = None

            query = """
            INSERT INTO booking_agent_work_for
            (email, airline_name)
            VALUES ('{}','{}')
            """
            cursor.execute(query.format(username, airline_name))
            conn.commit()
            cursor.close()

            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_booking_agent.html")
