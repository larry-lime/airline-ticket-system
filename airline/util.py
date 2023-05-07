from airline.db import get_db
from werkzeug.exceptions import abort

import pandas as pd
import json
import plotly
import plotly.express as px
from flask import flash


def refund(ticket_id):
    """
    Refunds a ticket
    """
    conn = get_db()
    cursor = conn.cursor()
    query = "DELETE FROM purchases WHERE ticket_id = '{}'"
    cursor.execute(query.format(ticket_id))
    conn.commit()
    cursor.close()


def get_tickets(flight_num):
    """
    Returns a list of all tickets for a given flight
    """
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


def get_airports():
    """
    Returns a list of all airports in the database
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT airport_name, airport_city
            FROM airport
            """
    cursor.execute(query)
    airport_list = cursor.fetchall()
    cursor.close()
    return airport_list


def get_airlines():
    """
    Returns a list of all airlines in the database
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT airline_name
            FROM airline
            """
    cursor.execute(query)
    airlines = cursor.fetchall()
    cursor.close()
    return airlines


def load_purchases(username, start_date="", end_date=""):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Get the sum of purchases for the last 6 months

    # TODO: Test this to make sure it works
    if start_date != "" and end_date != "":
        query = """
                SELECT MONTH(purchase_date) as month,
                       SUM(price)           as total
                FROM (SELECT purchase_date,
                             price,
                             customer_email
                      FROM purchases
                               NATURAL JOIN ticket
                               NATURAL JOIN flight
                      WHERE customer_email = '{}'
                        AND purchase_date >= '{}'
                        AND purchase_date <= '{}'
                      ) as t
                GROUP BY month;
                """
        # Get all the available tickets for a given flight and date range
        cursor.execute(query.format(username, start_date, end_date))
    else:
        query = """
                SELECT MONTH(purchase_date) as month,
                       SUM(price)           as total
                FROM (SELECT purchase_date,
                             price,
                             customer_email
                      FROM purchases
                               NATURAL JOIN ticket
                               NATURAL JOIN flight
                      WHERE customer_email = '{}'
                        AND purchase_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)) as t
                GROUP BY month;
                """
        # Get all the available tickets for a given flight
        cursor.execute(query.format(username))
    purchases = cursor.fetchall()
    cursor.close()
    return purchases


def plot_customer_purchase_totals(username, start_date="", end_date=""):
    # TODO: Not perfect, so fix this!
    num_months = 6
    if start_date != "" and end_date != "":
        num_months = max(
            # convert start and end date to epoch time
            (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days // 30, 1
        )
    amount_per_month = [0 for _ in range(12)]
    purchases = load_purchases(username, start_date, end_date)
    for purchase in purchases:
        amount_per_month[purchase["month"] - 1] = purchase["total"]

    # Default behavior: show the total amount of purchases for the last 6 months
    # get current month
    this_month = pd.Timestamp.now().month

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    df = pd.DataFrame(
        {
            "$USD Amount": [
                amount_per_month[i] for i in range(this_month - num_months, this_month)
            ],
            "Months": [months[i] for i in range(this_month - num_months, this_month)],
        }
    )
    fig = px.bar(df, x="Months", y="$USD Amount", barmode="group")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def customer_get_purchases(username, user_type):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # if user_type == 'customer':
    query = """
            SELECT airline_name,
                flight_num,
                ticket_id,
                customer_email,
                booking_agent_id,
                purchase_date,
                departure_airport,
                DATE_FORMAT(departure_time, '%h:%i %p') AS departure_time,
                DATE_FORMAT(departure_time, '%Y-%m-%d') AS departure_date,
                arrival_airport,
                DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
                DATE_FORMAT(arrival_time, '%Y-%m-%d') AS arrival_date,
                price,
                status,
                airplane_id,
                a1.airport_city as departure_city,
                a2.airport_city as arrival_city 

            FROM purchases
            NATURAL JOIN ticket
            NATURAL JOIN flight
            JOIN airport as a1 on departure_airport = a1.airport_name
            JOIN airport as a2 on arrival_airport = a2.airport_name
            WHERE customer_email = '{}'
        """
    # Get all the available tickets for a given flight
    # TODO: Add conditional to allow booking_agents to get purchases too
    cursor.execute(query.format(username))
    purchases = cursor.fetchall()
    cursor.close()

    return purchases


def booking_agent_get_purchases(agent_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT airline_name,
            flight_num,
            ticket_id,
            customer_email,
            booking_agent_id,
            purchase_date,
            departure_airport,
            DATE_FORMAT(departure_time, '%h:%i %p') AS departure_time,
            DATE_FORMAT(departure_time, '%Y-%m-%d') AS departure_date,
            arrival_airport,
            DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
            DATE_FORMAT(arrival_time, '%Y-%m-%d') AS arrival_date,
            price,
            status,
            airplane_id,
            a1.airport_city as departure_city,
            a2.airport_city as arrival_city 

        FROM purchases
        NATURAL JOIN ticket
        NATURAL JOIN flight
        JOIN airport as a1 on departure_airport = a1.airport_name
        JOIN airport as a2 on arrival_airport = a2.airport_name
        WHERE booking_agent_id = '{}'
    """
    # Get all the available tickets for a given flight
    cursor.execute(query.format(agent_id))
    purchases = cursor.fetchall()
    cursor.close()

    return purchases


def get_user_info(username, user_type):
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

    if user_info is None:
        abort(404)

    return user_info


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
