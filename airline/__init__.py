from flask import Flask
from dotenv import load_dotenv

import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    # create and configure the app
    app.config.from_mapping(
        SECRET_KEY="dev",
        MYSQLHOST=os.getenv("MYSQLHOST"),
        MYSQLUSER=os.getenv("MYSQLUSER"),
        MYSQLPASSWORD=os.getenv("MYSQLPASSWORD"),
        MYSQLDATABASE=os.getenv("MYSQLDATABASE"),
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
