SELECT DISTINCT a.airport_city
FROM flight as f 
JOIN (ticket NATURAL JOIN purchases) on ticket.flight_num = f.flight_num
JOIN airport as a on f.arrival_airport = a.airport_name
WHERE ticket.airline_name = 'Delta' and 
purchases.purchase_date >= (NOW() - INTERVAL 1 YEAR)
GROUP BY f.arrival_airport
ORDER BY COUNT(*) DESC
LIMIT 3

