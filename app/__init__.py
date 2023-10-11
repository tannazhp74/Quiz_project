import logging

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
oauthClient = None

_log = logging.getLogger(__name__)
