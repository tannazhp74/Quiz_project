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

transaction_ns = Namespace(
    "transaction",
    description="transaction related operations",
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


@transaction_ns.route("/")
class CreateTransListRest(UserResource):
    def options(self):
        pass

    def post(self):
        data = request.get_json()
        card_id = data.get('card_id')
        amount = data.get('amount')
        description = data.get('description')

        card = Card.query.get(card_id)
        if not card or card.status != 'ACTIVE':
            return {'message': 'Card not found'}, 404

        # Create a new transaction associated with the card
        new_transaction = Transaction(card_id=card.id, amount=amount, description=description)
        db.session.add(new_transaction)
        db.session.commit()

        return {'message': 'Transaction created successfully'}, 201


    def get(self,card_id):

        card = Card.query.get(card_id)
        if not card:
            return jsonify({'message': 'Card not found'}), 404

        filter_type = request.json.get('filter')  # The filter argument specifies the view type

        if filter_type == 'detailed':
            # Retrieve transactions associated with the card in a detailed view
            transactions = Transaction.query.filter_by(card_id=card.id).all()
            transactions_desc = transactions.query.filter_by(description=request.description).all()
            transaction_list = [
                {

                    'id': t.id,
                    'amount': t.amount,
                    'description': t.description,
                    'date_created': t.date_created
                }
                for t in transactions_desc
            ]
        elif filter_type == 'summary':
            user_id = request.user_id  # Assuming you have access to the user's ID from the token

            # Retrieve user's active and passive cards
            active_cards = Card.query.filter_by(user_id=user_id, status="ACTIVE").all()
            passive_cards = Card.query.filter_by(user_id=user_id, status="PASSIVE").all()

            # Calculate the total amount spent on active and passive cards
            active_total_amount = sum([t.amount for card in active_cards for t in Transaction.query.filter_by(card_id=card.id).all()])
            passive_total_amount = sum([t.amount for card in passive_cards for t in Transaction.query.filter_by(card_id=card.id).all()])

            transaction_list = {
                'active_cards_count': len(active_cards),
                'active_total_amount': active_total_amount,
                'passive_total_amount': passive_total_amount
            }
        else:
            return ({'message': 'Invalid filter type'}), 400

        return ({'transactions': transaction_list}), 200
