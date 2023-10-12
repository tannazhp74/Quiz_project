import logging



from app.model import *
from app.rest.api_v1 import create_api_v1_bp

_log = logging.getLogger(__name__)


def create_app(test=False) -> Flask:
    """Construct the core application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123454321@localhost/db_test"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config['SECRET_KEY']='12345'
    db.init_app(app)
    api_v1 = create_api_v1_bp()
    app.register_blueprint(api_v1)
    app.config["PROPAGATE_EXCEPTIONS"] = True  # so the error handlers can handle custom exceptions
    # app.register_blueprint(error_handler_blueprint)
    return  app