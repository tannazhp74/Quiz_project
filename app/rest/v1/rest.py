import json
from datetime import timedelta, datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restx import Namespace, Resource, cors, fields
from functools import wraps
from flask import Flask, request, jsonify
import jwt
from app import db
from config import Config
from model import Transaction
from model.card import Card
from model.user import User
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(request.headers)
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'Token is missing'}, 401

        user_id = decode_token(token)

        if user_id is None:
            return {'message': 'Invalid or expired token'}, 401

        return f(user_id=user_id, *args, **kwargs)

    return decorated


def decode_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.DecodeError:
        return None  # Token is invalid


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

quiz_namespace = Namespace(
    'Quiz',
    description='Quiz endpoints',
    decorators=[cors.crossdomain(origin="*")],
    authorizations=authorizations
)

register_model = quiz_namespace.model('Register user', {
    'username': fields.String,
    'password': fields.String,
    'email': fields.String
})

login_model = quiz_namespace.model('Login user', {
    'username': fields.String,
    'password': fields.String
})

create_card_model = quiz_namespace.model('Create card model', {
    'card_no': fields.String,
})

update_card_model = quiz_namespace.model('Update card model', {
    'card_id': fields.Integer,
    'card_no': fields.String,
    'status': fields.String
})

create_transaction_model = quiz_namespace.model('Create transaction model', {
    "card_id": fields.Integer,
    "amount": fields.Float,
    "description": fields.String
})

filter_enum_values = ['summary', 'detailed']
list_transaction_model = quiz_namespace.model('List transaction model', {
    "filter": fields.String(enum=filter_enum_values),
    "description": fields.String,
    'card_id': fields.Integer(required=False)
})


@quiz_namespace.route('/')
class Home(Resource):
    @quiz_namespace.doc('home')
    def get(self):
        return {'message': 'Welcome to test'}, 200


@quiz_namespace.route('/register')
class RegisterUser(Resource):
    @quiz_namespace.doc('register')
    @quiz_namespace.expect(register_model)
    def post(self):
        # Get user data from the request
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return {'message': 'Username or email already in use'}, 400

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Automatically create a card for the user and set its status to "ACTIVE"
        auto_card = Card(label='SYSTEM_CARD', user_id=new_user.id, status='PASSIVE', card_no=1)
        db.session.add(auto_card)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201


@quiz_namespace.route('/login')
class Login(Resource):
    @quiz_namespace.doc('login')
    @quiz_namespace.expect(login_model)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Check if the user exists in the database
        user = User.query.filter_by(username=username).first()

        if not user:
            return {'message': 'User not found'}, 401

        # Verify the password
        if not check_password_hash(user.password, password):
            return {'message': 'Incorrect password'}, 401

        # Generate a JWT token for the user
        token_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expiration time
        }

        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')

        redis_client.set(f'user :{user.id}', user.to_json(), ex=300)  # 300 seconds (5 minutes) expiration

        precreated_card = Card.query.filter_by(card_no='SYSTEM_CARD', user_id=user.id).first()
        if precreated_card and precreated_card.status != "ACTIVE":
            precreated_card.status = "ACTIVE"
            db.session.commit()

        redis_data = redis_client.get(f'user :{user.id}')

        return {'token': token, 'redis_data': json.loads(redis_data)}, 200


@quiz_namespace.route('/create_card')
class CreateCard(Resource):
    @quiz_namespace.doc('create card', security='apikey')
    @quiz_namespace.expect(create_card_model)
    @token_required
    def post(self, user_id):
        data = request.get_json()
        card_no = data.get('card_no')

        if not user_id:
            return {'message': 'User not found'}, 404

        card = Card.query.filter_by(card_no=card_no, user_id=user_id).first()

        if card is None:
            new_card = Card(card_no=card_no, user_id=user_id, label='NOT_SYSTEM_CARD', status='ACTIVE')
            db.session.add(new_card)
            db.session.commit()
        else:
            return {'message': 'The user has already this card'}, 400

        return {'message': 'Card created successfully'}, 201


