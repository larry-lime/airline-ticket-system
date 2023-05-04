from airline.db import get_db
from werkzeug.exceptions import abort


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

def get_purchases(username,user_type):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    #if user_type == 'curstomer':
    query = """
            SELECT airline_name,
                flight_num,
                ticket_id,
                customer_email,
                booking_agent_id,
                purchase_date,
                departure_airport,
                DATE_FORMAT(departure_time, '%h:%i %p') AS departure_time,
                arrival_airport,
                DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
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

def ba_get_purchases(username, agent_id):
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
            arrival_airport,
            DATE_FORMAT(arrival_time, '%h:%i %p') AS arrival_time,
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
    # TODO: Add conditional to allow booking_agents to get purchases too
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
