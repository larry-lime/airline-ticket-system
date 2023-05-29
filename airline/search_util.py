from airline.db import get_db
from werkzeug.exceptions import abort

import pandas as pd
import json
import plotly
import plotly.express as px


def search_as_airline_staff(
    airline_name,
    going_to_airport,
    leaving_from_airport,
    departure_date,
    return_date,
):
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
                a2.airport_city as arrival_city, 
                (SELECT purchases.customer_email FROM ticket NATURAL JOIN purchases
                WHERE ticket.flight_num = f.flight_num) as customer_email
            FROM flight as f
            JOIN airport as a1 on f.departure_airport = a1.airport_name
            JOIN airport as a2 on f.arrival_airport = a2.airport_name
            WHERE airline_name = '{}' 
            and (f.departure_airport = '{}' and f.arrival_airport = '{}')
            or (f.departure_airport = '{}' and f.arrival_airport = '{}' and f.departure_time ='{}')
            or (f.departure_airport = '{}' and f.arrival_airport = '{}' and f.departure_time ='{}')
            """
    cursor.execute(
        query.format(
            airline_name,
            leaving_from_airport,
            going_to_airport,
            leaving_from_airport,
            going_to_airport,
            departure_date,
            going_to_airport,
            leaving_from_airport,
            return_date,
        )
    )
    flights = cursor.fetchall()
    cursor.close()
    return flights


def general_search(
    leaving_from_airport,
    going_to_airport,
    departure_date,
    return_date,
):
    """
    This function is used to search for flights by customers and booking agents
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    error = None
    # TODO: Add return date functionality in the future
    if leaving_from_airport and going_to_airport and departure_date:
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
                WHERE (f.departure_airport = '{}' and f.arrival_airport = '{}')
                OR (f.departure_airport = '{}' and f.arrival_airport = '{}' and f.departure_time ='{}')
                """
        # OR (f.departure_airport = '{}' and f.arrival_airport = '{}' and f.departure_time ='{}')
        cursor.execute(
            query.format(
                leaving_from_airport,
                going_to_airport,
                leaving_from_airport,
                going_to_airport,
                departure_date,
            )
        )
    elif leaving_from_airport and going_to_airport:
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
                WHERE (f.departure_airport = '{}' and f.arrival_airport = '{}')
                """
        cursor.execute(
            query.format(
                leaving_from_airport,
                going_to_airport,
            )
        )

    flights = cursor.fetchall()
    cursor.close()
    return flights


def search_all_flights():
    """
    This function is used to search for all flights
    """
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
                a2.airport_city as arrival_city,
                t.ticket_id as ticket_id,
                p.ticket_id as purchased_ticket_id,
                p.customer_email as customer_email
            FROM flight as f
            NATURAL JOIN ticket as t
            LEFT JOIN purchases as p on t.ticket_id = p.ticket_id
            JOIN airport as a1 on f.departure_airport = a1.airport_name
            JOIN airport as a2 on f.arrival_airport = a2.airport_name
            """
    cursor.execute(query)
    all_flights = cursor.fetchall()
    cursor.close()
    return all_flights


# TODO: Finish this function
def search_all_tickets():
    """
    This function is used to search for all tickets
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Get a list of all tickets that have not been purchased
    # Flights that have tickets
    query = """
            SELECT airline_name,
                flight_num,
                ticket_id,
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

            FROM ticket
            NATURAL JOIN flight
            JOIN airport as a1 on departure_airport = a1.airport_name
            JOIN airport as a2 on arrival_airport = a2.airport_name
            WHERE ticket_id NOT IN (SELECT ticket_id FROM purchases)
            """
    cursor.execute(query)
    all_tickets = cursor.fetchall()
    cursor.close()
    return all_tickets
