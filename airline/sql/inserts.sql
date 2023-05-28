DELETE
FROM ticket;

DELETE
FROM flight;

DELETE
FROM airplane;

DELETE
FROM airline_staff;

DELETE
FROM customer;

DELETE
FROM booking_agent;

DELETE
FROM airport;

DELETE
FROM airline;

DELETE
FROM airline_staff;

-- airline table
INSERT INTO airline (airline_name)
VALUES ('Delta'),
       ('United'),
       ('American'),
       ('Southwest'),
       ('JetBlue');
;

-- airline_staff table
INSERT INTO airline_staff (username,
                           PASSWORD,
                           first_name,
                           last_name,
                           date_of_birth,
                           airline_name)
VALUES ('johndoe',
        'password123',
        'John',
        'Doe',
        '1990-01-01',
        'Delta'),
       ('janedoe',
        'password456',
        'Jane',
        'Doe',
        '1995-05-05',
        'United'),
       ('bobsmith',
        'password789',
        'Bob',
        'Smith',
        '1985-10-10',
        'American'),
       ('sallysmith',
        'password321',
        'Sally',
        'Smith',
        '1989-02-14',
        'Southwest'),
       ('billythekid',
        'password654',
        'Billy',
        'Kid',
        '1997-12-25',
        'JetBlue');

-- permission table
INSERT INTO permission (username, permission_type)
VALUES ('johndoe', 'admin'),
       ('janedoe', 'read'),
       ('bobsmith', 'write'),
       ('sallysmith', 'read'),
       ('billythekid', 'write');

-- airplane table
INSERT INTO airplane (airline_name, airplane_id, seats)
VALUES ('Delta', 1, 200),
       ('United', 2, 180),
       ('American', 3, 160),
       ('Southwest', 4, 140),
       ('JetBlue', 5, 120);

-- airport table
INSERT INTO airport (airport_name, airport_city)
VALUES ('JFK', 'New York City'),
       ('LAX', 'Los Angeles'),
       ('ORD', 'Chicago'),
       ('DFW', 'Dallas'),
       ('MIA', 'Miami'),
       ('SFO', 'San Francisco'),
       ('DEN', 'Denver'),
       ('BOS', 'Boston');

-- Booking Agent Table
INSERT INTO booking_agent (username, password, first_name, last_name, booking_agent_id)
VALUES ('agent1', 'password1', 'John', 'Doe', 1),
       ('agent2', 'password2', 'Jane', 'Smith', 2),
       ('agent3', 'password3', 'Michael', 'Johnson', 3),
       ('agent4', 'password4', 'Emily', 'Brown', 4),
       ('agent5', 'password5', 'David', 'Wilson', 5);

-- Booking Agent Work For Table
INSERT INTO booking_agent_work_for (email, airline_name)
VALUES ('agent1', 'Delta'),
       ('agent2', 'United'),
       ('agent3', 'American'),
       ('agent4', 'Southwest'),
       ('agent5', 'JetBlue');

-- Customer Table
-- TODO: Hash these passwords with generate_password_hash() and insert them again
INSERT INTO customer (username, password, first_name, last_name, building_number, street, city, state, phone_number,
                      passport_number, passport_expiration, passport_country, date_of_birth)
VALUES ('johndoe@gmail.com', 'password1', 'John', 'Doe', '123', 'Main Street', 'City 1', 'State 1', '1234567890',
        'ABC123', '2025-01-01', 'Country 1', '1990-01-01'),
       ('janedoe@gmail.com', 'password2', 'Jane', 'Doe', '456', 'Oak Avenue', 'City 2', 'State 2', '0987654321',
        'DEF456', '2023-06-30', 'Country 2', '1985-05-15'),
       ('jamesbrown@gmail.com', 'password3', 'James', 'Brown', '789', 'Elm Road', 'City 3', 'State 3', '5551234567',
        'GHI789', '2024-12-15', 'Country 3', '1992-09-20'),
       ('sarahjohnson@gmail.com', 'password4', 'Sarah', 'Johnson', '234', 'Cedar Lane', 'City 1', 'State 1',
        '9876543210',
        'JKL234', '2023-08-31', 'Country 1', '1988-11-10'),
       ('millybob@gmail.com', 'password5', 'Milly', 'Bob', '567', 'Pine Street', 'City 2', 'State 2', '1112223333',
        'MNO567', '2022-10-25', 'Country 2', '1995-03-25');

-- Flight Table
INSERT INTO flight (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price,
                    STATUS, airplane_id)
VALUES ('American', 123, 'JFK', '2023-06-01 12:00:00', 'LAX', '2023-06-01 15:00:00', 250, 'On Time', 3),
       ('Delta', 456, 'LAX', '2023-06-15 08:30:00', 'JFK', '2023-06-15 17:45:00', 350, 'Delayed', 1),
       ('United', 789, 'ORD', '2023-06-20 06:15:00', 'LAX', '2023-06-20 09:30:00', 150, 'On Time', 2),
       ('Southwest', 1011, 'DEN', '2023-06-10 15:45:00', 'SFO', '2023-06-10 17:15:00', 100, 'On Time', 4),
       ('JetBlue', 1213, 'BOS', '2023-06-25 09:15:00', 'MIA', '2023-06-25 13:30:00', 200, 'Delayed', 5);

-- Ticket Table
INSERT INTO ticket (ticket_id, airline_name, flight_num)
VALUES (1, 'American', 123),
       (2, 'Delta', 456),
       (3, 'United', 789),
       (4, 'Southwest', 1011),
       (5, 'JetBlue', 1213);

-- Purchases Table
-- INSERT INTO purchases(ticket_id, customer_email, booking_agent_id, purchase_date)
-- VALUES (1, 'johndoe@gmail.com', 1, '2023-06-01'),
--        (2, 'janedoe@gmail.com', 2, '2023-06-10'),
--        (3, 'jamesbrown@gmail.com', 3, '2023-06-15'),
--        (4, 'sarahjohnson@gmail.com', NULL, '2023-06-05'),
--        (5, 'millybob@gmail.com', NULL, '2023-06-20');
