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

from airline.auth import login_required, user_is_logged_in
from airline.db import get_db
from airline.util import *

bp = Blueprint("airline", __name__)


# TODO: Update this and populate this with content when the post() table is updated with actual content
@bp.route("/<int:post_id>/post", methods=("GET", "POST"))
def post(post_id):
    return render_template("airline/post.html", post_id=post_id)


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
    # TODO: Remove this when the post() function above is finished and when there is actual post content in the database
    posts = [
        {
            "id": 1,
            "title": "Welcome to Airline",
            "summary": "This is a website for airline reservation",
            "image_url": "https://www.wikihow.com/images/thumb/6/65/Italicize-Text-in-HTML-Step-1.jpg/aid2477375-v4-677px-Italicize-Text-in-HTML-Step-1.jpg",
        },
        {
            "id": 2,
            "title": "New Routes Added!",
            "summary": "We have added new routes to our list of destinations.",
            "image_url": "https://www.wikihow.com/images/thumb/6/65/Italicize-Text-in-HTML-Step-1.jpg/aid2477375-v4-677px-Italicize-Text-in-HTML-Step-1.jpg",
        },
        {
            "id": 2,
            "title": "Travel Tips",
            "summary": "Here are some helpful tips for making your air travel experience more comfortable and enjoyable.",
            "image_url": "https://www.wikihow.com/images/thumb/6/65/Italicize-Text-in-HTML-Step-1.jpg/aid2477375-v4-677px-Italicize-Text-in-HTML-Step-1.jpg",
        },
    ]

    purchases = None
    graphJSON = None

    if user_is_logged_in():
        username = g.user["username"]
        purchases = get_purchases(username, g.user_type)
        graphJSON = plot_purchases_totals(username)

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
        graphJSON=graphJSON,
        posts=posts,
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
