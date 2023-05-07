CREATE TRIGGER update_commission
AFTER INSERT ON purchases
FOR EACH ROW
BEGIN
    IF NEW.booking_agent_id IS NOT NULL THEN
        UPDATE booking_agent AS b
        SET commission = commission + 10
        WHERE b.booking_agent_id = NEW.booking_agent_id;
    END IF;
END;
