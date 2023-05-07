from airline.db import get_db
from werkzeug.exceptions import abort

import pandas as pd
import json
import plotly
import plotly.express as px


def get_commission(booking_agent_id, start_date="", end_date=""):
    """
    Gets the commision for the agent for the past 30 days
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if start_date != "" and end_date != "":
        query = """
                SELECT
                  SUM(price * 0.4) AS commission
                FROM
                  purchases
                  NATURAL JOIN ticket
                  NATURAL JOIN flight
                WHERE
                  purchases.booking_agent_id = {}
                  AND purchase_date >= '{}'
                  AND purchase_date <= '{}';
                """
        cursor.execute(query.format(booking_agent_id, start_date, end_date))
    else:
        query = """
                SELECT
                  SUM(price * 0.4) AS commission
                FROM
                  purchases
                  NATURAL JOIN ticket
                  NATURAL JOIN flight
                WHERE
                  purchases.booking_agent_id = {}
                  AND purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY);
                """
        cursor.execute(query.format(booking_agent_id))
    commission = cursor.fetchone()
    cursor.close()
    return commission


def get_total_tickets_sold(booking_agent_id, start_date="", end_date=""):
    """
    Gets the total tickets sold by the agent for the past 30 days or a specified date range
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if start_date != "" and end_date != "":
        query = """
                SELECT
                  COUNT(*) AS total_tickets_sold
                FROM
                  purchases
                WHERE
                  purchases.booking_agent_id = {}
                  AND purchase_date >= '{}'
                  AND purchase_date <= '{}'
                """
        cursor.execute(query.format(booking_agent_id, start_date, end_date))
    else:
        query = """
                SELECT
                  COUNT(*) AS total_tickets_sold
                FROM
                  purchases
                WHERE
                  purchases.booking_agent_id = {}
                  AND purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """
        cursor.execute(query.format(booking_agent_id))
    total_tickets_sold = cursor.fetchone()
    cursor.close()
    return total_tickets_sold

def get_top_5_customers_6_months(booking_agent_id):
    """
    Gets the top 5 customers for the agent based on the number of tickets sold in the past 6 months
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT customer_email, COUNT(*) AS total_tickets_bought
            FROM purchases
            WHERE booking_agent_id = {}
            AND purchase_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY customer_email
            ORDER BY total_tickets_bought DESC
            LIMIT 5
            """
    cursor.execute(query.format(booking_agent_id))
    top_5_customers = cursor.fetchall()
    cursor.close()
    return top_5_customers

def get_top_5_customers_1_year(booking_agent_id):
    """
    Gets the top 5 customers for the agent based on the number of tickets sold in the past year
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT customer_email, COUNT(*) AS total_tickets_bought
            FROM purchases
            WHERE booking_agent_id = {}
            AND purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY customer_email
            ORDER BY total_tickets_bought DESC
            LIMIT 5
            """
    cursor.execute(query.format(booking_agent_id))
    top_5_customers = cursor.fetchall()
    cursor.close()
    return top_5_customers

