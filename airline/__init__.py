from flask import Flask
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


def create_app():
    app = Flask(__name__)
    # create and configure the app
    app.config.from_mapping(
        SECRET_KEY="dev",
        MYSQL_HOST="localhost",
        MYSQL_USER="root",
        MYSQL_PASSWORD=env_vars["MYSQL_PASSWORD"],
        MYSQL_DB_NAME="airline",
    )

    from . import db

    db.init_app(app)

    # Register the authentication blueprint
    from . import auth

    app.register_blueprint(auth.bp)

    # Register the airline blueprint
    from . import airline

    app.register_blueprint(airline.bp)
    app.add_url_rule("/", endpoint="index")

    return app
