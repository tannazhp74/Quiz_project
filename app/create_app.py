import logging
from app.model import *

_log = logging.getLogger(__name__)


def create_app(test=False) -> Flask:
    """Construct the core application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123454321@localhost/QuizProjectDB"
    db.init_app(app)

    return app
