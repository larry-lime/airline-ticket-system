SELECT
  COUNT(*) AS total_tickets_sold
FROM
  purchases
WHERE
  purchases.booking_agent_id = 1
  AND purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)

