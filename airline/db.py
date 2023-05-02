import mysql.connector

import click
from flask import current_app, g


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


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    insert_sample_data()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
