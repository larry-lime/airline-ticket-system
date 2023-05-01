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

    with current_app.open_resource("schema.sql") as f:
        cursor = conn.cursor()
        query = f.read().decode("utf8")
        cursor.execute(query, multi=True)
        data = cursor.fetchall()
        print(data) if data else print("No returned data")
        cursor.close()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
