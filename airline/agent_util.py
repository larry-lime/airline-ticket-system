from airline.db import get_db

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


def plot_top_5_customers_6_months(booking_agent_id):
    """
    Plots the top 5 customers for the agent based on the number of tickets sold in the past 6 months
    """
    customers = get_top_5_customers_6_months(booking_agent_id)
    customer_list = []
    total_tickets_bought = []

    for customer in customers:
        customer_list.append(customer["customer_email"])
        total_tickets_bought.append(customer["total_tickets_bought"])

    df = pd.DataFrame({"Customers": customer_list, "Total Tickets Bought": total_tickets_bought})
    fig = px.bar(df, x="Customers", y="Total Tickets Bought", barmode="group")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def plot_top_5_customers_1_year(booking_agent_id):
    """
    Plot the top 5 customers for the agent based on total commision of the past year
    """
    customers = get_top_5_customers_1_year(booking_agent_id)

    customers_list = []
    commission_per_customer = []

    for customer in customers:
        customers_list.append(customer["customer_email"])
        commission_per_customer.append(customer["total_commission"])

    df = pd.DataFrame({"Customers": customers_list, "Commission Total": commission_per_customer})
    fig = px.bar(df, x="Customers", y="Commission Total", barmode="group")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_top_5_customers_1_year(booking_agent_id):
    """
    Gets the top 5 customers for the agent based on total commision of the past year
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT customer_email, SUM(price * 0.4) AS total_commission
            FROM purchases
                     NATURAL JOIN ticket
                     NATURAL JOIN flight
                     JOIN (booking_agent
                           JOIN booking_agent_work_for bawf
                           ON booking_agent.username = bawf.email)
                     ON purchases.booking_agent_id = booking_agent.booking_agent_id
                     AND flight.airline_name = bawf.airline_name
            WHERE purchases.booking_agent_id = {}
              AND purchase_date >= DATE_SUB(NOW()
                , INTERVAL 1 YEAR)
            GROUP BY customer_email
            ORDER BY total_commission
                    DESC
            LIMIT 5;
            """
    cursor.execute(query.format(booking_agent_id))
    top_5_customers = cursor.fetchall()
    cursor.close()
    return top_5_customers
