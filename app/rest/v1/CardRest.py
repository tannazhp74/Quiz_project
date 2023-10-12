# from app.rest.v1.common import DEFAULT_HEADERS_CT_JSON
from http import HTTPStatus
import jwt
from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import app
from app.model.users import User
from app.model.card import Card
from app import db
from app.model.transactions import Transaction
import datetime
from flask_restx import Namespace, cors, fields
from flask_restx import Resource

DEFAULT_CONTENT_TYPE_JSON = "application/json"

# Standard set of headers returned from Strata API
DEFAULT_HEADERS_CT_JSON = {"content-type": DEFAULT_CONTENT_TYPE_JSON}

card_ns = Namespace(
    "card",
    description="card related operations",
    decorators=[cors.crossdomain(origin="*")],
)

class UserResource(Resource):
    """
    Global exception handling for all Strata resources.
    """

    def options(self):
        pass

    def dispatch_request(self, *args, **kwargs):
        return super().dispatch_request(*args, **kwargs)


@card_ns.route("/")
class CreateCardListRest(UserResource):
    def options(self):
        pass

    def post(self):
        data = request.get_json()
        card_no = data.get('card_no')
        user_id = data.get('user_id')

        user = User.query.get(user_id)
        card = Card.query.filter_by(card_no=card_no, user_id=user_id).first()
        if card is None:
            if not user:
                return {'message': 'User not found'}, 404
            else:
                try:
                    # Create a new card and add it to the user's cards
                    new_card = Card(
                        card_no=card_no, user_id=user.id,
                        status='ACTIVE',label='Not_SYSTEM_CARD')
                    db.session.add(new_card)
                    db.session.commit()

                    return {'message': 'Card created successfully'}, 201
                except:
                    return {'message': 'Invalid card number or user id '}, 404
        else:
            return {'message': 'The user already use this card number '}, 404


#
@card_ns.route("/<string:id>/")
class UpdateCardListRest(UserResource):
    def options(self):
        pass

    def put(self, id):
            data = request.get_json()
            card = Card.query.get(id)

            if not card:
                return {'message': 'Card not found'}, 404

            # Update card details (except for "SYSTEM_CARD")
            if card.label != "SYSTEM_CARD":
                if 'card_no' in data and data.get('card_no') :
                    card.card_no = data.get('card_no', card.card_no)
                    db.session.commit()
                    return {'message': 'Card updated successfully'}, 200
                else:
                    return {'message': 'Card_no is not defined'}, 404
            else:
                return {'message': "This card can not be modified"}, 404

    def delete(self,id):
        card = Card.query.get(id)

        if not card:
            return {'message': 'Card not found'}, 404

        if not card.label == 'SYSTEM_CARD':
            # Mark the card as "DELETED"
            card.status = "DELETED"
            db.session.commit()
        else:
            return {'message': 'This card can not be modified'}, 401

        return {'message': 'Card marked as deleted'}, 200
