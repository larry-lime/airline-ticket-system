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
from werkzeug.exceptions import abort

from airline.auth import login_required
from airline.db import get_db

bp = Blueprint("airline", __name__)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    INSERT INTO post (title, body, author_id)
                    VALUES ('{}', '{}', {})
                    """
            cursor.execute(query.format(title, body, g.user["id"]))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

    return render_template("airline/create.html")


def get_post(id, check_author=True):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT p.id, title, body, created, author_id, username
            FROM post p JOIN user u ON p.author_id = u.id
            WHERE p.id = '{}'
            """
    cursor.execute(query.format(id))
    post = cursor.fetchone()
    cursor.close()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT airport_name, airport_city
                FROM airport
                """
        cursor.execute(query)
        airports = cursor.fetchall()
        cursor.close()

    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        going_to_airport = session["going_to"] = request.form.get("going_to")
        leaving_from_airport = session["leaving_from"] = request.form.get(
            "leaving_from"
        )
        departure_date = session["departure_date"] = request.form.get("departure_date")
        return_date = session["return_date"] = request.form.get("return_date")

        if (
            going_to_airport is None
            or leaving_from_airport is None
            or departure_date is None
        ):
            error = "One or more fields are empty. Please fill out all fields."
        elif return_date is None:
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                )
            )
        else:  # User wants a return trip
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

    return render_template("airline/index.html", airports=airports)


@bp.route("/search", methods=("GET", "POST"))
def search_results():
    if request.method == "GET":
        going_to_airport = request.args.get("going_to_airport")
        leaving_from_airport = request.args.get("leaving_from_airport")
        departure_date = request.args.get("departure_date")
        return_date = request.args.get("return_date")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT airport_name, airport_city
                FROM airport
                """
        cursor.execute(query)
        airports = cursor.fetchall()
        cursor.close()


        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None
        query = """
                SELECT *
                FROM flight
                JOIN airport on flight.departure_airport = airport.airport_name
                """
        cursor.execute(query)
        flights = cursor.fetchall()
        cursor.close()

        return render_template(
            "airline/results.html",
            going_to_airport=going_to_airport,
            leaving_from_airport=leaving_from_airport,
            departure_date=departure_date,
            return_date=return_date,
            flights=flights,
            airports=airports,
        )
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        error = None

        going_to_airport = session["going_to"] = request.form.get("going_to")
        leaving_from_airport = session["leaving_from"] = request.form.get(
            "leaving_from"
        )
        departure_date = session["departure_date"] = request.form.get("departure_date")
        return_date = session["return_date"] = request.form.get("return_date")

        if (
            going_to_airport is None
            or leaving_from_airport is None
            or departure_date is None
        ):
            error = "One or more fields are empty. Please fill out all fields."
        elif return_date is None:
            return redirect(
                url_for(
                    "airline.search_results",
                    going_to_airport=going_to_airport,
                    leaving_from_airport=leaving_from_airport,
                    departure_date=departure_date,
                )
            )
        else:  # User wants a return trip
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


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            cursor = conn.cursor()
            query = """
                    UPDATE post SET title = '{}', body = '{}'
                    WHERE id = '{}'
                    """
            cursor.execute(query.format(title, body, id))
            conn.commit()
            cursor.close()
            return redirect(url_for("airline.index"))

    return render_template("airline/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    conn = get_db()
    cursor = conn.cursor()
    query = "DELETE FROM post WHERE id = '{}'"
    cursor.execute(query.format(id))
    conn.commit()
    cursor.close()
    return redirect(url_for("airline.index"))
