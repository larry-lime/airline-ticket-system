import mysql.connector

import click
from flask import current_app, g
from gpt4free import theb


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DB_NAME"],
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    conn = get_db()

    # Create tables
    cursor = conn.cursor()
    with current_app.open_resource("sql/schema.sql") as f:
        queries = f.read().decode("utf8")
        for query in queries.split(";"):
            if query.strip():
                cursor.execute(query)
        conn.commit()
        data = cursor.fetchall()
        print(data) if data else print("Tables Created")

    cursor.close()

def create_triggers():
    conn = get_db()

    # Create tables
    cursor = conn.cursor()
    with current_app.open_resource("sql/triggers.sql") as f:
        queries = f.read().decode("utf8")
        for query in queries.split(";"):
            if query.strip():
                cursor.execute(query)
        conn.commit()
        data = cursor.fetchall()
        print(data) if data else print("Triggers added")

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
    insert_sample_data()
    create_triggers()
    click.echo("Initialized the database.")


@click.command("insert-posts")
def insert_posts_command():
    """Create a sample post"""
    username = "billythekid"
    destination_city = "Boston"
    airport = "BOS"

    x = f"Write a 200 word blogpost about travel destinations in {destination_city}."
    body = "".join(theb.Completion.create(x))
    insert_posts(username, airport, destination_city, body)
    click.echo("Inserted sample post")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(insert_posts_command)
