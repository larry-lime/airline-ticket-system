import logging
import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    # create and configure the app
    app.config.from_mapping(
        SECRET_KEY="dev",
        MYSQL_HOST="localhost",
        MYSQL_USER="root",
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD"),
        MYSQL_DB_NAME="flask_tutorial_blog",
    )

    from . import db

    db.init_app(app)

    # Register the authentication blueprint
    from . import auth

    app.register_blueprint(auth.bp)

    # Register the blog blueprint
    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    return app
