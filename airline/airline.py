import datetime
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# TODO: Split this into three files: one for each user type
from werkzeug.security import generate_password_hash
from airline.auth import login_required, user_is_logged_in
from airline.db import get_db

from airline.util import (
    get_airports,
    get_posts,
    get_flight,
    get_tickets,
    get_user_info,
    refund,
    customer_get_purchases,
    plot_customer_purchase_totals,
    booking_agent_get_purchases,
)

from airline.search_util import (
    search_all_flights,
    search_all_tickets,
    search_as_airline_staff,
    general_search,
)
from airline.staff_util import (
    get_next_month_flights,
    get_top_agents_of_year,
    get_top_agents_of_month,
    top_customers,
    top_destinations_of_year,
    top_destinations_of_last_3_months,
    get_total_tickets_sold_1_year,
    get_total_tickets_sold_1_months,
    get_revenue_dist,
    plot_revenue_split,
)
from airline.agent_util import (
    get_commission,
    get_total_tickets_sold,
    get_top_5_customers_1_year,
    get_top_5_customers_6_months,
    plot_top_5_customers_1_year,
    plot_top_5_customers_6_months,
)
from airline.error_checking import (
    error_check_search,
    error_check_update_graph,
    error_check_update_summary,
)

bp = Blueprint("airline", __name__)