@quiz_namespace.route('/update_card')
class UpdateCard(Resource):
    @quiz_namespace.doc('Update card', security='apikey')
    @quiz_namespace.expect(update_card_model)
    @token_required
    def put(self, user_id):
        data = request.get_json()
        card = Card.query.get(data.get('card_id'))

        if not card:
            return {'message': 'Card not found'}, 404

        # Update card details (except for "SYSTEM_CARD")
        if card.label != "SYSTEM_CARD":
            card.card_no = data.get('card_no', card.card_no)
            card.status = data.get('status', card.status)

            db.session.commit()

        return {'message': 'Card updated successfully'}, 200


@quiz_namespace.route('/delete_card/<int:card_id>')
class DeleteCard(Resource):
    @quiz_namespace.doc('Delete card', security='apikey')
    @quiz_namespace.expect()
    @token_required
    def delete(self, user_id, card_id):
        card = Card.query.get(card_id)

        if not card:
            return {'message': 'Card not found'}, 404

        if not card.label == 'SYSTEM_CARD':
            # Mark the card as "DELETED"
            card.status = "DELETED"
            db.session.commit()
        else:
            return {'message': 'This card can not be modified'}, 401

        return {'message': 'Card marked as deleted'}, 200


@quiz_namespace.route('/create_transaction')
class CreateTransaction(Resource):
    @quiz_namespace.doc('Create transaction', security='apikey')
    @quiz_namespace.expect(create_transaction_model)
    @token_required
    def post(self, user_id):
        data = request.get_json()
        card_id = data.get('card_id')
        amount = data.get('amount')
        description = data.get('description')

        card = Card.query.get(card_id)

        if not card:
            return {'message': 'Card not found'}, 404

        if card.status != "ACTIVE":
            return {'message': 'Card is not active'}, 400

        # Create a new transaction associated with the card
        new_transaction = Transaction(card_id=card.id, amount=amount, description=description)
        db.session.add(new_transaction)
        db.session.commit()

        return {'message': 'Transaction created successfully'}, 201


@quiz_namespace.route('/list_transactions')
class ListTransactions(Resource):
    @quiz_namespace.doc('List transactions', security='apikey')
    @quiz_namespace.expect(list_transaction_model)
    @token_required
    def post(self, user_id):
        filter_type = request.json.get('filter')  # The filter argument specifies the view type

        if filter_type == 'detailed':
            card_id = request.json.get('card_id')

            if not card_id:
                return {'message': 'Enter car id'}, 400

            card = Card.query.get(card_id)

            if not card:
                return {'message': 'Card not found'}, 404

            description = request.json.get('description')  # The filter argument specifies the view type

            # Retrieve transactions associated with the card in a detailed view
            transactions = Transaction.query.filter_by(card_id=card.id).all()
            transaction_list = [
                {
                    'id': t.id,
                    'amount': t.amount,
                    'description': t.description,
                    'date_created': str(t.date_created)
                }
                for t in transactions if t.description == description
            ]

        elif filter_type == 'summary':

            # Retrieve user's active and passive cards
            active_cards = Card.query.filter_by(user_id=user_id, status="ACTIVE").all()
            passive_cards = Card.query.filter_by(user_id=user_id, status="PASSIVE").all()

            # Calculate the total amount spent on active and passive cards
            active_total_amount = sum([t.amount for card in active_cards for t in card.transactions])
            passive_total_amount = sum([t.amount for card in passive_cards for t in card.transactions])

            transaction_list = {
                'active_cards_count': len(active_cards),
                'active_total_amount': active_total_amount,
                'passive_total_amount': passive_total_amount
            }
        else:
            return {'message': 'Invalid filter type'}, 400

        return {'transactions': transaction_list}, 200


@quiz_namespace.route('/list_cards')
class ListCards(Resource):
    @quiz_namespace.doc('List cards', security='apikey')
    @token_required
    def get(self, user_id):
        cards = Card.query.filter_by(user_id=user_id).all()
        card_list = [
            {
                'id': item.id,
                'card_no': item.card_no,
                'label': item.label,
                'user_id': item.user_id,
                'date_created': str(item.date_created),
                'date_modified': str(item.date_modified)
            }
            for item in cards if item.status != 'DELETED'
        ]

        return {'card list': card_list}, 200
