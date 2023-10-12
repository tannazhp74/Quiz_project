from flask import Flask
from app import db
from config import Config
from rest.api_v1 import api_v1
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(api_v1)

    db.init_app(app)

    return app