@bp.route("/<int:post_id>/post", methods=("GET", "POST"))
def post(post_id):
    post = request.args.get("post_id")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT *
            FROM post
            WHERE id = {}
            """
    cursor.execute(query.format(post_id))
    post = cursor.fetchone()
    cursor.close()

    return render_template("airline/post.html", post=post)


@bp.route("/", methods=("GET", "POST"))
def index():
    airports = get_airports()
    delete_ticket_id = request.args.get("delete_ticket_id")
    username = g.user["username"] if user_is_logged_in() else None
    purchases = posts = []
    graphJSON = graphJSON2 = graphJSON3 = graphJSON9 = graphJSON10 = flights = None
    commission = total_tickets_sold = None
    month_top_booking_agents = (
        year_top_booking_agents
    ) = frequent_customers = year_top_destinations = month_top_destinations = []
    top_5_customers_6_months = top_5_customers_1_year = []
    revenue_dist = total_tickets_sold_1_month = total_tickets_sold_1_year = 0
    posts = get_posts()

    if delete_ticket_id is not None:
        refund(delete_ticket_id)

    if g.user_type == "airline_staff" and g.user:
        airline_name = g.user["airline_name"]
        flights = get_next_month_flights(airline_name)
        month_top_booking_agents = get_top_agents_of_month(airline_name)
        year_top_booking_agents = get_top_agents_of_year(airline_name)
        frequent_customers = top_customers(airline_name)
        year_top_destinations = top_destinations_of_year(airline_name)
        month_top_destinations = top_destinations_of_last_3_months(airline_name)
        total_tickets_sold_1_month = get_total_tickets_sold_1_months(airline_name)
        total_tickets_sold_1_year = get_total_tickets_sold_1_year(airline_name)
        revenue_dist = get_revenue_dist(airline_name)
        graphJSON3 = plot_revenue_split(airline_name)

    elif g.user_type == "customer" and g.user:
        purchases = customer_get_purchases(username, g.user_type) if user_is_logged_in() else None
        graphJSON = plot_customer_purchase_totals(username)

    elif g.user_type == "booking_agent" and g.user:
        commission = get_commission(g.user["booking_agent_id"])
        booking_agent_id = g.user["booking_agent_id"]
        total_tickets_sold = get_total_tickets_sold(g.user["booking_agent_id"])
        top_5_customers_6_months = get_top_5_customers_6_months(g.user["booking_agent_id"])
        top_5_customers_1_year = get_top_5_customers_1_year(g.user["booking_agent_id"])

        purchases = booking_agent_get_purchases(booking_agent_id) if user_is_logged_in() else None
        graphJSON9 = plot_top_5_customers_1_year(booking_agent_id)
        graphJSON10 = plot_top_5_customers_6_months(booking_agent_id)

    if request.method == "POST":
        leaving_from_airport = request.form.get("leaving_from")
        going_to_airport = request.form.get("going_to")
        departure_date = request.form.get("departure_date")
        return_date = request.form.get("return_date")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        button_pressed = request.args.get("bp")

        if button_pressed == "update_graph":
            # TODO: Fix this so it works
            error = error_check_update_graph(start_date, end_date)
            graphJSON = plot_customer_purchase_totals(username, start_date, end_date)
            if error is None:
                # NOTE: The exception here will never happen
                return render_template(
                    "airline/index.html",
                    airports=airports,
                    flights=flights,
                    graphJSON=graphJSON,
                    posts=posts,
                    purchases=purchases,
                    month_top_booking_agents=month_top_booking_agents,
                    year_top_booking_agents=year_top_booking_agents,
                    frequent_customers=frequent_customers,
                    year_top_destinations=year_top_destinations,
                    month_top_destinations=month_top_destinations,
                )
        elif button_pressed == "update_summary":
            error = error_check_update_summary(start_date, end_date)
            commission = get_commission(g.user["booking_agent_id"], start_date, end_date)
            total_tickets_sold = get_total_tickets_sold(
                g.user["booking_agent_id"], start_date, end_date
            )
            if error is None:
                return render_template(
                    "airline/index.html",
                    airports=airports,
                    flights=flights,
                    posts=posts,
                    purchases=purchases,
                    commission=commission,
                    total_tickets_sold=total_tickets_sold,
                    start_date=start_date,
                    end_date=end_date,
                )
        elif button_pressed == "search_flights":
            error = error_check_search(leaving_from_airport, going_to_airport, departure_date)

            if error is None:
                return redirect(
                    url_for(
                        "airline.search_results",
                        going_to_airport=going_to_airport,
                        leaving_from_airport=leaving_from_airport,
                        departure_date=departure_date,
                        return_date=return_date,
                    )
                )

        flash(error)

    return render_template(
        "airline/index.html",
        airports=airports,
        flights=flights,
        graphJSON=graphJSON,
        graphJSON2=graphJSON2,
        graphJSON3=graphJSON3,
        graphJSON9=graphJSON9,
        graphJSON10=graphJSON10,
        posts=posts,
        purchases=purchases,
        month_top_booking_agents=month_top_booking_agents,
        year_top_booking_agents=year_top_booking_agents,
        frequent_customers=frequent_customers,
        year_top_destinations=year_top_destinations,
        month_top_destinations=month_top_destinations,
        commission=commission,
        total_tickets_sold=total_tickets_sold,
        top_5_customers_6_months=top_5_customers_6_months,
        top_5_customers_1_year=top_5_customers_1_year,
        total_tickets_sold_1_month=total_tickets_sold_1_month,
        total_tickets_sold_1_year=total_tickets_sold_1_year,
        revenue_dist=revenue_dist,
    )


@bp.route("/search", methods=("GET", "POST"))
def search_results():
    get_all_flights = request.args.get("search_all_flights")
    get_all_tickets = request.args.get("search_all_tickets")
    going_to_airport = request.args.get("going_to_airport")
    leaving_from_airport = request.args.get("leaving_from_airport")
    departure_date = request.args.get("departure_date")
    return_date = request.args.get("return_date")

    airports = get_airports()
    flights = []

    if get_all_flights is not None and get_all_flights == "True":
        flights = search_all_flights()

    elif get_all_tickets is not None and get_all_tickets == "True":
        flights = search_all_tickets()

    elif g.user_type == "airline_staff":
        airline_name = g.user["airline_name"]
        flights = search_as_airline_staff(
            airline_name,
            going_to_airport,
            leaving_from_airport,
            departure_date,
            return_date,
        )
    else:
        flights = general_search(
            leaving_from_airport,
            going_to_airport,
            departure_date,
            return_date,
        )

    if request.method == "POST":
        error = None

        # TODO: Change this to not use session variables
        going_to_airport = request.form.get("going_to")
        leaving_from_airport = request.form.get("leaving_from")
        departure_date = request.form.get("departure_date")
        return_date = request.form.get("return_date")

        error = error_check_search(leaving_from_airport, going_to_airport, departure_date)

        if error is None:
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                    return_date=return_date,
                )
            )

        flash(error)

    return render_template(
        "airline/results.html",
        going_to_airport=going_to_airport,
        leaving_from_airport=leaving_from_airport,
        departure_date=departure_date,
        return_date=return_date,
        flights=flights,
        airports=airports,
    )


@bp.route("/<int:id>/purchase", methods=("GET", "POST"))
@login_required
def purchase_ticket(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT username
            FROM customer
            """
    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    flight = get_flight(id)
    tickets = get_tickets(id)

    # TODO: Add a trigger to UPDATE a booking agent's commission when a ticket is purchased
    if request.method == "POST":
        customer_email = None
        user_info = get_user_info(g.user["username"], g.user_type)
        ticket_id = request.form.get("ticket")
        error = None

        if ticket_id is None:
            error = "Ticket is required."

        if g.user_type == "booking_agent":
            session["customer_email"] = customer_email = request.form.get("customer_email")
            if customer_email is None:
                error = "Customer email is required."

        if error is None:
            purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if g.user_type == "customer":
                conn = get_db()
                cursor = conn.cursor()
                query = """
                        INSERT INTO purchases(ticket_id, customer_email, purchase_date)
                        VALUES ({},'{}','{}')
                        """
                cursor.execute(query.format(ticket_id, user_info["username"], purchase_date))
                conn.commit()
                cursor.close()

            elif g.user_type == "booking_agent":
                booking_agent_id = g.user["booking_agent_id"]

                conn = get_db()
                cursor = conn.cursor()
                query = """
                        INSERT INTO purchases(ticket_id,
                                              customer_email,
                                              purchase_date,
                                              booking_agent_id)
                        VALUES ({},'{}','{}','{}')
                        """
                cursor.execute(
                    query.format(ticket_id, customer_email, purchase_date, booking_agent_id)
                )
                conn.commit()
                cursor.close()

            return redirect(url_for("airline.index"))

        flash(error)

    return render_template(
        "airline/purchase_ticket.html",
        flight=flight,
        tickets=tickets,
        customers=customers,
    )


