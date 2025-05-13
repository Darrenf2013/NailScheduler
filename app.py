import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database - using SQLite for simplicity
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///nailbooking.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize the app with the extension
db.init_app(app)

# Load the user loader function
from models import User  # noqa: E402

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    # Import the models
    import models  # noqa: F401

    # Check if database is already initialized
    try:
        user_count = User.query.count()
        if user_count == 0:
            # Database exists but no users - tables are already created
            logging.info("Database exists but no users found")
        else:
            logging.info(f"Database already contains {user_count} users")
    except Exception as e:
        # If error occurs, tables probably don't exist yet
        try:
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
