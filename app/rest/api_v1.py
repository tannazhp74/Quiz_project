import logging

from flask import Blueprint
from flask_restx import Api

from app.rest.v1.LoginRest import user_ns
from app.rest.v1.CardRest import card_ns
from app.rest.v1.TransactionRest import transaction_ns


_log = logging.getLogger(__name__)

ALL_NAMESPACES = [
    user_ns,
    card_ns,
    transaction_ns
]


def create_api_v1_bp() -> Blueprint:
    """
    Create the API V1 blueprint.
    """
    api_bp = Blueprint("api_v1", __name__, url_prefix="/")
    # Doc page url will be `/strata/api/doc`. A bit confusing.
    api = Api(api_bp, doc=False, version="1.0", title="Pocket Strata API Version 1")
    for ns in ALL_NAMESPACES:
        api.add_namespace(ns)
    return api_bp
