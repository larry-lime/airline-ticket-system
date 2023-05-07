SELECT DISTINCT
  a.airport_city
FROM
  flight AS f
  JOIN (
    ticket
    NATURAL JOIN purchases
  ) ON ticket.flight_num = f.flight_num
  JOIN airport AS a ON f.arrival_airport = a.airport_name
WHERE
  ticket.airline_name = 'Delta'
  AND purchases.purchase_date >= (NOW() - INTERVAL 1 YEAR)
GROUP BY
  f.arrival_airport
ORDER BY
  COUNT(*) DESC
LIMIT
  3;

SELECT
COUNT(*) * 10 AS commission
FROM
purchases
WHERE
purchases.booking_agent_id = 1
AND purchases.purchase_date > DATE_SUB(NOW(), INTERVAL 30 DAY);

