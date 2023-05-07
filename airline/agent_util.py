from airline.db import get_db
from werkzeug.exceptions import abort

import pandas as pd
import json
import plotly
import plotly.express as px

def get_commission(booking_agent_id):
    """
    Gets the commision for the agent for the past 30 days
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT
              COUNT(*) * 10 AS commission
            FROM
              purchases
            WHERE
              purchases.booking_agent_id = {}
              AND purchases.purchase_date > DATE_SUB(NOW(), INTERVAL 30 DAY);
            """
    cursor.execute(query.format(booking_agent_id))
    commission = cursor.fetchone()
    cursor.close()
    return commission
