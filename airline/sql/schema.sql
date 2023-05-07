-- Set global sql_mode to allow for group by without aggregation
SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

-- Blog Tables
DROP TABLE IF EXISTS post;

DROP TABLE IF EXISTS user;

-- Airline Database
DROP TABLE IF EXISTS booking_agent_work_for;

DROP TABLE IF EXISTS booking_agent;

DROP TABLE IF EXISTS purchases;

DROP TABLE IF EXISTS ticket;

DROP TABLE IF EXISTS flight;

DROP TABLE IF EXISTS airplane;

DROP TABLE IF EXISTS permission;

DROP TABLE IF EXISTS airline_staff;

DROP TABLE IF EXISTS airline;

DROP TABLE IF EXISTS airport;

DROP TABLE IF EXISTS customer;

-- Blog Tables
CREATE TABLE
  post (
    id INT AUTO_INCREMENT NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    body TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    image_url VARCHAR(255) NOT NULL,
    author_username VARCHAR(50),
    reference_airport VARCHAR(50) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (author_username) REFERENCES airline_staff(username),
    FOREIGN KEY (reference_airport) REFERENCES airport(airport_name)
  );

-- Airline Dashboard Tables
CREATE TABLE
  airline (
    airline_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (airline_name)
  );

-- Airline Staff Table
CREATE TABLE
  airline_staff (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    airline_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (username),
    FOREIGN KEY (airline_name) REFERENCES airline (airline_name)
  );

-- User Permissions
CREATE TABLE
  permission (
    username VARCHAR(50) NOT NULL,
    permission_type VARCHAR(50) NOT NULL,
    PRIMARY KEY (username, permission_type),
    FOREIGN KEY (username) REFERENCES airline_staff (username)
  );

-- Airplane Table
CREATE TABLE
  airplane (
    airline_name VARCHAR(50) NOT NULL,
    airplane_id INT(11) NOT NULL,
    seats INT(11) NOT NULL,
    PRIMARY KEY (airline_name, airplane_id),
    FOREIGN KEY (airline_name) REFERENCES airline (airline_name)
  );

-- Airport Table
CREATE TABLE
  airport (
    airport_name VARCHAR(50) NOT NULL,
    airport_city VARCHAR(50) NOT NULL,
    PRIMARY KEY (airport_name)
  );

-- Booking Agent Table
CREATE TABLE
  booking_agent (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    booking_agent_id INT(11) NOT NULL,
    commission INT DEFAULT 0,
    PRIMARY KEY (username)
  );

-- Booking Agent Works For Table
CREATE TABLE
  booking_agent_work_for (
    email VARCHAR(50) NOT NULL,
    airline_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (email, airline_name),
    FOREIGN KEY (email) REFERENCES booking_agent (username),
    FOREIGN KEY (airline_name) REFERENCES airline (airline_name)
  );

-- Customer Table
CREATE TABLE
  customer (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    building_number VARCHAR(30) NOT NULL,
    street VARCHAR(30) NOT NULL,
    city VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    passport_number VARCHAR(30) NOT NULL,
    passport_expiration DATE NOT NULL,
    passport_country VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    PRIMARY KEY (username)
  );

-- Flight Table
CREATE TABLE
  flight (
    airline_name VARCHAR(50) NOT NULL,
    flight_num INT(11) NOT NULL,
    departure_airport VARCHAR(50) NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_airport VARCHAR(50) NOT NULL,
    arrival_time DATETIME NOT NULL,
    price DECIMAL(10, 0) NOT NULL,
    STATUS VARCHAR(50) NOT NULL,
    airplane_id INT(11) NOT NULL,
    PRIMARY KEY (airline_name, flight_num),
    FOREIGN KEY (airline_name, airplane_id) REFERENCES airplane (airline_name, airplane_id),
    FOREIGN KEY (departure_airport) REFERENCES airport (airport_name),
    FOREIGN KEY (arrival_airport) REFERENCES airport (airport_name)
  );

-- Ticket Table
CREATE TABLE
  ticket (
    ticket_id INT(11) NOT NULL,
    airline_name VARCHAR(50) NOT NULL,
    flight_num INT(11) NOT NULL,
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (airline_name, flight_num) REFERENCES flight (airline_name, flight_num)
  );

-- Purchases Table
CREATE TABLE
  purchases (
    ticket_id INT(11) NOT NULL,
    customer_email VARCHAR(50) NOT NULL,
    booking_agent_id INT(11),
    purchase_date DATE NOT NULL,
    PRIMARY KEY (ticket_id, customer_email),
    FOREIGN KEY (ticket_id) REFERENCES ticket (ticket_id),
    FOREIGN KEY (customer_email) REFERENCES customer (username)
  );
