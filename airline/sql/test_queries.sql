SELECT (SELECT COUNT(*)
        FROM purchases as p1
        WHERE p1.booking_agent_id is not null)
           /
       (SELECT COUNT(*)
        FROM purchases as p2) as ratio;
