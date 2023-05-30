import mysql.connector
import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQLHOST"],
            user=current_app.config["MYSQLUSER"],
            password=current_app.config["MYSQLPASSWORD"],
            database=current_app.config["MYSQLDATABASE"],
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    conn = mysql.connector.connect(
        host=current_app.config["MYSQLHOST"],
        user=current_app.config["MYSQLUSER"],
        password=current_app.config["MYSQLPASSWORD"],
    )

    # Create tables
    cursor = conn.cursor()
    with current_app.open_resource("init_db/init_db.sql") as f:
        queries = f.read().decode("utf8")
        for query in queries.split(";"):
            if query.strip():
                cursor.execute(query)
        conn.commit()
    cursor.close()


def insert_sample_data():
    conn = get_db()

    cursor = conn.cursor()
    with current_app.open_resource("sql/inserts.sql") as f:
        queries = f.read().decode("utf8")
        for query in queries.split(";"):
            if query.strip():
                cursor.execute(query)
        conn.commit()
        data = cursor.fetchall()
        print(data) if data else print("Sample Data Inserted")
    cursor.close()


def insert_posts(username, airport, destination_city, post_body):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    query = """
            INSERT INTO post (title,
                              summary,
                              body,
                              image_url,
                              author_username,
                              reference_airport
                              )
            VALUES ('{}', '{}', "{}", '{}', '{}', '{}')
            """
    # Get all the available tickets for a given flight
    cursor.execute(
        query.format(
            f"Travel Destinations in {destination_city}",
            f"The various wonderful places to go in {destination_city}!",
            post_body,
            "",
            username,
            airport,
        )
    )
    tickets = cursor.fetchall()
    conn.commit()
    cursor.close()

    return tickets


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
