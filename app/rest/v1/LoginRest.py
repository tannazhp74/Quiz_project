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

user_ns = Namespace(
    "user",
    description="user related operations",
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


@user_ns.route("/register")
class RegisterListRest(UserResource):
    def options(self):
        pass

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
        auto_card = Card(card_no='Auto_CARD', user_id=new_user.id,status='PASSIVE',label='SYSTEM_CARD')
        db.session.add(auto_card)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201


@user_ns.route("/login")
class LoginListRest(UserResource):
    def options(self):
        pass

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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)  # Token expiration time
        }
        # token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        #
        # redis_client.set(f'user :{user.id}', user.to_json, ex=300)  # 300 seconds (5 minutes) expiration

        precreated_card = Card.query.filter_by(card_no='Auto_CARD', user_id=user.id).first()
        if precreated_card and precreated_card.status != "ACTIVE":
            precreated_card.status = "ACTIVE"
            db.session.commit()

        return {'token': "token"}, 200
