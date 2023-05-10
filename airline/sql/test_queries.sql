SELECT customer_email, SUM(price * 0.4) AS total_commission
FROM purchases
         NATURAL JOIN ticket
         NATURAL JOIN flight
         JOIN (booking_agent join booking_agent_work_for bawf on booking_agent.username = bawf.email)
              on purchases.booking_agent_id = booking_agent.booking_agent_id and flight.airline_name = bawf.airline_name
WHERE purchases.booking_agent_id = 99
  AND purchase_date >= DATE_SUB(NOW()
    , INTERVAL 1 YEAR)
GROUP BY customer_email
ORDER BY total_commission
        DESC
LIMIT 5;
