from flask import Flask
# Railway has their own environment variables
import os


def create_app():
    app = Flask(__name__)
# create and configure the app
    app.config.from_mapping(
        SECRET_KEY="dev",
        MYSQL_URL=os.getenv("MYSQL_URL"),
        MYSQLDATABASE=os.getenv("MYSQLDATABASE"),
        MYSQLHOST=os.getenv("MYSQLHOST"),
        MYSQLPASSWORD=os.getenv("MYSQLPASSWORD"),
        MYSQLPORT=os.getenv("MYSQLPORT"),
        MYSQLUSER=os.getenv("MYSQLUSER"),
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
