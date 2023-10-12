from os import environ


class Config:
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get('FLASK_ENV')
    FLASK_RUN_PORT = environ.get("FLASK_RUN_PORT")
    MAX_CONTENT_LENGTH = environ.get("MAX_CONTENT_LENGTH")
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    SECRET_KEY = environ.get("SECRET_KEY")