@bp.route("/continue_staff_action", methods=("GET", "POST"))
@login_required
def staff_action():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT permission_type FROM permission WHERE username = '{}'"
        username = g.user["username"]

        cursor.execute(query.format(username))
        permission_type = cursor.fetchone()
        cursor.close()

        staff_action = request.form.get("staff_action")

        if permission_type["permission_type"] == "admin" and staff_action == "create_new_flight":
            return redirect(url_for("airline.add_flight"))
        elif (
            permission_type["permission_type"] in ["write", "admin"]
            and staff_action == "change_status"
        ):
            return redirect(url_for("airline.change_status"))
        elif permission_type["permission_type"] == "admin" and staff_action == "add_airplane":
            return redirect(url_for("airline.add_airplane"))
        elif permission_type["permission_type"] == "admin" and staff_action == "add_new_airport":
            return redirect(url_for("airline.add_new_airport"))
        elif (
            permission_type["permission_type"] == "admin" and staff_action == "grant_new_permission"
        ):
            return redirect(url_for("airline.grant_new_permission"))
        elif permission_type["permission_type"] == "admin" and staff_action == "add_booking_agent":
            return redirect(url_for("airline.add_booking_agent"))
        else:
            error = f"User {username} doesn't have the permission"

        flash(error)
    return render_template("airline/index.html")


