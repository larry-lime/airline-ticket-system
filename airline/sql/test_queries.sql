SELECT
  COUNT(*) AS total_tickets_sold
FROM
  purchases
WHERE
  purchases.booking_agent_id = 1
  AND purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY);

SELECT
  customer_email,
  COUNT(*) AS total_tickets_bought
FROM
  purchases
WHERE
  booking_agent_id = 1
  AND purchase_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY
  customer_email
ORDER BY
  total_tickets_bought DESC
LIMIT
  5
