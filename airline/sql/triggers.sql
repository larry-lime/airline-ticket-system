CREATE TRIGGER update_commission AFTER
INSERT
  ON purchases FOR EACH ROW BEGIN IF NEW.booking_agent_id IS NOT NULL THEN
UPDATE booking_agent AS b
SET
  commission = commission + 0.4 * (
    SELECT
      price
    FROM
      purchases
      NATURAL JOIN ticket
      NATURAL JOIN flight
    WHERE
      purchases.ticket_id = NEW.ticket_id
    LIMIT
      1
  )
WHERE
  b.booking_agent_id = NEW.booking_agent_id;

END IF;
END;
