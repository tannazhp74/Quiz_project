import json

import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restx import Namespace, Resource, cors, fields
from functools import wraps
from flask import Flask, request, jsonify
from app.model.card import Card
from config import Config
from model.user import User
from service.card import CardService
from service.transaction import TransactionService
from service.user import UserService


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
        try:
            UserService.user_register(username, password, email)
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            return {'message': 'User not registered'}, 404


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

        try:
            token, redis_data = UserService.user_login(user)
            return {'token': token, 'redis_data': json.loads(redis_data)}, 200
        except  Exception as e:
            return {'message': 'User not login'}, 404


@quiz_namespace.route('/create_card')
class CreateCard(Resource):
    @quiz_namespace.doc('create card', security='apikey')
    @quiz_namespace.expect(create_card_model)
    @token_required
    def post(self, user_id):
        data = request.get_json()
        card_no = data.get('card_no')
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User not found'}

        try:
            CardService.card_insert(user_id=user_id, card_no=card_no)
            return {'message': 'Card created successfully'}, 201
        except Exception as e:
            return {'message': 'Card not created'}, 404


@quiz_namespace.route('/update_card')
class UpdateCard(Resource):
    @quiz_namespace.doc('Update card', security='apikey')
    @quiz_namespace.expect(update_card_model)
    @token_required
    def put(self):
        data = request.get_json()
        card = Card.query.get(data.get('card_id'))

        if not card:
            return {'message': 'Card not found'}, 404

        # Update card details (except for "SYSTEM_CARD")
        try:
            CardService.card_update(data=data, card=card)
            return {'message': 'Card updated successfully'}, 200
        except Exception as e:

            return {'message': 'Card not updated'}, 404


@quiz_namespace.route('/delete_card/<int:card_id>')
class DeleteCard(Resource):
    @quiz_namespace.doc('Delete card', security='apikey')
    @quiz_namespace.expect()
    @token_required
    def delete(self, card_id):
        card = Card.query.get(card_id)
        if not card:
            return {'message': 'Card not found'}, 404
        try:
            CardService.card_delete(card)
            return {'message': 'Card marked as deleted'}, 200
        except Exception as e:

            return {'message': 'Card not deleted'}, 404


@quiz_namespace.route('/create_transaction')
class CreateTransaction(Resource):
    @quiz_namespace.doc('Create transaction', security='apikey')
    @quiz_namespace.expect(create_transaction_model)
    @token_required
    def post(self):
        data = request.get_json()
        card_id = data.get('card_id')
        amount = data.get('amount')
        description = data.get('description')

        card = Card.query.get(card_id)

        if not card:
            return {'message': 'Card not found'}, 404

        if card.status != "ACTIVE":
            return {'message': 'Card is not active'}, 400

        try:
            TransactionService.transaction_insert(card=card, amount=amount, description=description)
            return {'message': 'Transaction created successfully'}, 201
        except Exception as e:

            return {'message': 'Transaction not created'}, 404


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
            transaction_list = TransactionService.transaction_list_detailed(card)

        elif filter_type == 'summary':
            transaction_list = TransactionService.transaction_list_summary(user_id)

        else:
            return {'message': 'Invalid filter type'}, 400

        return {'transactions': transaction_list}, 200


@quiz_namespace.route('/list_cards')
class ListCards(Resource):
    @quiz_namespace.doc('List cards', security='apikey')
    @token_required
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User not found'}, 401
        cards = Card.query.filter_by(user_id=user_id).all()
        if not cards:
            return {'message': "The user hasn't this card no"}, 401
        try:
            card_list = CardService.card_list(cards)
            return {'card list': card_list}, 200
        except Exception as e:
            return {'message': 'Card not listed'}, 404
