from argparse import Namespace

import jwt
from flask import jsonify, request
from werkzeug.security import check_password_hash
import app
from app.model.users import User
from app.model.card import Card
from app import db
from app.model.transactions import Transaction
import datetime
from flask_restx import Namespace, cors, fields

login_ns = Namespace(
    "login",
    description="login related operations",
    decorators=[cors.crossdomain(origin="*")],
)


@login_ns.route("/")
class LoginListRest():
    def options(self):
        pass

    def post(self):
        print('/////')
        # Get user data from the request
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({'message': 'Username or email already in use'}), 400

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Automatically create a card for the user and set its status to "ACTIVE"
        auto_card = Card(card_no='AUTO_CARD', user_id=new_user.id)
        db.session.add(auto_card)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
# def login(redis_client=None):
def login(redis_client=None):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the user exists in the database
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    # Verify the password
    if not check_password_hash(user.password, password):
        return jsonify({'message': 'Incorrect password'}), 401

    # Generate a JWT token for the user
    token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expiration time (adjust as needed)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
    # redis_client.set(f'user_token:{user.id}', token, ex=300)  # 300 seconds (5 minutes) expiration

    precreated_card = Card.query.filter_by(card_no='AUTO_CARD', user_id=user.id).first()
    if precreated_card and precreated_card.status != "ACTIVE":
        precreated_card.status = "ACTIVE"
        db.session.commit()

    return json