@bp.route("/add_flight", methods=("GET", "POST"))
# search func.
def add_flight():
    if request.method == "POST":
        g.user["username"]
        airline_name = g.user["airline_name"]
        flight_num = request.form["flight_num"]
        departure_airport = request.form["departure_airport"]
        departure_time = request.form["departure_time"]
        arrival_airport = request.form["arrival_airport"]
        arrival_time = request.form["arrival_time"]
        price = request.form["price"]
        status = request.form["STATUS"]
        airplane_id = request.form["airplane_id"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM flight WHERE flight_num = '{}'"
        cursor.execute(query.format(flight_num))
        flight_data = cursor.fetchone()
        if flight_data is not None:
            error = "Flight has existed in the system"
        else:
            query = """
                INSERT INTO flight
                (flight_num, airline_name, departure_airport, 
                departure_time, arrival_airport, arrival_time, 
                price, STATUS, airplane_id) 
                VALUES ('{}','{}','{}',
                '{}','{}','{}',
                '{}','{}','{}') 
                """
            cursor.execute(
                query.format(
                    flight_num,
                    airline_name,
                    departure_airport,
                    departure_time,
                    arrival_airport,
                    arrival_time,
                    price,
                    status,
                    airplane_id,
                )
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_flight.html")


@bp.route("/add_airplane", methods=("GET", "POST"))
# search func.
def add_airplane():
    if request.method == "POST":
        airline_name = g.user["airline_name"]
        airplane_id = request.form["airplane_id"]
        seats = request.form["seats"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM airplane WHERE airline_name = '{}' and\
              airplane_id = '{}'"
        cursor.execute(query.format(airline_name, airplane_id))
        data = cursor.fetchone()
        if data is not None:
            error = "Airplane has existed in the system"
        else:
            query = """
                INSERT INTO airplane
                (airline_name, airplane_id, seats) 
                VALUES ('{}','{}','{}') 
                """
            cursor.execute(query.format(airline_name, airplane_id, seats))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_airplane.html")


@bp.route("/add_new_airport", methods=("GET", "POST"))
# search func.
def add_new_airport():
    if request.method == "POST":
        airport_name = request.form["airport_name"]
        airport_city = request.form["airport_city"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM airport WHERE airport_name = '{}' and\
              airport_city = '{}'"
        cursor.execute(query.format(airport_name, airport_city))
        data = cursor.fetchone()
        if data is not None:
            error = "Airport has existed in the system"
        else:
            query = """
                INSERT INTO airport
                (airport_name, airport_city) 
                VALUES ('{}','{}') 
                """
            cursor.execute(query.format(airport_name, airport_city))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_new_airport.html")


@bp.route("/change_status", methods=("GET", "POST"))
def change_status():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT flight_num
            FROM flight
            """
    cursor.execute(query)
    flight_nums = cursor.fetchall()
    cursor.close()
    error = None

    if request.method == "POST":
        flight_num = request.form["flight_num"]
        STATUS = request.form["STATUS"]
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM flight WHERE flight_num = '{}' and STATUS = '{}'"
        cursor.execute(query.format(flight_num, STATUS))
        data = cursor.fetchone()
        if data is not None:
            error = "STATUS is the same"
        else:
            query = """
                UPDATE flight
                SET STATUS = '{}' 
                WHERE flight_num = '{}'
                """
            cursor.execute(query.format(STATUS, flight_num))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/change_status.html", flight_nums=flight_nums)


@bp.route("/grant_new_permission", methods=("GET", "POST"))
def grant_new_permission():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT username
            FROM airline_staff
            """
    cursor.execute(query)
    usernames = cursor.fetchall()
    cursor.close()
    error = None

    if request.method == "POST":
        username = request.form["username"]
        permission_type = request.form["permission_type"]
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM permission WHERE username = '{}' and permission_type = '{}'"
        cursor.execute(query.format(username, permission_type))
        data = cursor.fetchone()
        if data is not None:
            error = "Permission is the same"
        else:
            query = """
                UPDATE permission
                SET permission_type = '{}' 
                WHERE username = '{}'
                """
            cursor.execute(query.format(permission_type, username))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/grant_new_permission.html", usernames=usernames)


@bp.route("/add_booking_agent", methods=("GET", "POST"))
def add_booking_agent():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        booking_agent_id = request.form["booking_agent_id"]
        airline_name = request.form["airline_name"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        query = "SELECT * FROM booking_agent WHERE username = '{}'"
        cursor.execute(query.format(username))
        data = cursor.fetchone()
        if data is not None:
            error = "Booking agent has existed in the system"
        else:
            query = """
                INSERT INTO booking_agent
                (username, password,first_name,last_name,booking_agent_id) 
                VALUES ('{}','{}','{}','{}','{}') 
                """
            cursor.execute(
                query.format(
                    username,
                    generate_password_hash(password),
                    first_name,
                    last_name,
                    booking_agent_id,
                )
            )

            conn.commit()
            cursor.close()

            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            error = None

            query = """
            INSERT INTO booking_agent_work_for
            (email, airline_name)
            VALUES ('{}','{}')
            """
            cursor.execute(query.format(username, airline_name))
            conn.commit()
            cursor.close()

            return redirect(url_for("airline.index"))

        conn.commit()
        cursor.close()

        flash(error)

    return render_template("airline/add_booking_agent.html")
