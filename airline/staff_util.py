from airline.db import get_db


def get_next_month_flights(airline_name):
    """
    Returns all flights of the next month
    """
    # TODO: Add missing columns like departure_city, arrival_city, and formatted time
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT *
            FROM flight
            WHERE airline_name = '{}' and 
            departure_time <= ( NOW( ) + INTERVAL 1 MONTH )
            """
    cursor.execute(query.format(airline_name))
    flights = cursor.fetchall()
    cursor.close()
    return flights


def get_top_agents_of_month(airline_name):
    """
    Returns the top 5 booking agents of the last month
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT DISTINCT b1.username
            FROM booking_agent as b1 
            JOIN purchases as p1 on b1.booking_agent_id = p1.booking_agent_id
            JOIN booking_agent_work_for as bw on b1.username = bw.email
            WHERE bw.airline_name = '{}' and 
            p1.purchase_date >= (NOW() - INTERVAL 1 MONTH)
            GROUP BY b1.booking_agent_id
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """
    cursor.execute(query.format(airline_name))
    month_top_booking_agents = cursor.fetchall()
    cursor.close()
    return month_top_booking_agents


def get_top_agents_of_year(airline_name):
    """
    Returns the top 5 booking agents of the last year
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT DISTINCT b1.username
            FROM booking_agent as b1 
            JOIN purchases as p1 on b1.booking_agent_id = p1.booking_agent_id
            JOIN booking_agent_work_for as bw on b1.username = bw.email
            WHERE bw.airline_name = '{}' and 
            p1.purchase_date >= (NOW() - INTERVAL 1 YEAR)
            GROUP BY b1.booking_agent_id
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """
    cursor.execute(query.format(airline_name))
    year_top_booking_agents = cursor.fetchall()
    cursor.close()
    return year_top_booking_agents


def top_destinations_of_year(airline_name):
    """
    Returns the top 3 destinations of the last year
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT DISTINCT a.airport_city
            FROM flight as f 
            JOIN (ticket NATURAL JOIN purchases) on ticket.flight_num = f.flight_num
            JOIN airport as a on f.arrival_airport = a.airport_name
            WHERE ticket.airline_name = '{}' and 
            purchases.purchase_date >= (NOW() - INTERVAL 1 YEAR)
            GROUP BY f.arrival_airport
            ORDER BY COUNT(*) DESC
            LIMIT 3
            """
    cursor.execute(query.format(airline_name))
    year_top_destinations = cursor.fetchall()
    cursor.close()
    return year_top_destinations


def top_destinations_of_last_3_months(airline_name):
    """
    Returns the top 3 destinations of the last 3 months
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT DISTINCT a.airport_city
            FROM flight as f 
            JOIN (ticket NATURAL JOIN purchases) on ticket.flight_num = f.flight_num
            JOIN airport as a on f.arrival_airport = a.airport_name
            WHERE ticket.airline_name = '{}' and 
            purchases.purchase_date >= (NOW() - INTERVAL 3 MONTH)
            GROUP BY f.arrival_airport
            ORDER BY COUNT(*) DESC
            LIMIT 3
            """
    cursor.execute(query.format(airline_name))
    month_top_destinations = cursor.fetchall()
    cursor.close()
    return month_top_destinations


def top_customers(airline_name):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT *
            FROM purchases as p NATURAL JOIN ticket as t NATURAL JOIN flight
            WHERE t.airline_name = '{}' and 
            p.purchase_date >= (NOW() - INTERVAL 1 YEAR)
            GROUP BY p.customer_email
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """
    cursor.execute(query.format(airline_name))
    frequent_customers = cursor.fetchall()
    cursor.close()
    return frequent_customers


def get_total_tickets_sold_1_months(airline_name):
    """
    Returns the total number of tickets sold by the airline
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT
              COUNT(*) as total_tickets
            FROM
              purchases
              NATURAL JOIN ticket
              NATURAL JOIN flight
            WHERE airline_name = '{}'
            AND purchase_date >= (NOW() - INTERVAL 1 MONTH)
            """
    cursor.execute(query.format(airline_name))
    total_tickets = cursor.fetchone()
    cursor.close()
    return total_tickets or 0


def get_total_tickets_sold_1_year(airline_name):
    """
    Returns the total number of tickets sold by the airline
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT
              COUNT(*) as total_tickets
            FROM
              purchases
              NATURAL JOIN ticket
              NATURAL JOIN flight
            WHERE airline_name = '{}'
            AND purchase_date >= (NOW() - INTERVAL 1 YEAR)
            """
    cursor.execute(query.format(airline_name))
    total_tickets = cursor.fetchone()
    cursor.close()
    return total_tickets or 0


def get_revenue_dist(airline_name):
    """
    Returns what percentage of the revenue is from direct sales and what percentage is from booking agents
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # divide total volume by total volume of direct sales
    query = """
            SELECT (SELECT COUNT(*)
                FROM purchases as p1
                WHERE p1.booking_agent_id is not null)
                   /
               (SELECT COUNT(*)
                FROM purchases as p2) as ratio;
            """
    cursor.execute(query.format(airline_name))
    revenue_ratio = cursor.fetchone()
    cursor.close()
    return int(revenue_ratio["ratio"] * 100)
